# Phase 2: Backend Implementation Todo List - TikTok Content Posting API

## Overview
This document outlines the detailed implementation tasks for Phase 2 of the TikTok content posting feature. Phase 2 focuses on backend API enhancements to support the frontend UI created in Phase 1.

## Prerequisites
- ✅ Frontend implementation (Phase 1) completed
- ✅ TikTok OAuth flow already implemented
- ✅ Database migration with TikTok posting fields applied
- ✅ Basic TikTok content service exists

## Implementation Tasks

### Section 1: Database Models & Schemas
**Location**: `backend/src/models/` and `backend/src/models/instance_schemas.py`

#### Task 1.1: Verify TikTok Fields in InstanceTask Model
- [ ] Verify `tiktok_post_data` (JSONB) field exists
- [ ] Verify `tiktok_publish_id` (VARCHAR 255) field exists  
- [ ] Verify `tiktok_post_status` (VARCHAR 50) field exists
- [ ] Verify `tiktok_post_url` (VARCHAR 500) field exists
- [ ] Verify `scheduled_post_time` (TIMESTAMP) field exists
- [ ] Run `npm run build` and `npm run lint` to verify

#### Task 1.2: Create Task Detail Response Schemas
**File**: `backend/src/models/instance_schemas.py`
- [ ] Create `TaskDetailResponse` Pydantic model
- [ ] Add `planning` field with steps structure
- [ ] Add `execution_logs` field for agent logs
- [ ] Add `attached_media` field for reference images
- [ ] Include all existing task fields
- [ ] Run tests: `poetry run pytest tests/models/`

#### Task 1.3: Create TikTok Posting Request Schemas
**File**: `backend/src/models/instance_schemas.py`
- [ ] Create `TikTokPostRequest` schema with title, privacy_level, etc.
- [ ] Create `TikTokPostStatusResponse` schema
- [ ] Add validation for privacy_level enum
- [ ] Add optional account_id field for multi-account
- [ ] Run tests: `poetry run pytest tests/models/`

#### Task 1.4: Add Helper Methods to InstanceTask
**File**: `backend/src/models/instance.py`
- [ ] Add `get_video_url()` method to extract from output_data
- [ ] Add `can_post_to_tiktok()` validation method
- [ ] Add `update_tiktok_status()` method
- [ ] Write unit tests in `tests/models/test_instance_task_tiktok.py`

### Section 2: Task Detail Endpoint
**Location**: `backend/src/api/routes/tasks.py`

#### Task 2.1: Create Task Detail Endpoint
**Endpoint**: `GET /api/v1/tasks/{task_id}/detail`
- [ ] Add route handler with proper decorators
- [ ] Add user authentication dependency
- [ ] Verify task ownership
- [ ] Return 404 if task not found
- [ ] Run build/lint after implementation

#### Task 2.2: Format Execution Steps as Logs
- [ ] Parse execution_steps JSONB field
- [ ] Transform to execution_logs format
- [ ] Add agent names and timestamps
- [ ] Handle null/empty execution_steps
- [ ] Test with various log formats

#### Task 2.3: Create Mock Planning Data
- [ ] Generate planning steps based on task type
- [ ] Add status indicators (completed/pending)
- [ ] Make it believable for demo purposes
- [ ] Return consistent structure
- [ ] Document mock data logic

#### Task 2.4: Format Attached Media
- [ ] Query InstanceMedia for task references
- [ ] Format URLs and metadata
- [ ] Handle missing media gracefully
- [ ] Add media type classification
- [ ] Test with multiple media items

#### Task 2.5: Write Integration Tests
**File**: `tests/api/test_task_detail.py`
- [ ] Test successful task detail retrieval
- [ ] Test unauthorized access (403)
- [ ] Test non-existent task (404)
- [ ] Test response structure validation
- [ ] Test with tasks having video output
- [ ] Run: `poetry run pytest tests/api/test_task_detail.py -v`

### Section 3: TikTok Posting Endpoint
**Location**: `backend/src/api/routes/tasks.py`

