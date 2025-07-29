"""Supabase Storage Service for managing images and videos."""

import io
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID, uuid4

from PIL import Image
from supabase import Client, create_client

from src.core.config import get_settings
from src.utils.db_helper import get_asyncpg_connection


settings = get_settings()


class StoragePathGenerator:
    """Generates standardized storage paths for different asset types."""
    
    @staticmethod
    def generate_image_path(product_id: UUID, image_type: str, sub_type: Optional[str] = None, 
                          filename: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Generate storage path for images."""
        base = f"products/{product_id}"
        
        if image_type == "reference":
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
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
    def generate_video_path(product_id: UUID, video_type: str, platform: Optional[str] = None,
                          filename: Optional[str] = None, session_id: Optional[str] = None) -> str:
        """Generate storage path for videos."""
        base = f"products/{product_id}"
        
        if video_type == "demo":
            session_id = session_id or str(uuid4())
            return f"{base}/demos/{session_id}_demo.mp4"
            
        elif video_type == "ad" and platform:
            session_id = session_id or str(uuid4())
            return f"{base}/ads/{platform}/{session_id}_{platform}.mp4"
            
        elif video_type == "raw":
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
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
        
        # Bucket names
        self.IMAGE_BUCKET = "product-images"
        self.VIDEO_BUCKET = "product-videos"  
        self.REFERENCE_BUCKET = "reference-images"
    
    async def upload_image(self, product_id: UUID, image_data: bytes, image_type: str,
                         sub_type: Optional[str] = None, filename: Optional[str] = None,
                         session_id: Optional[str] = None, optimize: bool = True) -> Dict[str, Any]:
        """Upload an image with automatic optimization and metadata storage."""
        # Generate path
        path = self.path_generator.generate_image_path(
            product_id=product_id,
            image_type=image_type,
            sub_type=sub_type,
            filename=filename,
            session_id=session_id
        )
        
        # Determine bucket
        bucket = self.REFERENCE_BUCKET if image_type == "reference" else self.IMAGE_BUCKET
        
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
        if bucket == self.IMAGE_BUCKET:
            public_url = self.client.storage.from_(bucket).get_public_url(path)
        else:
            # Reference images are private, need authenticated URL
            public_url = f"{settings.supabase_url}/storage/v1/object/authenticated/{bucket}/{path}"
        
        # Store metadata in database
        metadata = await self._store_image_metadata(
            product_id=product_id,
            storage_path=path,
            public_url=public_url,
            image_type=image_type,
            sub_type=sub_type,
            file_size=file_size,
            dimensions=dimensions,
            format=format,
            session_id=session_id
        )
        
        return {
            "success": True,
            "path": path,
            "url": public_url,
            "metadata": metadata,
            "size": file_size,
            "dimensions": dimensions
        }
    
    async def upload_video(self, product_id: UUID, video_data: bytes, video_type: str,
                         platform: Optional[str] = None, filename: Optional[str] = None,
                         session_id: Optional[str] = None) -> Dict[str, Any]:
        """Upload a video with metadata storage."""
        # Generate path
        path = self.path_generator.generate_video_path(
            product_id=product_id,
            video_type=video_type,
            platform=platform,
            filename=filename,
            session_id=session_id
        )
        
        # Check file size
        file_size = len(video_data)
        if file_size > 100 * 1024 * 1024:  # 100MB limit
            raise ValueError(f"Video size {file_size} exceeds 100MB limit")
        
        # Upload to Supabase
        response = self.client.storage.from_(self.VIDEO_BUCKET).upload(
            path=path,
            file=video_data,
            file_options={"content-type": "video/mp4"}
        )
        
        if hasattr(response, 'error') and response.error:
            raise Exception(f"Upload failed: {response.error}")
        
        # Get public URL
        public_url = self.client.storage.from_(self.VIDEO_BUCKET).get_public_url(path)
        
        # Store metadata
        metadata = await self._store_video_metadata(
            product_id=product_id,
            storage_path=path,
            public_url=public_url,
            video_type=video_type,
            file_size=file_size
        )
        
        return {
            "success": True,
            "path": path,
            "url": public_url,
            "metadata": metadata,
            "size": file_size
        }
    
    async def list_product_images(self, product_id: UUID, image_type: Optional[str] = None) -> List[Dict]:
        """List all images for a product."""
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            if image_type:
                query = """
                    SELECT id, storage_path, public_url, image_type, sub_type, file_size,
                           width, height, format, created_at
                    FROM image_metadata
                    WHERE product_id = $1 AND image_type = $2 AND status = 'active'
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, product_id, image_type)
            else:
                query = """
                    SELECT id, storage_path, public_url, image_type, sub_type, file_size,
                           width, height, format, created_at
                    FROM image_metadata
                    WHERE product_id = $1 AND status = 'active'
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, product_id)
            
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def list_product_videos(self, product_id: UUID, video_type: Optional[str] = None) -> List[Dict]:
        """List all videos for a product."""
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            if video_type:
                query = """
                    SELECT id, storage_path, public_url, video_type, file_size, created_at
                    FROM video_metadata
                    WHERE product_id = $1 AND video_type = $2 AND status = 'active'
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, product_id, video_type)
            else:
                query = """
                    SELECT id, storage_path, public_url, video_type, file_size, created_at
                    FROM video_metadata
                    WHERE product_id = $1 AND status = 'active'
                    ORDER BY created_at DESC
                """
                rows = await conn.fetch(query, product_id)
            
            return [dict(row) for row in rows]
        finally:
            await conn.close()
    
    async def delete_image(self, path: str) -> None:
        """Delete an image from storage and mark as deleted in database."""
        # Determine bucket from path
        bucket = self.REFERENCE_BUCKET if "/reference/" in path else self.IMAGE_BUCKET
        
        # Delete from storage
        self.client.storage.from_(bucket).remove([path])
        
        # Mark as deleted in database
        await self._mark_image_deleted(path)
    
    async def delete_video(self, path: str) -> None:
        """Delete a video from storage and mark as deleted in database."""
        # Delete from storage
        self.client.storage.from_(self.VIDEO_BUCKET).remove([path])
        
        # Mark as deleted in database
        await self._mark_video_deleted(path)
    
    async def delete_product_assets(self, product_id: UUID) -> Dict[str, int]:
        """Delete all assets for a product."""
        # Get all assets
        images = await self.list_product_images(product_id)
        videos = await self.list_product_videos(product_id)
        
        # Get reference images separately
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            ref_query = """
                SELECT storage_path FROM image_metadata
                WHERE product_id = $1 AND image_type = 'reference' AND status = 'active'
            """
            ref_rows = await conn.fetch(ref_query, product_id)
            reference_paths = [row['storage_path'] for row in ref_rows]
        finally:
            await conn.close()
        
        # Delete from storage
        if images:
            image_paths = [img['storage_path'] for img in images if img['image_type'] != 'reference']
            if image_paths:
                self.client.storage.from_(self.IMAGE_BUCKET).remove(image_paths)
        
        if reference_paths:
            self.client.storage.from_(self.REFERENCE_BUCKET).remove(reference_paths)
        
        if videos:
            video_paths = [vid['storage_path'] for vid in videos]
            self.client.storage.from_(self.VIDEO_BUCKET).remove(video_paths)
        
        # Mark as deleted in database
        await self._mark_product_assets_deleted(product_id)
        
        return {
            "images": len(images) - len(reference_paths),
            "videos": len(videos),
            "references": len(reference_paths)
        }
    
    async def get_signed_url(self, path: str, bucket: str, expires_in: int = 3600) -> str:
        """Get a signed URL for private content."""
        response = self.client.storage.from_(bucket).create_signed_url(path, expires_in)
        return response['signedURL']
    
    async def cleanup_temp_images(self, older_than_hours: int = 24) -> int:
        """Clean up temporary images older than specified hours."""
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            # Find old temp images
            query = """
                SELECT storage_path FROM image_metadata
                WHERE image_type = 'temp' 
                AND status = 'active'
                AND created_at < NOW() - INTERVAL '%s hours'
            """
            rows = await conn.fetch(query, older_than_hours)
            
            if rows:
                paths = [row['storage_path'] for row in rows]
                # Delete from storage
                self.client.storage.from_(self.IMAGE_BUCKET).remove(paths)
                
                # Mark as deleted
                for path in paths:
                    await self._mark_image_deleted(path)
            
            return len(rows)
        finally:
            await conn.close()
    
    # Private methods for database operations
    
    async def _store_image_metadata(self, **kwargs) -> Dict:
        """Store image metadata in database."""
        # Use direct asyncpg connection
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            query = """
                INSERT INTO image_metadata (
                    product_id, storage_path, public_url, image_type, sub_type,
                    file_size, width, height, format, generation_session_id
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING id, created_at
            """
            
            dimensions = kwargs.get('dimensions', (None, None))
            
            row = await conn.fetchrow(
                query,
                kwargs['product_id'],
                kwargs['storage_path'],
                kwargs['public_url'],
                kwargs['image_type'],
                kwargs.get('sub_type'),
                kwargs['file_size'],
                dimensions[0] if dimensions else None,
                dimensions[1] if dimensions else None,
                kwargs.get('format', 'unknown'),
                kwargs.get('session_id')
            )
            
            return {
                "id": str(row['id']),
                "created_at": row['created_at'].isoformat()
            }
        finally:
            await conn.close()
    
    async def _store_video_metadata(self, **kwargs) -> Dict:
        """Store video metadata in database."""
        # Use direct asyncpg connection
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            query = """
                INSERT INTO video_metadata (
                    product_id, storage_path, public_url, video_type, file_size
                ) VALUES ($1, $2, $3, $4, $5)
                RETURNING id, created_at
            """
            
            row = await conn.fetchrow(
                query,
                kwargs['product_id'],
                kwargs['storage_path'],
                kwargs['public_url'],
                kwargs['video_type'],
                kwargs['file_size']
            )
            
            return {
                "id": str(row['id']),
                "created_at": row['created_at'].isoformat()
            }
        finally:
            await conn.close()
    
    async def _mark_image_deleted(self, path: str):
        """Mark image as deleted in database."""
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            await conn.execute(
                "UPDATE image_metadata SET status = 'deleted' WHERE storage_path = $1",
                path
            )
        finally:
            await conn.close()
    
    async def _mark_video_deleted(self, path: str):
        """Mark video as deleted in database."""  
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            await conn.execute(
                "UPDATE video_metadata SET status = 'deleted' WHERE storage_path = $1",
                path
            )
        finally:
            await conn.close()
    
    async def _mark_product_assets_deleted(self, product_id: UUID):
        """Mark all product assets as deleted."""
        conn = await get_asyncpg_connection(use_direct_url=False)
        try:
            await conn.execute(
                "UPDATE image_metadata SET status = 'deleted' WHERE product_id = $1",
                product_id
            )
            await conn.execute(
                "UPDATE video_metadata SET status = 'deleted' WHERE product_id = $1",
                product_id
            )
        finally:
            await conn.close()