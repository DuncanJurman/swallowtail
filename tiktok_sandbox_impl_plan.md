TikTok Sandbox Implementation Plan for  │ │
│ │ MVP Demo                                │ │
│ │                                         │ │
│ │ Overview                                │ │
│ │                                         │ │
│ │ We'll implement a minimal TikTok OAuth  │ │
│ │ flow and content posting functionality  │ │
│ │ using the sandbox environment to create │ │
│ │  a demo video showing the complete      │ │
│ │ integration. This will be built on your │ │
│ │  existing Next.js frontend and FastAPI  │ │
│ │ backend architecture.                   │ │
│ │                                         │ │
│ │ Phase 1: Backend OAuth Implementation   │ │
│ │                                         │ │
│ │ 1.1 Create TikTok Service Module        │ │
│ │                                         │ │
│ │ File: backend/src/services/tiktok/      │ │
│ │ - __init__.py                           │ │
│ │ - oauth.py - OAuth flow handling        │ │
│ │ - content_api.py - Content posting      │ │
│ │ functions                               │ │
│ │ - models.py - TikTok-specific Pydantic  │ │
│ │ models                                  │ │
│ │ - config.py - TikTok API configuration  │ │
│ │                                         │ │
│ │ 1.2 OAuth Implementation (oauth.py)     │ │
│ │                                         │ │
│ │ # Key components:                       │ │
│ │ - Generate authorization URL with state │ │
│ │  for CSRF protection                    │ │
│ │ - Exchange authorization code for       │ │
│ │ access token                            │ │
│ │ - Refresh token management              │ │
│ │ - Store tokens encrypted in database    │ │
│ │                                         │ │
│ │ 1.3 Database Updates                    │ │
│ │                                         │ │
│ │ - Add instance_tiktok_credentials table │ │
│ │  to store OAuth tokens                  │ │
│ │ - Encrypt tokens using existing         │ │
│ │ encryption patterns                     │ │
│ │ - Link to instance_credentials table    │ │
│ │                                         │ │
│ │ 1.4 API Endpoints                       │ │
│ │                                         │ │
│ │ File: backend/src/api/routes/tiktok.py  │ │
│ │ - GET /api/v1/tiktok/auth - Generate    │ │
│ │ auth URL                                │ │
│ │ - GET /api/v1/tiktok/callback - Handle  │ │
│ │ OAuth callback                          │ │
│ │ - POST /api/v1/tiktok/post - Post       │ │
│ │ content (sandbox)                       │ │
│ │ - GET /api/v1/tiktok/account - Get      │ │
│ │ account info                            │ │
│ │                                         │ │
│ │ Phase 2: Frontend OAuth Flow            │ │
│ │                                         │ │
│ │ 2.1 TikTok Connection Component         │ │
│ │                                         │ │
│ │ File: frontend/components/instances/tik │ │
│ │ tok-connect.tsx                         │ │
│ │ - "Connect TikTok Account" button       │ │
│ │ - OAuth popup handling                  │ │
│ │ - Success/error states                  │ │
│ │ - Account display after connection      │ │
│ │                                         │ │
│ │ 2.2 Update Instance Settings Page       │ │
│ │                                         │ │
│ │ File: frontend/app/(auth)/instances/[id │ │
│ │ ]/settings/page.tsx                     │ │
│ │ - Add TikTok connection section         │ │
│ │ - Show connected accounts               │ │
│ │ - Disconnect functionality              │ │
│ │                                         │ │
│ │ 2.3 Content Posting Interface           │ │
│ │                                         │ │
│ │ File: frontend/components/tasks/tiktok- │ │
│ │ post.tsx                                │ │
│ │ - Simple form to create TikTok post     │ │
│ │ - Video upload (for demo, can be mock)  │ │
│ │ - Caption input                         │ │
│ │ - Post button                           │ │
│ │                                         │ │
│ │ Phase 3: Sandbox Configuration          │ │
│ │                                         │ │
│ │ 3.1 Sandbox Setup                       │ │
│ │                                         │ │
│ │ 1. Create sandbox in TikTok Developer   │ │
│ │ Portal                                  │ │
│ │ 2. Add your TikTok account as target    │ │
│ │ user                                    │ │
│ │ 3. Configure sandbox with Login Kit and │ │
│ │  limited Content Posting API            │ │
│ │                                         │ │
│ │ 3.2 Environment Configuration           │ │
│ │                                         │ │
│ │ # .env additions                        │ │
│ │ TIKTOK_CLIENT_KEY=your_sandbox_client_k │ │
│ │ ey                                      │ │
│ │ TIKTOK_CLIENT_SECRET=your_sandbox_clien │ │
│ │ t_secret                                │ │
│ │ TIKTOK_SANDBOX_MODE=true                │ │
│ │ TIKTOK_REDIRECT_URI=https://skipper-eco │ │
│ │ m.com/api/v1/tiktok/callback            │ │
│ │                                         │ │
│ │ Phase 4: Demo Video Flow                │ │
│ │                                         │ │
│ │ 4.1 Video Script (2-3 minutes)          │ │
│ │                                         │ │
│ │ 1. Start at Landing Page (0:00-0:15)    │ │
│ │   - Show https://skipper-ecom.com       │ │
│ │   - Navigate to dashboard               │ │
│ │ 2. Show Instance Management (0:15-0:30) │ │
│ │   - Display existing instance           │ │
│ │   - Click into instance settings        │ │
│ │ 3. Connect TikTok Account (0:30-1:00)   │ │
│ │   - Click "Connect TikTok Account"      │ │
│ │   - Show OAuth popup (sandbox)          │ │
│ │   - Authorize and redirect back         │ │
│ │   - Display connected account           │ │
│ │ 4. Create Content Task (1:00-1:30)      │ │
│ │   - Navigate to tasks page              │ │
│ │   - Type: "Post a video about our new   │ │
│ │ product to TikTok"                      │ │
│ │   - Submit task                         │ │
│ │ 5. Show Task Processing (1:30-2:00)     │ │
│ │   - Display task in queue               │ │
│ │   - Show status updates                 │ │
│ │   - Mock content creation               │ │
│ │ 6. Demonstrate Posting (2:00-2:30)      │ │
│ │   - Show generated content              │ │
│ │   - Click "Post to TikTok"              │ │
│ │   - Display success message             │ │
│ │   - Show post URL (sandbox)             │ │
│ │                                         │ │
│ │ Phase 5: Implementation Details         │ │
│ │                                         │ │
│ │ 5.1 Minimal OAuth Flow                  │ │
│ │                                         │ │
│ │ # Simplified flow for demo              │ │
│ │ 1. Generate auth URL with required      │ │
│ │ scopes                                  │ │
│ │ 2. User authorizes in popup             │ │
│ │ 3. Callback extracts code               │ │
│ │ 4. Exchange for access token            │ │
│ │ 5. Store encrypted token                │ │
│ │ 6. Return success to frontend           │ │
│ │                                         │ │
│ │ 5.2 Mock Content Posting                │ │
│ │                                         │ │
│ │ Since sandbox has limitations:          │ │
│ │ - Use dummy video URL                   │ │
│ │ - Show realistic UI flow                │ │
│ │ - Return mock success response          │ │
│ │ - Display sandbox disclaimer            │ │
│ │                                         │ │
│ │ 5.3 Key Files to Create/Modify          │ │
│ │                                         │ │
│ │ 1. Backend:                             │ │
│ │   - src/services/tiktok/oauth.py        │ │
│ │   - src/services/tiktok/content_api.py  │ │
│ │   - src/api/routes/tiktok.py            │ │
│ │   - src/models/tiktok_credentials.py    │ │
│ │ 2. Frontend:                            │ │
│ │   -                                     │ │
│ │ components/instances/tiktok-connect.tsx │ │
│ │   - app/(auth)/instances/[id]/settings/ │ │
│ │ page.tsx                                │ │
│ │   - lib/tiktok-client.ts                │ │
│ │   - types/tiktok.ts                     │ │
│ │                                         │ │
│ │ Phase 6: Testing & Recording            │ │
│ │                                         │ │
│ │ 6.1 Test Sandbox Flow                   │ │
│ │                                         │ │
│ │ - Verify OAuth works with sandbox       │ │
│ │ - Test token storage                    │ │
│ │ - Confirm account info retrieval        │ │
│ │                                         │ │
│ │ 6.2 Record Demo Video                   │ │
│ │                                         │ │
│ │ - Use OBS or similar                    │ │
│ │ - Follow script precisely               │ │
│ │ - Show real domain (skipper-ecom.com)   │ │
│ │ - Include sandbox disclaimer overlay    │ │
│ │                                         │ │
│ │ Timeline                                │ │
│ │                                         │ │
│ │ - Day 1: Backend OAuth implementation   │ │
│ │ (4 hours)                               │ │
│ │ - Day 2: Frontend components (4 hours)  │ │
│ │ - Day 3: Sandbox testing & video        │ │
│ │ recording (2 hours)                     │ │
│ │                                         │ │
│ │ Notes                                   │ │
│ │                                         │ │
│ │ - Keep implementation minimal for MVP   │ │
│ │ - Focus on demonstrating the flow, not  │ │
│ │ full functionality                      │ │
│ │ - Use sandbox limitations as feature    │ │
│ │ (shows understanding)                   │ │
│ │ - Ensure all URLs show your production  │ │
│ │ domain                                  │ │
│ │                                         │ │
│ │ This plan creates a working TikTok      │ │
│ │ integration demo that satisfies their   │ │
│ │ requirements while being achievable in  │ │
│ │ a short timeframe.  