#### Task 3.1: Create Posting Endpoint
**Endpoint**: `POST /api/v1/tasks/{task_id}/post-to-tiktok`
- [ ] Add route handler with request body
- [ ] Validate user authentication
- [ ] Verify task ownership
- [ ] Check task status is completed
- [ ] Run build/lint

#### Task 3.2: Validate Video Output
- [ ] Check output_data contains video_url
- [ ] Verify media_type is "video"
- [ ] Validate video URL is accessible
- [ ] Return 400 if no video output
- [ ] Test validation logic

#### Task 3.3: Get TikTok Credentials
- [ ] Query InstanceTikTokCredentials for instance
- [ ] Support account_id selection if provided
- [ ] Handle no credentials case (return 404)
- [ ] Decrypt access tokens
- [ ] Test credential retrieval

#### Task 3.4: Implement Token Refresh
- [ ] Check if token is expired
- [ ] Call refresh_access_token if needed
- [ ] Update stored credentials
- [ ] Handle refresh failures
- [ ] Write test for refresh flow

#### Task 3.5: Query Creator Info
- [ ] Call TikTok query_creator_info API
- [ ] Validate privacy_level against options
- [ ] Store creator info in response
- [ ] Handle API errors gracefully
- [ ] Test with mock responses

#### Task 3.6: Post Video via PULL_FROM_URL
- [ ] Build post_info structure
- [ ] Set source_info with video URL
- [ ] Call TikTok posting API
- [ ] Extract publish_id from response
- [ ] Handle posting errors

#### Task 3.7: Update Database
- [ ] Store publish_id in task
- [ ] Update tiktok_post_status to "PROCESSING"
- [ ] Store request data in tiktok_post_data
- [ ] Set scheduled_post_time if provided
- [ ] Commit transaction

#### Task 3.8: Write Unit Tests
**File**: `tests/api/test_tiktok_posting.py`
- [ ] Test successful posting flow
- [ ] Test no video output error
- [ ] Test no credentials error
- [ ] Test expired token refresh
- [ ] Test TikTok API errors
- [ ] Run: `poetry run pytest tests/api/test_tiktok_posting.py -v`

#### Task 3.9: Write Integration Tests
**File**: `tests/integration/test_tiktok_posting_flow.py`
- [ ] Mock TikTok API responses
- [ ] Test end-to-end posting flow
- [ ] Test with different privacy levels
- [ ] Test multi-account selection
- [ ] Verify database updates
- [ ] Run: `poetry run pytest tests/integration/test_tiktok_posting_flow.py -v`

### Section 4: Post Status Endpoint
**Location**: `backend/src/api/routes/tasks.py`

#### Task 4.1: Create Status Endpoint
**Endpoint**: `GET /api/v1/tasks/{task_id}/post-status`
- [ ] Add route handler
- [ ] Verify user authentication
- [ ] Check task has publish_id
- [ ] Return 404 if no TikTok post
- [ ] Run build/lint

#### Task 4.2: Check TikTok Post Status
- [ ] Get credentials for task's instance
- [ ] Call TikTok check_post_status API
- [ ] Parse status response
- [ ] Map to internal status enum
- [ ] Handle API errors

#### Task 4.3: Update Task Status
- [ ] Update tiktok_post_status field
- [ ] Store TikTok URL if published
- [ ] Record fail_reason if failed
- [ ] Update last_checked timestamp
- [ ] Test status updates

#### Task 4.4: Write Tests
**File**: `tests/api/test_post_status.py`
- [ ] Test successful status check
- [ ] Test processing status
- [ ] Test published status with URL
- [ ] Test failed status with reason
- [ ] Test no publish_id error
- [ ] Run: `poetry run pytest tests/api/test_post_status.py -v`

### Section 5: Enhanced TikTok Content Service
**Location**: `backend/src/services/tiktok/content_api.py`

#### Task 5.1: Add post_video_from_task Method
- [ ] Create method signature with task parameter
- [ ] Extract video URL from task output_data
- [ ] Build caption from suggested_caption
- [ ] Set appropriate privacy level
- [ ] Call existing post_video_sandbox

