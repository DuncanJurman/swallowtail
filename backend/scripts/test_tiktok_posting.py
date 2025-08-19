#!/usr/bin/env python3
"""
Manual testing script for TikTok content posting MVP.

This script demonstrates the full flow of:
1. Uploading a test video to instance storage
2. Creating a mock task with the video URL
3. Posting the video to TikTok
4. Checking the posting status

Usage:
    python scripts/test_tiktok_posting.py
"""

import asyncio
import sys
from pathlib import Path
from uuid import UUID, uuid4
import httpx
# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import get_settings
from src.services.tiktok.content_api import TikTokContentAPI
from src.services.tiktok.config import tiktok_config


# Test configuration
TEST_INSTANCE_ID = UUID("00000000-0000-0000-0000-000000000001")  # Test instance
TEST_VIDEO_URL = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
TEST_SUPABASE_VIDEO_URL = None  # Will be set after upload


async def test_storage_upload():
    """Test uploading a video to instance storage."""
    print("\n📦 Testing Storage Upload...")
    print("-" * 50)
    
    storage = SupabaseStorageService()
    
    # For MVP, we'll simulate upload by using a test URL
    # In production, would actually upload video data
    test_path = f"instances/{TEST_INSTANCE_ID}/tests/test_video_{uuid4()}.mp4"
    
    print(f"✅ Simulated upload to path: {test_path}")
    
    # Generate a mock Supabase URL
    settings = get_settings()
    mock_url = f"{settings.supabase_url}/storage/v1/object/public/instance-media/{test_path}"
    
    print(f"📍 Mock storage URL: {mock_url}")
    
    return mock_url


async def test_tiktok_api_connection():
    """Test basic TikTok API connection."""
    print("\n🔌 Testing TikTok API Connection...")
    print("-" * 50)
    
    print(f"Mode: {'SANDBOX' if tiktok_config.sandbox_mode else 'PRODUCTION'}")
    print(f"API Base: {tiktok_config.api_base_url}")
    print(f"Client Key Configured: {bool(tiktok_config.client_key)}")
    
    if not tiktok_config.client_key:
        print("⚠️  Warning: TikTok client key not configured")
        print("   Set TIKTOK_CLIENT_KEY in your .env file")
        return False
    
    print("✅ TikTok API configured")
    return True


async def test_post_video_to_tiktok(video_url: str):
    """Test posting a video to TikTok."""
    print("\n📤 Testing TikTok Video Post...")
    print("-" * 50)
    
    # For testing, you'll need valid credentials
    # These should be obtained through OAuth flow
    test_access_token = "YOUR_TEST_ACCESS_TOKEN"  # TODO: Set from OAuth
    test_open_id = "YOUR_TEST_OPEN_ID"           # TODO: Set from OAuth
    
    if test_access_token == "YOUR_TEST_ACCESS_TOKEN":
        print("⚠️  Warning: Using placeholder credentials")
        print("   For real testing, complete OAuth flow first")
        print("   Visit: /api/v1/tiktok/auth to start OAuth")
        
        # Simulate success for MVP demo
        mock_publish_id = f"test_{uuid4()}"
        print(f"\n🎬 Simulated post with publish_id: {mock_publish_id}")
        return mock_publish_id
    
    try:
        # Initialize content API
        async with TikTokContentAPI(
            access_token=test_access_token,
            open_id=test_open_id
        ) as content_api:
            
            # Query creator info
            print("📊 Querying creator info...")
            creator_info = await content_api.query_creator_info()
            print(f"   Username: {creator_info.get('creator_username', 'Unknown')}")
            print(f"   Privacy options: {creator_info.get('privacy_level_options', [])}")
            
            # Post video
            print("\n🚀 Posting video...")
            result = await content_api.post_video_from_url(
                video_url=video_url,
                title="Test video from Swallowtail MVP! 🚀 #swallowtail #test",
                privacy_level="SELF_ONLY"  # Private for testing
            )
            
            if result.get("success"):
                publish_id = result.get("publish_id")
                print(f"✅ Posted successfully!")
                print(f"   Publish ID: {publish_id}")
                print(f"   Status: {result.get('status')}")
                return publish_id
            else:
                print(f"❌ Failed to post: {result.get('message')}")
                return None
                
    except Exception as e:
        print(f"❌ Error posting video: {e}")
        return None


