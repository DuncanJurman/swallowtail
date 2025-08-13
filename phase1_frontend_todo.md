# Phase 1: Frontend Task Detail Page - Implementation Todo List

## Prerequisites
- [ ] Navigate to frontend directory: `cd /Users/duncanjurman/Desktop/Swallowtail/frontend`
- [ ] Ensure all dependencies are installed: `npm install`
- [ ] Run initial build to verify baseline: `npm run build`
- [ ] Run initial lint to ensure clean start: `npm run lint`

## 1. Create Task Detail Page Structure (Section 1.1)

### 1.1.1 Create Route Structure
- [ ] Create directory: `app/(auth)/instances/[id]/tasks/[taskId]/`
- [ ] Create server component: `page.tsx`
- [ ] Create client component: `page-client.tsx`
- [ ] Run `npm run build` to verify routing works
- [ ] Run `npm run lint` to check for issues

### 1.1.2 Create Type Definitions
- [ ] Create file: `types/task-detail.ts`
- [ ] Define `TaskDetail` interface with all fields
- [ ] Define `TaskPlanningStep` interface for mock planning data
- [ ] Define `ExecutionLog` interface for logs section
- [ ] Define `AttachedMedia` interface for reference images
- [ ] Run `npm run build` to verify type safety
- [ ] Run `npm run lint`

### 1.1.3 Create Mock Data Generator
- [ ] Create file: `lib/mock-data/task-detail-mock.ts`
- [ ] Create function to generate mock planning steps
- [ ] Create function to generate mock execution logs
- [ ] Create function to generate sample attached media
- [ ] Export complete mock task detail object
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

## 2. Implement Section 1: Task Planning (Placeholder)

### 2.1.1 Create Planning Section Component
- [ ] Create file: `components/tasks/task-planning-section.tsx`
- [ ] Import Card, Badge, and Checkbox from UI components
- [ ] Create todo-style checklist component
- [ ] Add status indicators (pending/in-progress/completed)
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 2.1.2 Add Attached Media Display
- [ ] Create file: `components/tasks/attached-media-gallery.tsx`
- [ ] Implement image grid layout
- [ ] Add image modal/lightbox for full view
- [ ] Handle empty state when no images attached
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 2.1.3 Integrate Planning Section into Page
- [ ] Import planning section into `page-client.tsx`
- [ ] Pass mock planning data as props
- [ ] Style with proper spacing and layout
- [ ] Test expandable/collapsible functionality
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

## 3. Implement Section 2: Agent Execution Logs (Placeholder)

### 3.1.1 Create Logs Section Component
- [ ] Create file: `components/tasks/execution-logs-section.tsx`
- [ ] Import Collapsible from Radix UI
- [ ] Create log entry component with timestamp
- [ ] Add agent identification badges
- [ ] Implement color coding for log levels
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 3.1.2 Add Log Filtering and Search
- [ ] Add filter dropdown for log levels
- [ ] Add filter by agent type
- [ ] Add search input for log content
- [ ] Implement expand/collapse all functionality
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 3.1.3 Integrate Logs Section
- [ ] Import logs section into `page-client.tsx`
- [ ] Pass mock execution logs as props
- [ ] Add loading skeleton for future real data
- [ ] Test collapsible interactions
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

## 4. Implement Section 3: Final Output & TikTok Posting

### 4.1.1 Create Output Display Component
- [ ] Create file: `components/tasks/task-output-section.tsx`
- [ ] Add video player component (HTML5)
- [ ] Add thumbnail display
- [ ] Display video metadata (duration, resolution)
- [ ] Show suggested caption
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.2 Add TikTok Posting Checkbox
- [ ] Add conditional rendering for video output only
- [ ] Create checkbox with label "Post to TikTok"
- [ ] Add state management for checkbox
- [ ] Add info tooltip about sandbox mode
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.3 Create TikTok Posting Dialog (Section 1.2)
- [ ] Create file: `components/tasks/tiktok-post-dialog.tsx`
- [ ] Import Dialog from Radix UI
- [ ] Add video preview in dialog
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.4 Add Caption Editor
- [ ] Add textarea for caption editing
- [ ] Pre-fill with suggested caption
- [ ] Add character counter (2200 max)
- [ ] Add hashtag highlighting
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.5 Add Privacy Settings
- [ ] Create Select component for privacy level
- [ ] Add options: PUBLIC_TO_EVERYONE, MUTUAL_FOLLOW_FRIENDS, SELF_ONLY
- [ ] Default to SELF_ONLY for sandbox
- [ ] Add sandbox mode warning badge
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.6 Add Interaction Settings
- [ ] Add Switch/Checkbox for "Disable Duet"
- [ ] Add Switch/Checkbox for "Disable Stitch"
- [ ] Add Switch/Checkbox for "Disable Comments"
- [ ] Group in collapsible "Advanced Settings"
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.7 Add Account Selector
- [ ] Create dropdown for multiple TikTok accounts
- [ ] Show account avatar and username
- [ ] Handle single account case (no dropdown)
- [ ] Add "Connect Account" option if none connected
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.8 Add Schedule Picker (UI Only)
- [ ] Import Calendar and TimePicker components
- [ ] Create date/time selector
- [ ] Add "Post Now" vs "Schedule" toggle
- [ ] Add note that scheduling is coming soon
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 4.1.9 Add Dialog Actions
- [ ] Add Cancel button
- [ ] Add "Post to TikTok" button
- [ ] Add loading state for button
- [ ] Add form validation
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