# Current Status:

## Completed:

### Phase 1: Backend OAuth Implementation ✅
- ✅ TikTok service module structure created
  - `backend/src/services/tiktok/__init__.py`
  - `backend/src/services/tiktok/oauth.py` - OAuth flow handling
  - `backend/src/services/tiktok/content_api.py` - Content posting functions
  - `backend/src/services/tiktok/models.py` - TikTok-specific Pydantic models
  - `backend/src/services/tiktok/config.py` - TikTok API configuration
  
- ✅ OAuth service with proper TikTok specifications
  - Authorization URL generation with CSRF state
  - Code-to-token exchange
  - Token refresh mechanism
  - User info retrieval
  - Token revocation

- ✅ Content API service (using real API calls in sandbox)
  - Query creator info endpoint
  - Video posting with PULL_FROM_URL and FILE_UPLOAD
  - Proper error handling
  - Post status checking

- ✅ API Routes created
  - `backend/src/api/routes/tiktok.py`
  - POST `/api/v1/tiktok/auth` - Generate auth URL
  - GET `/api/v1/tiktok/callback` - Handle OAuth callback
  - POST `/api/v1/tiktok/post` - Post content
  - GET `/api/v1/tiktok/account/{instance_id}` - Get account info
  - DELETE `/api/v1/tiktok/disconnect/{instance_id}` - Disconnect account

