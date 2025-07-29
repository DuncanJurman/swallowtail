# Storage Architecture for Swallowtail

## Executive Summary

This document outlines the storage architecture for Swallowtail's image and video assets. Since the platform only needs to store reference images and final approved images (not intermediate generation steps), we can optimize for cost efficiency while maintaining performance. Our primary recommendation is **Supabase Storage** due to existing infrastructure integration, with **Cloudflare R2** as a compelling alternative for significant cost savings.

## Table of Contents
1. [Storage Requirements](#storage-requirements)
2. [Cost Analysis](#cost-analysis)
3. [Recommended Solution: Supabase Storage](#recommended-solution-supabase-storage)
4. [Alternative: Cloudflare R2](#alternative-cloudflare-r2)
5. [Implementation Architecture](#implementation-architecture)
6. [Storage Optimization Strategies](#storage-optimization-strategies)
7. [Database Schema](#database-schema)
8. [Migration Strategy](#migration-strategy)

---

## Storage Requirements

### What We Need to Store

1. **Reference Images** (User Uploaded)
   - Product reference photos
   - Brand guideline images
   - Style inspiration images
   - Average size: 2-5 MB per image
   - Retention: Permanent (while product active)

2. **Final Approved Images** (Generated)
   - Product photography (main + variants)
   - Lifestyle images
   - Marketing materials
   - Average size: 1-3 MB per image (after optimization)
   - Retention: Permanent (while product active)

3. **Videos** (Future)
   - Product demonstration videos
   - Social media clips
   - Average size: 10-50 MB per video
   - Retention: Permanent (while product active)

### What We DON'T Store
- ❌ Intermediate generation attempts
- ❌ Refinement iterations
- ❌ Rejected images
- ❌ Temporary session data

### Estimated Storage Needs

```
Per Product:
- Reference images: 3-5 images × 3 MB = 15 MB
- Final images: 10-15 images × 2 MB = 30 MB
- Videos (future): 3-5 videos × 30 MB = 150 MB
- Total per product: ~200 MB

Scale Projections:
- 100 products: 20 GB
- 1,000 products: 200 GB
- 10,000 products: 2 TB

Monthly bandwidth (assuming 10x storage in views):
- 100 products: 200 GB
- 1,000 products: 2 TB
- 10,000 products: 20 TB
```

---

## Cost Analysis

### Storage Provider Comparison

| Provider | Storage Cost | Bandwidth Cost | Free Tier | Additional Costs |
|----------|--------------|----------------|-----------|------------------|
| **Supabase Storage** | $0.021/GB/mo | $0.09/GB | 1 GB storage, 2 GB bandwidth | Integrated with existing DB |
| **Cloudflare R2** | $0.015/GB/mo | $0 (FREE!) | 10 GB storage, unlimited bandwidth | $0.36/million requests |
| **AWS S3** | $0.023/GB/mo | $0.09/GB | None | Request costs, complexity |
| **Google Cloud** | $0.020/GB/mo | $0.12/GB | 5 GB storage | Request costs |
| **Backblaze B2** | $0.006/GB/mo | $0.01/GB | 10 GB storage | API costs |

### Monthly Cost Projections

```python
# Cost calculation for 1,000 products (200 GB storage, 2 TB bandwidth)

costs = {
    "Supabase Storage": {
        "storage": 200 * 0.021,  # $4.20
        "bandwidth": 2000 * 0.09,  # $180
        "total": 184.20
    },
    "Cloudflare R2": {
        "storage": 200 * 0.015,  # $3.00
        "bandwidth": 0,  # FREE!
        "requests": 2 * 0.36,  # ~$0.72 (2M requests)
        "total": 3.72  # 98% savings!
    },
    "AWS S3 + CloudFront": {
        "storage": 200 * 0.023,  # $4.60
        "bandwidth": 2000 * 0.085,  # $170
        "total": 174.60
    }
}
```

**Key Insight**: Cloudflare R2's free bandwidth makes it incredibly cost-effective at scale.

---

## Recommended Solution: Supabase Storage

### Why Supabase Storage?

1. **Seamless Integration**: Already using Supabase for PostgreSQL
2. **Unified Authentication**: Same auth system for DB and storage
3. **RLS Policies**: Row Level Security extends to storage
4. **Simple API**: Minimal additional complexity
5. **Good CDN**: Built-in CDN for global distribution

### Implementation

```python
from supabase import create_client, Client
from typing import Optional, Dict, Any
import aiofiles
from PIL import Image
import io

class SupabaseStorageManager:
    """Manages image storage using Supabase Storage."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        self.client: Client = create_client(supabase_url, supabase_key)
        self.bucket_name = "product-images"
        self._ensure_bucket()
        
    def _ensure_bucket(self):
        """Ensure storage bucket exists."""
        try:
            self.client.storage.create_bucket(
                self.bucket_name,
                options={
                    "public": True,  # Public for CDN access
                    "file_size_limit": 10485760,  # 10MB limit
                    "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"]
                }
            )
        except:
            pass  # Bucket already exists
            
    async def upload_image(self, 
                         file_data: bytes,
                         file_path: str,
                         metadata: Dict[str, Any]) -> str:
        """Upload image to Supabase Storage."""
        
        # Optimize image before upload
        optimized_data = await self._optimize_image(file_data)
        
        # Upload to Supabase
        response = self.client.storage.from_(self.bucket_name).upload(
            path=file_path,
            file=optimized_data,
            file_options={"content-type": "image/webp"}
        )
        
        if response.error:
            raise Exception(f"Upload failed: {response.error}")
            
        # Get public URL
        public_url = self.client.storage.from_(self.bucket_name).get_public_url(file_path)
        
        # Store metadata in database
        await self._store_metadata(file_path, public_url, metadata)
        
        return public_url
        
    async def _optimize_image(self, image_data: bytes) -> bytes:
        """Optimize image for storage (resize, compress, convert to WebP)."""
        
        img = Image.open(io.BytesIO(image_data))
        
        # Resize if too large
        max_dimension = 2048
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
        # Convert to WebP for better compression
        output = io.BytesIO()
        img.save(output, format='WEBP', quality=85, optimize=True)
        
        return output.getvalue()
        
    async def upload_reference_image(self,
                                   product_id: str,
                                   image_data: bytes,
                                   original_filename: str) -> str:
        """Upload reference image for a product."""
        
        file_path = f"products/{product_id}/reference/{generate_id()}_{original_filename}"
        
        metadata = {
            "type": "reference",
            "product_id": product_id,
            "original_filename": original_filename,
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        return await self.upload_image(image_data, file_path, metadata)
        
    async def upload_generated_image(self,
                                   product_id: str,
                                   session_id: str,
                                   image_data: bytes,
                                   image_type: str) -> str:
        """Upload final approved generated image."""
        
        file_path = f"products/{product_id}/generated/{image_type}/{generate_id()}.webp"
        
        metadata = {
            "type": "generated",
            "product_id": product_id,
            "session_id": session_id,
            "image_type": image_type,
            "approved_at": datetime.utcnow().isoformat()
        }
        
        return await self.upload_image(image_data, file_path, metadata)
        
    async def delete_product_images(self, product_id: str):
        """Delete all images for a product."""
        
        # List all files for product
        files = self.client.storage.from_(self.bucket_name).list(
            path=f"products/{product_id}"
        )
        
        # Delete each file
        for file in files:
            self.client.storage.from_(self.bucket_name).remove(
                [f"products/{product_id}/{file['name']}"]
            )

class SupabaseVideoManager(SupabaseStorageManager):
    """Extended manager for video storage."""
    
    def __init__(self, supabase_url: str, supabase_key: str):
        super().__init__(supabase_url, supabase_key)
        self.video_bucket = "product-videos"
        self._ensure_video_bucket()
        
    def _ensure_video_bucket(self):
        """Create video bucket with larger size limits."""
        try:
            self.client.storage.create_bucket(
                self.video_bucket,
                options={
                    "public": True,
                    "file_size_limit": 104857600,  # 100MB limit
                    "allowed_mime_types": ["video/mp4", "video/webm"]
                }
            )
        except:
            pass
```

### Supabase RLS Policies

```sql
-- Storage RLS policies for access control
CREATE POLICY "Users can upload reference images for their products"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'product-images' AND
    (storage.foldername(name))[2] IN (
        SELECT id::text FROM products WHERE owner_id = auth.uid()
    )
);

CREATE POLICY "Public read access for product images"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'product-images');

CREATE POLICY "Users can delete their product images"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id = 'product-images' AND
    (storage.foldername(name))[2] IN (
        SELECT id::text FROM products WHERE owner_id = auth.uid()
    )
);
```

---

## Alternative: Cloudflare R2

### Why Consider R2?

1. **Zero Bandwidth Costs**: Free egress is game-changing at scale
2. **S3 Compatible**: Easy migration path
3. **Global Performance**: Cloudflare's edge network
4. **Simple Pricing**: Predictable costs

### Implementation

```python
import boto3
from botocore.config import Config

class CloudflareR2Manager:
    """Manages image storage using Cloudflare R2."""
    
    def __init__(self, account_id: str, access_key: str, secret_key: str):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=f'https://{account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        self.bucket_name = 'swallowtail-images'
        self.public_url_base = f'https://images.swallowtail.com'  # Custom domain
        
    async def upload_image(self,
                         file_data: bytes,
                         file_path: str,
                         metadata: Dict[str, Any]) -> str:
        """Upload image to R2."""
        
        # Optimize image
        optimized_data = await self._optimize_image(file_data)
        
        # Upload to R2
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=file_path,
            Body=optimized_data,
            ContentType='image/webp',
            Metadata=metadata,
            CacheControl='public, max-age=31536000'  # 1 year cache
        )
        
        # Return public URL
        return f"{self.public_url_base}/{file_path}"
        
    def setup_lifecycle_rules(self):
        """Set up lifecycle rules for automatic cleanup."""
        
        lifecycle_config = {
            'Rules': [
                {
                    'ID': 'delete-temp-files',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': 'temp/'},
                    'Expiration': {'Days': 1}
                },
                {
                    'ID': 'archive-old-products',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': 'products/'},
                    'Transitions': [{
                        'Days': 365,
                        'StorageClass': 'GLACIER'
                    }]
                }
            ]
        }
        
        self.s3_client.put_bucket_lifecycle_configuration(
            Bucket=self.bucket_name,
            LifecycleConfiguration=lifecycle_config
        )
```

### R2 with Cloudflare Workers

```javascript
// Cloudflare Worker for image optimization and serving
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Parse image transformation parameters
    const options = {
      width: url.searchParams.get('w'),
      height: url.searchParams.get('h'),
      quality: url.searchParams.get('q') || '85',
      format: url.searchParams.get('f') || 'auto'
    };
    
    // Get image from R2
    const objectKey = url.pathname.slice(1);
    const object = await env.BUCKET.get(objectKey);
    
    if (!object) {
      return new Response('Not found', { status: 404 });
    }
    
    // Apply transformations using Cloudflare Image Resizing
    const transformedImage = await fetch(url.toString(), {
      cf: {
        image: {
          width: options.width,
          height: options.height,
          quality: options.quality,
          format: options.format
        }
      }
    });
    
    // Cache the transformed image
    const response = new Response(transformedImage.body, {
      headers: {
        'Content-Type': `image/${options.format}`,
        'Cache-Control': 'public, max-age=31536000',
        'CDN-Cache-Control': 'max-age=31536000'
      }
    });
    
    return response;
  }
};
```

---

## Implementation Architecture

### Storage Service Interface

```python
from abc import ABC, abstractmethod
from typing import Protocol, Optional

class StorageBackend(Protocol):
    """Protocol for storage backends."""
    
    async def upload(self, 
                    file_data: bytes,
                    path: str,
                    metadata: Dict[str, Any]) -> str:
        """Upload file and return URL."""
        ...
        
    async def delete(self, path: str) -> bool:
        """Delete file."""
        ...
        
    async def get_url(self, path: str) -> str:
        """Get public URL for file."""
        ...

class UnifiedStorageManager:
    """Unified interface for multiple storage backends."""
    
    def __init__(self, primary_backend: StorageBackend, 
                 fallback_backend: Optional[StorageBackend] = None):
        self.primary = primary_backend
        self.fallback = fallback_backend
        
    async def store_image(self,
                         image_data: bytes,
                         image_metadata: ImageMetadata) -> StorageResult:
        """Store image with automatic optimization and fallback."""
        
        # Generate storage path
        path = self._generate_path(image_metadata)
        
        # Optimize image
        optimized_data = await self._optimize_for_storage(image_data)
        
        try:
            # Try primary storage
            url = await self.primary.upload(
                file_data=optimized_data,
                path=path,
                metadata=image_metadata.dict()
            )
            
            # Store metadata in database
            await self._store_metadata(url, image_metadata, "primary")
            
            return StorageResult(
                success=True,
                url=url,
                backend="primary",
                size=len(optimized_data)
            )
            
        except Exception as e:
            if self.fallback:
                # Try fallback storage
                url = await self.fallback.upload(
                    file_data=optimized_data,
                    path=path,
                    metadata=image_metadata.dict()
                )
                
                await self._store_metadata(url, image_metadata, "fallback")
                
                return StorageResult(
                    success=True,
                    url=url,
                    backend="fallback",
                    size=len(optimized_data)
                )
            else:
                raise
                
    async def _optimize_for_storage(self, image_data: bytes) -> bytes:
        """Optimize image for storage efficiency."""
        
        optimizer = ImageOptimizer()
        
        # Apply optimizations
        optimized = await optimizer.optimize(
            image_data,
            max_dimension=2048,
            target_format="webp",
            quality=85,
            strip_metadata=True
        )
        
        return optimized
```

### Caching Layer

```python
class ImageCacheManager:
    """CDN and local cache management."""
    
    def __init__(self, storage_manager: UnifiedStorageManager):
        self.storage = storage_manager
        self.redis = get_redis_client()
        self.local_cache = LRUCache(maxsize=1000)
        
    async def get_image_url(self, 
                          image_id: str,
                          transformations: Optional[Dict] = None) -> str:
        """Get image URL with caching."""
        
        # Generate cache key
        cache_key = self._generate_cache_key(image_id, transformations)
        
        # Check local cache
        if cache_key in self.local_cache:
            return self.local_cache[cache_key]
            
        # Check Redis cache
        cached_url = await self.redis.get(f"img_url:{cache_key}")
        if cached_url:
            self.local_cache[cache_key] = cached_url
            return cached_url
            
        # Get from storage
        base_url = await self.storage.get_url(image_id)
        
        # Apply transformations if needed
        if transformations:
            url = self._apply_transformations(base_url, transformations)
        else:
            url = base_url
            
        # Cache the URL
        await self.redis.setex(f"img_url:{cache_key}", 3600, url)
        self.local_cache[cache_key] = url
        
        return url
```

---

## Storage Optimization Strategies

### 1. Image Optimization Pipeline

```python
class ImageOptimizer:
    """Comprehensive image optimization pipeline."""
    
    def __init__(self):
        self.formats_priority = ["webp", "avif", "jpeg"]
        
    async def optimize(self,
                      image_data: bytes,
                      max_dimension: int = 2048,
                      target_format: str = "auto",
                      quality: int = 85) -> bytes:
        """Optimize image for web delivery."""
        
        # Open image
        img = Image.open(io.BytesIO(image_data))
        
        # Resize if needed
        if img.width > max_dimension or img.height > max_dimension:
            img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
            
        # Determine best format
        if target_format == "auto":
            format = self._determine_best_format(img)
        else:
            format = target_format
            
        # Save with optimization
        output = io.BytesIO()
        save_kwargs = {
            'format': format.upper(),
            'quality': quality,
            'optimize': True
        }
        
        if format == 'webp':
            save_kwargs['method'] = 6  # Slower but better compression
            
        img.save(output, **save_kwargs)
        
        return output.getvalue()
        
    def _determine_best_format(self, img: Image) -> str:
        """Determine optimal format based on image characteristics."""
        
        # Check if image has transparency
        if img.mode == 'RGBA':
            return 'webp'  # WebP supports transparency
            
        # Check image complexity
        complexity = self._calculate_complexity(img)
        
        if complexity < 0.3:
            return 'webp'  # Simple images compress well with WebP
        else:
            return 'jpeg'  # Complex images may be better as JPEG
```

### 2. Lifecycle Management

```python
class StorageLifecycleManager:
    """Manages storage lifecycle and cleanup."""
    
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
        self.db = get_db_session()
        
    async def cleanup_inactive_products(self, days_inactive: int = 180):
        """Clean up images for inactive products."""
        
        # Find inactive products
        inactive_products = await self.db.query("""
            SELECT id, last_active_at 
            FROM products 
            WHERE last_active_at < NOW() - INTERVAL '%s days'
            AND status != 'archived'
        """, [days_inactive])
        
        for product in inactive_products:
            # Archive images to cold storage
            await self._archive_product_images(product.id)
            
            # Update product status
            await self.db.execute("""
                UPDATE products 
                SET status = 'archived', archived_at = NOW()
                WHERE id = %s
            """, [product.id])
            
    async def optimize_storage_usage(self):
        """Optimize overall storage usage."""
        
        # Find duplicate images
        duplicates = await self._find_duplicate_images()
        
        # Deduplicate
        for duplicate_set in duplicates:
            await self._deduplicate_images(duplicate_set)
            
        # Convert old formats to WebP
        await self._convert_legacy_formats()
        
        # Remove orphaned files
        await self._cleanup_orphaned_files()
```

### 3. Smart Caching Strategy

```python
class SmartCacheStrategy:
    """Intelligent caching based on usage patterns."""
    
    def __init__(self):
        self.access_tracker = AccessTracker()
        
    async def get_cache_headers(self, 
                              image_type: str,
                              product_status: str) -> Dict[str, str]:
        """Generate optimal cache headers."""
        
        headers = {
            'Cache-Control': 'public',
            'Vary': 'Accept'
        }
        
        if product_status == 'active':
            # Active products - moderate caching
            headers['Cache-Control'] += ', max-age=86400'  # 1 day
        elif product_status == 'mature':
            # Mature products - long caching
            headers['Cache-Control'] += ', max-age=2592000'  # 30 days
        else:
            # Inactive - very long caching
            headers['Cache-Control'] += ', max-age=31536000'  # 1 year
            
        # Add stale-while-revalidate for better performance
        headers['Cache-Control'] += ', stale-while-revalidate=86400'
        
        return headers
```

---

## Database Schema

### Image Metadata Tables

```sql
-- Image metadata storage
CREATE TABLE image_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    
    -- Image identification
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    cdn_url TEXT,
    
    -- Image details
    image_type VARCHAR(50) NOT NULL, -- 'reference', 'generated', 'marketing'
    sub_type VARCHAR(50), -- 'main', 'lifestyle', 'detail', etc.
    
    -- File information
    file_size INTEGER NOT NULL,
    width INTEGER,
    height INTEGER,
    format VARCHAR(10), -- 'webp', 'jpeg', 'png'
    
    -- Generation details
    generation_session_id VARCHAR(255),
    evaluation_score NUMERIC(3,2),
    
    -- Storage backend
    storage_backend VARCHAR(50) DEFAULT 'supabase', -- 'supabase', 'r2', 's3'
    
    -- Status
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'archived', 'deleted'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP,
    archived_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_images_product (product_id),
    INDEX idx_images_type (image_type, sub_type),
    INDEX idx_images_status (status),
    INDEX idx_images_accessed (last_accessed_at)
);

-- Video metadata (future)
CREATE TABLE video_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    
    -- Video identification
    storage_path TEXT NOT NULL,
    public_url TEXT NOT NULL,
    streaming_url TEXT, -- For HLS/DASH
    
    -- Video details
    video_type VARCHAR(50) NOT NULL,
    duration_seconds INTEGER,
    file_size INTEGER NOT NULL,
    resolution VARCHAR(20), -- '1920x1080', '1280x720'
    codec VARCHAR(50),
    
    -- Processing status
    processing_status VARCHAR(50) DEFAULT 'pending',
    thumbnails JSONB, -- Array of thumbnail URLs
    
    -- Storage and status
    storage_backend VARCHAR(50) DEFAULT 'supabase',
    status VARCHAR(50) DEFAULT 'active',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    last_accessed_at TIMESTAMP
);

-- Access tracking for intelligent caching
CREATE TABLE asset_access_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_type VARCHAR(20) NOT NULL, -- 'image' or 'video'
    asset_id UUID NOT NULL,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_source VARCHAR(50), -- 'web', 'api', 'admin'
    
    -- Partitioned by month for performance
    PRIMARY KEY (id, accessed_at)
) PARTITION BY RANGE (accessed_at);

-- Create monthly partitions
CREATE TABLE asset_access_log_2024_01 PARTITION OF asset_access_log
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
-- Continue for each month...
```

---

## Migration Strategy

### Phase 1: Initial Setup (Week 1)

```python
class StorageMigration:
    """Handles migration to new storage system."""
    
    async def phase1_setup(self):
        """Set up storage infrastructure."""
        
        # 1. Create Supabase buckets
        await self.create_supabase_buckets()
        
        # 2. Set up database tables
        await self.run_migrations()
        
        # 3. Configure CDN
        await self.configure_cdn()
        
        # 4. Set up monitoring
        await self.setup_monitoring()
```

### Phase 2: Gradual Migration (Week 2-3)

```python
async def migrate_existing_images(batch_size: int = 100):
    """Migrate existing images to new storage."""
    
    migrator = StorageMigrator()
    
    # Get images to migrate
    while True:
        images = await get_unmigrated_images(limit=batch_size)
        
        if not images:
            break
            
        for image in images:
            try:
                # Download from old storage
                image_data = await download_from_old_storage(image.old_url)
                
                # Upload to new storage
                new_url = await storage_manager.upload(
                    file_data=image_data,
                    path=generate_new_path(image),
                    metadata=image.metadata
                )
                
                # Update database
                await update_image_url(image.id, new_url)
                
                # Mark as migrated
                await mark_migrated(image.id)
                
            except Exception as e:
                await log_migration_error(image.id, str(e))
```

### Phase 3: Cutover (Week 4)

1. **Switch writes to new storage**
2. **Update all read paths**
3. **Monitor for issues**
4. **Clean up old storage**

---

## Cost Optimization Tips

### 1. Intelligent Tiering

```python
class StorageTiering:
    """Implement storage tiering for cost optimization."""
    
    async def analyze_access_patterns(self):
        """Analyze image access patterns for tiering."""
        
        # Get access statistics
        stats = await self.db.query("""
            SELECT 
                im.id,
                im.product_id,
                im.file_size,
                COUNT(aal.id) as access_count,
                MAX(aal.accessed_at) as last_access
            FROM image_metadata im
            LEFT JOIN asset_access_log aal ON im.id = aal.asset_id
            WHERE im.created_at < NOW() - INTERVAL '30 days'
            GROUP BY im.id
        """)
        
        # Categorize images
        for image in stats:
            if image.access_count == 0:
                await self.move_to_archive(image.id)
            elif image.last_access < datetime.now() - timedelta(days=90):
                await self.move_to_cold_storage(image.id)
```

### 2. Format Optimization

```python
# Serve WebP to supported browsers
async def get_optimal_format(request_headers: Dict) -> str:
    """Determine optimal image format based on browser support."""
    
    accept = request_headers.get('Accept', '')
    
    if 'image/webp' in accept:
        return 'webp'
    elif 'image/avif' in accept:
        return 'avif'
    else:
        return 'jpeg'
```

### 3. Bandwidth Optimization

```python
# Implement responsive images
def generate_srcset(base_url: str, sizes: List[int]) -> str:
    """Generate srcset for responsive images."""
    
    srcset = []
    for size in sizes:
        url = f"{base_url}?w={size}"
        srcset.append(f"{url} {size}w")
        
    return ", ".join(srcset)

# Usage in frontend
# <img srcset="image.jpg?w=400 400w, image.jpg?w=800 800w" 
#      sizes="(max-width: 600px) 400px, 800px">
```

---

## Monitoring and Alerts

```python
class StorageMonitoring:
    """Monitor storage usage and costs."""
    
    def __init__(self):
        self.metrics = {
            "storage_used_gb": Gauge(),
            "bandwidth_used_gb": Counter(),
            "storage_cost_usd": Gauge(),
            "api_requests": Counter(),
            "upload_errors": Counter()
        }
        
    async def collect_metrics(self):
        """Collect storage metrics."""
        
        # Storage usage
        usage = await self.get_storage_usage()
        self.metrics["storage_used_gb"].set(usage.total_gb)
        
        # Calculate costs
        cost = self.calculate_monthly_cost(usage)
        self.metrics["storage_cost_usd"].set(cost)
        
        # Set up alerts
        if cost > COST_ALERT_THRESHOLD:
            await send_alert(f"Storage costs exceeded ${COST_ALERT_THRESHOLD}")
```

---

## Conclusion

For Swallowtail's needs, **Supabase Storage** provides the best balance of integration simplicity and features, making it the recommended choice for initial implementation. However, as the platform scales, **Cloudflare R2** becomes increasingly attractive due to its zero bandwidth costs, potentially saving thousands of dollars monthly.

The architecture is designed to be storage-agnostic, allowing for easy migration between providers as needs evolve. By storing only final approved images and implementing aggressive optimization strategies, storage costs remain minimal while maintaining high performance.

Key takeaways:
1. Start with Supabase Storage for simplicity
2. Plan for Cloudflare R2 migration at scale
3. Optimize images aggressively (WebP, sizing)
4. Implement intelligent caching and tiering
5. Monitor costs and usage continuously