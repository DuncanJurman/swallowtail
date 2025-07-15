"""TrendScannerAgent implementation with TikTok Shop, Amazon, and Google Trends integration."""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Page, Browser

from ...models.research import TrendData, TrendSource
from ...core.config import get_settings
from ..base import BaseAgent, AgentResult


class RateLimiter:
    """Simple rate limiter for API calls."""
    
    def __init__(self, requests_per_minute: int = 10):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if we've exceeded rate limit."""
        async with self.lock:
            now = datetime.now()
            # Remove requests older than 1 minute
            self.requests = [req for req in self.requests if now - req < timedelta(minutes=1)]
            
            if len(self.requests) >= self.requests_per_minute:
                # Wait until the oldest request is 1 minute old
                wait_time = 60 - (now - self.requests[0]).total_seconds()
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    self.requests.pop(0)
            
            self.requests.append(now)


class TikTokShopScanner:
    """Scanner for TikTok Shop trending products."""
    
    def __init__(self, requests_per_minute: int = 10, cache_ttl_minutes: int = 30):
        self.rate_limiter = RateLimiter(requests_per_minute)
        self.cache_ttl_minutes = cache_ttl_minutes
        self.cache = {}
        self.last_error = None
        self.logger = logging.getLogger("TikTokShopScanner")
        self.base_url = "https://www.tiktok.com/shop"
        
    async def scan(self, categories: Optional[List[str]] = None) -> List[TrendData]:
        """Main scanning method that returns TrendData objects."""
        try:
            # Get trending products
            products = await self.extract_trending_products()
            
            # Get viral metrics for each product
            trends = []
            for product in products[:20]:  # Limit to top 20 to avoid rate limits
                viral_metrics = await self._fetch_viral_metrics(product["product_id"])
                if viral_metrics:
                    trend_data = self.to_trend_data(product, viral_metrics)
                    trends.append(trend_data)
                    
            # Sort by growth rate
            trends.sort(key=lambda x: x.growth_rate, reverse=True)
            return trends
            
        except Exception as e:
            self.logger.error(f"Error scanning TikTok Shop: {e}")
            self.last_error = str(e)
            return []
    
    async def extract_trending_products(self) -> List[Dict[str, Any]]:
        """Extract trending products from TikTok Shop."""
        try:
            # For now, we'll use a simplified approach
            # In production, this would use Playwright to render JavaScript
            products = []
            
            # Mock implementation - replace with actual scraping
            html = await self._fetch_page(f"{self.base_url}/trending")
            if not html:
                return []
                
            soup = BeautifulSoup(html, 'html.parser')
            
            for product_card in soup.find_all('div', class_='product-card'):
                try:
                    product = {
                        "product_id": product_card.get('data-product-id'),
                        "name": product_card.find('h3', class_='product-title').text.strip(),
                        "price": self._parse_price(product_card.find('div', class_='price').text),
                        "sales_indicator": product_card.find('div', class_='sales-count').text.strip(),
                        "category": product_card.find('div', class_='category').text.strip(),
                        "rating": float(product_card.find('div', class_='rating').text.strip())
                    }
                    products.append(product)
                except Exception as e:
                    self.logger.warning(f"Error parsing product card: {e}")
                    continue
                    
            return products
            
        except Exception as e:
            self.logger.error(f"Error extracting products: {e}")
            return []
    
    def parse_sales_volume(self, sales_text: str) -> int:
        """Parse sales volume from text like '10K+ sold'."""
        # Extract number and multiplier
        match = re.search(r'([\d.]+)([KMB]?)\+?\s*sold', sales_text, re.IGNORECASE)
        if not match:
            return 0
            
        number = float(match.group(1))
        multiplier = match.group(2).upper() if match.group(2) else ''
        
        multipliers = {'K': 1000, 'M': 1_000_000, 'B': 1_000_000_000}
        return int(number * multipliers.get(multiplier, 1))
    
    def calculate_viral_score(self, viral_metrics: Dict[str, Any]) -> float:
        """Calculate viral score based on engagement metrics."""
        # Normalize different metrics
        video_score = min(viral_metrics.get('videos_count', 0) / 10000, 1.0)
        view_score = min(viral_metrics.get('total_views', 0) / 50_000_000, 1.0)
        creator_score = min(viral_metrics.get('creator_posts', 0) / 500, 1.0)
        growth_score = min(viral_metrics.get('growth_7d', 0), 1.0)
        
        # Weighted average
        weights = {
            'growth': 0.4,
            'views': 0.3,
            'videos': 0.2,
            'creators': 0.1
        }
        
        viral_score = (
            weights['growth'] * growth_score +
            weights['views'] * view_score +
            weights['videos'] * video_score +
            weights['creators'] * creator_score
        )
        
        return round(viral_score, 2)
    
    def to_trend_data(self, product: Dict[str, Any], viral_metrics: Dict[str, Any]) -> TrendData:
        """Convert product data to TrendData model."""
        # Parse sales volume
        sales_volume = self.parse_sales_volume(product.get('sales_indicator', '0'))
        
        # Calculate confidence score
        viral_score = self.calculate_viral_score(viral_metrics)
        confidence = min(0.3 + (viral_score * 0.7), 0.95)  # Base confidence + viral boost
        
        # Extract hashtags as related topics
        hashtags = viral_metrics.get('hashtags', [])
        
        return TrendData(
            source=TrendSource.TIKTOK_SHOP,
            keywords=[product['name'].lower()],
            growth_rate=viral_metrics.get('growth_7d', 0),
            current_volume=sales_volume,
            three_month_avg=int(sales_volume * 0.7),  # Estimate
            yoy_change=0.0,  # Would need historical data
            geographic_hotspots=["US"],  # Default for now
            related_topics=hashtags[:5],  # Top 5 hashtags
            confidence_score=confidence,
            metadata={
                "product_id": product['product_id'],
                "price": str(product['price']),
                "category": product['category'],
                "rating": product['rating'],
                "viral_score": viral_score,
                "video_count": viral_metrics.get('videos_count', 0),
                "total_views": viral_metrics.get('total_views', 0)
            }
        )
    
    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with rate limiting."""
        await self.rate_limiter.wait_if_needed()
        
        try:
            # In production, use Playwright for JavaScript rendering
            # For now, return mock data for testing
            return self._get_mock_trending_page()
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def _fetch_viral_metrics(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Fetch viral metrics for a product."""
        # In production, this would scrape actual TikTok data
        # For now, return mock metrics
        return self._get_mock_viral_metrics(product_id)
    
    async def fetch_with_rate_limit(self, url: str) -> Optional[str]:
        """Fetch URL with rate limiting."""
        return await self._fetch_page(url)
    
    async def fetch_with_cache(self, url: str) -> Optional[str]:
        """Fetch URL with caching."""
        # Check cache
        cache_key = url
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < timedelta(minutes=self.cache_ttl_minutes):
                return cached_data
        
        # Fetch new data
        data = await self._fetch_page(url)
        if data:
            self.cache[cache_key] = (datetime.now(), data)
        
        return data
    
    def _parse_price(self, price_text: str) -> Decimal:
        """Parse price from text."""
        # Remove currency symbols and extract number
        price_match = re.search(r'[\d.]+', price_text)
        return Decimal(price_match.group(0)) if price_match else Decimal('0')
    
    def _get_mock_trending_page(self) -> str:
        """Get mock trending page for development."""
        return """
        <div class="trending-products">
            <div class="product-card" data-product-id="123456">
                <h3 class="product-title">Eco-Friendly Water Bottle</h3>
                <div class="price">$24.99</div>
                <div class="sales-count">10K+ sold</div>
                <div class="rating">4.8</div>
                <div class="category">Home & Kitchen</div>
            </div>
            <div class="product-card" data-product-id="789012">
                <h3 class="product-title">LED Strip Lights</h3>
                <div class="price">$19.99</div>
                <div class="sales-count">50K+ sold</div>
                <div class="rating">4.6</div>
                <div class="category">Home Improvement</div>
            </div>
        </div>
        """
    
    def _get_mock_viral_metrics(self, product_id: str) -> Dict[str, Any]:
        """Get mock viral metrics for development."""
        mock_data = {
            "123456": {
                "videos_count": 1250,
                "total_views": 5_500_000,
                "creator_posts": 45,
                "hashtags": ["#ecofriendly", "#sustainable", "#waterbottle"],
                "growth_7d": 0.35,
                "first_seen": "2024-01-15"
            },
            "789012": {
                "videos_count": 8500,
                "total_views": 45_000_000,
                "creator_posts": 320,
                "hashtags": ["#ledlights", "#roomdecor", "#tiktokfinds"],
                "growth_7d": 0.85,
                "first_seen": "2024-01-20"
            }
        }
        return mock_data.get(product_id, {
            "videos_count": 100,
            "total_views": 500_000,
            "creator_posts": 10,
            "hashtags": ["#trending"],
            "growth_7d": 0.15,
            "first_seen": "2024-01-25"
        })