- ✅ Tests implemented and passing
  - `backend/tests/services/test_tiktok_oauth.py` - 6 tests passing
  - `backend/tests/services/test_tiktok_content.py` - 5 tests passing
  - All 11 tests verified working

## Next Steps:

### 1. Add Database Table (Priority: HIGH) ✅
- ✅ Created `instance_tiktok_credentials` table
- ✅ Implemented encrypted token storage
- ✅ Created Alembic migration `e6494a274b11_add_tiktok_credentials_table.py`
- ✅ Migration successfully applied to database
- ✅ Updated OAuth service to save credentials
- ✅ Updated API routes to use stored credentials
- ✅ Modified to support multiple TikTok accounts per instance
- ✅ Added second migration `9ed9fb38e8d5` to remove unique constraint
- ✅ Added account naming feature for easy identification
- ✅ Updated endpoints to handle account selection

### 2. Frontend OAuth Flow (Phase 2) ✅ COMPLETED
- ✅ Create TikTok connection component
- ✅ Update instance settings page
- ✅ Implement OAuth popup handling

#### Phase 2 Completed Implementation

 Phase 2: Frontend TikTok OAuth Flow     │ │
│ │ Implementation Plan                     │ │
│ │                                         │ │
│ │ Overview                                │ │
│ │                                         │ │
│ │ Implement a clean, user-friendly TikTok │ │
│ │  connection flow that integrates        │ │
│ │ seamlessly with the existing            │ │
│ │ Swallowtail frontend architecture,      │ │
│ │ supporting multiple TikTok accounts per │ │
│ │  instance.                              │ │
│ │                                         │ │
│ │ 1. Create Instance Settings Page        │ │
│ │ Structure                               │ │
│ │                                         │ │
│ │ Files to create:                        │ │
│ │ - frontend/app/(auth)/instances/[id]/se │ │
│ │ ttings/page.tsx - Server component for  │ │
│ │ settings page                           │ │
│ │ - frontend/app/(auth)/instances/[id]/se │ │
│ │ ttings/page-client.tsx - Client         │ │
│ │ component with interactive elements     │ │
│ │ - frontend/components/instances/setting │ │
│ │ s/tiktok-connection.tsx - TikTok        │ │
│ │ connection management component         │ │
│ │ - frontend/lib/tiktok-client.ts -       │ │
│ │ TikTok API client wrapper               │ │
│ │ - frontend/types/tiktok.ts - TypeScript │ │
│ │  interfaces for TikTok data             │ │
│ │                                         │ │
│ │ 2. TikTok Connection Component Design   │ │
│ │                                         │ │
│ │ Component Structure:                    │ │
│ │                                         │ │
│ │ TikTokConnection                        │ │
│ │ ├── Connected Accounts Section          │ │
│ │ │   ├── Account Cards (multiple         │ │
│ │ accounts)                               │ │
│ │ │   │   ├── Avatar & Display Name       │ │
│ │ │   │   ├── Account Name (optional)     │ │
│ │ │   │   ├── Connection Status           │ │
│ │ │   │   ├── Last Synced                 │ │
│ │ │   │   └── Disconnect Button           │ │
│ │ │   └── Add New Account Button          │ │
│ │ └── Empty State (when no accounts)      │ │
│ │     ├── TikTok Icon                     │ │
│ │     ├── Descriptive Text                │ │
│ │     └── Connect Account Button          │ │
│ │                                         │ │
│ │ Key Features:                           │ │
│ │                                         │ │
│ │ - Multiple Account Support: Display all │ │
│ │  connected TikTok accounts with clear   │ │
│ │ identification                          │ │
│ │ - Account Naming: Allow users to add    │ │
│ │ friendly names to distinguish accounts  │ │
│ │ - Visual Feedback: Show connection      │ │
│ │ status, token expiration warnings       │ │
│ │ - Sandbox Indicator: Clear visual       │ │
│ │ indication when in sandbox mode         │ │
│ │                                         │ │
│ │ 3. OAuth Flow Implementation            │ │
│ │                                         │ │
│ │ OAuth Popup Handler:                    │ │
│ │                                         │ │
│ │ // frontend/lib/tiktok-oauth.ts         │ │
│ │ export class TikTokOAuth {              │ │
│ │   static async                          │ │
│ │ initiateConnection(instanceId: string,  │ │
│ │ accountName?: string) {                 │ │
│ │     // 1. Call backend to get auth URL  │ │
│ │     // 2. Open popup window with        │ │
│ │ specific dimensions                     │ │
│ │     // 3. Listen for callback messages  │ │
│ │     // 4. Handle success/error states   │ │
│ │     // 5. Refresh account list on       │ │
│ │ success                                 │ │
│ │   }                                     │ │
│ │ }                                       │ │
│ │                                         │ │
│ │ Callback Page:                          │ │
│ │                                         │ │
│ │ - Create                                │ │
│ │ frontend/app/tiktok/callback/page.tsx   │ │
│ │ - Handle OAuth callback from TikTok     │ │
│ │ - Post message to parent window         │ │
│ │ - Show success/error UI                 │ │
│ │ - Auto-close after 3 seconds            │ │
│ │                                         │ │
│ │ 4. UI/UX Design Decisions               │ │
│ │                                         │ │
│ │ Visual Design:                          │ │
│ │                                         │ │
│ │ - Color Scheme: Use TikTok brand colors │ │
│ │  (black/white/red accent) for           │ │
│ │ connection buttons                      │ │
│ │ - Icons: Import TikTok icon from        │ │
│ │ lucide-react or custom SVG              │ │
│ │ - Cards: Use existing Card component    │ │
│ │ pattern from instance-card.tsx          │ │
│ │ - Status Indicators:                    │ │
│ │   - Green dot for active connections    │ │
│ │   - Yellow warning for expiring tokens  │ │
│ │   - Red for disconnected/error states   │ │
│ │                                         │ │
│ │ User Flow:                              │ │
│ │                                         │ │
│ │ 1. User navigates to Instance Settings  │ │
│ │ 2. Sees TikTok section with connected   │ │
│ │ accounts or empty state                 │ │
│ │ 3. Clicks "Connect TikTok Account"      │ │
│ │ 4. Optional: Enters friendly account    │ │
│ │ name                                    │ │
│ │ 5. OAuth popup opens → completes flow → │ │
│ │  auto-closes                            │ │
│ │ 6. Main page updates with new           │ │
│ │ connection                              │ │
│ │ 7. Success toast notification           │ │
│ │                                         │ │
│ │ 5. API Integration                      │ │
│ │                                         │ │
│ │ TikTok API Client:                      │ │
│ │                                         │ │
│ │ // frontend/lib/tiktok-client.ts        │ │
│ │ class TikTokApiClient {                 │ │
│ │   async generateAuthUrl(instanceId:     │ │
│ │ string, accountName?: string)           │ │
│ │   async getAccounts(instanceId: string) │ │
│ │   async disconnectAccount(instanceId:   │ │
│ │ string, accountId: string)              │ │
│ │   async postContent(data:               │ │
│ │ TikTokPostRequest)                      │ │
│ │ }                                       │ │
│ │                                         │ │
│ │ React Query Hooks:                      │ │
│ │                                         │ │
│ │ // frontend/hooks/use-tiktok.ts         │ │
│ │ export function                         │ │
│ │ useTikTokAccounts(instanceId: string)   │ │
│ │ export function useConnectTikTok()      │ │
│ │ export function useDisconnectTikTok()   │ │
│ │                                         │ │
│ │ 6. Settings Page Layout                 │ │
│ │                                         │ │
│ │ Instance Settings                       │ │
│ │ ├── General Settings                    │ │
│ │ ├── Platform Connections                │ │
│ │ │   └── TikTok                          │ │
│ │ │       ├── Section Header with Icon    │ │
│ │ │       ├── Description Text            │ │
│ │ │       ├── Connected Accounts List     │ │
│ │ │       └── Add Account Button          │ │
│ │ ├── Notifications                       │ │
│ │ └── Advanced Options                    │ │
│ │                                         │ │
│ │ 7. Component Implementation Details     │ │
│ │                                         │ │
│ │ TikTokConnectionCard Component:         │ │
│ │                                         │ │
│ │ - Display TikTok profile info (avatar,  │ │
│ │ display name, follower count)           │ │
│ │ - Show account name if provided         │ │
│ │ - Token status indicator                │ │
│ │ - Last sync timestamp                   │ │
│ │ - Quick actions (View Profile,          │ │
│ │ Disconnect)                             │ │
│ │                                         │ │
│ │ Error Handling:                         │ │
│ │                                         │ │
│ │ - Network errors → Show retry button    │ │
│ │ - OAuth errors → Display specific error │ │
│ │  message                                │ │
│ │ - Token expiration → Prompt to          │ │
│ │ reconnect                               │ │
│ │ - API limits → Show rate limit message  │ │
│ │                                         │ │
│ │ 8. Sandbox Mode Considerations          │ │
│ │                                         │ │
│ │ Visual Indicators:                      │ │
│ │                                         │ │
│ │ - "Sandbox Mode" badge on all           │ │
│ │ TikTok-related UI                       │ │
│ │ - Info tooltip explaining sandbox       │ │
│ │ limitations                             │ │
│ │ - Different color scheme (muted) for    │ │
│ │ sandbox accounts                        │ │
│ │                                         │ │
│ │ Limitations UI:                         │ │
│ │                                         │ │
│ │ - Show info box explaining:             │ │
│ │   - Content only visible to test users  │ │
│ │   - Limited API capabilities            │ │
│ │   - Test account requirements           │ │
│ │                                         │ │
│ │ 9. Content Posting Interface (Future)   │ │
│ │                                         │ │
│ │ Quick Preview:                          │ │
│ │                                         │ │
│ │ - Simple modal for posting from         │ │
│ │ instance dashboard                      │ │
│ │ - Video URL/file input                  │ │
│ │ - Caption field with character counter  │ │
│ │ - Privacy settings dropdown             │ │
│ │ - Account selector (if multiple         │ │
│ │ accounts)                               │ │
│ │ - Post button with loading state        │ │
│ │                                         │ │
│ │ 10. Implementation Steps                │ │
│ │                                         │ │
│ │ 1. Set up TikTok Sandbox App            │ │
│ │ (Prerequisites)                         │ │
│ │   - Configure redirect URI: https://ski │ │
│ │ pper-ecom.com/tiktok/callback           │ │
│ │   - Add webhook endpoints if needed     │ │
│ │   - Set up test users                   │ │
│ │ 2. Create Base Components (Day 1)       │ │
│ │   - Settings page structure             │ │
│ │   - TikTok types and interfaces         │ │
│ │   - API client setup                    │ │
│ │   - Empty connection component          │ │
│ │ 3. Implement OAuth Flow (Day 1-2)       │ │
│ │   - Auth URL generation                 │ │
│ │   - Popup window handler                │ │
│ │   - Callback page                       │ │
│ │   - Message passing between windows     │ │
│ │   - Error handling                      │ │
│ │ 4. Build Connection UI (Day 2)          │ │
│ │   - Account cards                       │ │
│ │   - Multiple account support            │ │
│ │   - Disconnect functionality            │ │
│ │   - Loading states                      │ │
│ │   - Error states                        │ │
│ │ 5. Testing & Polish (Day 3)             │ │
│ │   - End-to-end OAuth testing            │ │
│ │   - Error scenario testing              │ │
│ │   - UI polish and animations            │ │
│ │   - Accessibility testing               │ │
│ │                                         │ │
│ │ 11. Technical Considerations            │ │
│ │                                         │ │
│ │ State Management:                       │ │
│ │                                         │ │
│ │ - Use TanStack Query for server state   │ │
│ │ (account list)                          │ │
│ │ - Local state for UI interactions       │ │
│ │ (loading, modals)                       │ │
│ │ - Optimistic updates for disconnect     │ │
│ │ actions                                 │ │
│ │                                         │ │
│ │ Security:                               │ │
│ │                                         │ │
│ │ - CSRF token validation (handled by     │ │
│ │ backend)                                │ │
│ │ - Secure popup communication            │ │
│ │ - No client-side token storage          │ │
│ │                                         │ │
│ │ Performance:                            │ │
│ │                                         │ │
│ │ - Lazy load TikTok components           │ │
│ │ - Debounce account refresh              │ │
│ │ - Cache account data appropriately      │ │
│ │                                         │ │
│ │ 12. Future Enhancements                 │ │
│ │                                         │ │
│ │ - Batch content posting                 │ │
│ │ - Analytics integration                 │ │
│ │ - Automated posting schedules           │ │
│ │ - Multi-account content management      │ │
│ │ - TikTok Shop integration (when         │ │
│ │ available)                              │ │

