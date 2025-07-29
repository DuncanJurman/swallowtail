"""Dummy Market Research Agent - placeholder for future implementation."""

from typing import Any, Dict

from ..agents.base import BaseAgent, AgentResult


class MarketResearchAgent(BaseAgent):
    """Dummy market research agent for testing purposes."""
    
    def __init__(self):
        """Initialize with market research configuration."""
        super().__init__(
            name="market_research",
            role="Market Research Specialist",
            goal="Conduct thorough market research and competitive analysis",
            backstory="""You are an expert market researcher with years of experience 
            analyzing trends, competitors, and market opportunities.""",
            tools=[],  # Would use search tools in real implementation
            allow_delegation=False,
            verbose=True
        )
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute market research (dummy implementation)."""
        product_category = context.get("product_category", "general")
        
        # Return mock data for testing
        mock_research = {
            "market_size": "$1.2B",
            "growth_rate": "15% YoY",
            "top_competitors": [
                {"name": "Competitor A", "market_share": "25%"},
                {"name": "Competitor B", "market_share": "20%"},
                {"name": "Competitor C", "market_share": "15%"}
            ],
            "trends": [
                "Increasing demand for eco-friendly products",
                "Shift towards online shopping",
                "Price sensitivity due to inflation"
            ],
            "opportunities": [
                "Untapped demographic: Gen Z consumers",
                "Geographic expansion: Southeast markets",
                "Product differentiation through sustainability"
            ],
            "recommended_price_range": "$25-$45",
            "note": "This is dummy data for testing purposes"
        }
        
        return AgentResult(
            success=True,
            data=mock_research,
            metadata={"agent": "market_research", "mock_data": True}
        )