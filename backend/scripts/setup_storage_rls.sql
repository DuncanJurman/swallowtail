-- Row Level Security (RLS) policies for Supabase Storage
-- Run this after creating the storage buckets

-- Enable RLS on storage.objects table
ALTER TABLE storage.objects ENABLE ROW LEVEL SECURITY;

-- Policy: Allow authenticated users to upload images to their own products
CREATE POLICY "Users can upload images to their products"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id IN ('product-images', 'product-videos') AND
    -- Extract product_id from path: products/{product_id}/...
    (string_to_array(name, '/'))[2] IN (
        SELECT id::text 
        FROM products 
        WHERE owner_id = auth.uid()
    )
);

-- Policy: Allow authenticated users to upload reference images (private bucket)
CREATE POLICY "Users can upload reference images to their products"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
    bucket_id = 'reference-images' AND
    (string_to_array(name, '/'))[2] IN (
        SELECT id::text 
        FROM products 
        WHERE owner_id = auth.uid()
    )
);

-- Policy: Public read access for product images and videos
CREATE POLICY "Public read access for product assets"
ON storage.objects FOR SELECT
TO public
USING (bucket_id IN ('product-images', 'product-videos'));

-- Policy: Only product owners can view reference images
CREATE POLICY "Product owners can view reference images"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'reference-images' AND
    (string_to_array(name, '/'))[2] IN (
        SELECT id::text 
        FROM products 
        WHERE owner_id = auth.uid()
    )
);

-- Policy: Users can update their own product images (for metadata updates)
CREATE POLICY "Users can update their product images"
ON storage.objects FOR UPDATE
TO authenticated
USING (
    bucket_id IN ('product-images', 'product-videos', 'reference-images') AND
    (string_to_array(name, '/'))[2] IN (
        SELECT id::text 
        FROM products 
        WHERE owner_id = auth.uid()
    )
);

-- Policy: Users can delete their own product images
CREATE POLICY "Users can delete their product images"
ON storage.objects FOR DELETE
TO authenticated
USING (
    bucket_id IN ('product-images', 'product-videos', 'reference-images') AND
    (string_to_array(name, '/'))[2] IN (
        SELECT id::text 
        FROM products 
        WHERE owner_id = auth.uid()
    )
);

-- Create a function to extract product_id from storage path
CREATE OR REPLACE FUNCTION storage.get_product_id_from_path(object_name text)
RETURNS uuid AS $$
BEGIN
    -- Path format: products/{product_id}/...
    -- Extract the second element after splitting by '/'
    RETURN (string_to_array(object_name, '/'))[2]::uuid;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create a function to check if user owns the product
CREATE OR REPLACE FUNCTION storage.user_owns_product(user_id uuid, product_id uuid)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 
        FROM products 
        WHERE id = product_id 
        AND owner_id = user_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Additional helper policies for service role operations

-- Policy: Service role can do anything (for backend operations)
CREATE POLICY "Service role has full access"
ON storage.objects
TO service_role
USING (true)
WITH CHECK (true);

-- Create indexes for better performance on storage queries
CREATE INDEX IF NOT EXISTS idx_storage_objects_bucket_path 
ON storage.objects(bucket_id, name);

-- Bucket-specific configurations

-- Set CORS for public buckets (allows frontend to upload directly)
UPDATE storage.buckets 
SET public = true,
    file_size_limit = 10485760, -- 10MB for images
    allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif']
WHERE id = 'product-images';

UPDATE storage.buckets 
SET public = true,
    file_size_limit = 104857600, -- 100MB for videos
    allowed_mime_types = ARRAY['video/mp4', 'video/webm', 'video/quicktime']
WHERE id = 'product-videos';

UPDATE storage.buckets 
SET public = false, -- Private bucket
    file_size_limit = 10485760, -- 10MB
    allowed_mime_types = ARRAY['image/jpeg', 'image/png', 'image/webp']
WHERE id = 'reference-images';

-- Grant necessary permissions to authenticated users
GRANT SELECT ON storage.objects TO authenticated;
GRANT INSERT, UPDATE, DELETE ON storage.objects TO authenticated;
GRANT SELECT ON storage.buckets TO authenticated;

-- Grant public read for public buckets
GRANT SELECT ON storage.objects TO anon;
GRANT SELECT ON storage.buckets TO anon;