### Phase 2 Completion Summary

#### ✅ Completed Files (July 31, 2025):

**Frontend Implementation:**
1. `frontend/types/tiktok.ts` - Complete TypeScript interfaces
2. `frontend/lib/tiktok-client.ts` - API client wrapper
3. `frontend/lib/tiktok-oauth.ts` - OAuth popup handler
4. `frontend/app/tiktok/callback/page.tsx` - OAuth callback page
5. `frontend/app/(auth)/instances/[id]/settings/page.tsx` - Settings page (server component)
6. `frontend/app/(auth)/instances/[id]/settings/page-client.tsx` - Settings page (client component)
7. `frontend/components/instances/settings/tiktok-connection.tsx` - TikTok connection component
8. `frontend/components/ui/tabs.tsx` - Tabs component for settings page
9. Updated `frontend/components/instances/instance-card.tsx` - Added settings link

**Key Features Implemented:**
- ✅ Multiple TikTok accounts per instance support
- ✅ Account naming for easy identification
- ✅ OAuth popup flow with secure message passing
- ✅ Token status indicators (active/expiring/expired)
- ✅ Auto-refresh of expired tokens
- ✅ Disconnect functionality
- ✅ Sandbox mode visual indicators
- ✅ Empty state design
- ✅ Responsive UI design
- ✅ Build and lint passing

