# Storage API Usage Guide

## Overview

The Swallowtail storage system provides a unified interface for managing images and videos with automatic optimization, product-based partitioning, and metadata tracking.

## Storage Service API

### Initialization

```python
from src.services.storage import SupabaseStorageService

# Initialize the storage service
storage = SupabaseStorageService()
```

### Image Upload

#### Upload Reference Image (User-provided)

```python
# Reference images are NOT optimized to preserve original quality
result = await storage.upload_image(
    product_id=product_id,
    image_data=image_bytes,  # Raw image bytes
    image_type="reference",
    filename="product_reference.jpg"
)

# Result contains:
# {
#     "success": True,
#     "path": "products/{product_id}/reference/20240315_120530_product_reference.jpg",
#     "url": "https://your-project.supabase.co/storage/v1/object/authenticated/reference-images/...",
#     "metadata": {"id": "...", "created_at": "..."},
#     "size": 2048576,
#     "dimensions": None  # Not calculated for reference images
# }
```

#### Upload Generated Image (AI-created)

```python
# Generated images ARE optimized (WebP conversion, resizing)
result = await storage.upload_image(
    product_id=product_id,
    image_data=generated_bytes,
    image_type="generated",
    sub_type="main",  # or "lifestyle", "detail", "marketing"
    session_id="abc123",  # From generation session
    optimize=True  # Default is True
)

# Result contains optimized image URL and dimensions
```

#### Upload Temporary Image (For evaluation)

```python
# Temporary images for evaluation workflow
result = await storage.upload_image(
    product_id=product_id,
    image_data=temp_bytes,
    image_type="temp",
    session_id="eval_session_123",
    optimize=False  # Usually skip optimization for temp
)
```

### Video Upload

```python
# Videos have a 100MB size limit
result = await storage.upload_video(
    product_id=product_id,
    video_data=video_bytes,
    video_type="demo",  # or "ad", "raw"
    platform="tiktok",  # Optional, for ads
    filename="product_demo.mp4"
)

# Result contains:
# {
#     "success": True,
#     "path": "products/{product_id}/demos/{session_id}_demo.mp4",
#     "url": "https://your-project.supabase.co/storage/v1/object/public/product-videos/...",
#     "metadata": {"id": "...", "created_at": "..."},
#     "size": 10485760
# }
```

### List Product Assets

```python
# List all images for a product
images = await storage.list_product_images(
    product_id=product_id,
    image_type="generated"  # Optional filter
)

# Returns list of image metadata:
# [
#     {
#         "id": "uuid",
#         "storage_path": "products/.../main/session_final.webp",
#         "public_url": "https://...",
#         "image_type": "generated",
#         "sub_type": "main",
#         "file_size": 204800,
#         "width": 1024,
#         "height": 1024,
#         "format": "webp",
#         "created_at": "2024-03-15T12:05:30"
#     }
# ]
```

### Delete Assets

```python
# Delete a specific image
await storage.delete_image(
    path="products/{product_id}/generated/main/session_final.webp"
)

# Delete ALL assets for a product
deleted_counts = await storage.delete_product_assets(product_id)
# Returns: {"images": 15, "videos": 3, "references": 5}
```

### Get Signed URLs (For private assets)

```python
# Get temporary access URL for private reference image
signed_url = await storage.get_signed_url(
    path="products/{product_id}/reference/image.jpg",
    bucket="reference-images",
    expires_in=3600  # 1 hour
)
```

### Cleanup Temporary Files

```python
# Clean up temp files older than 24 hours
deleted_count = await storage.cleanup_temp_images(older_than_hours=24)
```

## API Endpoints

### Upload Image Endpoint

```python
from fastapi import APIRouter, UploadFile, File
from uuid import UUID

router = APIRouter()

@router.post("/api/v1/products/{product_id}/images/upload")
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    image_type: str = "reference",
    sub_type: Optional[str] = None
):
    """Upload an image for a product."""
    # Read file data
    image_data = await file.read()
    
    # Upload to storage
    result = await storage.upload_image(
        product_id=product_id,
        image_data=image_data,
        image_type=image_type,
        sub_type=sub_type,
        filename=file.filename
    )
    
    return {
        "success": result["success"],
        "url": result["url"],
        "metadata": result["metadata"]
    }
```

### List Images Endpoint

```python
@router.get("/api/v1/products/{product_id}/images")
async def list_product_images(
    product_id: UUID,
    image_type: Optional[str] = None
):
    """List all images for a product."""
    images = await storage.list_product_images(
        product_id=product_id,
        image_type=image_type
    )
    
    return {"images": images, "count": len(images)}
```

### Delete Image Endpoint

```python
@router.delete("/api/v1/products/{product_id}/images/{image_id}")
async def delete_product_image(
    product_id: UUID,
    image_id: UUID
):
    """Delete a specific image."""
    # Get image path from database
    async with get_db() as db:
        image = await db.fetchrow(
            "SELECT storage_path FROM image_metadata WHERE id = $1 AND product_id = $2",
            image_id, product_id
        )
        
    if not image:
        raise HTTPException(404, "Image not found")
        
    await storage.delete_image(image["storage_path"])
    
    return {"success": True, "message": "Image deleted"}
```

## Direct Frontend Upload (Using Supabase JS)

For better performance, you can upload directly from the frontend:

```javascript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Upload image directly from frontend
async function uploadProductImage(productId, file, imageType) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const path = `products/${productId}/${imageType}/${timestamp}_${file.name}`
  
  const { data, error } = await supabase.storage
    .from('product-images')
    .upload(path, file, {
      contentType: file.type,
      upsert: false
    })
    
  if (error) throw error
  
  // Get public URL
  const { data: { publicUrl } } = supabase.storage
    .from('product-images')
    .getPublicUrl(path)
    
  // Save metadata to database via API
  await saveImageMetadata(productId, path, publicUrl, file.size)
  
  return publicUrl
}
```

## Image Optimization Details

The storage service automatically optimizes images with these settings:

- **Max Dimension**: 2048px (maintains aspect ratio)
- **Format**: WebP (better compression than JPEG/PNG)
- **Quality**: 85% (good balance of quality/size)
- **Method**: Slowest compression for best file size

Example size savings:
- Original PNG: 5MB → Optimized WebP: 500KB (90% reduction)
- Original JPEG: 2MB → Optimized WebP: 400KB (80% reduction)

## Error Handling

```python
from src.services.storage import SupabaseStorageService

try:
    result = await storage.upload_image(...)
except ValueError as e:
    # Invalid parameters (e.g., wrong image_type)
    print(f"Invalid input: {e}")
except Exception as e:
    # Storage or network errors
    print(f"Upload failed: {e}")
```

## Best Practices

1. **Always specify product_id** for proper partitioning
2. **Use appropriate image_type** to ensure correct folder placement
3. **Include session_id** for generated content traceability
4. **Enable optimization** for generated images (saves bandwidth)
5. **Set up cleanup jobs** for temporary files
6. **Monitor storage usage** to control costs
7. **Use direct upload** from frontend for large files

## Storage Limits

- **Images**: 10MB per file
- **Videos**: 100MB per file
- **Reference Images**: Private bucket, requires authentication
- **Public Assets**: Served via CDN for fast delivery

## Cost Optimization Tips

1. **Optimize all generated images** (80-90% size reduction)
2. **Clean up temp files regularly** (24-hour retention)
3. **Use lifecycle rules** for old products
4. **Monitor bandwidth usage** via Supabase dashboard
5. **Consider Cloudflare R2** for high-bandwidth scenarios