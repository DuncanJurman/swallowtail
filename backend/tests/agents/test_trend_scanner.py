"""Comprehensive tests for TrendScannerAgent with TikTok Shop focus."""

import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.models.research import TrendData, TrendSource


class TestTikTokShopScanner:
    """Test suite for TikTok Shop trend scanning functionality."""
    
    @pytest.fixture
    def mock_tiktok_trending_page(self):
        """Mock HTML response from TikTok Shop trending page."""
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
    
    @pytest.fixture
    def mock_tiktok_product_details(self):
        """Mock product details with viral metrics."""
        return {
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
    
    @pytest.mark.asyncio
    async def test_extract_trending_products(self, mock_tiktok_trending_page):
        """Test extraction of trending products from TikTok Shop."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        # Mock the page fetching
        with patch.object(scanner, '_fetch_page', return_value=mock_tiktok_trending_page):
            products = await scanner.extract_trending_products()
        
        assert len(products) == 2
        assert products[0]["product_id"] == "123456"
        assert products[0]["name"] == "Eco-Friendly Water Bottle"
        assert products[0]["price"] == Decimal("24.99")
        assert products[0]["sales_indicator"] == "10K+ sold"
        assert products[0]["category"] == "Home & Kitchen"
        
        assert products[1]["product_id"] == "789012"
        assert products[1]["sales_indicator"] == "50K+ sold"
    
    @pytest.mark.asyncio
    async def test_parse_sales_volume(self):
        """Test parsing of sales volume indicators."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        # Test various sales formats
        assert scanner.parse_sales_volume("10K+ sold") == 10_000
        assert scanner.parse_sales_volume("50K+ sold") == 50_000
        assert scanner.parse_sales_volume("1.5M sold") == 1_500_000
        assert scanner.parse_sales_volume("100+ sold") == 100
        assert scanner.parse_sales_volume("5.2K sold recently") == 5_200
    
    @pytest.mark.asyncio
    async def test_calculate_viral_score(self, mock_tiktok_product_details):
        """Test viral score calculation based on engagement metrics."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        # High viral score - many videos, high growth
        score1 = scanner.calculate_viral_score(mock_tiktok_product_details["789012"])
        assert 0.8 <= score1 <= 1.0  # Should be high
        
        # Medium viral score - fewer videos, moderate growth
        score2 = scanner.calculate_viral_score(mock_tiktok_product_details["123456"])
        assert 0.4 <= score2 <= 0.7  # Should be medium
    
    @pytest.mark.asyncio
    async def test_scan_with_categories(self):
        """Test scanning specific product categories."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        categories = ["Beauty & Personal Care", "Electronics", "Fashion"]
        
        with patch.object(scanner, '_fetch_category_page') as mock_fetch:
            mock_fetch.return_value = "<div>Mock category page</div>"
            
            results = await scanner.scan_categories(categories)
            
            assert mock_fetch.call_count == 3
            for category in categories:
                mock_fetch.assert_any_call(category)
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner(requests_per_minute=2)
        
        start_time = datetime.now()
        
        # Make 3 requests - should take at least 30 seconds due to rate limiting
        with patch.object(scanner, '_fetch_page', return_value="<div>Mock</div>"):
            for _ in range(3):
                await scanner.fetch_with_rate_limit("https://example.com")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        assert elapsed >= 30  # Should have waited after 2nd request
    
    @pytest.mark.asyncio
    async def test_error_handling_network_failure(self):
        """Test handling of network failures."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        with patch.object(scanner, '_fetch_page', side_effect=Exception("Network error")):
            trends = await scanner.scan()
            
            # Should return empty list on error, not crash
            assert trends == []
            assert scanner.last_error == "Network error"
    
    @pytest.mark.asyncio
    async def test_convert_to_trend_data(self, mock_tiktok_product_details):
        """Test conversion of raw product data to TrendData model."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        product = {
            "product_id": "123456",
            "name": "Eco-Friendly Water Bottle",
            "price": Decimal("24.99"),
            "sales_indicator": "10K+ sold",
            "category": "Home & Kitchen"
        }
        
        viral_metrics = mock_tiktok_product_details["123456"]
        
        trend_data = scanner.to_trend_data(product, viral_metrics)
        
        assert isinstance(trend_data, TrendData)
        assert trend_data.source == TrendSource.TIKTOK_SHOP
        assert "eco-friendly water bottle" in trend_data.keywords
        assert trend_data.growth_rate == 0.35
        assert trend_data.current_volume == 10_000  # From sales parsing
        assert trend_data.confidence_score > 0
        assert len(trend_data.related_topics) > 0
    
    @pytest.mark.asyncio
    async def test_geographic_detection(self):
        """Test detection of geographic trending patterns."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        # Mock different regional pages
        regional_data = {
            "US": ["Product A", "Product B"],
            "UK": ["Product B", "Product C"],
            "CA": ["Product A", "Product C"]
        }
        
        with patch.object(scanner, '_fetch_regional_trends', side_effect=lambda region: regional_data[region]):
            geo_trends = await scanner.analyze_geographic_trends(["US", "UK", "CA"])
            
            # Product A trending in US and CA
            assert geo_trends["Product A"] == ["US", "CA"]
            # Product B trending in US and UK
            assert geo_trends["Product B"] == ["US", "UK"]
            # Product C trending in UK and CA
            assert geo_trends["Product C"] == ["UK", "CA"]
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self):
        """Test caching of fetched data."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner(cache_ttl_minutes=5)
        
        mock_response = "<div>Cached content</div>"
        
        with patch.object(scanner, '_fetch_page', return_value=mock_response) as mock_fetch:
            # First call - should fetch
            result1 = await scanner.fetch_with_cache("https://example.com/trending")
            assert mock_fetch.call_count == 1
            
            # Second call - should use cache
            result2 = await scanner.fetch_with_cache("https://example.com/trending")
            assert mock_fetch.call_count == 1  # Still 1, used cache
            
            assert result1 == result2
    
    @pytest.mark.asyncio
    async def test_full_scan_workflow(self, mock_tiktok_trending_page, mock_tiktok_product_details):
        """Test complete scanning workflow from start to finish."""
        from src.agents.research.trend_scanner import TikTokShopScanner
        
        scanner = TikTokShopScanner()
        
        with patch.object(scanner, '_fetch_page', return_value=mock_tiktok_trending_page):
            with patch.object(scanner, '_fetch_viral_metrics', side_effect=lambda pid: mock_tiktok_product_details.get(pid, {})):
                trends = await scanner.scan()
        
        assert len(trends) == 2
        
        # Check first trend (LED lights - higher viral score)
        trend1 = trends[0]
        assert isinstance(trend1, TrendData)
        assert "LED Strip Lights" in trend1.keywords[0]
        assert trend1.growth_rate == 0.85
        assert trend1.current_volume == 50_000
        
        # Check second trend
        trend2 = trends[1]
        assert "Eco-Friendly Water Bottle" in trend2.keywords[0]
        assert trend2.growth_rate == 0.35


