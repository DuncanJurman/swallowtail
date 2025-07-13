# Swallowtail Backend Architecture

## Overview
The Swallowtail backend is built using Python with CrewAI (built on LangChain) for multi-agent orchestration, FastAPI for REST APIs, and Redis for shared state management.

## Directory Structure
```
backend/
├── src/
│   ├── agents/         # AI agents implementation
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Core utilities
│   ├── models/        # Data models
│   ├── services/      # Business logic (future)
│   └── utils/         # Helper utilities (future)
├── tests/             # Test files
├── run.py            # Application entry point
└── pyproject.toml    # Poetry configuration
```

## Implemented Files

### Core Infrastructure

#### `src/core/config.py`
- **Purpose**: Centralized configuration management using Pydantic Settings
- **Key Features**:
  - Environment variable support with `.env` file loading
  - Type-safe configuration with validation
  - Settings for OpenAI, Redis, API server, and external services
  - Caching with `@lru_cache` for performance
- **Key Settings**: `openai_api_key`, `redis_url`, `api_host/port`, `cors_origins`

#### `src/core/state.py`
- **Purpose**: Shared state management for agent coordination
- **Key Components**:
  - `SharedState` class: Redis-based state storage with JSON serialization
  - `StateKey` enum: Standard keys for common state values
  - `WorkflowStatus` enum: Tracks current workflow stage
- **Methods**:
  - `get()`, `set()`, `delete()`: Basic state operations
  - `update_workflow_status()`: Workflow state management
  - Namespaced Redis keys to prevent collisions

### Data Models

#### `src/models/product.py`
- **Purpose**: Product-related data structures
- **Models**:
  - `ProductIdea`: Market research output with trend data
  - `SupplierInfo`: Supplier details and pricing
  - `ProductListing`: Complete product information for store
- **Features**: Pydantic models with validation and default values

#### `src/models/checkpoint.py`
- **Purpose**: Human-in-the-loop checkpoint system
- **Models**:
  - `HumanCheckpoint`: Approval point with status tracking
  - `CheckpointType`: Types of checkpoints (product selection, supplier approval, etc.)
  - `CheckpointStatus`: Current state (pending, approved, rejected)
- **Methods**: `approve()`, `reject()`, `request_revision()`

### Agent System

#### `src/agents/base.py`
- **Purpose**: Base class for all agents
- **Key Features**:
  - Abstract base class enforcing agent interface
  - Integration with CrewAI Agent and LangChain LLM
  - Shared state access for all agents
  - Logging system per agent
  - Standard `AgentResult` format
- **Methods**:
  - `execute()`: Abstract method for agent tasks
  - `create_task()`: CrewAI task creation
  - State management helpers

#### `src/agents/orchestrator.py`
- **Purpose**: Central coordinator for all agents
- **Responsibilities**:
  - Workflow management and planning
  - Agent registration and invocation
  - Human checkpoint creation
  - Workflow resumption after approvals
- **Key Methods**:
  - `register_agent()`: Add agents to the system
  - `execute()`: Run workflows
  - `resume_after_checkpoint()`: Continue after human input
- **Current Workflows**: Product launch workflow with checkpoints

#### `src/agents/market_research.py`
- **Purpose**: Find trending products and opportunities
- **Tools**: DuckDuckGo web search via LangChain
- **Process**:
  1. Search for trending products
  2. Analyze competition and demand
  3. Generate structured `ProductIdea` objects
  4. Return 3 product recommendations
- **Output**: List of product ideas with rationale and data sources

### API Layer

#### `src/api/main.py`
- **Purpose**: FastAPI application setup
- **Features**:
  - CORS middleware configuration
  - Router registration
  - Debug mode with auto-docs
  - API versioning setup

#### `src/api/routes/health.py`
- **Purpose**: Health check endpoint
- **Endpoints**:
  - `GET /health`: Check API and Redis status
- **Response**: Health status with dependency checks

#### `src/api/routes/agents.py`
- **Purpose**: Agent workflow control
- **Endpoints**:
  - `POST /api/v1/agents/workflow/start`: Start new workflow
  - `GET /api/v1/agents/workflow/status`: Get current status
- **Features**:
  - Agent initialization and registration
  - Workflow request/response models
  - Error handling

#### `src/api/routes/checkpoints.py`
- **Purpose**: Human checkpoint management
- **Endpoints**:
  - `GET /api/v1/checkpoints/`: List pending checkpoints
  - `GET /api/v1/checkpoints/{id}`: Get checkpoint details
  - `POST /api/v1/checkpoints/{id}/resolve`: Approve/reject checkpoint
- **Features**:
  - Checkpoint resolution with notes
  - Workflow continuation after approval
  - Related data retrieval

### Entry Points

#### `run.py`
- **Purpose**: Application startup script
- **Features**:
  - Environment variable loading
  - Logging configuration
  - Uvicorn server launch with hot reload
  - Path configuration for imports

## Configuration Files

#### `pyproject.toml`
- Poetry dependency management
- Development tools configuration (black, ruff, mypy)
- Python 3.11+ requirement

#### `requirements.txt`
- Quick setup dependencies for pip users
- Core packages: crewai, langchain, fastapi, redis

#### `.env.example`
- Template for environment variables
- API keys placeholders
- Configuration examples

## Current Capabilities

1. **Multi-Agent Orchestration**: CrewAI-based agent coordination
2. **Market Research**: Automated product discovery with web search
3. **Human Checkpoints**: Approval system at critical decisions
4. **State Management**: Redis-based shared state between agents
5. **REST API**: FastAPI endpoints for frontend integration
6. **Workflow Management**: Status tracking and resumption

## Next Steps

1. **Additional Agents**:
   - Product Sourcing Agent
   - Content Creation Agents (copy, image, video)
   - Marketing Agent
   - Fulfillment Agent

2. **Integrations**:
   - Shopify API for product management
   - Image generation APIs
   - Supplier APIs (Alibaba, etc.)
   - Ad platform APIs

3. **Features**:
   - WebSocket support for real-time updates
   - Background task processing
   - Advanced error handling and retries
   - Metrics and monitoring

## Testing

Currently, the test structure is set up but tests need to be implemented:
- Unit tests for individual agents
- Integration tests for workflows
- API endpoint tests
- State management tests