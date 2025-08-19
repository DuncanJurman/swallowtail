 TikTok Content Posting MVP Implementation Plan                                 │ │
│ │                                                                                │ │
│ │ Overview                                                                       │ │
│ │                                                                                │ │
│ │ A focused, MVP-first approach to implement TikTok content posting with         │ │
│ │ instance-based Supabase storage. This plan prioritizes core functionality and  │ │
│ │ testability while avoiding overengineering.                                    │ │
│ │                                                                                │ │
│ │ Architecture                                                                   │ │
│ │                                                                                │ │
│ │ Task Output (video URL) → Instance Storage → TikTok API → Post Status Tracking │ │
│ │                                                                                │ │
│ │ Phase 1: Storage Setup for Instance Isolation                                  │ │
│ │                                                                                │ │
│ │ 1.1 Update Storage Service for Instance-Based Paths                            │ │
│ │                                                                                │ │
│ │ - Modify src/services/storage.py:                                              │ │
│ │   - Change storage paths from products/{product_id}/ to                        │ │
│ │ instances/{instance_id}/                                                       │ │
│ │   - Add instance_id parameter to all upload methods                            │ │
│ │   - Implement instance-based access control                                    │ │
│ │                                                                                │ │
│ │ 1.2 Create Storage Buckets                                                     │ │
│ │                                                                                │ │
│ │ - New File scripts/setup_instance_storage.py:                                  │ │
│ │   - Create buckets: instance-media (public), instance-temp (private)           │ │
│ │   - Set up RLS policies for instance-based access                              │ │
│ │                                                                                │ │
│ │ 1.3 Database Schema Updates                                                    │ │
│ │                                                                                │ │
│ │ - Migration: Add storage metadata tables:                                      │ │
│ │   - instance_media: Track all media files per instance                         │ │
│ │   - Link media to tasks for easy retrieval                                     │ │
│ │                                                                                │ │
│ │ Phase 2: Simplify TikTok Content API                                           │ │
│ │                                                                                │ │
│ │ 2.1 Enhanced Content Service                                                   │ │
│ │                                                                                │ │
│ │ - Update src/services/tiktok/content_api.py:                                   │ │
│ │   - Add TikTokContentAPI class with proper error handling                      │ │
│ │   - Implement retry logic with exponential backoff                             │ │
│ │   - Add URL validation (only allow Supabase domains)                           │ │
│ │   - Create post_video_from_url() method                                        │ │
│ │                                                                                │ │
│ │ 2.2 Task to TikTok Pipeline                                                    │ │
│ │                                                                                │ │
│ │ - New Method in content API:                                                   │ │
│ │ async def post_task_output_to_tiktok(task_id, caption, privacy_settings)       │ │
│ │   - Extract video URL from task output_data                                    │ │
│ │   - Validate URL is from Supabase                                              │ │
│ │   - Post to TikTok using PULL_FROM_URL                                         │ │
│ │   - Update task with publish_id                                                │ │
│ │                                                                                │ │
│ │ Phase 3: API Endpoints                                                         │ │
│ │                                                                                │ │
│ │ 3.1 Simplified Task Posting Endpoint                                           │ │
│ │                                                                                │ │
│ │ - Update src/api/routes/tasks.py:                                              │ │
│ │   - Single endpoint: POST /tasks/{task_id}/post-to-tiktok                      │ │
│ │   - Request body: caption, privacy settings                                    │ │
│ │   - Response: publish_id, status                                               │ │
│ │                                                                                │ │
│ │ 3.2 Status Checking                                                            │ │
│ │                                                                                │ │
│ │ - Add Endpoint: GET /tasks/{task_id}/tiktok-status                             │ │
│ │   - Check TikTok API for post status                                           │ │
│ │   - Update task when complete                                                  │ │
│ │   - Return TikTok URL when published                                           │ │
│ │                                                                                │ │
│ │ Phase 4: Testing Implementation                                                │ │
│ │                                                                                │ │
│ │ 4.1 Storage Tests                                                              │ │
│ │                                                                                │ │
│ │ - New File tests/services/test_instance_storage.py:                            │ │
│ │   - Test instance isolation                                                    │ │
│ │   - Test upload/download functionality                                         │ │
│ │   - Test access control                                                        │ │
│ │                                                                                │ │
│ │ 4.2 TikTok Integration Tests                                                   │ │
│ │                                                                                │ │
│ │ - New File tests/integration/test_tiktok_posting.py:                           │ │
│ │   - Mock TikTok API responses                                                  │ │
│ │   - Test full pipeline: task → storage → TikTok                                │ │
│ │   - Test error scenarios                                                       │ │
│ │                                                                                │ │
│ │ 4.3 Manual Testing Script                                                      │ │
│ │                                                                                │ │
│ │ - New File scripts/test_tiktok_posting.py:                                     │ │
│ │   - Upload test video to instance storage                                      │ │
│ │   - Create mock task with video URL                                            │ │
│ │   - Post to TikTok sandbox                                                     │ │
│ │   - Check status until complete                                                │ │
│ │                                                                                │ │
│ │ Phase 5: Frontend Integration (Optional)                                       │ │
│ │                                                                                │ │
│ │ 5.1 Task Detail Enhancement                                                    │ │
│ │                                                                                │ │
│ │ - Show "Post to TikTok" button when task has video output                      │ │
│ │ - Display posting status                                                       │ │
│ │ - Show TikTok URL when published                                               │ │
│ │                                                                                │ │
│ │ Key Simplifications from Original Plan                                         │ │
│ │                                                                                │ │
│ │ 1. No Complex Metadata: Simple JSONB storage for post data                     │ │
│ │ 2. No Multi-Account Support Initially: One TikTok account per instance         │ │
│ │ 3. No Scheduling: Direct posting only                                          │ │
│ │ 4. No Custom Domains: Use Supabase URLs directly                               │ │
│ │ 5. No Complex Caching: Rely on Supabase CDN                                    │ │
│ │                                                                                │ │
│ │ Implementation Order                                                           │ │
│ │                                                                                │ │
│ │ 1. Day 1: Storage service updates for instance isolation                       │ │
│ │ 2. Day 2: TikTok content API enhancements                                      │ │
│ │ 3. Day 3: API endpoints and database updates                                   │ │
│ │ 4. Day 4: Integration tests and manual testing                                 │ │
│ │ 5. Day 5: Bug fixes and documentation                                          │ │
│ │                                                                                │ │
│ │ Files to Modify/Create                                                         │ │
│ │                                                                                │ │
│ │ Modify:                                                                        │ │
│ │                                                                                │ │
│ │ - src/services/storage.py - Instance-based paths                               │ │
│ │ - src/services/tiktok/content_api.py - Enhanced posting                        │ │
│ │ - src/api/routes/tasks.py - Posting endpoints                                  │ │
│ │ - src/models/instance.py - Add TikTok fields to InstanceTask                   │ │
│ │                                                                                │ │
│ │ Create:                                                                        │ │
│ │                                                                                │ │
│ │ - scripts/setup_instance_storage.py - Storage setup                            │ │
│ │ - scripts/test_tiktok_posting.py - Manual testing                              │ │
│ │ - tests/services/test_instance_storage.py - Storage tests                      │ │
│ │ - tests/integration/test_tiktok_posting.py - Integration tests                 │ │
│ │ - Migration file for storage metadata tables                                   │ │
│ │                                                                                │ │
│ │ Success Criteria                                                               │ │
│ │                                                                                │ │
│ │ 1. ✅ Videos stored with instance isolation in Supabase                         │ │
│ │ 2. ✅ Task outputs can be posted to TikTok                                      │ │
│ │ 3. ✅ Status tracking from processing to published                              │ │
│ │ 4. ✅ Tests pass for all critical paths                                         │ │
│ │ 5. ✅ Manual test successfully posts to TikTok sandbox                          │ │
│ │                                                                                │ │
│ │ Notes                                                                          │ │
│ │                                                                                │ │
│ │ - Focus on PULL_FROM_URL method (simpler than file upload)                     │ │
│ │ - Use sandbox mode for all testing                                             │ │
│ │ - Keep authentication simple (existing OAuth implementation)                   │ │
│ │ - Prioritize working MVP over perfect architecture  