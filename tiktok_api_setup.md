# TikTok API Integration Setup for Swallowtail

## Overview
To enable Swallowtail users to manage their TikTok accounts, post content, and manage ads, we need to integrate multiple TikTok APIs. Each API has different requirements and approval processes.

## TikTok API Types

### 1. Content Posting API
- **Purpose**: Automate video/photo uploads, schedule posts, manage multiple accounts
- **Features**: Direct posting, draft uploads, multi-account management
- **Requirements**: App audit for public content visibility

### 2. Marketing API (Business API)
- **Purpose**: Manage TikTok Ads at scale, campaign automation
- **Features**: Batch ad creation, creative management, automated reporting
- **Requirements**: TikTok Business account

### 3. Accounts API
- **Purpose**: Manage Business Account activity programmatically
- **Features**: Account insights, content moderation, organic publishing
- **Requirements**: Business account verification

### 4. Creator Marketplace API
- **Purpose**: Access creator data, manage influencer collaborations
- **Features**: Creator discovery, campaign management
- **Requirements**: Specific business use case

## Implementation Plan

### Phase 1: Frontend Preparation (Prerequisites)

#### 1.1 Create Legal Pages
- **Privacy Policy** (`/privacy`)
  - Must include data collection practices
  - TikTok-specific data handling disclosures
  - User rights and data deletion procedures
  
- **Terms of Service** (`/terms`)
  - Service description
  - User responsibilities
  - Liability limitations
  
**Important**: Both pages must be visible in main navigation, not hidden in menus

#### 1.2 Update Homepage
- Must be a fully developed, externally facing website
- Cannot be just a landing page or login page
- Must clearly describe Swallowtail's functionality
- Include information about multi-account management capabilities

#### 1.3 Prepare App Assets
- **App Icon**: Clear image, no sensitive content, consistent with brand
- **App Name**: Cannot reference "TikTok", must match service name
- **App Description**: Clear explanation of multi-account management features

### Phase 2: TikTok Developer Account Setup

#### 2.1 Register as Developer
1. Go to https://developers.tiktok.com
2. Sign up with email
3. Verify via OTP
4. Complete developer profile

#### 2.2 Create Separate Apps
We need two apps for different API access:

**App 1: Content Management**
- Name: "Swallowtail Content Manager"
- Purpose: Content Posting API access
- Category: Business/Productivity

**App 2: Business Operations**
- Name: "Swallowtail Business Suite"
- Purpose: Marketing API, Accounts API
- Category: Business Tools

### Phase 3: Content Posting API Setup

#### 3.1 App Configuration
```
App Name: Swallowtail Content Manager
Category: Business/Productivity
Platform: Web
Website URL: https://skipper-ecom.com
Privacy Policy: https://skipper-ecom.com/privacy
Terms of Service: https://skipper-ecom.com/terms
Redirect URI: https://skipper-ecom.com/auth/tiktok/callback
```

#### 3.2 Required Scopes
- `video.publish` - Post videos
- `user.info.basic` - Access basic user info
- `video.list` - List user's videos
- `video.upload` - Upload video content

#### 3.3 Domain Verification
- Verify ownership of skipper-ecom.com
- Add TXT record or HTML file verification

### Phase 4: Business API Setup

#### 4.1 Marketing API Requirements
- Create TikTok Business account
- Link to TikTok Ads Manager
- Complete business verification
- Request Marketing API access

#### 4.2 API Features Available
- **Batch Delivery**: Create thousands of campaigns instantly
- **Creative Management**: Centralized creative library
- **Automated Bidding**: AI-powered bid optimization
- **Custom Audiences**: Upload and manage audiences
- **Reporting**: Comprehensive analytics

### Phase 5: OAuth 2.0 Implementation

#### 5.1 OAuth Endpoints
```
Authorization: https://www.tiktok.com/v2/auth/authorize/
Token: https://open.tiktokapis.com/v2/oauth/token/
Refresh: https://open.tiktokapis.com/v2/oauth/token/
Revoke: https://open.tiktokapis.com/v2/oauth/revoke/
```

#### 5.2 OAuth Flow
1. Generate authorization URL with scopes
2. User authorizes on TikTok
3. Receive authorization code
4. Exchange code for access token
5. Store tokens securely server-side

#### 5.3 Token Management
```json
{
  "access_token": "act.xxx",
  "expires_in": 86400,
  "open_id": "user_open_id",
  "refresh_expires_in": 31536000,
  "refresh_token": "rft.xxx",
  "scope": "user.info.basic,video.publish",
  "token_type": "Bearer"
}
```

