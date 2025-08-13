# TikTok Content Posting API - Sandbox Implementation Plan

## Overview
This document outlines the implementation plan for integrating TikTok's Content Posting API (sandbox mode) into the Swallowtail platform, enabling users to post task-generated videos directly to TikTok from the task detail page.

## Architecture Context

### Frontend Structure (Next.js 15)
- **App Router**: `/app/(auth)/instances/[id]/tasks/[taskId]/`
- **Component Library**: Radix UI with Tailwind CSS v3
- **State Management**: TanStack Query for server state, Zustand for client state
- **Existing TikTok Integration**: OAuth flow already implemented in `/app/tiktok/callback/`

### Backend Structure (FastAPI + CrewAI)
- **Database**: PostgreSQL via Supabase with Alembic migrations
- **Task System**: Instance-based task management with CrewAI agents
- **TikTok Service**: OAuth and content API services already scaffolded
- **Database Fields**: TikTok posting fields added via migration `11acbb169f19`:
  - `tiktok_post_data` (JSONB)
  - `tiktok_publish_id` (VARCHAR 255)
  - `tiktok_post_status` (VARCHAR 50)
  - `tiktok_post_url` (VARCHAR 500)
  - `scheduled_post_time` (TIMESTAMP)

## Phase 1: Frontend - Task Detail Page Structure

### 1.1 Task Detail Page Layout
**Files**: 
- `/app/(auth)/instances/[id]/tasks/[taskId]/page.tsx` (Server Component)
- `/app/(auth)/instances/[id]/tasks/[taskId]/page-client.tsx` (Client Component)

The task detail page will have three main sections:

#### Section 1: Task Planning (Frontend Placeholder)
- **Purpose**: Display the execution plan the Manager Agent would create
- **Components**:
  - Todo-style checklist with planned steps
  - Status indicators (pending/in-progress/completed) for each step
  - Display attached reference images from `attached_media_ids`
  - Expandable card design using existing UI components
- **Implementation**: 
  - Mock data structure for planning steps
  - No backend integration needed for MVP
  - Prepare for future WebSocket updates

#### Section 2: Agent Execution Logs (Frontend Placeholder)
- **Purpose**: Show agent activity and decision-making process
- **Components**:
  - Collapsible log entries with timestamps
  - Agent identification badges
  - Color-coded log levels (info/warning/error)
  - Expandable details using Radix UI Collapsible
- **Implementation**:
  - Static placeholder content
  - Structure ready for `execution_steps` data
  - Prepare for real-time updates via WebSocket

#### Section 3: Final Output & TikTok Posting
- **Purpose**: Display task results and enable TikTok posting
- **Components**:
  - Video player (HTML5) for generated content
  - Metadata display from `output_data`
  - "Post to TikTok" checkbox (conditional on video output)
  - TikTok posting dialog component
  - Status indicators for posting progress
- **Implementation**:
  - Integrates with actual task data
  - Conditional rendering based on `output_format` === 'video'
  - Real API integration for posting

### 1.2 TikTok Posting Dialog Component
**File**: `/components/tasks/tiktok-post-dialog.tsx`

**Features**:
- Video preview with controls
- Editable caption (pre-filled from `output_data.suggested_caption`)
- Privacy level selector:
  - PUBLIC_TO_EVERYONE
  - MUTUAL_FOLLOW_FRIENDS  
  - SELF_ONLY (default for sandbox)
- Interaction toggles:
  - Disable duet
  - Disable stitch
  - Disable comments
- Account selector (for multi-account instances)
- Schedule picker (UI only - posts immediately)
- Submit button with loading state

## Phase 2: Backend - API Enhancement

### 2.1 Task Detail Endpoint
**File**: `/src/api/routes/tasks.py`

**New Endpoint**: `GET /api/v1/tasks/{task_id}/detail`

**Response Structure**:
```python
{
  "task": {
    "id": "uuid",
    "description": "string",
    "status": "completed",
    "output_data": {
      "video_url": "https://...",
      "thumbnail_url": "https://...",
      "suggested_caption": "string",
      "media_type": "video"
    },
    "tiktok_post_status": "string|null",
    "tiktok_publish_id": "string|null"
  },
  "planning": {  # Mock data
    "steps": [
      {
        "id": 1,
        "description": "Analyze task requirements",
        "status": "completed"
      }
    ]
  },
  "execution_logs": [  # From execution_steps
    {
      "timestamp": "ISO8601",
      "agent": "Manager",
      "action": "string",
      "details": {}
    }
  ],
  "attached_media": [  # Reference images
    {
      "id": "uuid",
      "url": "https://...",
      "type": "reference"
    }
  ]
}
```

### 2.2 TikTok Posting Endpoint
**File**: `/src/api/routes/tasks.py`

**New Endpoint**: `POST /api/v1/tasks/{task_id}/post-to-tiktok`

**Request Body**:
```python
{
  "title": "string",  # Caption with hashtags
  "privacy_level": "SELF_ONLY",  # Sandbox default
  "disable_duet": false,
  "disable_stitch": false,
  "disable_comment": false,
  "account_id": "uuid|null",  # For multi-account
  "scheduled_time": "ISO8601|null"  # Dummy for MVP
}
```

**Processing Flow**:
1. Validate task has video output
2. Get TikTok credentials for instance
3. Refresh token if expired
4. Query creator info via TikTok API
5. Post video using PULL_FROM_URL method
6. Store publish_id in database
7. Update task status fields
8. Return response with publish_id

### 2.3 Post Status Endpoint
**File**: `/src/api/routes/tasks.py`

**New Endpoint**: `GET /api/v1/tasks/{task_id}/post-status`

