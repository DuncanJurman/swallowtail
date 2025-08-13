# Swallow

Deployed at: skipper-ecom.com
## 🎯 Overview
Swallowtail is an AI-powered business management platform that enables users to manage multiple businesses (instances) through natural language commands. The frontend is built with Next.js 15, TypeScript, and Tailwind CSS v4, providing a modern, responsive interface for interacting with AI agents.

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 15.4.3 (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS v3.4.0 (with custom theme configuration)
- **UI Components**: Radix UI (accessibility-first primitives)
- **State Management**: 
  - Zustand (global client state)
  - TanStack Query (server state & caching)
- **Forms**: React Hook Form + Zod validation
- **Real-time**: Socket.io Client (prepared for WebSocket integration)
- **Animations**: Framer Motion
- **Icons**: Lucide React

### Directory Structure
```
frontend/
├── app/                        # Next.js App Router
│   ├── (auth)/                # Protected routes group
│   │   ├── dashboard/         # Main dashboard page
│   │   │   └── page.tsx      # Dashboard with stats & activity
│   │   ├── instances/         # Instance management
│   │   │   ├── page.tsx      # List all instances (with mock data)
│   │   │   ├── [id]/         # Dynamic instance routes
│   │   │   │   ├── tasks/    # Task management
│   │   │   │   │   ├── page.tsx         # Server component
│   │   │   │   │   └── page-client.tsx  # Client component
│   │   │   │   └── settings/ # Instance settings
│   │   │   │       ├── page.tsx         # Server component
│   │   │   │       └── page-client.tsx  # Client component with tabs
│   │   │   └── new/          # Create new instance (pending)
│   │   └── layout.tsx        # Auth layout with sidebar/topbar
│   ├── tiktok/               # TikTok OAuth flow
│   │   └── callback/         # OAuth callback handler
│   │       └── page.tsx      # Handles OAuth response
│   ├── globals.css           # Tailwind CSS imports & theme
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Landing page
│
├── components/
│   ├── ui/                   # Base UI components
│   │   ├── button.tsx       # Button with variants
│   │   ├── card.tsx         # Card container system
│   │   ├── input.tsx        # Form input
│   │   ├── textarea.tsx     # Multi-line input
│   │   ├── badge.tsx        # Status indicators
│   │   ├── dialog.tsx       # Modal dialogs
│   │   └── tabs.tsx         # Tabbed interface (Radix UI)
│   ├── shared/              # Shared layout components
│   │   ├── sidebar.tsx      # Collapsible navigation
│   │   └── topbar.tsx       # Search & user menu
│   ├── instances/           # Instance-specific components
│   │   ├── instance-card.tsx # Display instance info
│   │   └── settings/        # Settings components
│   │       └── tiktok-connection.tsx # TikTok OAuth management
│   └── tasks/               # Task management components
│       └── task-input.tsx   # Natural language input
│
├── lib/                     # Utilities & configurations
│   ├── api-client.ts       # Axios instance setup
│   ├── query-client.tsx    # TanStack Query provider
│   ├── utils.ts            # cn() utility for classNames
│   ├── tailwind-colors.ts  # Color mapping utilities
│   ├── tiktok-client.ts    # TikTok API client wrapper
│   └── tiktok-oauth.ts     # OAuth popup handler
│
├── types/                   # TypeScript definitions
│   ├── instance.ts         # Instance interfaces  
│   ├── task.ts             # Task interfaces
│   └── tiktok.ts           # TikTok OAuth & API types
│
└── public/                  # Static assets
```

## 🎨 Design System

### Tailwind CSS v3 Configuration
We use Tailwind CSS v3.4.0 with a custom theme configuration:

```javascript
/* tailwind.config.js */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "hsl(201 96% 32%)",
          foreground: "hsl(0 0% 100%)",
        },
        // ... more custom colors
      }
    }
  }
}
```

**Color Usage**: Colors are used with standard Tailwind classes:
- ✅ `bg-primary`
- ✅ `text-muted-foreground`
- ✅ `border-input`

### Component Architecture
We follow an atomic design approach:

1. **UI Components** (`/components/ui/`)
   - Pure, reusable components
   - No business logic
   - Fully typed props
   - Accessibility built-in

2. **Feature Components** (`/components/[feature]/`)
   - Domain-specific components
   - Compose UI components
   - Handle feature logic

3. **Layout Components** (`/components/shared/`)
   - Navigation elements
   - Page structure
   - Responsive behavior

## 📱 Key Features Implemented

### 1. Landing Page (`/`)
- Hero section with call-to-action
- Feature cards showcasing capabilities
- Responsive grid layout
- Navigation to dashboard

### 2. Dashboard (`/dashboard`)
- **Stats Grid**: 
  - Total Instances
  - Active Tasks
  - Completed Today
  - Success Rate
- **Activity Feed**: Real-time task updates
- **Quick Actions**: Links to common tasks

### 3. Instance Management (`/instances`)
- **Instance Cards**: Visual representation of each business
  - Name and description
  - Type badge (Ecommerce/Social Media)
  - Platform connections
  - Task statistics
  - Quick action buttons
- **Grid Layout**: Responsive card grid
- **Instance Creation**: Button to add new instances (pending implementation)

### 4. Task Management (`/instances/[id]/tasks`)
- **Natural Language Input**: 
  - Large textarea for task description
  - Priority selector (Urgent/Normal/Low)
  - Submit button
- **Task Queue Display**:
  - Real-time task list
  - Status indicators (pending/in-progress/completed)
  - Agent assignment
  - Timestamps
  - Progress tracking
- **Filtering**: Toggle between all/active/completed tasks

### 5. Navigation System
- **Sidebar** (`/components/shared/sidebar.tsx`):
  - Collapsible design
  - Icon + text navigation
  - Active route highlighting
  - Mobile hamburger menu
  - Smooth transitions
- **TopBar** (`/components/shared/topbar.tsx`):
  - Global search (UI only)
  - User menu dropdown
  - Responsive design

## 🔌 API Integration

### Setup
```typescript
// lib/api-client.ts
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
  headers: { 'Content-Type': 'application/json' }
});
```

### Query Client
```typescript
// lib/query-client.tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  }
});
```

### API Endpoints (Prepared)
- `GET /instances` - List all instances
- `POST /instances` - Create new instance
- `GET /instances/{id}` - Get instance details
- `POST /instances/{id}/tasks` - Create task
- `GET /instances/{id}/tasks` - List tasks

## 🚀 Development Workflow

### Prerequisites
- Node.js 22.x
- npm 11.x

### Setup
```bash
# Install dependencies
npm install

# Start development server (runs on port 3001)
npm run dev

# Build for production (includes ESLint)
npm run build

# Run production server
npm start

# Run ESLint separately
npm run lint
```

### Environment Variables
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

For production deployment:
```env
NEXT_PUBLIC_API_URL=<your-backend-api-url>
NEXT_PUBLIC_WS_URL=<your-websocket-url>
NEXT_PUBLIC_APP_URL=<your-frontend-url>
NEXT_PUBLIC_TIKTOK_SANDBOX_MODE=true
```

### ESLint Configuration
The project uses ESLint 9 with a flat config (`eslint.config.mjs`):
- Extends `next/core-web-vitals` for Next.js best practices
- Uses `@eslint/eslintrc` FlatCompat for compatibility
- Fully integrated with the build process
- No false positive JSX parsing errors

### Current Routes
- `/` - Public landing page
- `/dashboard` - Protected dashboard (auth group)
- `/instances` - Instance listing (auth group)
- `/instances/[id]/tasks` - Task management (auth group)
- `/instances/new` - Instance creation wizard (pending)

## 🧩 Component Examples

### Using UI Components
```tsx
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

<Card>
  <CardHeader>
    <CardTitle>Example Card</CardTitle>
  </CardHeader>
  <CardContent>
    <Button variant="primary" size="lg">
      Click Me
    </Button>
  </CardContent>
</Card>
```

### Creating Protected Pages
```tsx
// Place in app/(auth)/ directory
export default function ProtectedPage() {
  return (
    <div className="container mx-auto p-6">
      {/* Page content */}
    </div>
  );
}
```

## 🔄 State Management

### Global State (Zustand)
```typescript
// stores/instance-store.ts (example)
interface InstanceStore {
  selectedInstance: Instance | null;
  setSelectedInstance: (instance: Instance) => void;
}
```

### Server State (TanStack Query)
```typescript
// Example query
const { data, isLoading } = useQuery({
  queryKey: ['instances'],
  queryFn: () => apiClient.get('/instances').then(res => res.data)
});
```

## 📝 Next Steps

### High Priority
- [ ] Instance creation wizard implementation
- [ ] Real API integration (currently using mock data)
- [ ] WebSocket integration for real-time updates
- [ ] Authentication flow with protected routes
- [ ] Error boundaries and loading states

### Medium Priority
- [ ] Agent configuration interface
- [ ] Analytics dashboard
- [ ] Dark mode toggle
- [ ] Task templates
- [ ] Bulk operations


## 🐛 Known Issues
1. WebSocket connection not yet implemented
2. Mock data is hardcoded in components
3. No authentication system
4. Form validation needs enhancement
5. No error handling for API calls

## 📋 Recent Updates

### August 13, 2025 - TikTok Content Posting Integration (Phase 1)
- **Task Detail Page Enhancement** (`/app/(auth)/instances/[id]/tasks/[taskId]/`):
  - Implemented three-section layout using Tabs component
  - **Planning Section**: Displays todo-style execution plan with checkboxes and reference images
  - **Agent Execution Logs Section**: Shows agent activity with timestamps and badges (placeholder data)
  - **Final Output Section**: Video player with metadata, captions, and TikTok posting checkbox
- **TikTok Posting Dialog** (`/components/tasks/tiktok-post-dialog.tsx`):
  - Full-featured posting interface with video preview
  - Editable caption with character counter (2200 max)
  - Privacy level selector (Sandbox mode defaults to SELF_ONLY)
  - Interaction settings (disable duet/stitch/comments)
  - Account selector for multi-account support
  - Sandbox mode warning banner
- **API Hooks** (`/lib/hooks/use-tiktok-post.ts`):
  - `usePostToTikTok`: Mutation hook for posting videos
  - `useTikTokPostStatus`: Query hook for checking post status with auto-polling
  - `useTaskDetail`: Query hook for fetching task details with planning and logs
  - `useTikTokAccounts`: Query hook for fetching instance TikTok accounts
- **New UI Components**:
  - Label component (`/components/ui/label.tsx`) using Radix UI
  - Select component (`/components/ui/select.tsx`) with dropdown functionality
  - Toast hook (`/components/ui/use-toast.tsx`) for notifications
- **Type Safety**: Complete TypeScript interfaces for all TikTok posting data structures

### August 7, 2025 - TikTok OAuth Dialog Fix
- **Fixed Radix UI Dialog Not Closing Issue**:
  - Problem: Dialog component wasn't closing after OAuth success despite state being updated to `false`
  - Root cause: State updates from OAuth message event listeners weren't triggering proper React re-renders
  - Solution: Created centralized `closeDialog` function that:
    - Uses `setTimeout(0)` to ensure state updates happen in next tick
    - Increments a `dialogKey` to force Dialog component to unmount/remount
    - Ensures all dialog state is properly cleaned up
  - Applied fix to all dialog close scenarios (success, error, cancel)
  - This resolved the issue where the TikTok OAuth dialog would remain visible after successful authentication

### July 31, 2025 - TikTok OAuth Integration (Phase 2)
- **OAuth Flow Implementation**:
  - Created TikTok API client (`/lib/tiktok-client.ts`) with account management
  - Implemented OAuth popup handler (`/lib/tiktok-oauth.ts`) with secure message passing
  - Added OAuth callback page (`/app/tiktok/callback/page.tsx`) with auto-close functionality
- **Instance Settings Page**:
  - Created settings page structure with tabbed interface
  - Added platform connections tab for social media integrations
  - Implemented responsive design with mobile support
- **TikTok Connection Component** (`/components/instances/settings/tiktok-connection.tsx`):
  - Support for multiple TikTok accounts per instance
  - Account naming feature for easy identification
  - Real-time token status indicators (active/expiring/expired)
  - Account cards with profile info and quick actions
  - Empty state design for first-time connections
  - Sandbox mode indicators and warnings
- **UI Components Added**:
  - Tabs component (`/components/ui/tabs.tsx`) using Radix UI
  - Custom TikTok icon component
  - Enhanced dialog for account naming
- **Type Safety**:
  - Complete TypeScript interfaces for TikTok data (`/types/tiktok.ts`)
  - Enhanced account types with computed properties (token expiry status)

### July 29, 2025 - TikTok API Integration Preparation
- Added Privacy Policy page (`/privacy`) with TikTok-specific data handling disclosures
- Added Terms of Service page (`/terms`) with comprehensive service terms
- Created Footer component with legal links visible on all pages
- Updated sidebar navigation to include Privacy Policy and Terms links
- Enhanced landing page with multi-account management features and instance architecture explanation
- Added app icon placeholder (`/public/swallowtail-icon.svg`) for TikTok app submissions
- Ensured all legal pages are publicly accessible without authentication
- All pages now include proper footer with legal links for TikTok compliance

### Previous Updates (July 29, 2025)

### Tailwind CSS Migration
- Downgraded from Tailwind CSS v4 beta to v3.4.0 for stability
- Converted `@theme` CSS configuration to `tailwind.config.js`
- Updated all component classes from v4 syntax (e.g., `bg-[--color-primary]`) to v3 syntax (e.g., `bg-primary`)
- Added necessary v3 plugins: `@tailwindcss/forms` and `@tailwindcss/typography`

### ESLint Configuration
- Implemented ESLint 9 flat config with Next.js 15 compatibility
- Removed `ignoreDuringBuilds` - ESLint now runs during production builds
- Fixed false positive JSX parsing errors using `@eslint/eslintrc` FlatCompat
- Added `@eslint/compat` and `typescript-eslint` for better TypeScript support

### Build System
- All builds now complete successfully with linting enabled
- Dev server runs on port 3001 as configured
- All pages accessible and returning HTTP 200 status

## 💡 Development Tips

1. **Type Safety**: Always define interfaces for props and API responses
2. **Component Reuse**: Check `/components/ui` before creating new components
3. **Styling**: Use Tailwind utilities with CSS variable syntax
4. **State**: Prefer server state over client state when possible
5. **Performance**: Use React.memo for expensive components
6. **Accessibility**: Test with keyboard navigation

## 📚 Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS v3](https://tailwindcss.com)
- [Radix UI](https://www.radix-ui.com)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://zustand-demo.pmnd.rs)

---

Last Updated: August 7, 2025
Next.js Version: 15.4.3
Tailwind CSS Version: 3.4.0
ESLint: Version 9 with flat config, fully integrated with builds