#### Task 5.2: Validate Supabase URLs
- [ ] Check URL is from Supabase storage
- [ ] Verify URL is publicly accessible
- [ ] Add URL validation helper
- [ ] Handle invalid URLs gracefully
- [ ] Test URL validation

#### Task 5.3: Add Retry Logic
- [ ] Implement exponential backoff
- [ ] Set max retry attempts (3)
- [ ] Handle rate limit errors specially
- [ ] Log retry attempts
- [ ] Test retry mechanism

#### Task 5.4: Enhanced Error Mapping
- [ ] Map TikTok error codes to user-friendly messages
- [ ] Add specific handling for common errors
- [ ] Include troubleshooting hints
- [ ] Log detailed error info
- [ ] Test error scenarios

#### Task 5.5: Write Service Tests
**File**: `tests/services/test_tiktok_content_enhanced.py`
- [ ] Test post_video_from_task method
- [ ] Test URL validation
- [ ] Test retry logic
- [ ] Test error mapping
- [ ] Mock external API calls
- [ ] Run: `poetry run pytest tests/services/test_tiktok_content_enhanced.py -v`

### Section 6: Comprehensive Testing Suite

#### Task 6.1: Unit Tests - Models
**File**: `tests/models/test_tiktok_schemas.py`
- [ ] Test TaskDetailResponse validation
- [ ] Test TikTokPostRequest validation
- [ ] Test enum constraints
- [ ] Test optional fields
- [ ] Test serialization
- [ ] Run: `poetry run pytest tests/models/test_tiktok_schemas.py -v`

#### Task 6.2: Unit Tests - Service Methods
**File**: `tests/services/test_tiktok_service_units.py`
- [ ] Test each service method in isolation
- [ ] Mock all external dependencies
- [ ] Test edge cases
- [ ] Test error handling
- [ ] Verify return types
- [ ] Run: `poetry run pytest tests/services/test_tiktok_service_units.py -v`

#### Task 6.3: Integration Tests - Task Detail
**File**: `tests/integration/test_task_detail_integration.py`
- [ ] Test with real database
- [ ] Create test data fixtures
- [ ] Test with various task states
- [ ] Verify response completeness
- [ ] Test performance (< 200ms)
- [ ] Run: `poetry run pytest tests/integration/test_task_detail_integration.py -v`

#### Task 6.4: Integration Tests - Posting Flow
**File**: `tests/integration/test_posting_integration.py`
- [ ] Test complete posting workflow
- [ ] Mock TikTok API responses
- [ ] Test database transactions
- [ ] Verify all fields updated
- [ ] Test rollback on errors
- [ ] Run: `poetry run pytest tests/integration/test_posting_integration.py -v`

#### Task 6.5: Integration Tests - Status Checking
**File**: `tests/integration/test_status_integration.py`
- [ ] Test status polling
- [ ] Test status transitions
- [ ] Test with various TikTok responses
- [ ] Verify database updates
- [ ] Test concurrent status checks
- [ ] Run: `poetry run pytest tests/integration/test_status_integration.py -v`

#### Task 6.6: Error Scenario Tests
**File**: `tests/api/test_error_scenarios.py`
- [ ] Test network failures
- [ ] Test TikTok API errors
- [ ] Test invalid data handling
- [ ] Test timeout scenarios
- [ ] Test rate limiting
- [ ] Run: `poetry run pytest tests/api/test_error_scenarios.py -v`

#### Task 6.7: Token Refresh Tests
**File**: `tests/services/test_token_refresh.py`
- [ ] Test expired token detection
- [ ] Test successful refresh
- [ ] Test refresh failure
- [ ] Test credential updates
- [ ] Test concurrent refreshes
- [ ] Run: `poetry run pytest tests/services/test_token_refresh.py -v`

#### Task 6.8: Multi-Account Tests
**File**: `tests/api/test_multi_account.py`
- [ ] Test account selection
- [ ] Test default account
- [ ] Test invalid account_id
- [ ] Test account switching
- [ ] Test per-account credentials
- [ ] Run: `poetry run pytest tests/api/test_multi_account.py -v`

