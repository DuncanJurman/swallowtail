# Swallowtail Frontend Architecture Plan

## Overview
A modern, responsive web application that enables users to manage multiple AI-powered business instances through an intuitive, visual-first interface.

## Tech Stack Recommendations

### Core Framework
- **Next.js 14+** with App Router for server components and optimal performance
- **TypeScript** for type safety and better developer experience
- **React 18+** for UI components

### UI & Styling
- **Tailwind CSS** for utility-first styling
- **Radix UI** for accessible, unstyled component primitives
- **Framer Motion** for smooth animations and transitions
- **Lucide React** for consistent iconography

### State Management
- **Zustand** for global state (lightweight, TypeScript-friendly)
- **TanStack Query** for server state and caching
- **React Hook Form** with Zod for form handling and validation

### Real-time & Communication
- **WebSocket** (native or Socket.io) for real-time task updates
- **Server-Sent Events** as fallback for one-way updates

### Additional Libraries
- **Recharts** for analytics dashboards
- **React Dropzone** for file uploads
- **DnD Kit** for drag-and-drop interfaces
- **Tiptap** for rich text editing (task descriptions)

## Directory Structure

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/              # Auth-required layout
│   │   │   ├── dashboard/       # Main dashboard
│   │   │   ├── instances/       
│   │   │   │   ├── [id]/        # Instance detail pages
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── tasks/
│   │   │   │   │   ├── agents/
│   │   │   │   │   ├── analytics/
│   │   │   │   │   └── settings/
│   │   │   │   └── new/         # Instance creation flow
│   │   │   └── settings/        # Account settings
│   │   ├── (public)/            # Public routes
│   │   │   ├── login/
│   │   │   └── signup/
│   │   └── api/                 # API routes if needed
│   │
│   ├── components/
│   │   ├── ui/                  # Base UI components
│   │   │   ├── button/
│   │   │   ├── card/
│   │   │   ├── dialog/
│   │   │   └── ...
│   │   ├── instances/           # Instance-specific components
│   │   │   ├── InstanceCard/
│   │   │   ├── InstanceGrid/
│   │   │   └── CreateInstanceWizard/
│   │   ├── tasks/               # Task management components
│   │   │   ├── TaskInput/
│   │   │   ├── TaskQueue/
│   │   │   ├── TaskTimeline/
│   │   │   └── TaskResults/
│   │   ├── agents/              # Agent configuration
│   │   │   ├── AgentCustomizer/
│   │   │   ├── AgentPersonality/
│   │   │   └── AgentWorkflow/
│   │   └── shared/              # Shared components
│   │       ├── Navigation/
│   │       ├── Sidebar/
│   │       └── RealTimeIndicator/
│   │
│   ├── hooks/                   # Custom React hooks
│   ├── lib/                     # Utilities and helpers
│   ├── services/                # API service layers
│   ├── stores/                  # Zustand stores
│   ├── types/                   # TypeScript types
│   └── styles/                  # Global styles
```

## Core UI Components & Patterns

### 1. Dashboard Home
- **Instance Grid**: Card-based view of all instances with key metrics
- **Global Activity Feed**: Recent tasks across all instances
- **Quick Actions**: Create instance
- **Performance Overview**: Aggregate analytics

### 2. Instance Management
- **Visual Profile Builder**: 
  - Drag-drop image uploads for brand assets
- **Instance Types Toggle**: Clear differentiation between Ecommerce/Social
- **Platform Connections**: OAuth flow for social media accounts, (giving agents access to such accounts)

### 3. Task Interface
- **Natural Language Input**:
  - Large textarea for user input
  - Task priority and scheduling
- **Execution Visualization**:
  - Real-time progress timeline
  - Agent activity indicators
  - Intermediate results preview
- **Approval Queue**: 
  - Side panel for pending approvals or human aproval checkpoints reached by agents
  - Batch approval actions

### 4. Agent Configuration
- **Customize Agents**: can see all agents in the instance and their base template and can modify template (such as what to focus on, style, tone, etc.) accordingly and save



## Key User Flows

### 1. Instance Creation Flow
```
Landing → Choose Type → Business Profile → Visual Identity → 
Platform Connections → Agent Setup → Review & Launch
```

### 2. Task Submission Flow
```
Select Instance → Type Task → Manager Agents Suggests Breakdown → 
User Confirms → Real-time Execution → Review Results → 
Approve/Reject Actions at humman approval checkpounts
```

### 3. Daily Management Flow
```
Dashboard Overview → Check Notifications → Review Task Queue → 
Handle Approvals → Monitor Performance → Adjust Settings
```

## Design Principles

### Visual Hierarchy
- **Card-based layouts** for clear content separation
- **Progressive disclosure** for complex features
- **Consistent spacing** using 8px grid system

### Interaction Patterns
- **Optimistic updates** for immediate feedback
- **Inline editing** where possible
- **Keyboard shortcuts** for power users
- **Mobile-first responsive design**

### Accessibility
- **Keyboard navigation** for all interactions
- **High contrast mode** support

### Performance
- **Code splitting** by route
- **Image optimization** with Next.js Image
- **Skeleton screens** during loading
- **Virtual scrolling** for large lists

## Component Architecture Examples

### TaskInput Component
```typescript
interface TaskInputProps {
  instanceId: string
  onSubmit: (task: TaskPayload) => void
  suggestions?: TaskSuggestion[]
}