class AmazonBestSellersScanner:
    """Scanner for Amazon Best Sellers - placeholder for now."""
    
    async def scan(self) -> List[TrendData]:
        """Scan Amazon Best Sellers."""
        # To be implemented after TikTok Shop is complete
        return []


class GoogleTrendsScanner:
    """Scanner for Google Trends - placeholder for now."""
    
    async def scan(self) -> List[TrendData]:
        """Scan Google Trends."""
        # To be implemented after core scanners are complete
        return []


class TrendScannerAgent(BaseAgent):
    """Agent responsible for scanning multiple sources for emerging trends."""
    
    def __init__(self):
        """Initialize TrendScannerAgent without CrewAI dependency."""
        self.name = "TrendScannerAgent"
        self.logger = logging.getLogger(f"agent.{self.name}")
        self.min_growth_threshold = 0.20  # 20% growth minimum
        
        # Initialize scanners
        self.tiktok_scanner = TikTokShopScanner()
        self.amazon_scanner = AmazonBestSellersScanner()
        self.google_trends_scanner = GoogleTrendsScanner()
        
    async def execute(self, context: Dict[str, Any]) -> List[TrendData]:
        """Main execution: scan all sources for trends."""
        self.logger.info("Starting trend scanning across all sources")
        
        # Update configuration from context
        if 'min_growth' in context:
            self.min_growth_threshold = context['min_growth']
        
        # Get trends from all sources
        all_trends = await self.scan_all_sources()
        
        # Filter by growth threshold
        high_growth_trends = self.filter_high_growth(all_trends)
        
        # Rank trends
        ranked_trends = self.rank_trends(high_growth_trends)
        
        self.logger.info(f"Found {len(ranked_trends)} high-growth trends")
        return ranked_trends[:10]  # Top 10 trends
    
    async def scan_all_sources(self) -> List[TrendData]:
        """Scan all configured sources for trends."""
        # Run all scanners in parallel
        tasks = [
            self.tiktok_scanner.scan(),
            self.amazon_scanner.scan(),
            self.google_trends_scanner.scan()
        ]
        
        all_trends = []
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                source_name = ['TikTok Shop', 'Amazon', 'Google Trends'][i]
                self.logger.error(f"Error scanning {source_name}: {result}")
            else:
                all_trends.extend(result)
        
        return all_trends
    
    def filter_high_growth(self, trends: List[TrendData]) -> List[TrendData]:
        """Filter trends by minimum growth threshold."""
        return [
            trend for trend in trends
            if trend.growth_rate >= self.min_growth_threshold
        ]
    
    def rank_trends(self, trends: List[TrendData]) -> List[TrendData]:
        """Rank trends by composite score."""
        # Calculate composite score for each trend
        for trend in trends:
            # Factors: growth rate, confidence, volume
            growth_score = min(trend.growth_rate, 1.0) * 0.5
            confidence_score = trend.confidence_score * 0.3
            volume_score = min(trend.current_volume / 100_000, 1.0) * 0.2
            
            trend.metadata['composite_score'] = growth_score + confidence_score + volume_score
        
        # Sort by composite score
        return sorted(trends, key=lambda x: x.metadata.get('composite_score', 0), reverse=True)