### Phase 6: Backend Integration Architecture

#### 6.1 Database Schema Updates
```sql
-- TikTok credentials table
CREATE TABLE instance_tiktok_credentials (
    id UUID PRIMARY KEY,
    instance_id UUID REFERENCES instances(id),
    tiktok_open_id VARCHAR(255) UNIQUE,
    access_token TEXT ENCRYPTED,
    refresh_token TEXT ENCRYPTED,
    token_expires_at TIMESTAMP,
    refresh_expires_at TIMESTAMP,
    scopes TEXT[],
    account_type VARCHAR(50), -- 'personal' or 'business'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### 6.2 API Service Structure
```
backend/
  services/
    tiktok/
      __init__.py
      oauth.py          # OAuth flow handling
      content_api.py    # Content posting functions
      business_api.py   # Marketing API functions
      models.py         # TikTok-specific models
      utils.py          # Helper functions
```

### Phase 7: App Submission Process

#### 7.1 Pre-Submission Checklist
- [ ] Website fully functional with all pages
- [ ] Privacy Policy and Terms visible
- [ ] App icon uploaded
- [ ] Clear app description
- [ ] Demo account prepared
- [ ] All redirect URIs verified
- [ ] Prototype functionality working

#### 7.2 Review Timeline
- Initial submission: 3-4 days
- If feedback provided: Additional 5-7 days
- Total time: Up to 2 weeks per app

#### 7.3 Common Rejection Reasons
- Generic app names (e.g., "App123")
- Missing or hidden legal pages
- Non-functional website
- Incomplete app information
- Policy violations

### Phase 8: Post-Approval Requirements

#### 8.1 Ongoing Compliance
- Respond to TikTok communications within 48 hours
- Update integration for API changes
- Maintain security standards
- Regular audits for policy compliance

#### 8.2 Content Posting Audit
- Required for public content visibility
- Verify Terms of Service compliance
- May take additional 1-2 weeks
- Without audit: Content defaults to private

## Technical Implementation Details

### API Rate Limits
- Content Posting: 100 posts/day per user
- Marketing API: Varies by endpoint
- Implement exponential backoff
- Queue management for bulk operations

### Error Handling
```python
# Common TikTok API errors
ERRORS = {
    "invalid_token": "Token expired or invalid",
    "rate_limit": "API rate limit exceeded",
    "permission_denied": "Missing required scope",
    "account_restricted": "Account under review"
}
```

### Security Considerations
- Store all tokens encrypted
- Implement token refresh before expiry
- Log all API activities
- Monitor for suspicious patterns
- Implement user consent flows

## Multi-Account Management Strategy

### Account Linking Flow
1. User initiates TikTok connection
2. OAuth flow with instance context
3. Store credentials linked to instance
4. Enable account-specific features based on type

### Account Types
- **Personal Account**: Content posting only
- **Business Account**: Full API access, no monetization
- **Creator Account**: Content + monetization features

## Roadmap Timeline

### Week 1: Frontend Preparation
- Day 1-2: Create privacy policy and terms pages
- Day 3-4: Update homepage and navigation
- Day 5: Prepare app assets and descriptions

### Week 2: Developer Setup
- Day 1-2: Create developer account
- Day 3-4: Set up both apps
- Day 5: Configure all settings

### Week 3: Backend Implementation
- Day 1-2: OAuth flow implementation
- Day 3-4: API service creation
- Day 5: Database updates

### Week 4: Testing & Submission
- Day 1-2: Integration testing
- Day 3: Submit Content API app
- Day 4: Submit Business API app
- Day 5: Prepare for review feedback

### Week 5-6: Approval & Iteration
- Monitor review status
- Address feedback
- Implement audit requirements
- Launch to users

## Important Notes

1. **TikTok-Specific Quirks**
   - Uses `client_key` instead of `client_id` in OAuth
   - Business accounts cannot monetize content
   - Private content default without audit

2. **Maintenance Requirements**
   - API versions update frequently
   - Must migrate when endpoints deprecated
   - Keep communication channels open

3. **Cost Considerations**
   - APIs are free to use
   - Rate limits apply
   - Consider caching strategies

## Resources

- [TikTok for Developers](https://developers.tiktok.com)
- [Business API Portal](https://business-api.tiktok.com/portal/docs)
- [OAuth Documentation](https://developers.tiktok.com/doc/oauth-user-access-token-management)
- [Content Posting Guide](https://developers.tiktok.com/doc/content-posting-api-get-started)