Features:
- Rich text editor with @mentions for agents
- Task templates dropdown
- Priority selector
- Schedule picker
- File attachments for context
```

### InstanceCard Component
```typescript
interface InstanceCardProps {
  instance: Instance
  metrics?: InstanceMetrics
  onQuickAction?: (action: QuickAction) => void
}

Features:
- Hero image with overlay stats
- Platform icons with connection status
- Active task indicator
- Quick action menu
- Hover state with additional info
```

## Real-time Features

### WebSocket Events
- `task.created`, `task.updated`, `task.completed`
- `agent.thinking`, `agent.acting`
- `approval.required`, `approval.processed`
- `instance.metrics.updated`

### UI Updates
- **Presence indicators**: Show when agents are active
- **Live counters**: Task completion, pending approvals
- **Progress bars**: Multi-step task execution
- **Toast notifications**: Important status changes

This architecture provides a solid foundation for building an intuitive, scalable frontend that aligns with Swallowtail's AI-powered multi-instance management goals.




-----



Swallowtail Frontend MVP       │ │
│ │ Implementation Plan            │ │
│ │                                │ │
│ │ Phase 1: Project Setup & Core  │ │
│ │ Infrastructure (Day 1-2)       │ │
│ │                                │ │
│ │ 1.1 Initialize Next.js Project │ │
│ │                                │ │
│ │ - Create new Next.js 14 app    │ │
│ │ with TypeScript and App Router │ │
│ │ - Configure Tailwind CSS with  │ │
│ │ custom design tokens           │ │
│ │ - Set up ESLint, Prettier, and │ │
│ │  TypeScript configurations     │ │
│ │ - Install core dependencies    │ │
│ │ (Radix UI, Framer Motion,      │ │
│ │ Lucide React)                  │ │
│ │                                │ │
│ │ 1.2 Set Up Base Architecture   │ │
│ │                                │ │
│ │ - Create directory structure   │ │
│ │ as outlined in the design plan │ │
│ │ - Configure path aliases in    │ │
│ │ tsconfig.json                  │ │
│ │ - Set up environment variables │ │
│ │  structure                     │ │
│ │ - Create base layout with auth │ │
│ │  wrapper                       │ │
│ │                                │ │
│ │ 1.3 Design System Foundation   │ │
│ │                                │ │
│ │ - Create UI component library  │ │
│ │ structure                      │ │
│ │ - Implement base components:   │ │
│ │ Button, Card, Input, Dialog,   │ │
│ │ Badge                          │ │
│ │ - Set up theme configuration   │ │
│ │ with CSS variables             │ │
│ │ - Create typography and        │ │
│ │ spacing scales                 │ │
│ │                                │ │
│ │ 1.4 API Client Setup           │ │
│ │                                │ │
│ │ - Create typed API client      │ │
│ │ using fetch                    │ │
│ │ - Set up TanStack Query        │ │
│ │ configuration                  │ │
│ │ - Create API service layer     │ │
│ │ with error handling            │ │
│ │ - Implement authentication     │ │
│ │ interceptors                   │ │
│ │                                │ │
│ │ Phase 2: Core Layout &         │ │
│ │ Navigation (Day 3-4)           │ │
│ │                                │ │
│ │ 2.1 App Shell                  │ │
│ │                                │ │
│ │ - Implement responsive sidebar │ │
│ │  navigation                    │ │
│ │ - Create top navigation bar    │ │
│ │ with user menu                 │ │
│ │ - Add mobile hamburger menu    │ │
│ │ - Implement route-based active │ │
│ │  states                        │ │
│ │                                │ │
│ │ 2.2 Dashboard Layout           │ │
│ │                                │ │
│ │ - Create dashboard home page   │ │
│ │ structure                      │ │
│ │ - Implement instance grid      │ │
│ │ layout                         │ │
│ │ - Add skeleton loaders for     │ │
│ │ data fetching                  │ │
│ │ - Create empty states for new  │ │
│ │ users                          │ │
│ │                                │ │
│ │ 2.3 Instance Management Layout │ │
│ │                                │ │
│ │ - Create instance detail page  │ │
│ │ layout                         │ │
│ │ - Implement tab navigation     │ │
│ │ (Tasks, Agents, Analytics,     │ │
│ │ Settings)                      │ │
│ │ - Add breadcrumb navigation    │ │
│ │ - Create loading and error     │ │
│ │ states                         │ │
│ │                                │ │
│ │ Phase 3: Instance Creation     │ │
│ │ Flow (Day 5-7)                 │ │
│ │                                │ │
│ │ 3.1 Create Instance Wizard     │ │
│ │                                │ │
│ │ - Multi-step form with         │ │
│ │ progress indicator             │ │
│ │ - Step 1: Choose instance type │ │
│ │  (Ecommerce/Social)            │ │
│ │ - Step 2: Business profile     │ │
│ │ form with validation           │ │
│ │ - Step 3: Visual identity      │ │
│ │ upload with drag-drop          │ │
│ │ - Step 4: Platform connections │ │
│ │  (OAuth simulation for MVP)    │ │
│ │ - Step 5: Review and launch    │ │
│ │                                │ │
│ │ 3.2 Form Components            │ │
│ │                                │ │
│ │ - Implement React Hook Form    │ │
│ │ with Zod validation            │ │
│ │ - Create reusable form field   │ │
│ │ components                     │ │
│ │ - Add error handling and       │ │
│ │ validation messages            │ │
│ │ - Implement form persistence   │ │
│ │ between steps                  │ │
│ │                                │ │
│ │ 3.3 File Upload                │ │
│ │                                │ │
│ │ - Implement React Dropzone for │ │
│ │  image uploads                 │ │
│ │ - Create image preview         │ │
│ │ components                     │ │
│ │ - Add file validation (size,   │ │
│ │ type)                          │ │
│ │ - Create upload progress       │ │
│ │ indicators                     │ │
│ │                                │ │
│ │ Phase 4: Task Management       │ │
│ │ Interface (Day 8-10)           │ │
│ │                                │ │
│ │ 4.1 Task Input Component       │ │
│ │                                │ │
│ │ - Large textarea with          │ │
│ │ auto-resize                    │ │
│ │ - Priority selector            │ │
│ │ (Urgent/Normal/Low)            │ │
│ │ - Schedule picker for future   │ │
│ │ tasks                          │ │
│ │ - Submit button with loading   │ │
│ │ state                          │ │
│ │                                │ │
│ │ 4.2 Task Queue Display         │ │
│ │                                │ │
│ │ - Task list with status        │ │
│ │ indicators                     │ │
│ │ - Real-time progress bars      │ │
│ │ - Agent activity indicators    │ │
│ │ - Filter and sort options      │ │
│ │                                │ │
│ │ 4.3 Task Timeline              │ │
│ │                                │ │
│ │ - Visual timeline of task      │ │
│ │ execution                      │ │
│ │ - Expandable task details      │ │
│ │ - Status badges and timestamps │ │
│ │ - Agent assignments display    │ │
│ │                                │ │
│ │ 4.4 Approval Queue             │ │
│ │                                │ │
│ │ - Side panel for pending       │ │
│ │ approvals                      │ │
│ │ - Task context and details     │ │
│ │ - Approve/Reject buttons       │ │
│ │ - Batch actions for multiple   │ │
│ │ approvals                      │ │
│ │                                │ │
│ │ Phase 5: Real-time Updates &   │ │
│ │ WebSocket (Day 11-12)          │ │
│ │                                │ │
│ │ 5.1 WebSocket Integration      │ │
│ │                                │ │
│ │ - Set up Socket.io client      │ │
│ │ - Create WebSocket context     │ │
│ │ provider                       │ │
│ │ - Implement connection status  │ │
│ │ indicator                      │ │
│ │ - Handle reconnection logic    │ │
│ │                                │ │
│ │ 5.2 Real-time UI Updates       │ │
│ │                                │ │
│ │ - Task status updates          │ │
│ │ - Progress percentage displays │ │
│ │ - Agent activity indicators    │ │
│ │ - Toast notifications for      │ │
│ │ events                         │ │
│ │                                │ │
│ │ 5.3 State Management           │ │
│ │                                │ │
│ │ - Set up Zustand stores for    │ │
│ │ instances, tasks, and UI state │ │
│ │ - Implement optimistic updates │ │
│ │ - Create selectors for         │ │
│ │ performance                    │ │
│ │ - Handle WebSocket state       │ │
│ │ synchronization                │ │
│ │                                │ │
│ │ Phase 6: Agent Configuration   │ │
│ │ UI (Day 13-14)                 │ │
│ │                                │ │
│ │ 6.1 Agent List View            │ │
│ │                                │ │
│ │ - Display all agents for an    │ │
│ │ instance                       │ │
│ │ - Show agent roles and current │ │
│ │  status                        │ │
│ │ - Add/remove agent             │ │
│ │ capabilities                   │ │
│ │ - Agent activity indicators    │ │
│ │                                │ │
│ │ 6.2 Agent Customization        │ │
│ │                                │ │
│ │ - Personality configuration    │ │
│ │ sliders                        │ │
│ │ - Tone and style settings      │ │
│ │ - Platform-specific            │ │
│ │ preferences                    │ │
│ │ - Save and reset functionality │ │
│ │                                │ │
│ │ Phase 7: Polish & Integration  │ │
│ │ (Day 15-16)                    │ │
│ │                                │ │
│ │ 7.1 Loading States             │ │
│ │                                │ │
│ │ - Implement skeleton screens   │ │
│ │ throughout                     │ │
│ │ - Add loading spinners for     │ │
│ │ actions                        │ │
│ │ - Create smooth transitions    │ │
│ │ - Handle error boundaries      │ │
│ │                                │ │
│ │ 7.2 Responsive Design          │ │
│ │                                │ │
│ │ - Test and fix mobile layouts  │ │
│ │ - Implement touch gestures     │ │
│ │ - Optimize for tablet views    │ │
│ │ - Add keyboard navigation      │ │
│ │                                │ │
│ │ 7.3 Integration Testing        │ │
│ │                                │ │
│ │ - Connect to backend APIs      │ │
│ │ - Test real-time updates       │ │
│ │ - Verify error handling        │ │
│ │ - Performance optimization     │ │
│ │                                │ │
│ │ Implementation Notes           │ │
│ │                                │ │
│ │ Priority Order                 │ │
│ │                                │ │
│ │ 1. Dashboard and instance grid │ │
│ │  (visual impact)               │ │
│ │ 2. Instance creation flow      │ │
│ │ (core functionality)           │ │
│ │ 3. Task input and queue (main  │ │
│ │ user interaction)              │ │
│ │ 4. Real-time updates (enhanced │ │
│ │  experience)                   │ │
│ │ 5. Agent configuration         │ │
│ │ (advanced features)            │ │
│ │                                │ │
│ │ MVP Simplifications            │ │
│ │                                │ │
│ │ - Use mock OAuth for platform  │ │
│ │ connections                    │ │
│ │ - Simplified analytics (basic  │ │
│ │ counters only)                 │ │
│ │ - Limited to core agent types  │ │
│ │ - Basic approval flow without  │ │
│ │ complex routing                │ │
│ │                                │ │
│ │ Key Components to Build First  │ │
│ │                                │ │
│ │ 1. InstanceCard - Reusable     │ │
│ │ across dashboard               │ │
│ │ 2. TaskInput - Core            │ │
│ │ interaction component          │ │
│ │ 3. CreateInstanceWizard -      │ │
│ │ Critical user flow             │ │
│ │ 4. TaskQueue - Main            │ │
│ │ operational view               │ │
│ │ 5. AgentList - Configuration   │ │
│ │ interface                      │ │
│ │                                │ │
│ │ Testing Strategy               │ │
│ │                                │ │
│ │ - Unit tests for UI components │ │
│ │  with React Testing Library    │ │
│ │ - Integration tests for user   │ │
│ │ flows                          │ │
│ │ - E2E tests for critical paths │ │
│ │  (instance creation, task      │ │
│ │ submission)                    │ │
│ │ - Visual regression tests with │ │
│ │  Chromatic                     │ │
│ │                                │ │
│ │ This plan focuses on building  │ │
│ │ a functional MVP that          │ │
│ │ demonstrates the core value    │ │
│ │ proposition while maintaining  │ │
│ │ flexibility for future         │ │
│ │ enhancements.