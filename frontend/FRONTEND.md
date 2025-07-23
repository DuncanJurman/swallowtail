# Swallowtail Frontend Documentation

## Overview
This frontend application is built with Next.js 14+, TypeScript, and Tailwind CSS to provide a modern, responsive interface for managing multiple AI-powered business instances.

## Tech Stack
- **Framework**: Next.js 14+ with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI (to be installed)
- **State Management**: Zustand (to be installed)
- **Data Fetching**: TanStack Query (to be installed)
- **Real-time**: Socket.io Client (to be installed)
- **Forms**: React Hook Form + Zod (to be installed)
- **Animations**: Framer Motion (to be installed)
- **Icons**: Lucide React (to be installed)

## Setup Log

### 2024-07-23: Initial Setup
1. Created frontend directory
2. Initialized Next.js project with:
   - TypeScript support
   - Tailwind CSS
   - App Router
   - ESLint
   - Import alias `@/*`

3. Configured development environment:
   - Added Prettier with Tailwind plugin
   - Set up ESLint with Prettier integration
   - Configured strict TypeScript settings

4. Tailwind CSS customization:
   - Added custom color palette (primary, secondary, semantic colors)
   - Configured design tokens and spacing
   - Added custom animations and utilities
   - Set up CSS variables for theming

5. Installed core dependencies:
   - UI: Radix UI, Framer Motion, Lucide React
   - State: Zustand, TanStack Query
   - Forms: React Hook Form, Zod
   - Real-time: Socket.io Client
   - Others: clsx, tailwind-merge, class-variance-authority

6. Created base directory structure following the design plan

7. Implemented core UI components:
   - Button (with variants and sizes)
   - Card (with sub-components)
   - Input
   - Dialog

8. Set up API infrastructure:
   - Created typed API client with error handling
   - Configured TanStack Query provider
   - Added environment variables support

9. Created TypeScript types for:
   - Instance entity
   - Task entity

10. Built landing page showcasing the design system

## Directory Structure
```
frontend/
├── app/                      # Next.js App Router
├── components/              # React components
├── hooks/                   # Custom React hooks
├── lib/                     # Utilities and helpers
├── services/                # API service layers
├── stores/                  # Zustand stores
├── types/                   # TypeScript types
├── styles/                  # Global styles
├── public/                  # Static assets
└── frontend.md             # This documentation
```

## Development Guidelines

### Component Structure
- Use functional components with TypeScript
- Follow naming convention: PascalCase for components
- Colocate tests with components (*.test.tsx)
- Keep components focused and single-purpose

### State Management
- Local state: useState for component-specific state
- Global state: Zustand stores for app-wide state
- Server state: TanStack Query for API data

### Styling
- Use Tailwind CSS utility classes
- Create reusable component classes in globals.css when needed
- Follow mobile-first responsive design

### Type Safety
- Define interfaces for all props and data structures
- Use strict TypeScript configuration
- Avoid `any` types

## API Integration
- Backend URL: http://localhost:8000 (configurable via env)
- WebSocket URL: ws://localhost:8000 (for real-time updates)

## Key Features to Implement
1. Instance Management (Create, List, Configure)
2. Task Management (Submit, Track, Approve)
3. Agent Configuration
4. Real-time Updates
5. Analytics Dashboard

## Testing Strategy
- Unit tests: Components and utilities
- Integration tests: API interactions
- E2E tests: Critical user flows

## Performance Considerations
- Code splitting by route
- Image optimization with Next.js Image
- Lazy loading for heavy components
- Virtual scrolling for large lists