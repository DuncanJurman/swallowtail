#!/usr/bin/env python3
"""
Get TikTok OAuth credentials from the database or complete OAuth flow.

This script helps you:
1. Check for existing credentials in the database
2. Start the OAuth flow if needed
3. Extract the access token and open_id for testing
"""

import sys
from pathlib import Path
import webbrowser
from datetime import datetime, timezone
import psycopg2
from cryptography.fernet import Fernet
import base64

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import get_settings
from src.services.tiktok.config import tiktok_config


def get_existing_credentials():
    """Check database for existing TikTok credentials using raw SQL."""
    print("\n🔍 Checking for existing TikTok credentials...")
    print("-" * 50)
    
    settings = get_settings()
    
    # Parse database URL for psycopg2
    db_url = settings.database_url.replace('+asyncpg', '').replace('postgresql+asyncpg', 'postgresql')
    
    try:
        # Connect using psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Query for TikTok credentials
        cur.execute("""
            SELECT 
                id, instance_id, account_name, tiktok_open_id,
                access_token_encrypted, refresh_token_encrypted,
                expires_at, refresh_expires_at, scopes, created_at
            FROM instance_tiktok_credentials
            ORDER BY created_at DESC
        """)
        
        rows = cur.fetchall()
        
        if not rows:
            print("❌ No TikTok credentials found in database")
            return None
        
        print(f"✅ Found {len(rows)} TikTok credential(s):")
        
        # Get encryption key
        encryption_key = settings.encryption_key
        if not encryption_key:
            print("⚠️  No encryption key found in settings")
            return None
        
        # Create Fernet instance for decryption
        fernet = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
        
        valid_creds = []
        for row in rows:
            (id, instance_id, account_name, tiktok_open_id,
             access_token_encrypted, refresh_token_encrypted,
             expires_at, refresh_expires_at, scopes, created_at) = row
            
            # Check if expired
            is_expired = expires_at < datetime.now(timezone.utc) if expires_at else True
            status = "❌ EXPIRED" if is_expired else "✅ VALID"
            
            print(f"\n  Account: {account_name or 'Unknown'}")
            print(f"  Instance ID: {instance_id}")
            print(f"  Open ID: {tiktok_open_id}")
            print(f"  Status: {status}")
            
            if not is_expired:
                # Decrypt token
                try:
                    if access_token_encrypted:
                        # Decrypt the token
                        decrypted_token = fernet.decrypt(access_token_encrypted.encode()).decode()
                        masked_token = f"{decrypted_token[:10]}...{decrypted_token[-10:]}" if len(decrypted_token) > 25 else "TOO_SHORT"
                        print(f"  Access Token: {masked_token}")
                        print(f"  Expires at: {expires_at}")
                        
                        valid_creds.append({
                            "account_name": account_name,
                            "instance_id": str(instance_id),
                            "open_id": tiktok_open_id,
                            "access_token": decrypted_token,
                            "expires_at": expires_at
                        })
                except Exception as e:
                    print(f"  ⚠️  Could not decrypt token: {e}")
        
        cur.close()
        conn.close()
        
        return valid_creds
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None


def start_oauth_flow():
    """Guide user through OAuth flow."""
    print("\n🔐 Starting TikTok OAuth Flow...")
    print("-" * 50)
    
    settings = get_settings()
    
    # Check if TikTok is configured
    if not tiktok_config.client_key:
        print("❌ TikTok is not configured!")
        print("\nAdd to your .env file:")
        print("  TIKTOK_CLIENT_KEY=your_client_key")
        print("  TIKTOK_CLIENT_SECRET=your_client_secret")
        print("  TIKTOK_REDIRECT_URI=https://skipper-ecom.com/tiktok/callback")
        return None
    
    # Build OAuth URL
    oauth_url = f"http://localhost:{settings.port}/api/v1/tiktok/auth"
    
    print("📝 Instructions:")
    print("1. Make sure the backend is running:")
    print("   poetry run python run.py")
    print()
    print("2. Visit this URL in your browser:")
    print(f"   {oauth_url}")
    print()
    print("3. Complete the TikTok login and authorization")
    print()
    print("4. After callback, check the response for credentials")
    print()
    
    # Try to open browser
    try:
        print("🌐 Opening browser...")
        webbrowser.open(oauth_url)
    except:
        print("⚠️  Could not open browser automatically")
    
    print("\n⏸️  After completing OAuth, run this script again to see credentials")


