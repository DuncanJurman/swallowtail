# Swallowtail Frontend

AI-powered business management platform frontend built with Next.js 14+, TypeScript, and Tailwind CSS.

## Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm start
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Navigation Routes

- `/` - Landing page
- `/dashboard` - Main dashboard with stats and activity
- `/instances` - View and manage all business instances
- `/instances/[id]/tasks` - Task management for a specific instance
- `/instances/new` - Create new instance (coming soon)

## Key Features Implemented

### 1. Dashboard Layout
- Responsive sidebar navigation with collapsible menu
- Mobile-friendly hamburger menu
- Top bar with search and user menu
- Route-based active states
- Clean, modern UI with Tailwind CSS

### 2. Instance Management
- Instance cards displaying key metrics
- Grid layout for multiple instances
- Instance type differentiation (Ecommerce/Social Media)
- Platform connection indicators
- Quick actions per instance

### 3. Task Management
- Natural language task input
- Priority selection (Urgent/Normal/Low)
- Real-time task queue with status indicators
- Progress tracking for in-progress tasks
- Filter tasks by status (All/Active/Completed)
- Agent assignment display

### 4. Reusable Components
- **Button**: Multiple variants and sizes
- **Card**: Flexible container with sub-components
- **Input/Textarea**: Form inputs with consistent styling
- **Dialog**: Modal dialogs
- **Badge**: Status and label indicators
- **InstanceCard**: Displays instance information
- **TaskInput**: Natural language task submission
- **Sidebar/TopBar**: Navigation components

## Tech Stack

- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS with custom design tokens
- **UI Components**: Radix UI primitives
- **State Management**: Zustand
- **Data Fetching**: TanStack Query
- **Forms**: React Hook Form + Zod
- **Real-time**: Socket.io Client (ready for integration)
- **Animations**: Framer Motion
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authenticated routes
│   │   ├── dashboard/     # Dashboard page
│   │   └── instances/     # Instance management
│   └── page.tsx           # Landing page
├── components/            # React components
│   ├── ui/               # Base UI components
│   ├── instances/        # Instance-specific components
│   ├── tasks/            # Task management components
│   └── shared/           # Shared components (navigation)
├── lib/                  # Utilities and API client
├── types/               # TypeScript type definitions
└── styles/              # Global styles
```

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Development Guidelines

1. **Components**: Use TypeScript for all components with proper prop interfaces
2. **Styling**: Utilize Tailwind CSS utilities, avoid inline styles
3. **State**: Use Zustand for global state, React state for component state
4. **API**: All API calls go through the typed API client
5. **Testing**: Components should be testable and follow single responsibility

## Scripts

```bash
# Development
npm run dev          # Start development server with Turbopack

# Building
npm run build        # Build for production
npm run start        # Run production build

# Code Quality
npm run lint         # Run ESLint
npm run prettier     # Format code with Prettier
```

## Next Steps

- [ ] Implement instance creation wizard
- [ ] Add real API integration
- [ ] Implement WebSocket for real-time updates
- [ ] Add authentication flow
- [ ] Create agent configuration UI
- [ ] Build analytics dashboard

## Contributing

1. Follow the existing code structure and naming conventions
2. Use TypeScript strictly (no `any` types)
3. Write self-documenting code
4. Test your changes thoroughly
5. Update documentation as needed