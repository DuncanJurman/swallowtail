"""Market trends research agent."""

from typing import Any, Dict, List

from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun

from ..models.product import ProductIdea
from .base import AgentResult, BaseAgent


class MarketResearchAgent(BaseAgent):
    """Agent responsible for finding trending products and market opportunities."""
    
    def __init__(self, shared_state=None):
        """Initialize the market research agent."""
        # Set up search tool
        search = DuckDuckGoSearchRun()
        search_tool = Tool(
            name="web_search",
            description="Search the web for trending products and market data",
            func=search.run,
        )
        
        super().__init__(
            name="market_research",
            role="Market Research Analyst",
            goal="Identify high-potential products based on market trends and data",
            backstory="""You are an expert market research analyst specializing in 
            e-commerce trends. You excel at identifying emerging products with high 
            demand and reasonable competition. You analyze search trends, social media, 
            and market data to find profitable opportunities.""",
            tools=[search_tool],
            shared_state=shared_state,
        )
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute market research to find product opportunities."""
        try:
            self.log_info("Starting market research")
            
            # Create research task
            task = self.create_task(
                description="""Research and identify 3 trending product opportunities 
                that show high potential for e-commerce success. For each product:
                1. Search for current trending products in various categories
                2. Analyze search volume trends and competition
                3. Identify target audience and key benefits
                4. Provide rationale for why this product would succeed
                
                Focus on products that are:
                - Currently trending or showing growth
                - Have reasonable competition (not oversaturated)
                - Can be sourced and shipped easily
                - Have clear target audiences
                
                Use web search to gather data from multiple sources.""",
                
                expected_output="""A detailed report with 3 product recommendations, 
                each including: product name, description, category, target audience, 
                key benefits, trend analysis, competition level, and rationale."""
            )
            
            # Execute the task
            result = task.execute()
            
            # Parse the result into ProductIdea objects
            products = self._parse_research_results(result)
            
            self.log_info(f"Found {len(products)} product opportunities")
            
            return AgentResult(
                success=True,
                data={
                    "products": [p.model_dump() for p in products],
                    "raw_analysis": result,
                }
            )
            
        except Exception as e:
            self.log_error(f"Market research failed: {str(e)}")
            return AgentResult(success=False, error=str(e))
    
    def _parse_research_results(self, raw_result: str) -> List[ProductIdea]:
        """Parse the raw research results into structured ProductIdea objects."""
        # In a real implementation, we'd use more sophisticated parsing
        # For now, we'll create some example products based on the result
        
        # This is a placeholder - in production, we'd parse the actual LLM output
        products = []
        
        # Example product ideas (would be extracted from actual results)
        example_products = [
            ProductIdea(
                name="Portable Air Purifier",
                description="Compact HEPA air purifier for personal spaces",
                category="Home & Health",
                target_audience="Urban professionals, allergy sufferers",
                key_benefits=[
                    "Removes 99.97% of airborne particles",
                    "Ultra-quiet operation",
                    "USB rechargeable"
                ],
                search_volume_trend="Rising 45% over 3 months",
                competition_level="Moderate",
                estimated_demand="High",
                rationale="Increased awareness of air quality post-pandemic",
                data_sources=["Google Trends", "Amazon Best Sellers"]
            ),
            ProductIdea(
                name="Smart Plant Monitor",
                description="Bluetooth soil sensor for indoor plants",
                category="Smart Home & Garden",
                target_audience="Urban millennials, plant enthusiasts",
                key_benefits=[
                    "Real-time soil moisture monitoring",
                    "App notifications for watering",
                    "Light and temperature tracking"
                ],
                search_volume_trend="Rising 60% over 6 months",
                competition_level="Low to Moderate",
                estimated_demand="Growing",
                rationale="Indoor gardening trend continues to grow",
                data_sources=["Social media trends", "Reddit communities"]
            ),
            ProductIdea(
                name="Ergonomic Laptop Stand",
                description="Adjustable aluminum laptop stand for better posture",
                category="Office & Computer",
                target_audience="Remote workers, students",
                key_benefits=[
                    "Reduces neck and back strain",
                    "Improves laptop cooling",
                    "Portable and lightweight"
                ],
                search_volume_trend="Stable high volume",
                competition_level="High but fragmented",
                estimated_demand="Consistent",
                rationale="Permanent shift to remote work creates ongoing demand",
                data_sources=["E-commerce data", "Workplace surveys"]
            )
        ]
        
        # In production, we'd extract these from the LLM's structured output
        return example_products[:3]