def save_test_credentials(creds):
    """Save credentials to a test file for easy use."""
    print("\n💾 Saving test credentials...")
    print("-" * 50)
    
    if not creds:
        print("❌ No valid credentials to save")
        return
    
    # Use the first valid credential
    cred = creds[0]
    
    test_file = Path(__file__).parent / "test_tiktok_credentials.py"
    
    content = f'''"""
Test TikTok credentials for development.
Generated: {datetime.now(timezone.utc).isoformat()}

SECURITY WARNING: Do not commit this file to version control!
Add to .gitignore: scripts/test_tiktok_credentials.py
"""

# TikTok OAuth Credentials (valid until {cred['expires_at']})
TIKTOK_ACCESS_TOKEN = "{cred['access_token']}"
TIKTOK_OPEN_ID = "{cred['open_id']}"
TIKTOK_ACCOUNT_NAME = "{cred.get('account_name', 'Unknown')}"

# Usage in test scripts:
# from test_tiktok_credentials import TIKTOK_ACCESS_TOKEN, TIKTOK_OPEN_ID
'''
    
    try:
        with open(test_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Saved to: {test_file}")
        print("\n⚠️  IMPORTANT SECURITY NOTES:")
        print("  • DO NOT commit this file to git")
        print("  • Add to .gitignore: scripts/test_tiktok_credentials.py")
        print("  • Token expires at:", cred['expires_at'])
        
        # Also update the test script
        update_test_script(cred)
        
    except Exception as e:
        print(f"❌ Could not save credentials: {e}")


def update_test_script(cred):
    """Update the test script with real credentials."""
    test_script = Path(__file__).parent / "test_storage_and_tiktok.py"
    
    if test_script.exists():
        print("\n📝 Update test_storage_and_tiktok.py:")
        print(f'  test_access_token = "{cred["access_token"][:10]}..."')
        print(f'  test_open_id = "{cred["open_id"]}"')


def main():
    """Main function."""
    print("=" * 60)
    print("🎯 TikTok OAuth Credentials Manager")
    print("=" * 60)
    
    # Check for existing credentials
    valid_creds = get_existing_credentials()
    
    if valid_creds:
        print("\n✅ Found valid credentials!")
        
        # Ask if user wants to save them
        print("\nWould you like to save these for testing?")
        print("(This will create test_tiktok_credentials.py)")
        response = input("Save credentials? (y/n): ").lower()
        
        if response == 'y':
            save_test_credentials(valid_creds)
        
        # Show how to use them
        print("\n📋 To use in test scripts:")
        print("-" * 40)
        cred = valid_creds[0]
        print(f'test_access_token = "{cred["access_token"]}"')
        print(f'test_open_id = "{cred["open_id"]}"')
        
    else:
        # No valid credentials, start OAuth flow
        print("\n❌ No valid credentials found")
        print("\nWould you like to start the OAuth flow?")
        response = input("Start OAuth? (y/n): ").lower()
        
        if response == 'y':
            start_oauth_flow()
        else:
            print("\n📝 Manual steps to get credentials:")
            print("1. Start backend: poetry run python run.py")
            print("2. Visit: http://localhost:8000/api/v1/tiktok/auth")
            print("3. Complete OAuth flow")
            print("4. Run this script again to extract credentials")
    
    print("\n" + "=" * 60)
    print("✅ Done!")
    print("=" * 60)


if __name__ == "__main__":
    main()