#### Task 6.9: Performance Tests
**File**: `tests/performance/test_tiktok_performance.py`
- [ ] Test endpoint response times
- [ ] Test concurrent requests
- [ ] Test database query optimization
- [ ] Test caching effectiveness
- [ ] Generate performance report
- [ ] Run: `poetry run pytest tests/performance/test_tiktok_performance.py -v`

#### Task 6.10: End-to-End Test
**File**: `tests/e2e/test_tiktok_posting_e2e.py`
- [ ] Create task with video output
- [ ] Post to TikTok
- [ ] Poll for status
- [ ] Verify final state
- [ ] Clean up test data
- [ ] Run: `poetry run pytest tests/e2e/test_tiktok_posting_e2e.py -v`

### Section 7: Documentation & Finalization

#### Task 7.1: Update API Documentation
**File**: `backend/docs/api/tiktok_posting.md`
- [ ] Document all new endpoints
- [ ] Add request/response examples
- [ ] Include error codes
- [ ] Add usage guidelines
- [ ] Include rate limits

#### Task 7.2: Update BACKEND.md
**File**: `backend/BACKEND.md`
- [ ] Add TikTok posting section
- [ ] Document new endpoints
- [ ] Update capabilities list
- [ ] Add configuration notes
- [ ] Include testing instructions

#### Task 7.3: Final Testing & Verification
- [ ] Run full test suite: `poetry run pytest`
- [ ] Check test coverage: `poetry run pytest --cov`
- [ ] Run linting: `poetry run ruff check`
- [ ] Run type checking: `poetry run mypy src/`
- [ ] Manual testing with frontend

## Success Criteria

### Functional Requirements
- [ ] Task detail endpoint returns planning, logs, and output data
- [ ] TikTok posting works with PULL_FROM_URL method
- [ ] Status checking provides real-time updates
- [ ] Multi-account selection works correctly
- [ ] Token refresh happens automatically

### Non-Functional Requirements
- [ ] All endpoints respond in < 500ms
- [ ] Test coverage > 80%
- [ ] No linting errors
- [ ] All tests passing
- [ ] Documentation complete

## Testing Commands

```bash
# Run all tests
poetry run pytest -v

# Run specific test categories
poetry run pytest tests/api/ -v          # API tests
poetry run pytest tests/services/ -v     # Service tests
poetry run pytest tests/integration/ -v  # Integration tests
poetry run pytest tests/e2e/ -v         # End-to-end tests

# Run with coverage
poetry run pytest --cov=src --cov-report=html

# Run linting
poetry run ruff check src/
poetry run mypy src/

# Run specific test file
poetry run pytest tests/api/test_tiktok_posting.py -v -s
```

## Environment Variables Required

```bash
# .env file
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_REDIRECT_URI=http://localhost:3001/tiktok/callback
TIKTOK_SANDBOX_MODE=true
ENCRYPTION_KEY=your_fernet_key
DATABASE_URL=your_database_url
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_KEY=your_service_key
```

## Notes

1. **Sandbox Mode**: All posts will be private (SELF_ONLY) in sandbox mode
2. **Rate Limits**: 
   - Query Creator Info: 20 req/min per token
   - Check Post Status: 30 req/min per token
3. **Video Requirements**: 
   - Max 4GB, 10 minutes
   - Must be from verified domain (Supabase)
4. **Testing**: Always mock TikTok API calls in tests
5. **Error Handling**: Log all TikTok API errors for debugging

## Dependencies

- FastAPI for API endpoints
- SQLAlchemy for database operations
- httpx for TikTok API calls
- Pydantic for data validation
- pytest for testing
- pytest-asyncio for async tests
- pytest-mock for mocking

## Completion Checklist

- [ ] All database models updated
- [ ] All schemas created
- [ ] Task detail endpoint working
- [ ] TikTok posting endpoint working
- [ ] Status checking endpoint working
- [ ] Service enhancements complete
- [ ] All tests written and passing
- [ ] Documentation updated
- [ ] Code reviewed and cleaned
- [ ] Ready for production deployment