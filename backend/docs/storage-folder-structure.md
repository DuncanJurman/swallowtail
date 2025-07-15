# Storage Folder Structure

## Overview

All storage is partitioned by product ID to ensure clean separation and easy management. Each product has its own folder hierarchy containing all related assets.

## Folder Structure

```
product-images/
└── products/
    └── {product_id}/
        ├── reference/              # User-uploaded reference images
        │   ├── {timestamp}_{filename}
        │   └── ...
        ├── generated/              # AI-generated final approved images
        │   ├── main/              # Main product photography
        │   │   ├── {session_id}_final.webp
        │   │   └── ...
        │   ├── lifestyle/         # Lifestyle and context images
        │   │   ├── {session_id}_{scene}_final.webp
        │   │   └── ...
        │   ├── detail/            # Detail shots and close-ups
        │   │   └── ...
        │   └── marketing/         # Marketing and ad creatives
        │       ├── social/        # Social media formats
        │       ├── display/       # Display ad formats
        │       └── email/         # Email campaign images
        └── temp/                   # Temporary evaluation images (auto-cleaned)
            └── {session_id}/
                └── ...

product-videos/
└── products/
    └── {product_id}/
        ├── demos/                  # Product demonstration videos
        │   ├── {session_id}_demo.mp4
        │   └── ...
        ├── ads/                    # Advertisement videos
        │   ├── tiktok/
        │   ├── youtube/
        │   └── instagram/
        └── raw/                    # Unprocessed video uploads
            └── ...

reference-images/                   # Private bucket - requires auth
└── products/
    └── {product_id}/
        ├── brand/                  # Brand guidelines and assets
        │   ├── logo.png
        │   ├── style_guide.pdf
        │   └── ...
        └── inspiration/            # Inspiration and mood boards
            └── ...
```

## Path Generation Rules

### Image Paths

```python
def generate_image_path(product_id: str, image_type: str, sub_type: str = None) -> str:
    """Generate storage path for images."""
    
    base = f"products/{product_id}"
    
    if image_type == "reference":
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{base}/reference/{timestamp}_{{filename}}"
        
    elif image_type == "generated":
        if sub_type:
            return f"{base}/generated/{sub_type}/{{session_id}}_final.webp"
        return f"{base}/generated/{{session_id}}_final.webp"
        
    elif image_type == "temp":
        return f"{base}/temp/{{session_id}}/{{image_id}}.webp"
```

### Video Paths

```python
def generate_video_path(product_id: str, video_type: str, platform: str = None) -> str:
    """Generate storage path for videos."""
    
    base = f"products/{product_id}"
    
    if video_type == "demo":
        return f"{base}/demos/{{session_id}}_demo.mp4"
        
    elif video_type == "ad" and platform:
        return f"{base}/ads/{platform}/{{session_id}}_{platform}.mp4"
        
    elif video_type == "raw":
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{base}/raw/{timestamp}_{{filename}}"
```

## Access Control

### Public Buckets (product-images, product-videos)
- Read: Public (for CDN serving)
- Write: Authenticated users who own the product
- Delete: Product owners only

### Private Bucket (reference-images)
- Read: Product owners and authorized team members
- Write: Product owners only
- Delete: Product owners only

## Cleanup Policies

### Temporary Files
- Location: `products/{product_id}/temp/`
- Retention: 24 hours
- Cleanup: Automatic via lifecycle rules or cron job

### Archived Products
- After 180 days of inactivity: Move to cold storage
- After 365 days: Compress and archive
- Deleted products: Remove all assets after 30-day grace period

## URL Structure

### Public Assets
```
https://{supabase_url}/storage/v1/object/public/product-images/products/{product_id}/generated/main/{filename}
```

### Private Assets (Requires Auth)
```
https://{supabase_url}/storage/v1/object/authenticated/reference-images/products/{product_id}/brand/{filename}
```

### CDN URLs (with Transformations)
```
https://{supabase_url}/storage/v1/render/image/public/product-images/products/{product_id}/generated/main/{filename}?width=800&height=800&resize=contain
```

## Best Practices

1. **Always use product ID** in paths for clean partitioning
2. **Include timestamps** in user-uploaded filenames to avoid conflicts
3. **Use session IDs** for AI-generated content traceability
4. **Standardize on WebP** for images (better compression)
5. **Implement cleanup** for temporary and old files
6. **Use meaningful subfolder names** for organization
7. **Version control** brand assets in reference-images