async def test_check_post_status(publish_id: str):
    """Test checking the status of a TikTok post."""
    print("\n🔍 Checking Post Status...")
    print("-" * 50)
    
    if publish_id.startswith("test_"):
        # Simulated status for MVP
        print(f"📊 Status for {publish_id}:")
        print(f"   Status: PUBLISHED (simulated)")
        print(f"   URL: https://www.tiktok.com/@test/video/{publish_id}")
        return
    
    # Real status check would go here
    test_access_token = "YOUR_TEST_ACCESS_TOKEN"  # TODO: Set from OAuth
    test_open_id = "YOUR_TEST_OPEN_ID"           # TODO: Set from OAuth
    
    try:
        async with TikTokContentAPI(
            access_token=test_access_token,
            open_id=test_open_id
        ) as content_api:
            
            status = await content_api.check_post_status(publish_id)
            print(f"📊 Status for {publish_id}:")
            print(f"   Status: {status.get('status')}")
            
            if status.get('status') == 'PUBLISH_COMPLETE':
                print(f"   Post ID: {status.get('post_id')}")
                print(f"   URL: https://www.tiktok.com/@user/video/{status.get('post_id')}")
            elif status.get('fail_reason'):
                print(f"   Error: {status.get('fail_reason')}")
                
    except Exception as e:
        print(f"❌ Error checking status: {e}")


async def test_api_endpoints():
    """Test the MVP API endpoints."""
    print("\n🌐 Testing API Endpoints...")
    print("-" * 50)
    
    settings = get_settings()
    base_url = f"http://localhost:{settings.port}"
    
    async with httpx.AsyncClient() as client:
        # Test connection endpoint
        print("Testing /api/v1/tiktok-mvp/test-connection...")
        try:
            response = await client.get(f"{base_url}/api/v1/tiktok-mvp/test-connection")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Connection test passed")
                print(f"   Sandbox mode: {data.get('sandbox_mode')}")
                print(f"   Configured: {data.get('configured')}")
            else:
                print(f"❌ Connection test failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Could not connect to API: {e}")
            print("   Make sure the backend is running: poetry run python run.py")
            return
        
        # Test posting endpoint
        print("\nTesting /api/v1/tiktok-mvp/test-post...")
        test_data = {
            "title": "Test post from MVP script",
            "video_url": TEST_VIDEO_URL,
            "privacy_level": "SELF_ONLY"
        }
        
        try:
            # Note: This will fail without proper auth
            # For MVP, you might want to disable auth temporarily
            response = await client.post(
                f"{base_url}/api/v1/tiktok-mvp/test-post",
                json=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Post endpoint responded")
                print(f"   Success: {data.get('success')}")
                print(f"   Message: {data.get('message')}")
            else:
                print(f"⚠️  Post endpoint returned: {response.status_code}")
                print("   This is expected if auth is enabled")
                
        except Exception as e:
            print(f"❌ Error calling post endpoint: {e}")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("🎯 TikTok Content Posting MVP Test Suite")
    print("=" * 60)
    
    # Test 1: Storage Upload
    storage_url = await test_storage_upload()
    
    # Test 2: TikTok API Connection
    api_configured = await test_tiktok_api_connection()
    
    # Test 3: Post Video (if configured)
    if api_configured:
        publish_id = await test_post_video_to_tiktok(storage_url or TEST_VIDEO_URL)
        
        # Test 4: Check Status
        if publish_id:
            await asyncio.sleep(2)  # Wait a bit before checking
            await test_check_post_status(publish_id)
    
    # Test 5: API Endpoints
    await test_api_endpoints()
    
    print("\n" + "=" * 60)
    print("✅ Test suite complete!")
    print("\nNext steps for full testing:")
    print("1. Set up TikTok OAuth credentials in .env")
    print("2. Complete OAuth flow at /api/v1/tiktok/auth")
    print("3. Use real access token in this script")
    print("4. Upload a real video to Supabase storage")
    print("5. Post the video and monitor status")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())