**Response**:
```python
{
  "publish_id": "string",
  "status": "PROCESSING|PUBLISH_COMPLETE|FAILED",
  "fail_reason": "string|null",
  "tiktok_url": "string|null",
  "last_checked": "ISO8601"
}
```

### 2.4 Enhanced TikTok Content Service
**File**: `/src/services/tiktok/content_api.py`

**New Methods**:

```python
async def post_video_from_task(
    self,
    access_token: str,
    video_url: str,
    title: str,
    privacy_level: str = "SELF_ONLY",
    disable_duet: bool = False,
    disable_stitch: bool = False,
    disable_comment: bool = False
) -> Dict[str, Any]:
    """Post task video to TikTok using PULL_FROM_URL"""
    
async def check_post_status(
    self,
    access_token: str,
    publish_id: str
) -> Dict[str, Any]:
    """Check status of posted content"""
```

## Phase 3: Data Flow & Integration

### 3.1 Task Output Structure
Tasks generating videos must store data as:
```python
output_data = {
    "video_url": "https://storage.supabase.co/...",
    "thumbnail_url": "https://storage.supabase.co/...",
    "suggested_caption": "#SmartHome #LEDLights...",
    "media_type": "video",
    "duration_seconds": 30,
    "resolution": "1080x1920",
    "file_size": 10485760  # bytes
}
```

### 3.2 Complete User Flow
1. User navigates to `/instances/[id]/tasks/[taskId]`
2. Page loads three sections with task data
3. If task has video output, "Post to TikTok" checkbox appears
4. User checks checkbox → Dialog opens
5. User reviews/edits caption and settings
6. User clicks "Post Now"
7. Backend processes:
   - Validates permissions
   - Refreshes TikTok token if needed
   - Queries creator info
   - Posts via PULL_FROM_URL
   - Stores publish_id
8. Frontend polls status every 5 seconds
9. Shows success/failure message

### 3.3 Database Updates
Fields populated during posting:
- `tiktok_post_data`: Request parameters as JSONB
- `tiktok_publish_id`: TikTok's tracking ID
- `tiktok_post_status`: Status progression
- `tiktok_post_url`: Final URL when published
- `scheduled_post_time`: Timestamp (future feature)

## Phase 4: Error Handling & Edge Cases

### 4.1 Error Scenarios
- **No TikTok Account**: Show connection prompt with link to settings
- **Expired Token**: Auto-refresh or re-auth dialog
- **Video Too Large** (>4GB): Pre-validation with error message
- **Invalid Format**: Check before posting attempt
- **Rate Limits**: Queue with retry logic
- **Sandbox Restrictions**: Clear warning about private visibility

### 4.2 Sandbox Mode Limitations
- All posts are SELF_ONLY (private)
- No public post IDs returned
- Limited to test accounts
- Display "Sandbox Mode" badge in UI
- Info tooltip explaining restrictions

## Phase 5: Implementation Timeline

### Week 1: Backend Foundation
**Day 1-2**: 
- Implement task detail endpoint with mock planning data
- Add execution logs structure from execution_steps field

**Day 3-4**:
- Enhance TikTok content service with task-specific methods
- Implement posting endpoint with full validation
- Add status checking endpoint

**Day 5**:
- Integration testing
- Error handling implementation

### Week 2: Frontend Implementation
**Day 1-2**:
- Create task detail page with three-section layout
- Implement planning section with mock data
- Add execution logs placeholder

**Day 3-4**:
- Build TikTok posting dialog component
- Implement video preview and form controls
- Add account selector for multi-account support

**Day 5**:
- API integration with hooks
- Status polling implementation
- Loading and error states

### Week 3: Integration & Polish
**Day 1-2**:
- End-to-end testing with real TikTok sandbox
- Fix integration issues

**Day 3-4**:
- UI polish and responsive design
- Performance optimization
- Documentation

**Day 5**:
- Final testing and bug fixes
- Deployment preparation

## Technical Specifications

### API Rate Limits
- Query Creator Info: 20 requests/minute per access_token
- Post Status: 30 requests/minute per access_token
- Content Posting: Follow TikTok's daily caps

### Video Requirements
- **Formats**: MP4, WebM, MOV
- **Codecs**: H.264 (preferred), H.265, VP8, VP9
- **Size**: Maximum 4GB
- **Duration**: 3-10 minutes (user-dependent)
- **Resolution**: 360-4096 pixels
- **Frame Rate**: 23-60 FPS

### Security Considerations
- Validate video URLs before posting
- Ensure proper instance/user access control
- Token encryption (already implemented)
- Rate limiting on posting endpoints
- CSRF protection on state parameter

## Success Metrics
- Task detail page loads < 2 seconds
- TikTok posting success rate > 95%
- Status updates within 10 seconds
- Zero data loss on token refresh
- All sandbox posts visible in TikTok app

## Future Enhancements (Post-MVP)
- Real scheduled posting with Celery Beat
- Live agent execution logs via WebSocket
- Batch posting for multiple tasks
- Photo posting support (carousel)
- Cross-posting to multiple accounts simultaneously
- Analytics integration for post performance
- Auto-posting based on task configuration
- Webhook integration for post status updates

## Dependencies & Requirements
- TikTok Developer App with Content Posting API enabled
- Verified domain/URL prefix for PULL_FROM_URL
- Supabase storage for video hosting
- Valid TikTok test accounts for sandbox
- ENCRYPTION_KEY environment variable set
- TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET configured

## Risk Mitigation
- **API Changes**: Version API calls, maintain compatibility layer
- **Token Expiration**: Pre-check and refresh before operations
- **Large Videos**: Progress indicators, background processing
- **Sandbox Confusion**: Clear documentation and UI indicators
- **Network Issues**: Retry logic with exponential backoff

This plan provides a comprehensive, structured approach to implementing TikTok content posting while maintaining the existing architecture and preparing for future enhancements.