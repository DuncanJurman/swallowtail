#!/usr/bin/env python3
"""
Setup Supabase storage buckets for instance-based media storage.

This script creates the necessary storage buckets and configures
RLS policies for instance-based access control.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client, Client
from src.core.config import get_settings


def setup_storage_buckets(client: Client):
    """Create storage buckets for instance media."""
    
    buckets = [
        {
            "name": "instance-media",
            "public": True,  # Public for serving media
        },
        {
            "name": "instance-temp", 
            "public": False,  # Private for temporary files
        }
    ]
    
    for bucket in buckets:
        try:
            # Create bucket with minimal options first
            # The issue might be with how the Python client sends the options
            response = client.storage.create_bucket(
                bucket["name"],
                options={"public": bucket["public"]}
            )
            print(f"✅ Created bucket: {bucket['name']}")
        except Exception as e:
            error_str = str(e).lower()
            if "already exists" in error_str or "duplicate" in error_str:
                print(f"ℹ️  Bucket already exists: {bucket['name']}")
                # Try to update bucket configuration
                try:
                    client.storage.update_bucket(
                        bucket["name"],
                        options={"public": bucket["public"]}
                    )
                    print(f"✅ Updated bucket configuration: {bucket['name']}")
                except Exception as update_error:
                    print(f"⚠️  Could not update bucket {bucket['name']}: {update_error}")
            else:
                print(f"❌ Error creating bucket {bucket['name']}: {e}")
                print(f"   You may need to create this bucket manually in Supabase dashboard")


def print_mvp_notes():
    """
    Print notes about the MVP approach without RLS.
    """
    
    notes = """
🎯 MVP Approach: No RLS Policies
================================

This MVP uses the service key for all storage operations.
Access control is handled at the API level, not at the database level.

Benefits:
✅ Simpler implementation
✅ Faster development
✅ Easier debugging
✅ Can add RLS later when needed

Security Model:
- All storage operations use service key (admin access)
- Access control enforced in backend API endpoints
- Users never get direct Supabase access
- Instance isolation handled in application logic

When to add RLS:
- When you need direct client access to Supabase
- When you want defense-in-depth security
- When you have multiple services accessing storage
    """
    
    print(notes)


def main():
    """Main function to setup storage."""
    print("🚀 Setting up Supabase storage for instance-based media...")
    
    # Get settings
    settings = get_settings()
    
    # Create Supabase client with service key
    client = create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )
    
    # Setup buckets
    print("\n📦 Creating storage buckets...")
    setup_storage_buckets(client)
    
    # Show MVP approach notes
    print_mvp_notes()
    
    print("\n✨ Storage setup complete!")
    print("\nNext steps:")
    print("1. Test upload/download functionality")
    print("2. Implement instance isolation in API endpoints")
    print("3. Add RLS policies later when moving beyond MVP")


if __name__ == "__main__":
    main()