# Swallowtail Backend

Autonomous multi-agent e-commerce platform powered by CrewAI and LangChain.

## Quick Start

1. Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   # Using pip
   pip install -r requirements.txt
   
   # Or using poetry (recommended for development)
   poetry install
   ```

3. Start Redis (required for shared state):
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # Or install locally
   brew install redis  # macOS
   redis-server
   ```

4. Run the backend:
   ```bash
   python run.py
   ```

5. Access the API:
   - API docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## Project Structure

```
backend/
├── src/
│   ├── agents/         # AI agents (orchestrator, market research, etc.)
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Core utilities (config, state management)
│   ├── models/        # Pydantic models
│   ├── services/      # Business logic services
│   └── utils/         # Helper utilities
├── tests/             # Test files
├── run.py            # Application entry point
└── pyproject.toml    # Poetry configuration
```

## Key Components

- **Orchestrator Agent**: Coordinates all other agents and manages workflow
- **Market Research Agent**: Finds trending products and opportunities
- **Shared State**: Redis-based state management for agent coordination
- **Human Checkpoints**: Approval points for critical decisions

## API Endpoints

- `POST /api/v1/agents/workflow/start` - Start a new product launch workflow
- `GET /api/v1/agents/workflow/status` - Get current workflow status
- `GET /api/v1/checkpoints/` - List pending human checkpoints
- `POST /api/v1/checkpoints/{id}/resolve` - Resolve a checkpoint

## Development

Run tests:
```bash
pytest
```

Format code:
```bash
black .
ruff check . --fix
```

Type check:
```bash
mypy src
```