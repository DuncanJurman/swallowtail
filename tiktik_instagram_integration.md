TikTok & Instagram Integration Implementation  │ │
│ │ Plan                                           │ │
│ │                                                │ │
│ │ Overview                                       │ │
│ │                                                │ │
│ │ Implement OAuth authentication and API         │ │
│ │ integration to allow Swallowtail users to      │ │
│ │ connect their TikTok and Instagram business    │ │
│ │ accounts for programmatic content posting,     │ │
│ │ management, and advertising.                   │ │
│ │                                                │ │
│ │ Architecture Approach                          │ │
│ │                                                │ │
│ │ 1. Database Schema Updates                     │ │
│ │                                                │ │
│ │ - Add instance_credentials table to securely   │ │
│ │ store platform credentials                     │ │
│ │ - Add platform_connections table to track      │ │
│ │ OAuth tokens and connection status             │ │
│ │ - Use encryption for sensitive data (tokens,   │ │
│ │ secrets)                                       │ │
│ │ - Add fields to Instance model for platform    │ │
│ │ connection status                              │ │
│ │                                                │ │
│ │ 2. Backend Implementation                      │ │
│ │                                                │ │
│ │ OAuth Service (src/services/oauth_service.py)  │ │
│ │                                                │ │
│ │ - Base OAuth2 flow handler                     │ │
│ │ - Platform-specific implementations:           │ │
│ │   - TikTokOAuthService                         │ │
│ │   - InstagramOAuthService (via Facebook Login) │ │
│ │ - Token management (refresh, expiry tracking)  │ │
│ │ - Secure credential storage with encryption    │ │
│ │                                                │ │
│ │ Platform Services                              │ │
│ │                                                │ │
│ │ - src/services/tiktok_service.py:              │ │
│ │   - Content posting API                        │ │
│ │   - Account insights                           │ │
│ │   - Ad management                              │ │
│ │   - Creator marketplace integration            │ │
│ │ - src/services/instagram_service.py:           │ │
│ │   - Graph API integration                      │ │
│ │   - Content publishing                         │ │
│ │   - Analytics access                           │ │
│ │   - Story posting                              │ │
│ │                                                │ │
│ │ API Endpoints                                  │ │
│ │                                                │ │
│ │ - POST                                         │ │
│ │ /api/v1/instances/{id}/connections/tiktok/auth │ │
│ │  - Initiate TikTok OAuth                       │ │
│ │ - GET /api/v1/instances/{id}/connections/tikto │ │
│ │ k/callback - Handle OAuth callback             │ │
│ │ - POST /api/v1/instances/{id}/connections/inst │ │
│ │ agram/auth - Initiate Instagram OAuth          │ │
│ │ - GET /api/v1/instances/{id}/connections/insta │ │
│ │ gram/callback - Handle callback                │ │
│ │ - DELETE                                       │ │
│ │ /api/v1/instances/{id}/connections/{platform}  │ │
│ │ - Disconnect platform                          │ │
│ │ - GET /api/v1/instances/{id}/connections -     │ │
│ │ List all connections                           │ │
│ │                                                │ │
│ │ 3. Frontend Implementation                     │ │
│ │                                                │ │
│ │ Connection Management UI                       │ │
│ │                                                │ │
│ │ - New page: /instances/[id]/connections        │ │
│ │ - Platform connection cards showing:           │ │
│ │   - Connection status                          │ │
│ │   - Account info (username, profile pic)       │ │
│ │   - Last sync time                             │ │
│ │   - Connect/disconnect buttons                 │ │
│ │                                                │ │
│ │ OAuth Flow Components                          │ │
│ │                                                │ │
│ │ - Modal for initiating connection              │ │
│ │ - Redirect handling                            │ │
│ │ - Error states for failed connections          │ │
│ │ - Success confirmation                         │ │
│ │                                                │ │
│ │ 4. Security Considerations                     │ │
│ │                                                │ │
│ │ - Encrypt all stored tokens using Fernet       │ │
│ │ encryption                                     │ │
│ │ - Use environment variables for OAuth client   │ │
│ │ credentials                                    │ │
│ │ - Implement CSRF protection for OAuth flows    │ │
│ │ - Add rate limiting for API calls              │ │
│ │ - Audit logging for all platform operations    │ │
│ │                                                │ │
│ │ Implementation Steps                           │ │
│ │                                                │ │
│ │ Phase 1: Foundation (Week 1)                   │ │
│ │                                                │ │
│ │ 1. Create database migrations for credentials  │ │
│ │ storage                                        │ │
│ │ 2. Implement base OAuth service class          │ │
│ │ 3. Add encryption utilities                    │ │
│ │ 4. Create API endpoints structure              │ │
│ │ 5. Set up environment configuration            │ │
│ │                                                │ │
│ │ Phase 2: TikTok Integration (Week 2)           │ │
│ │                                                │ │
│ │ 1. Register app on TikTok Developer Portal     │ │
│ │ 2. Implement TikTok OAuth flow                 │ │
│ │ 3. Add TikTok API wrapper methods              │ │
│ │ 4. Create content posting functionality        │ │
│ │ 5. Add account insights retrieval              │ │
│ │                                                │ │
│ │ Phase 3: Instagram Integration (Week 3)        │ │
│ │                                                │ │
│ │ 1. Set up Facebook App for Instagram access    │ │
│ │ 2. Implement Facebook Login flow               │ │
│ │ 3. Add Instagram Graph API methods             │ │
│ │ 4. Create content publishing features          │ │
│ │ 5. Add analytics access                        │ │
│ │                                                │ │
│ │ Phase 4: Frontend & Testing (Week 4)           │ │
│ │                                                │ │
│ │ 1. Build connection management UI              │ │
│ │ 2. Implement OAuth flow in frontend            │ │
│ │ 3. Add error handling and retry logic          │ │
│ │ 4. Create integration tests                    │ │
│ │ 5. Security audit and documentation            │ │
│ │                                                │ │
│ │ API Capabilities by Platform                   │ │
│ │                                                │ │
│ │ TikTok                                         │ │
│ │                                                │ │
│ │ - Marketing API: Programmatic ad creation and  │ │
│ │ management                                     │ │
│ │ - Accounts API: Organic content posting,       │ │
│ │ moderation                                     │ │
│ │ - Creator Marketplace API: Influencer          │ │
│ │ collaborations                                 │ │
│ │ - Content Posting API: Direct publishing to    │ │
│ │ profile                                        │ │
│ │                                                │ │
│ │ Instagram (via Graph API)                      │ │
│ │                                                │ │
│ │ - Content Publishing: Feed posts, Stories,     │ │
│ │ Reels                                          │ │
│ │ - Insights: Analytics and performance metrics  │ │
│ │ - Comment Management: Moderation and responses │ │
│ │ - User Content: Access media and profile data  │ │
│ │ - Messaging: Business messaging (with          │ │
│ │ approval)                                      │ │
│ │                                                │ │
│ │ Required Credentials                           │ │
│ │                                                │ │
│ │ 1. TikTok:                                     │ │
│ │   - Client Key & Secret from TikTok Developer  │ │
│ │ Portal                                         │ │
│ │   - Approved app with required scopes          │ │
│ │ 2. Instagram:                                  │ │
│ │   - Facebook App ID & Secret                   │ │
│ │   - Instagram Business/Creator Account         │ │
│ │   - Facebook Page linked to Instagram          │ │
│ │                                                │ │
│ │ Next Steps After Implementation                │ │
│ │                                                │ │
│ │ 1. Add webhook support for real-time updates   │ │
│ │ 2. Implement batch operations for efficiency   │ │
│ │ 3. Add advanced scheduling features            │ │
│ │ 4. Create templates for common operations      │ │
│ │ 5. Build analytics dashboard         



 To set up TikTok API access, here's what you
  need to do:

  TikTok Developer Account Setup

  1. Create a TikTok Developer Account

  - Go to https://developers.tiktok.com
  - Click "Login" and sign in with your TikTok
  account
  - Complete the developer registration process

  2. Create Your App

  - Navigate to "Manage apps" in the developer
  portal
  - Click "Create app"
  - Fill in the required information:
    - App name: Swallowtail (or your preferred
  name)
    - Description: Describe your use case for the
   API
    - Platform: Select "Web"
    - Category: Select appropriate category
  (e.g., "Business")

  3. Configure OAuth Settings

  - In your app settings, add redirect URIs:
    - For development: http://localhost:8000/api/
  v1/oauth/tiktok/callback
    - For production: https://yourdomain.com/api/
  v1/oauth/tiktok/callback
  - Note: TikTok requires HTTPS for production
  redirect URIs

  4. Request API Access

  You'll need access to different APIs based on
  your needs:

  - Login Kit: For basic OAuth authentication
  - Content Posting API: To publish content
  - Business Account Management API: For account
  insights and management
  - Marketing API: For ads management

  5. Obtain Credentials

  Once your app is created, you'll get:
  - Client Key (like a client_id)
  - Client Secret

  6. Important Considerations

  App Approval Process:
  - Your app needs to be approved before you can
  use it in production
  - During development, you can test with your
  own account
  - For production use with other accounts,
  you'll need to submit for review

  Available Scopes:
  - user.info.basic - Basic user information
  - user.info.profile - Extended profile
  information
  - user.info.stats - User statistics
  - video.list - Access to user's videos
  - video.publish - Publish videos (requires
  approval)

  7. Testing Setup

  For initial testing, you can:
  1. Use your own TikTok account
  2. Add test users in the app settings
  3. Use sandbox mode if available

  Next Steps

  Once you have your credentials:
  1. Store them securely in your .env file
  2. We'll implement the OAuth flow
  3. Test basic authentication
  4. Add API endpoints for specific features

  Would you like me to guide you through creating
   the app on TikTok's developer portal, or do
  you want to do that first and then we can
  proceed with the implementation?