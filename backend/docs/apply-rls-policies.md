# Applying RLS Policies to Supabase Storage

## Instructions

The RLS (Row Level Security) policies need to be applied manually in the Supabase SQL editor. Follow these steps:

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor section
3. Copy and paste the contents of `scripts/setup_storage_rls.sql`
4. Execute the SQL commands

## What the RLS Policies Do

The policies implement the following security rules:

### Product Images Bucket (public)
- **Insert**: Authenticated users can upload images for their own products
- **Select**: Anyone can view images (public bucket)
- **Delete**: Only product owners can delete their images

### Product Videos Bucket (public)
- **Insert**: Authenticated users can upload videos for their own products
- **Select**: Anyone can view videos (public bucket)
- **Delete**: Only product owners can delete their videos

### Reference Images Bucket (private)
- **Insert**: Authenticated users can upload reference images for their own products
- **Select**: Only product owners can view their reference images
- **Delete**: Only product owners can delete their reference images

## Verification

After applying the policies, you can verify they're working by:

1. Running `test_storage_setup.py` which includes permission tests
2. Checking the Storage section in Supabase dashboard to see the policies listed
3. Testing uploads/downloads with different user contexts

## Important Notes

- The policies use the `auth.uid()` function to identify the current user
- Product ownership is determined by the `user_id` column in the products table
- The policies assume the storage paths follow the pattern: `products/{product_id}/...`
- Make sure your products table has proper foreign key relationships set up