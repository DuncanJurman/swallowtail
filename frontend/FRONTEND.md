# Swallowtail Frontend Implementation Guide

## 🎯 Overview
Swallowtail is an AI-powered business management platform that enables users to manage multiple businesses (instances) through natural language commands. The frontend is built with Next.js 15, TypeScript, and Tailwind CSS v4, providing a modern, responsive interface for interacting with AI agents.

## 🏗️ Architecture

### Tech Stack
- **Framework**: Next.js 15.4.3 (App Router)
- **Language**: TypeScript 5.x (strict mode)
- **Styling**: Tailwind CSS v4 (CSS variables approach)
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
│   │   │   ├── page.tsx      # List all instances
│   │   │   ├── [id]/         # Dynamic instance routes
│   │   │   │   └── tasks/    # Task management
│   │   │   │       ├── page.tsx         # Server component
│   │   │   │       └── page-client.tsx  # Client component
│   │   │   └── new/          # Create new instance (pending)
│   │   └── layout.tsx        # Auth layout with sidebar/topbar
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
│   │   └── dialog.tsx       # Modal dialogs
│   ├── shared/              # Shared layout components
│   │   ├── sidebar.tsx      # Collapsible navigation
│   │   └── topbar.tsx       # Search & user menu
│   ├── instances/           # Instance-specific components
│   │   └── instance-card.tsx # Display instance info
│   └── tasks/               # Task management components
│       └── task-input.tsx   # Natural language input
│
├── lib/                     # Utilities & configurations
│   ├── api-client.ts       # Axios instance setup
│   ├── query-client.tsx    # TanStack Query provider
│   ├── utils.ts            # cn() utility for classNames
│   └── tailwind-colors.ts  # Color mapping utilities
│
├── types/                   # TypeScript definitions
│   ├── instance.ts         # Instance interfaces
│   └── task.ts             # Task interfaces
│
└── public/                  # Static assets
```

## 🎨 Design System

### Tailwind CSS v4 Configuration
We use Tailwind CSS v4 with the new CSS variables approach:

```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  /* Color System */
  --color-background: hsl(0 0% 100%);
  --color-foreground: hsl(224 71.4% 4.1%);
  --color-primary: hsl(201 96% 32%);
  --color-secondary: hsl(220 14.3% 95.9%);
  /* ... more colors */
}
```

**Important**: All colors use CSS variable syntax:
- ❌ Old: `bg-primary`
- ✅ New: `bg-[--color-primary]`

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

# Start development server
npm run dev

# Build for production
npm run build

# Run production server
npm start
```

### Environment Variables
Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

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

## 💡 Development Tips

1. **Type Safety**: Always define interfaces for props and API responses
2. **Component Reuse**: Check `/components/ui` before creating new components
3. **Styling**: Use Tailwind utilities with CSS variable syntax
4. **State**: Prefer server state over client state when possible
5. **Performance**: Use React.memo for expensive components
6. **Accessibility**: Test with keyboard navigation

## 📚 Resources
- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS v4](https://tailwindcss.com)
- [Radix UI](https://www.radix-ui.com)
- [TanStack Query](https://tanstack.com/query)
- [Zustand](https://zustand-demo.pmnd.rs)

---

Last Updated: July 24, 2025
Next.js Version: 15.4.3
Tailwind CSS Version: 4.x