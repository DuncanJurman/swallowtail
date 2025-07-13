# Swallowtail Frontend

Next.js 15 dashboard for the autonomous e-commerce platform.

## Features

- Real-time agent status monitoring
- Human checkpoint approval interface
- Product selection and review
- WebSocket integration for live updates
- React Query for efficient data fetching

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Copy environment variables:
   ```bash
   cp .env.local.example .env.local
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

4. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── app/                 # Next.js app router pages
├── components/          # React components
│   ├── layout/         # Layout components (sidebar, header)
│   ├── checkpoints/    # Checkpoint approval components
│   └── ui/             # Shadcn UI components
├── hooks/              # Custom React hooks
├── lib/                # Utilities and API client
├── providers/          # React context providers
├── services/           # API service layer
└── types/              # TypeScript type definitions
```

## Key Technologies

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Component library
- **React Query** - Data fetching and caching
- **Socket.io** - Real-time WebSocket communication
- **Axios** - HTTP client

## Available Pages

- `/` - Dashboard overview
- `/checkpoints` - Review and approve pending decisions
- `/products` - Product management (coming soon)
- `/agents` - Agent monitoring (coming soon)
- `/analytics` - Performance analytics (coming soon)
- `/settings` - Configuration (coming soon)

## API Integration

The frontend connects to the backend API running on `http://localhost:8000` by default. Key endpoints:

- `POST /api/v1/agents/workflow/start` - Start new workflow
- `GET /api/v1/agents/workflow/status` - Get workflow status
- `GET /api/v1/checkpoints/` - List pending checkpoints
- `POST /api/v1/checkpoints/{id}/resolve` - Resolve checkpoint

## Development

Run the development server:
```bash
npm run dev
```

Build for production:
```bash
npm run build
```

Run linting:
```bash
npm run lint
```