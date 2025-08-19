# TikTok Content Posting API Implementation

## Overview
This document details the complete implementation of the TikTok content posting API backend functionality, including all files created/modified and their roles in the system.

## Implementation Status: ✅ COMPLETE (Backend API Ready)

## Architecture Flow
```
Task (with video output) → API Endpoints → TikTok Service → TikTok API (Sandbox)
                         ↓
                    Database Updates
                         ↓
                    Status Tracking
```

## Files Modified/Created in This Session

### 1. Database Models

#### `/backend/src/models/instance.py` (MODIFIED)
**Purpose**: Enhanced InstanceTask model with TikTok posting fields and methods

**Added Fields**:
- `tiktok_publish_id`: String field to store TikTok's publish ID
- `tiktok_post_status`: Track posting status (PROCESSING, PUBLISHED, FAILED)
- `tiktok_post_url`: Final TikTok video URL after publishing
- `tiktok_post_data`: JSONB field for complete posting metadata
- `scheduled_post_time`: Optional scheduling support

**Added Methods**:
- `can_post_to_tiktok()`: Validates if task is ready for TikTok posting
  - Checks task is completed
  - Verifies video URL exists
  - Prevents duplicate posting
- `get_video_url()`: Extracts video URL from output_data JSONB
- `update_tiktok_status()`: Updates posting status and related fields

**Fixed Issues**:
- Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`

### 2. API Schemas

#### `/backend/src/models/instance_schemas.py` (MODIFIED)
**Purpose**: Request/response schemas for TikTok posting endpoints

**Added Schemas**:

1. **TaskDetailResponse**:
   - Complete task information with planning steps and execution logs
   - Includes `can_post_to_tiktok` boolean flag
   - Extracts `suggested_caption` from output data
   - Formats execution steps as structured logs

2. **TaskPlanningStep**:
   - ID, title, description, status for planning visualization

3. **TaskExecutionLog**:
   - Timestamp, agent name, action, status, message, details
   - Status enum: info, success, warning, error

4. **TikTokPostRequest**:
   - `title`: Video caption (max 2200 chars)
   - `privacy_level`: Enum (PUBLIC_TO_EVERYONE, SELF_ONLY, etc.)
   - `disable_duet/stitch/comment`: Privacy controls
   - `video_cover_timestamp_ms`: Thumbnail frame selection
   - `schedule_time`: Optional scheduling
   - `account_id`: Multi-account support

5. **TikTokPostResponse**:
   - `success`: Boolean flag
   - `publish_id`: TikTok's tracking ID
   - `status`: Current posting status
   - `message`: User-friendly message
   - `task_id`: Reference to original task

6. **TikTokPostStatusResponse**:
   - `publish_id`: TikTok publish ID
   - `status`: Current TikTok status
   - `fail_reason`: Error details if failed
   - `post_url`: Final TikTok URL
   - `post_id`: TikTok post ID
   - `uploaded_bytes/downloaded_bytes`: Transfer metrics

### 3. API Endpoints

#### `/backend/src/api/routes/tasks.py` (MODIFIED)
**Purpose**: Three new endpoints for TikTok posting workflow

**New Endpoints**:

1. **GET `/api/v1/tasks/{task_id}/detail`**:
   ```python
   @router.get("/tasks/{task_id}/detail", response_model=TaskDetailResponse)
   async def get_task_detail(task_id: UUID, db: Session, user_id: UUID)
   ```
   - Returns comprehensive task information
   - **DUMMY**: Planning steps are generated mock data (not from real agents)
   - Formats execution_steps into structured logs
   - Checks TikTok posting readiness
   - Extracts suggested caption from output

2. **POST `/api/v1/tasks/{task_id}/post-to-tiktok`**:
   ```python
   @router.post("/tasks/{task_id}/post-to-tiktok", response_model=TikTokPostResponse)
   async def post_task_to_tiktok(task_id: UUID, post_request: TikTokPostRequest, db: Session, user_id: UUID)
   ```
   - Validates task completion and video availability
   - Retrieves TikTok credentials for instance
   - Handles automatic token refresh if expired
   - Queries creator info for privacy validation
   - Posts video using PULL_FROM_URL method
   - Updates task with publish_id and status
   - Stores complete request metadata

3. **GET `/api/v1/tasks/{task_id}/post-status`**:
   ```python
   @router.get("/tasks/{task_id}/post-status", response_model=TikTokPostStatusResponse)
   async def get_tiktok_post_status(task_id: UUID, db: Session, user_id: UUID)
   ```
   - Checks current publishing status from TikTok
   - Updates task when publishing completes
   - Generates final TikTok URL format: `https://www.tiktok.com/@{username}/video/{post_id}`
   - Handles failure reasons