**Documentation Updated:**
- ✅ backend.md - Added TikTok integration details
- ✅ frontend.md - Added Phase 2 implementation details

### 3. Test Sandbox OAuth Flow End-to-End (NEXT PRIORITY)
#### Prerequisites:
- Configure TikTok sandbox app with redirect URI: `https://skipper-ecom.com/tiktok/callback` (or `http://localhost:3001/tiktok/callback` for local testing)
- Add test users to sandbox app
- Set environment variables in backend `.env`:
  ```
  TIKTOK_CLIENT_KEY=your_sandbox_client_key
  TIKTOK_CLIENT_SECRET=your_sandbox_client_secret
  TIKTOK_REDIRECT_URI=http://localhost:3001/tiktok/callback
  TIKTOK_SANDBOX_MODE=true
  ```
- Set environment variables in frontend `.env.local`:
  ```
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  NEXT_PUBLIC_TIKTOK_SANDBOX_MODE=true
  ```

#### Testing Steps:
1. Start backend server with TikTok credentials configured
2. Start frontend dev server (`npm run dev`)
3. Navigate to an instance settings page
4. Click "Connect TikTok Account"
5. Complete OAuth flow with test account
6. Verify account appears in connected accounts list
7. Test token refresh (if possible)
8. Test disconnect functionality

### 4. Content Posting Interface (Optional Enhancement)
- Create posting modal or dedicated page
- Video URL/file upload input
- Caption editor with character count
- Privacy settings selector
- Account selector for multi-account instances
- Post status tracking

### 5. Demo Video Recording (Phase 4)
- Set up TikTok sandbox app first
- Follow the script in Phase 4 of original plan
- Show complete flow from connection to posting
- Highlight multi-account support