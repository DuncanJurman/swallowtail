# Swallowtail Frontend Architecture

## Overview
The Swallowtail frontend is a Next.js 15 application using the App Router, TypeScript, Tailwind CSS, and Shadcn/ui components. It provides a dashboard interface for monitoring and controlling the autonomous e-commerce agents.

## Directory Structure
```
frontend/
├── app/                 # Next.js app router pages
├── components/          # React components
├── hooks/              # Custom React hooks  
├── lib/                # Utilities and configurations
├── providers/          # React context providers
├── services/           # API service layer
├── types/              # TypeScript type definitions
└── public/             # Static assets
```

## Implemented Files

### Core Configuration

#### `package.json`
- **Dependencies**: Next.js 15, React 19, TypeScript, Tailwind CSS, Shadcn/ui components, React Query, Socket.io-client, Axios
- **Scripts**: dev, build, start, lint

#### `tsconfig.json`
- TypeScript configuration with strict mode
- Path aliases configured (@/* maps to root)
- Next.js plugin integration

#### `tailwind.config.js`
- Content paths configured for app/, components/
- Default Tailwind configuration

#### `.env.local.example`
- Template for environment variables
- API URL and WebSocket URL configuration

### App Router Structure

#### `app/layout.tsx`
- Root layout with providers
- Includes QueryProvider, WebSocketProvider, and Toaster
- Inter font configuration
- Global metadata

#### `app/globals.css`
- Tailwind CSS imports
- CSS variables for theming (light/dark mode ready)
- Base styles for consistent UI

#### `app/page.tsx`
- Homepage with dashboard layout
- Displays WorkflowStatus, QuickActions, and RecentActivity components

#### `app/checkpoints/page.tsx`
- Checkpoints page for reviewing pending approvals
- Lists all pending human checkpoints

### Providers

#### `providers/query-provider.tsx`
- React Query setup with QueryClient
- Default stale time of 1 minute
- Development tools included

#### `providers/websocket-provider.tsx`
- Socket.io client integration
- Connection management with reconnection logic
- Subscribe/unsubscribe methods for event handling
- Context for accessing socket throughout app

### Services

#### `lib/api-client.ts`
- Axios instance configuration
- Base URL from environment variables
- Request/response interceptors for auth (future)

#### `services/api.ts`
- API service layer with typed methods
- **Workflow API**: start(), getStatus()
- **Checkpoints API**: list(), get(), resolve()
- **Health API**: check()

### Type Definitions

#### `types/index.ts`
- TypeScript interfaces matching backend models
- Product types: ProductIdea, SupplierInfo, ProductListing
- Checkpoint types: HumanCheckpoint, CheckpointType, CheckpointStatus
- Workflow types: WorkflowStatus, AgentResult, WorkflowResponse
- Enums for type safety

### Components

#### Layout Components
- **`components/layout/dashboard-layout.tsx`**: Main layout wrapper with sidebar and header
- **`components/layout/sidebar.tsx`**: Navigation sidebar with links to all pages
- **`components/layout/header.tsx`**: Top header with WebSocket connection status

#### Dashboard Components
- **`components/workflow-status.tsx`**: Displays current workflow status with auto-refresh
- **`components/quick-actions.tsx`**: Button to start new product research workflow
- **`components/recent-activity.tsx`**: Real-time activity feed via WebSocket

#### Checkpoint Components
- **`components/checkpoints/checkpoints-list.tsx`**: Lists all pending checkpoints
- **`components/checkpoints/checkpoint-card.tsx`**: Individual checkpoint with approve/reject actions
- **`components/checkpoints/product-selection-view.tsx`**: Product comparison cards for selection

### UI Components (Shadcn/ui)
- **Button**: Primary action component
- **Card**: Container component for content sections
- **Badge**: Status indicators
- **Skeleton**: Loading states
- **Toast**: Notifications
- **Textarea**: Multi-line input
- **ScrollArea**: Scrollable containers
- **Separator**: Visual dividers

### Utilities

#### `lib/utils.ts`
- `cn()` function for className merging
- Combines clsx and tailwind-merge

## Key Features

### 1. Real-time Updates
- WebSocket integration for live agent status
- Auto-refreshing queries for workflow status
- Activity feed showing agent actions

### 2. Human Checkpoint System
- Visual checkpoint cards
- Product selection interface
- Approve/reject with notes
- Automatic workflow continuation

### 3. State Management
- React Query for server state
- Local state with React hooks
- WebSocket context for real-time events

### 4. Type Safety
- Full TypeScript coverage
- Types synchronized with backend models
- Enum usage for constants

### 5. Responsive Design
- Mobile-friendly layouts
- Grid system for different screen sizes
- Tailwind CSS utilities

## API Integration Pattern

```typescript
// Query example
const { data, isLoading } = useQuery({
  queryKey: ['workflow-status'],
  queryFn: workflowApi.getStatus,
  refetchInterval: 5000,
})

// Mutation example
const mutation = useMutation({
  mutationFn: () => workflowApi.start(),
  onSuccess: () => {
    queryClient.invalidateQueries(['workflow-status'])
  },
})
```

## WebSocket Events

Expected events from backend:
- `activity`: General activity updates
- `agent:status`: Agent state changes
- `workflow:update`: Workflow progress updates

## Next Steps

1. **Additional Pages**:
   - Products page for inventory management
   - Agents page for detailed monitoring
   - Analytics dashboard
   - Settings/configuration page

2. **Features**:
   - Authentication system
   - Dark mode toggle
   - Export functionality
   - Advanced filtering/search

3. **Improvements**:
   - Error boundaries
   - Optimistic updates
   - Offline support
   - Performance optimizations