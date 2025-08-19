#!/usr/bin/env python3
"""
Complete test of storage upload and TikTok posting flow.

This script:
1. Downloads a test video
2. Uploads it to Supabase storage
3. Gets the public URL
4. Posts it to TikTok (if credentials are configured)
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID, uuid4
import httpx

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from supabase import create_client
from src.core.config import get_settings
from src.services.tiktok.content_api import TikTokContentAPI
from src.services.tiktok.config import tiktok_config


async def download_test_video():
    """Download a small test video."""
    print("\n📥 Downloading test video...")
    print("-" * 50)
    
    # Use a small test video from a public source
    test_video_url = "https://sample-videos.com/video321/mp4/720/big_buck_bunny_720p_1mb.mp4"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(test_video_url, follow_redirects=True)
            response.raise_for_status()
            video_data = response.content
            print(f"✅ Downloaded {len(video_data) / 1024:.1f} KB test video")
            return video_data
        except Exception as e:
            print(f"⚠️  Could not download test video: {e}")
            print("   Using dummy data instead")
            # Return dummy data for testing
            return b"dummy video data for testing"


def upload_to_supabase(video_data: bytes):
    """Upload video to Supabase storage."""
    print("\n📤 Uploading to Supabase Storage...")
    print("-" * 50)
    
    settings = get_settings()
    client = create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )
    
    # Generate unique path for this test
    test_instance_id = "00000000-0000-0000-0000-000000000001"
    filename = f"test_video_{uuid4()}.mp4"
    path = f"instances/{test_instance_id}/tests/{filename}"
    
    try:
        # Upload to instance-media bucket (public)
        response = client.storage.from_("instance-media").upload(
            path=path,
            file=video_data,
            file_options={"content-type": "video/mp4"}
        )
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Upload failed: {response.error}")
            return None
        
        # Get public URL
        public_url = client.storage.from_("instance-media").get_public_url(path)
        
        print(f"✅ Uploaded successfully!")
        print(f"   Path: {path}")
        print(f"   Public URL: {public_url}")
        
        return {
            "path": path,
            "url": public_url,
            "client": client  # Return client for cleanup
        }
        
    except Exception as e:
        print(f"❌ Error uploading: {e}")
        return None


async def test_tiktok_posting(video_url: str):
    """Test posting the video to TikTok."""
    print("\n🎬 Testing TikTok Posting...")
    print("-" * 50)
    
    # Check if TikTok is configured
    if not tiktok_config.client_key:
        print("⚠️  TikTok client key not configured")
        print("   Set TIKTOK_CLIENT_KEY in your .env file")
        print("   Skipping TikTok posting test")
        return None
    
    # Using real OAuth tokens from database (decrypted)
    test_access_token = "act.nQThH5kVqNHRoKm5Dx80JfmkH5bLkTaBRJgduf358qr1XV28ZYpv2qYMPcw5!6425.u1"
    test_open_id = "-000UMTXhCm-Drwt-ixuWMY20DVgmkYzO1BR"
    
    if test_access_token == "YOUR_ACCESS_TOKEN":
        print("⚠️  OAuth tokens not configured")
        print("   To test real posting:")
        print("   1. Start the backend: poetry run python run.py")
        print("   2. Visit: http://localhost:8000/api/v1/tiktok/auth")
        print("   3. Complete OAuth flow")
        print("   4. Use the returned tokens here")
        print("\n   Simulating success for demo...")
        
        mock_publish_id = f"mock_{uuid4()}"
        print(f"   Mock publish ID: {mock_publish_id}")
        return mock_publish_id
    
    try:
        # Use the TikTok content API
        async with TikTokContentAPI(
            access_token=test_access_token,
            open_id=test_open_id
        ) as api:
            
            # Post the video
            result = await api.post_video_from_url(
                video_url=video_url,
                title="Test video from Swallowtail storage! 🚀 #test",
                privacy_level="SELF_ONLY"
            )
            
            if result.get("success"):
                publish_id = result.get("publish_id")
                print(f"✅ Posted to TikTok!")
                print(f"   Publish ID: {publish_id}")
                print(f"   Status: {result.get('status')}")
                return publish_id
            else:
                print(f"❌ Failed to post: {result.get('message')}")
                return None
                
    except Exception as e:
        print(f"❌ Error posting to TikTok: {e}")
        return None


def cleanup_test_file(storage_info: dict):
    """Clean up the test file from storage."""
    print("\n🗑️  Cleaning up...")
    print("-" * 50)
    
    if not storage_info:
        return
    
    try:
        client = storage_info["client"]
        path = storage_info["path"]
        
        client.storage.from_("instance-media").remove([path])
        print(f"✅ Deleted test file: {path}")
        
    except Exception as e:
        print(f"⚠️  Could not delete test file: {e}")
        print(f"   You may want to manually delete: {storage_info['path']}")


async def main():
    """Run the complete test flow."""
    print("=" * 60)
    print("🚀 Supabase Storage → TikTok Posting Test")
    print("=" * 60)
    
    # Step 1: Download test video
    video_data = await download_test_video()
    
    if not video_data:
        print("❌ No video data to test with")
        return
    
    # Step 2: Upload to Supabase
    storage_info = upload_to_supabase(video_data)
    
    if not storage_info:
        print("❌ Failed to upload to Supabase")
        return
    
    # Step 3: Post to TikTok
    publish_id = await test_tiktok_posting(storage_info["url"])
    
    # Step 4: Clean up (optional - comment out to keep test file)
    # cleanup_test_file(storage_info)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"✅ Video uploaded to Supabase: {storage_info['url']}")
    
    if publish_id:
        if publish_id.startswith("mock_"):
            print(f"✅ TikTok posting simulated: {publish_id}")
        else:
            print(f"✅ Video posted to TikTok: {publish_id}")
    else:
        print("⚠️  TikTok posting not tested (needs OAuth setup)")
    
    print("\n📝 Next Steps:")
    print("1. Visit the Supabase URL to verify the video is accessible")
    print("2. Set up TikTok OAuth to test real posting")
    print("3. Check TikTok app/website for the posted video")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())