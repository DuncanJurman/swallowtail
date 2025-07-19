"""
Example integration showing how a manager agent would use the ImageGenerationFlow.

This demonstrates the pattern for integrating flows with CrewAI agents.
"""

import os
import sys
from pathlib import Path
from uuid import uuid4
from typing import List, Dict, Any

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from crewai import Agent, Crew, Task
from src.tools.flow_tools import create_flow_tools
from src.core.config import get_settings


class ProductImageManager:
    """
    Example manager agent that coordinates image generation for products.
    
    This demonstrates how a higher-level agent can use the ImageGenerationFlow
    as a tool to handle complex image generation workflows.
    """
    
    def __init__(self):
        """Initialize the manager with flow tools."""
        self.generation_tool, self.status_tool = create_flow_tools()
        self.settings = get_settings()
    
    def create_manager_agent(self) -> Agent:
        """Create the product image manager agent."""
        return Agent(
            role="Product Image Manager",
            goal="Coordinate high-quality product image generation for e-commerce catalog",
            backstory="""You are an experienced e-commerce manager responsible for ensuring 
            all products have professional, high-quality images. You understand the importance 
            of visual consistency and accuracy in product representation.""",
            tools=[self.generation_tool, self.status_tool],
            allow_delegation=False,
            verbose=True
        )
    
    def create_batch_generation_task(self, products: List[Dict[str, Any]]) -> Task:
        """Create a task for batch image generation."""
        product_list = "\n".join([
            f"- {p['name']} (ID: {p['id']})" for p in products
        ])
        
        return Task(
            description=f"""
            Generate high-quality images for the following products:
            
            {product_list}
            
            For each product:
            1. Use the image_generation_flow tool to generate the image
            2. Monitor the generation status
            3. Report any failures or issues
            4. Compile a summary of results
            
            Ensure all images meet our quality standards (approval threshold: 0.85).
            """,
            expected_output="""
            A detailed report containing:
            - Success/failure status for each product
            - Final image URLs for successful generations
            - Number of attempts required for each
            - Any error messages or issues encountered
            - Overall batch success rate
            """,
            agent=self.create_manager_agent()
        )
    
    def create_single_product_task(self, product_info: Dict[str, Any]) -> Task:
        """Create a task for single product image generation."""
        return Task(
            description=f"""
            Generate a high-quality image for:
            
            Product: {product_info['name']}
            ID: {product_info['id']}
            Features: {', '.join(product_info['features'])}
            
            Requirements:
            1. Use the reference image at: {product_info['reference_url']}
            2. Apply style requirements: {product_info.get('style', 'default style')}
            3. Ensure approval threshold of {product_info.get('threshold', 0.85)}
            4. Monitor generation progress
            5. Report final result with image URL
            """,
            expected_output="""
            A comprehensive report including:
            - Generation success status
            - Final approved image URL
            - Number of attempts made
            - Quality scores achieved
            - Any feedback received during the process
            """,
            agent=self.create_manager_agent()
        )


def demonstrate_single_product_generation():
    """Demonstrate generating an image for a single product."""
    print("\n=== Single Product Image Generation Example ===\n")
    
    # Create manager
    manager = ProductImageManager()
    
    # Example product
    product = {
        "id": str(uuid4()),
        "name": "LED Gaming Mouse",
        "features": ["RGB lighting", "7 programmable buttons", "16000 DPI sensor"],
        "reference_url": "file:///path/to/reference/gaming_mouse.jpg",
        "style": {"background": "dark gradient", "lighting": "dramatic"},
        "threshold": 0.85
    }
    
    print(f"📦 Product: {product['name']}")
    print(f"   ID: {product['id']}")
    print(f"   Features: {len(product['features'])}")
    
    # Create task
    task = manager.create_single_product_task(product)
    
    # Create crew
    crew = Crew(
        agents=[manager.create_manager_agent()],
        tasks=[task],
        verbose=True
    )
    
    print("\n🚀 Starting image generation task...")
    print("   (This would execute the full flow in a real environment)")
    
    # In a real scenario with API keys and actual images:
    # result = crew.kickoff()
    # print(f"\n📊 Result: {result}")
    
    print("\n✅ Demonstration complete")


def demonstrate_batch_generation():
    """Demonstrate batch image generation for multiple products."""
    print("\n=== Batch Product Image Generation Example ===\n")
    
    # Create manager
    manager = ProductImageManager()
    
    # Example products
    products = [
        {
            "id": str(uuid4()),
            "name": "Wireless Keyboard",
            "features": ["Bluetooth 5.0", "Backlit keys", "Rechargeable"],
            "reference_url": "file:///path/to/keyboard.jpg"
        },
        {
            "id": str(uuid4()),
            "name": "USB-C Hub",
            "features": ["7 ports", "4K HDMI", "100W PD charging"],
            "reference_url": "file:///path/to/usb_hub.jpg"
        },
        {
            "id": str(uuid4()),
            "name": "Webcam 4K",
            "features": ["4K resolution", "Auto-focus", "Built-in mic"],
            "reference_url": "file:///path/to/webcam.jpg"
        }
    ]
    
    print(f"📦 Processing {len(products)} products:")
    for p in products:
        print(f"   - {p['name']} (ID: {p['id'][:8]}...)")
    
    # Create task
    task = manager.create_batch_generation_task(products)
    
    # Create crew
    crew = Crew(
        agents=[manager.create_manager_agent()],
        tasks=[task],
        verbose=True
    )
    
    print("\n🚀 Starting batch generation task...")
    print("   (This would process all products in a real environment)")
    
    print("\n✅ Demonstration complete")


def demonstrate_status_monitoring():
    """Demonstrate monitoring image generation status."""
    print("\n=== Status Monitoring Example ===\n")
    
    manager = ProductImageManager()
    
    # Example: checking status of a generation
    test_product_id = str(uuid4())
    
    print(f"📊 Checking status for product: {test_product_id}")
    
    # This would be used by an agent to check progress
    monitoring_task = Task(
        description=f"""
        Check the status of image generation for product ID: {test_product_id}
        
        Use the check_image_generation_status tool to get current progress.
        Report on:
        - Current status (not_started, in_progress, completed, failed)
        - Number of attempts made
        - Any feedback received
        - Final image URL if completed
        """,
        expected_output="A status report with all requested information",
        agent=manager.create_manager_agent()
    )
    
    print("   Status check configured")
    print("   (Would return actual status in production)")
    
    print("\n✅ Demonstration complete")


def main():
    """Run all demonstrations."""
    from dotenv import load_dotenv
    load_dotenv()
    
    settings = get_settings()
    print("🔧 Configuration:")
    print(f"   - OpenAI Model: {settings.openai_model}")
    print(f"   - API Key set: {bool(settings.openai_api_key)}")
    
    # Run demonstrations
    demonstrate_single_product_generation()
    demonstrate_batch_generation()
    demonstrate_status_monitoring()
    
    print("\n" + "="*50)
    print("💡 Integration Patterns Demonstrated:")
    print("   1. Single product image generation")
    print("   2. Batch processing multiple products")
    print("   3. Status monitoring during generation")
    print("   4. Error handling and reporting")
    print("\n🎯 Key Benefits:")
    print("   - Agents can trigger complex workflows with simple tool calls")
    print("   - Flow handles all orchestration and feedback loops")
    print("   - Manager agents can focus on higher-level coordination")
    print("   - Easy to integrate into existing agent architectures")


if __name__ == "__main__":
    main()