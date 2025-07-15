#!/usr/bin/env python3
"""
Setup script for Supabase Storage buckets.
Run this to create the necessary storage buckets with proper configuration.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_storage_buckets(client: Client):
    """Create storage buckets for images and videos."""
    
    buckets = [
        {
            "id": "product-images",
            "name": "Product Images",
            "public": True,  # Public for CDN access
            "file_size_limit": 10485760,  # 10MB limit
            "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/gif"]
        },
        {
            "id": "product-videos", 
            "name": "Product Videos",
            "public": True,  # Public for streaming
            "file_size_limit": 104857600,  # 100MB limit
            "allowed_mime_types": ["video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"]
        },
        {
            "id": "reference-images",
            "name": "Reference Images",
            "public": False,  # Private - only accessible to product owners
            "file_size_limit": 10485760,  # 10MB limit
            "allowed_mime_types": ["image/jpeg", "image/png", "image/webp"]
        }
    ]
    
    for bucket in buckets:
        try:
            # Create bucket
            # Create bucket with options
            options = {
                "public": bucket["public"],
                "allowed_mime_types": bucket["allowed_mime_types"]
            }
            # Only add file_size_limit if it's reasonable (API limitation)
            if bucket["file_size_limit"] <= 52428800:  # 50MB
                options["file_size_limit"] = bucket["file_size_limit"]
            
            response = client.storage.create_bucket(
                bucket["id"],
                options=options
            )
            print(f"✅ Created bucket: {bucket['name']} ({bucket['id']})")
            
        except Exception as e:
            if "already exists" in str(e):
                print(f"ℹ️  Bucket already exists: {bucket['name']} ({bucket['id']})")
                
                # Update bucket configuration if it exists
                try:
                    # Update bucket with options
                    update_options = {
                        "public": bucket["public"],
                        "allowed_mime_types": bucket["allowed_mime_types"]
                    }
                    # Only add file_size_limit if it's reasonable
                    if bucket["file_size_limit"] <= 52428800:  # 50MB
                        update_options["file_size_limit"] = bucket["file_size_limit"]
                    
                    client.storage.update_bucket(
                        bucket["id"],
                        options=update_options
                    )
                    print(f"✅ Updated bucket configuration: {bucket['name']}")
                except Exception as update_error:
                    print(f"❌ Failed to update bucket: {update_error}")
            else:
                print(f"❌ Failed to create bucket {bucket['name']}: {e}")


def main():
    """Main setup function."""
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        print("Make sure to set these in your .env file")
        return
        
    # Create Supabase client
    client = create_client(supabase_url, supabase_key)
    
    print("🚀 Setting up Supabase Storage buckets...")
    print("-" * 50)
    
    # Create buckets
    create_storage_buckets(client)
    
    print("-" * 50)
    print("✅ Storage setup complete!")
    print("\nNext steps:")
    print("1. Run the database migration to create metadata tables")
    print("2. Apply RLS policies for secure access")
    print("3. Test upload functionality")


if __name__ == "__main__":
    main()