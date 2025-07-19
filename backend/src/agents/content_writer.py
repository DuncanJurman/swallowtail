"""Dummy Content Writer Agent - placeholder for future implementation."""

from typing import Any, Dict

from ..agents.base import BaseAgent, AgentResult


class ContentWriterAgent(BaseAgent):
    """Dummy content writer agent for testing purposes."""
    
    def __init__(self):
        """Initialize with content writer configuration."""
        super().__init__(
            name="content_writer",
            role="Product Content Writer",
            goal="Create compelling product descriptions and marketing content",
            backstory="""You are an experienced e-commerce copywriter who crafts 
            product descriptions that convert browsers into buyers.""",
            tools=[],
            allow_delegation=False,
            inject_date=True,
            verbose=True
        )
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute content writing (dummy implementation)."""
        product_name = context.get("product_name", "Product")
        product_details = context.get("product_details", {})
        
        # Return mock content for testing
        mock_content = {
            "title": f"Premium {product_name} - Limited Edition",
            "headline": f"Experience the Ultimate {product_name}",
            "description": f"""
                Introducing our revolutionary {product_name}, designed with you in mind. 
                This premium product combines cutting-edge technology with timeless design 
                to deliver an unparalleled experience.

                Key Features:
                • Superior quality materials
                • Innovative design
                • Eco-friendly manufacturing
                • 1-year warranty
                • Free shipping

                Perfect for those who demand excellence in every aspect of their life.
            """.strip(),
            "meta_description": f"Shop our premium {product_name}. High-quality, eco-friendly, with free shipping. Order now!",
            "keywords": [product_name.lower(), "premium", "quality", "eco-friendly", "free shipping"],
            "note": "This is dummy content for testing purposes"
        }
        
        return AgentResult(
            success=True,
            data=mock_content,
            metadata={"agent": "content_writer", "mock_data": True}
        )