**Helper Functions**:
- `verify_task_access()`: Validates user owns the task via instance ownership

### 4. TikTok Service Enhancement

#### `/backend/src/services/tiktok/content_api.py` (MODIFIED)
**Purpose**: Enhanced TikTok Content API client

**Added Class**: `TikTokContentAPI`

**Key Methods**:

1. **`query_creator_info()`**:
   - Gets account capabilities and privacy options
   - Retry logic with exponential backoff
   - Handles rate limiting (429 errors)

2. **`post_video_sandbox()`**:
   - Posts video using PULL_FROM_URL method
   - URL validation (only Supabase domains allowed)
   - Builds proper post_info structure
   - Error mapping for better debugging
   - Returns publish_id for tracking

3. **`check_post_status()`**:
   - Monitors publishing progress
   - Returns detailed status information
   - Handles completion and failure states

4. **`post_video_from_task()`**:
   - Direct task-to-TikTok posting
   - Extracts video URL and caption from task
   - Validates video URL before posting

5. **`_is_valid_video_url()`**:
   - Security validation for video URLs
   - Only allows HTTPS protocol
   - Validates against approved domains:
     - supabase.co, supabase.io
     - storage.googleapis.com
     - s3.amazonaws.com

**Features**:
- Retry logic: 3 attempts with exponential backoff
- Rate limit handling with smart delays
- Comprehensive error mapping
- Async context manager support


### 6. Documentation

#### `/backend/BACKEND.md` (MODIFIED)
**Added Section**: Complete TikTok Integration documentation

**Documented**:
- Overview of TikTok integration
- All database models and enhancements
- Service architecture
- API endpoints with request/response formats
- Security features (encryption, validation)
- Testing approach
- Configuration requirements

## Dummy Implementations

### 1. Authentication (`/backend/src/api/deps.py`)
**DUMMY**: `get_current_user_id()` returns hardcoded test user
```python
def get_current_user_id():
    return UUID("00000000-0000-0000-0000-000000000000")
```
**Real Implementation Needed**: JWT or OAuth authentication

### 2. Planning Steps (`/backend/src/api/routes/tasks.py`)
**DUMMY**: Mock planning steps generated based on task description
```python
planning_steps = [
    TaskPlanningStep(
        id="1",
        title="Analyze Requirements",
        description="Parse task description and identify content type",
        status="completed" if task.status != InstanceTaskStatus.SUBMITTED else "pending"
    ),
    # ... more mock steps
]
```
**Real Implementation Needed**: Parse from actual agent planning phase

### 3. Media Storage URLs
**CURRENT**: Using Google test bucket videos for demo
```python
video_url = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
```
**Real Implementation Needed**: Actual Supabase storage URLs from real video generation

## Security Features

1. **Token Encryption**: All OAuth tokens encrypted with Fernet
2. **URL Validation**: Only verified domains allowed (Supabase, etc.)
3. **User Verification**: Tasks verified through instance ownership
4. **Scope Management**: OAuth scopes tracked and validated
5. **Automatic Token Refresh**: Transparent renewal on expiration

## Configuration Required

```bash
# .env file
TIKTOK_CLIENT_KEY=sbaw1fo3g3qtdxs0rn
TIKTOK_CLIENT_SECRET=ef03Mn4Ai4B6bbccByHhf7b2faZkSlrW
TIKTOK_REDIRECT_URI=https://skipper-ecom.com/tiktok/callback
TIKTOK_SANDBOX_MODE=true
ENCRYPTION_KEY=OysqVVaTm7RGK53wzC2IjOOebH29kzmO_nzsrX2yNKA=
```

## API Flow

### 1. Task Detail Flow
```
Client → GET /tasks/{id}/detail → Verify ownership → Format response → Return
```

### 2. Posting Flow
```
Client → POST /tasks/{id}/post-to-tiktok
    ↓
Validate task completed & has video
    ↓
Get TikTok credentials
    ↓
Refresh token if expired
    ↓
Query creator info
    ↓
Post video to TikTok
    ↓
Update database
    ↓
Return publish_id
```

### 3. Status Check Flow
```
Client → GET /tasks/{id}/post-status
    ↓
Get credentials
    ↓
Check TikTok API status
    ↓
Update task if complete/failed
    ↓
Return status with URL
```