class TestTrendScannerIntegration:
    """Integration tests for the complete TrendScannerAgent."""
    
    @pytest.mark.asyncio
    async def test_trend_scanner_agent_initialization(self):
        """Test TrendScannerAgent initialization with all scanners."""
        from src.agents.research.trend_scanner import TrendScannerAgent
        
        agent = TrendScannerAgent()
        
        assert hasattr(agent, 'tiktok_scanner')
        assert hasattr(agent, 'amazon_scanner')
        assert hasattr(agent, 'google_trends_scanner')
        assert agent.min_growth_threshold == 0.20
    
    @pytest.mark.asyncio
    async def test_execute_with_context(self):
        """Test agent execution with context parameters."""
        from src.agents.research.trend_scanner import TrendScannerAgent
        
        agent = TrendScannerAgent()
        
        context = {
            'seed_keywords': ['sustainable', 'eco-friendly'],
            'categories': ['Home & Kitchen', 'Beauty'],
            'min_growth': 0.30
        }
        
        with patch.object(agent, 'scan_all_sources', return_value=[]) as mock_scan:
            result = await agent.execute(context)
            
            mock_scan.assert_called_once()
            assert agent.min_growth_threshold == 0.30  # Updated from context
    
    @pytest.mark.asyncio 
    async def test_trend_aggregation(self):
        """Test aggregation of trends from multiple sources."""
        from src.agents.research.trend_scanner import TrendScannerAgent
        
        agent = TrendScannerAgent()
        
        # Mock trends from different sources
        tiktok_trends = [
            TrendData(
                source=TrendSource.TIKTOK_SHOP,
                keywords=["water bottle"],
                growth_rate=0.5,
                current_volume=10000
            )
        ]
        
        amazon_trends = [
            TrendData(
                source=TrendSource.AMAZON,
                keywords=["water bottle"],
                growth_rate=0.3,
                current_volume=50000
            )
        ]
        
        with patch.object(agent.tiktok_scanner, 'scan', return_value=tiktok_trends):
            with patch.object(agent.amazon_scanner, 'scan', return_value=amazon_trends):
                aggregated = await agent.scan_all_sources()
        
        # Should combine data from both sources
        assert len(aggregated) >= 1
        # The aggregated trend should have higher confidence due to multiple sources