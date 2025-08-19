"""Supabase Storage Service for managing images and videos."""

import io
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from uuid import UUID, uuid4

from PIL import Image
from supabase import Client, create_client

from src.core.config import get_settings


settings = get_settings()


class StoragePathGenerator:
    """Generates standardized storage paths for different asset types."""
    
    @staticmethod
    def generate_instance_image_path(instance_id: UUID, image_type: str, sub_type: Optional[str] = None, 
                          filename: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Generate storage path for images based on instance."""
        base = f"instances/{instance_id}"
        
        if image_type == "reference":
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            name = filename or "reference.jpg"
            return f"{base}/reference/{timestamp}_{name}"
            
        elif image_type == "generated":
            session_id = session_id or str(uuid4())
            if sub_type:
                return f"{base}/generated/{sub_type}/{session_id}_final.webp"
            return f"{base}/generated/{session_id}_final.webp"
            
        elif image_type == "temp":
            session_id = session_id or str(uuid4())
            image_id = str(uuid4())
            return f"{base}/temp/{session_id}/{image_id}.webp"
            
        else:
            raise ValueError(f"Unknown image type: {image_type}")
    
    @staticmethod
    def generate_instance_video_path(instance_id: UUID, video_type: str, platform: Optional[str] = None,
                          filename: Optional[str] = None, session_id: Optional[str] = None, task_id: Optional[UUID] = None) -> str:
        """Generate storage path for videos based on instance."""
        base = f"instances/{instance_id}"
        
        if video_type == "task_output" and task_id:
            # Videos generated as task outputs
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            return f"{base}/tasks/{task_id}/{timestamp}_output.mp4"
        elif video_type == "demo":
            session_id = session_id or str(uuid4())
            return f"{base}/demos/{session_id}_demo.mp4"
            
        elif video_type == "ad" and platform:
            session_id = session_id or str(uuid4())
            return f"{base}/ads/{platform}/{session_id}_{platform}.mp4"
            
        elif video_type == "raw":
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            name = filename or "upload.mp4"
            return f"{base}/raw/{timestamp}_{name}"
            
        else:
            raise ValueError(f"Unknown video type: {video_type}")


class ImageOptimizer:
    """Handles image optimization for storage efficiency."""
    
    @staticmethod
    def optimize_image(image_data: bytes, max_dimension: int = 2048, 
                      quality: int = 85, format: str = "WEBP") -> Tuple[bytes, Tuple[int, int]]:
        """Optimize image for web delivery. Returns optimized bytes and dimensions."""
        # Open image
        img = Image.open(io.BytesIO(image_data))
        
        # Convert RGBA to RGB if saving as JPEG
        if format.upper() == "JPEG" and img.mode == "RGBA":
            # Create a white background
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        
        # Resize if too large
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
        
        # Save with optimization
        output = io.BytesIO()
        save_kwargs = {
            'format': format.upper(),
            'quality': quality,
            'optimize': True
        }
        
        if format.upper() == 'WEBP':
            save_kwargs['method'] = 6  # Slower but better compression
            
        img.save(output, **save_kwargs)
        
        # Get image dimensions
        dimensions = (img.width, img.height)
        
        return output.getvalue(), dimensions


class SupabaseStorageService:
    """Main service for interacting with Supabase Storage."""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_service_key  # Use service key for backend operations
        )
        self.path_generator = StoragePathGenerator()
        self.optimizer = ImageOptimizer()
        
        # Bucket names - using instance-based buckets for MVP
        self.INSTANCE_MEDIA_BUCKET = "instance-media"  # Public bucket for all instance media
        self.INSTANCE_TEMP_BUCKET = "instance-temp"    # Private bucket for temporary files
    
    def validate_instance_access(self, instance_id: UUID, user_id: UUID) -> bool:
        """
        Validate that a user has access to an instance.
        
        For MVP, this is a placeholder that always returns True.
        In production, this would check the database to verify ownership.
        
        Args:
            instance_id: The instance to access
            user_id: The user attempting access
            
        Returns:
            True if access is allowed, False otherwise
        """
        # MVP: Allow all access (controlled at API endpoint level)
        # TODO: In production, query database to check instance.user_id == user_id
        return True
    
    async def upload_instance_image(self, instance_id: UUID, image_data: bytes, image_type: str,
                         sub_type: Optional[str] = None, filename: Optional[str] = None,
                         session_id: Optional[str] = None, optimize: bool = True) -> Dict[str, Any]:
        """Upload an image for an instance with automatic optimization and metadata storage."""
        # Generate path
        path = self.path_generator.generate_instance_image_path(
            instance_id=instance_id,
            image_type=image_type,
            sub_type=sub_type,
            filename=filename,
            session_id=session_id
        )
        
        # Use appropriate bucket
        bucket = self.INSTANCE_TEMP_BUCKET if image_type == "temp" else self.INSTANCE_MEDIA_BUCKET
        
        # Optimize image if requested
        file_size = len(image_data)
        dimensions = None
        format = "original"
        
        if optimize and image_type != "reference":  # Don't optimize reference images
            image_data, dimensions = self.optimizer.optimize_image(image_data)
            file_size = len(image_data)
            format = "webp"
        
        # Determine correct mime type
        if format == "original":
            # Guess mime type from filename or default to jpeg
            if filename and filename.lower().endswith('.png'):
                mime_type = "image/png"
            else:
                mime_type = "image/jpeg"
        else:
            mime_type = f"image/{format}"
        
        # Upload to Supabase
        response = self.client.storage.from_(bucket).upload(
            path=path,
            file=image_data,
            file_options={"content-type": mime_type}
        )
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Upload failed: {response.error}")
        
        # Get public URL
        if bucket == self.INSTANCE_MEDIA_BUCKET:
            public_url = self.client.storage.from_(bucket).get_public_url(path)
        else:
            # Temp images are private, need authenticated URL
            public_url = f"{settings.supabase_url}/storage/v1/object/authenticated/{bucket}/{path}"
        
        # Store metadata in database (if we have the tables)
        # For MVP, we'll store minimal metadata
        metadata = {
            "instance_id": str(instance_id),
            "path": path,
            "type": image_type,
            "size": file_size,
            "dimensions": dimensions
        }
        
        return {
            "success": True,
            "path": path,
            "url": public_url,
            "metadata": metadata,
            "size": file_size,
            "dimensions": dimensions
        }
    
    async def upload_instance_video(self, instance_id: UUID, video_data: bytes, video_type: str,
                         platform: Optional[str] = None, filename: Optional[str] = None,
                         session_id: Optional[str] = None, task_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Upload a video for an instance with metadata storage."""
        # Generate path
        path = self.path_generator.generate_instance_video_path(
            instance_id=instance_id,
            video_type=video_type,
            platform=platform,
            filename=filename,
            session_id=session_id,
            task_id=task_id
        )
        
        # Check file size
        file_size = len(video_data)
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError(f"Video size {file_size} exceeds 100MB limit")
        
        # Upload to Supabase
        response = self.client.storage.from_(self.INSTANCE_MEDIA_BUCKET).upload(
            path=path,
            file=video_data,
            file_options={"content-type": "video/mp4"}
        )
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Upload failed: {response.error}")
        
        # Get public URL
        public_url = self.client.storage.from_(self.INSTANCE_MEDIA_BUCKET).get_public_url(path)
        
        # Store metadata
        metadata = {
            "instance_id": str(instance_id),
            "task_id": str(task_id) if task_id else None,
            "path": path,
            "type": video_type,
            "size": file_size
        }
        
        return {
            "success": True,
            "path": path,
            "url": public_url,
            "metadata": metadata,
            "size": file_size
        }
    
    async def get_signed_url(self, path: str, bucket: str, expires_in: int = 3600) -> str:
        """Get a signed URL for private content."""
        response = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
        return response['signedURL']
    
    async def store_media_metadata(
        self,
        instance_id: UUID,
        storage_path: str,
        public_url: str,
        media_type: str,
        file_size: int,
        task_id: Optional[UUID] = None,
        media_subtype: Optional[str] = None,
        mime_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store media metadata in database (MVP version).
        
        In production, this would use proper database connections.
        For MVP, this is a placeholder that returns a mock ID.
        
        Args:
            instance_id: Instance that owns this media
            storage_path: Path in storage bucket
            public_url: Public URL for accessing the media
            media_type: 'image' or 'video'
            file_size: Size in bytes
            task_id: Optional associated task
            media_subtype: Optional subtype (e.g., 'reference', 'generated')
            mime_type: MIME type of the file
            metadata: Additional metadata as JSON
            
        Returns:
            Media record ID
        """
        # MVP: Return mock ID
        # TODO: In production, insert into instance_media table
        import uuid
        return str(uuid.uuid4())
    