## 5. Create API Hooks and Integration

### 5.1.1 Create Task Detail Hook
- [ ] Create file: `hooks/use-task-detail.ts`
- [ ] Create `useTaskDetail(taskId)` hook
- [ ] Use TanStack Query for data fetching
- [ ] Add loading and error states
- [ ] Return mock data for now
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 5.1.2 Create TikTok Posting Hook
- [ ] Create file: `hooks/use-tiktok-post.ts`
- [ ] Create `usePostToTikTok()` mutation hook
- [ ] Add optimistic updates
- [ ] Add success/error callbacks
- [ ] Mock API call for now
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 5.1.3 Create Post Status Hook
- [ ] Create file: `hooks/use-tiktok-status.ts`
- [ ] Create `useTikTokPostStatus(taskId)` hook
- [ ] Implement polling with 5-second interval
- [ ] Add stop polling on success/failure
- [ ] Mock status progression for now
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

## 6. Integrate Everything into Main Page

### 6.1.1 Wire Up Page Components
- [ ] Update `page.tsx` to fetch initial data
- [ ] Pass data to `page-client.tsx`
- [ ] Arrange three sections in proper layout
- [ ] Add responsive design for mobile
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 6.1.2 Add State Management
- [ ] Connect checkbox to dialog open state
- [ ] Wire up posting mutation
- [ ] Handle success/error states
- [ ] Add toast notifications
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 6.1.3 Add Loading States
- [ ] Add skeleton loaders for each section
- [ ] Add suspense boundaries
- [ ] Handle error boundaries
- [ ] Add retry functionality
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

## 7. Polish and Testing

### 7.1.1 Visual Polish
- [ ] Ensure consistent spacing with design system
- [ ] Add hover states and transitions
- [ ] Verify dark mode compatibility
- [ ] Add focus states for accessibility
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 7.1.2 Error Handling
- [ ] Add error states for each section
- [ ] Create fallback UI for failures
- [ ] Add user-friendly error messages
- [ ] Test network error scenarios
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 7.1.3 Performance Optimization
- [ ] Add lazy loading for heavy components
- [ ] Optimize image loading
- [ ] Minimize re-renders
- [ ] Check bundle size impact
- [ ] Run `npm run build`
- [ ] Run `npm run lint`


## 8. Documentation and Cleanup

### 8.1.1 Add Code Documentation
- [ ] Add JSDoc comments to components
- [ ] Document prop types
- [ ] Add usage examples
- [ ] Create README for task components
- [ ] Run `npm run build`
- [ ] Run `npm run lint`

### 8.1.2 Update Frontend.md
- [ ] Document new task detail page
- [ ] Add component hierarchy
- [ ] List new dependencies added
- [ ] Document mock data structure
- [ ] Run final `npm run build`
- [ ] Run final `npm run lint`

## 9. Final Verification

### 9.1.1 Full Testing Suite
- [ ] Test complete user flow
- [ ] Test all interactive elements
- [ ] Verify all sections render correctly
- [ ] Test with different task states
- [ ] Test responsive design on multiple devices

### 9.1.2 Build Verification
- [ ] Run `npm run build` - must pass
- [ ] Run `npm run lint` - must have zero errors
- [ ] Run `npm run type-check` if available
- [ ] Check console for any warnings
- [ ] Verify no regression in existing features

## Success Criteria Checklist
- [ ] Task detail page loads without errors
- [ ] All three sections display correctly
- [ ] Mock data appears in planning and logs sections
- [ ] Video player works with sample video
- [ ] TikTok posting dialog opens when checkbox clicked
- [ ] All form controls in dialog are functional
- [ ] No build errors
- [ ] No lint errors
- [ ] Page is responsive
- [ ] Page is accessible

**Total Estimated Time**: 11-16 hours

## Notes
- Run build and lint after EVERY component creation
- Commit after each major section completion
- Test in both development and production builds
- Keep mock data realistic to actual task structure
- Ensure all placeholder content clearly indicates "coming soon" features