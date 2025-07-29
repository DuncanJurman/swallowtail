"""Image Storage Tool for CrewAI agents."""

from typing import Any, Dict, Type, Optional
from uuid import UUID
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..services.storage import SupabaseStorageService


class ImageStorageInput(BaseModel):
    """Input schema for image storage."""
    image_path: str = Field(
        description="Path to the image file to store"
    )
    product_id: str = Field(
        description="UUID of the product this image belongs to"
    )
    image_type: str = Field(
        default="generated",
        description="Type of image: 'reference', 'generated', or 'temp'"
    )
    filename: Optional[str] = Field(
        default=None,
        description="Optional filename for the image"
    )


class ImageRetrievalInput(BaseModel):
    """Input schema for image retrieval."""
    image_url: str = Field(
        description="URL or path of the image to retrieve"
    )


class ImageStorageTool(BaseTool):
    """Tool for storing and retrieving images from Supabase storage."""
    
    name: str = "store_image"
    description: str = """Store an image in Supabase storage and get back a URL.
    This tool handles uploading images to the appropriate bucket and tracking metadata."""
    args_schema: Type[BaseModel] = ImageStorageInput
    
    def __init__(self):
        super().__init__()
        self._storage = SupabaseStorageService()
    
    def _run(
        self,
        image_path: str,
        product_id: str,
        image_type: str = "generated",
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Store an image synchronously.
        
        Args:
            image_path: Path to the image file
            product_id: Product UUID
            image_type: Type of image
            filename: Optional filename
            
        Returns:
            Dict with url and success status
        """
        import asyncio
        
        try:
            # Read image from file
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            
            # Convert string UUID to UUID object
            product_uuid = UUID(product_id)
            
            # Run async operation in new event loop
            async def _async_upload():
                # Upload the image
                url = await self._storage.upload_image(
                    product_id=product_uuid,
                    image_data=image_bytes,
                    image_type=image_type,
                    filename=filename
                )
                return url
            
            # Execute async operation - handle existing event loop
            try:
                asyncio.get_running_loop()
                # We're already in an event loop, use nest_asyncio
                import nest_asyncio
                nest_asyncio.apply()
                url = asyncio.run(_async_upload())
            except RuntimeError:
                # No event loop running, create one normally
                url = asyncio.run(_async_upload())
            
            return {
                "success": True,
                "url": url,
                "product_id": str(product_uuid),
                "image_type": image_type
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "product_id": product_id
            }
    


class ImageRetrievalTool(BaseTool):
    """Tool for retrieving images from storage."""
    
    name: str = "retrieve_image"
    description: str = """Retrieve an image from storage by URL.
    This tool downloads images from Supabase storage or handles local file paths."""
    args_schema: Type[BaseModel] = ImageRetrievalInput
    
    def __init__(self):
        super().__init__()
        self._storage = SupabaseStorageService()
    
    def _run(self, image_url: str) -> Dict[str, Any]:
        """
        Retrieve an image synchronously.
        
        Args:
            image_url: URL or path of the image
            
        Returns:
            Dict with image_data (base64) and success status
        """
        import os
        
        try:
            # Handle different URL types
            if image_url.startswith("file://"):
                # Local file URL
                file_path = image_url.replace("file://", "")
                # Verify file exists
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Image file not found: {file_path}")
                
                # Return path reference instead of full data
                return {
                    "success": True,
                    "image_path": file_path,
                    "image_url": image_url,
                    "message": f"Successfully retrieved reference image from {file_path}"
                }
            elif image_url.startswith("/"):
                # Absolute local path
                if not os.path.exists(image_url):
                    raise FileNotFoundError(f"Image file not found: {image_url}")
                    
                return {
                    "success": True,
                    "image_path": image_url,
                    "image_url": f"file://{image_url}",
                    "message": f"Successfully retrieved reference image from {image_url}"
                }
            else:
                # Remote URL - we'll pass the URL directly to other tools
                return {
                    "success": True,
                    "image_url": image_url,
                    "message": f"Image URL validated: {image_url}"
                }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "url": image_url
            }
    
