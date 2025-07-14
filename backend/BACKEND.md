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
│   ├── services/      # External service integrations
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

#### `src/core/celery_app.py`
- **Purpose**: Celery application configuration for task queue
- **Key Features**:
  - Redis as broker (DB 0) and result backend (DB 1)
  - Three queues: `default`, `agents`, `background`
  - Task routing based on name patterns
  - JSON serialization for compatibility
  - Auto-discovery of tasks in `src.core` and `src.agents`
- **Configuration**: 30-minute task timeout, UTC timezone, prefetch multiplier = 1

#### `src/core/tasks.py`
- **Purpose**: Task definitions and Celery utilities
- **Decorators**:
  - `@agent_task`: For agent-specific tasks (3 retries, 60s delay)
  - `@background_task`: For background processing (5 retries, 30s delay)
- **Utilities**:
  - `check_celery_health()`: Monitor worker status
  - `execute_agent_task()`: Async-compatible task execution
- **Example Tasks**:
  - `ping`: Simple health check task
  - `process_market_research`: Example agent task

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
- **Purpose**: Health check endpoint with dependency monitoring
- **Endpoints**:
  - `GET /health`: Check API, Redis, and Celery status
- **Response**: 
  - Overall health status ("healthy", "degraded", "error")
  - Redis connection status
  - Celery worker status and active worker list
  - API version

#### `src/api/routes/agents.py`
- **Purpose**: Agent workflow control
- **Endpoints**:
  - `POST /api/v1/agents/workflow/start`: Start new workflow (with validation to prevent multiple active workflows)
  - `GET /api/v1/agents/workflow/status`: Get current status
  - `POST /api/v1/agents/workflow/cancel`: Cancel active workflow
- **Features**:
  - Agent initialization and registration
  - Workflow request/response models
  - Error handling
  - Workflow state validation to prevent concurrent workflows
  - Workflow cancellation with state cleanup

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

### External Services

#### `src/services/pinecone.py`
- **Purpose**: Vector database service for managing product embeddings
- **Key Features**:
  - Pinecone client initialization with API key validation
  - Index creation with configurable dimension and metric
  - Vector upsert with metadata support
  - Similarity search with filtering capabilities
  - Namespace isolation for multi-tenant support
  - Batch operations for performance
- **Main Class**: `PineconeService`
  - `create_index_if_not_exists()`: Ensure index exists with proper configuration
  - `upsert_vectors()`: Add or update vectors with metadata
  - `query_similar_vectors()`: Find similar items with optional metadata filtering
  - `delete_vectors()`: Remove specific vectors by ID
  - `delete_all_vectors()`: Clear entire namespace
  - `get_index_stats()`: Monitor index usage and statistics
- **Configuration**:
  - `PINECONE_API_KEY`: API authentication
  - `PINECONE_INDEX_NAME`: Target index (default: "swallowtail-products")
  - `PINECONE_ENVIRONMENT`: Deployment environment (default: "gcp-starter")
- **Error Handling**: Custom `PineconeServiceError` for service-specific errors

### Database Layer

#### `src/core/database.py`
- **Purpose**: Database configuration and connection management
- **Database**: PostgreSQL (via Supabase)
- **Key Features**:
  - Async SQLAlchemy engine with asyncpg driver
  - Connection pooling configuration
  - Async session management
  - Database initialization utilities
- **Functions**:
  - `get_db()`: Dependency injection for database sessions
  - `init_db()`: Initialize database tables
  - `close_db()`: Cleanup database connections

#### `src/models/database.py`
- **Purpose**: SQLAlchemy ORM models for core entities
- **Tables**:
  - `products`: E-commerce product catalog with lifecycle tracking
  - `agents`: AI agent registry and performance metrics
  - `agent_tasks`: Task execution history and results
  - `market_opportunities`: Discovered opportunities awaiting evaluation
  - `agent_decisions`: Audit trail of agent decisions
  - `shared_knowledge`: Cross-product learning repository
- **Key Features**:
  - UUID primary keys for distributed systems
  - JSONB fields for flexible data storage
  - Comprehensive timestamps and audit trails
  - Relationships between entities
  - Enum types for status management

#### Database Migrations
- **Tool**: Alembic for schema version control
- **Configuration**: `alembic/env.py` configured for async operations
- **Commands**:
  ```bash
  # Create new migration
  poetry run alembic revision --autogenerate -m "Description"
  
  # Apply migrations
  poetry run alembic upgrade head
  
  # Rollback one version
  poetry run alembic downgrade -1
  ```

#### Database Configuration
- **Environment Variables**:
  - `DATABASE_URL`: PostgreSQL connection string (pooled)
  - `DATABASE_DIRECT_URL`: Direct connection for migrations
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_ANON_KEY`: Public API key
  - `SUPABASE_SERVICE_KEY`: Service role key for backend

#### Testing Database Setup
- **File**: `tests/test_database_setup.py`
- **Purpose**: Verify database connectivity and schema
- **Usage**: `poetry run python -m tests.test_database_setup`
- **Checks**:
  - Connection validity
  - Table existence
  - Migration status
  - Schema structure
  - Row counts

### Entry Points

#### `run.py`
- **Purpose**: Application startup script
- **Features**:
  - Environment variable loading
  - Logging configuration
  - Uvicorn server launch with hot reload
  - Path configuration for imports

#### `src/worker.py`
- **Purpose**: Celery worker entry point
- **Usage**: Called by Celery to start worker processes
- **Features**: Path configuration for module imports

### Scripts

#### `scripts/run_worker.sh`
- **Purpose**: Development script to start Celery worker
- **Features**:
  - Sets PYTHONPATH for proper imports
  - Runs worker with Poetry environment
  - Configures 4 concurrent workers
  - Monitors all three queues (default, agents, background)

## Task Queue System

#### Celery Configuration
- **File**: `src/core/celery_app.py`
- **Purpose**: Background task processing for long-running agent operations
- **Broker**: Redis (database 0)
- **Result Backend**: Redis (database 1)
- **Queues**:
  - `default`: General tasks
  - `agents`: Agent-specific tasks
  - `background`: Background processing

#### Running Celery Worker
```bash
# Development
./scripts/run_worker.sh

# Or directly
celery -A src.core.celery_app:celery_app worker --loglevel=info
```

## Configuration Files

#### `pyproject.toml`
- Poetry dependency management
- Development tools configuration (black, ruff, mypy)
- Python 3.11+ requirement
- Includes Celery and task queue dependencies

#### `requirements.txt`
- Quick setup dependencies for pip users
- Core packages: crewai, langchain, fastapi, redis

#### `.env.example`
- Template for environment variables
- API keys placeholders (OpenAI, Serper, Shopify, Pinecone)
- Configuration examples
- Pinecone settings for vector database
- Supabase database connection strings
- Service authentication keys

## Current Capabilities

1. **Multi-Agent Orchestration**: CrewAI-based agent coordination
2. **Market Research**: Automated product discovery with web search
3. **Human Checkpoints**: Approval system at critical decisions
4. **State Management**: Redis-based shared state between agents
5. **REST API**: FastAPI endpoints for frontend integration
6. **Workflow Management**: Status tracking and resumption
7. **Task Queue System**: Celery for background task processing
8. **Vector Database**: Pinecone integration for similarity search and embeddings
9. **Persistent Storage**: PostgreSQL database via Supabase for business data
10. **Database Migrations**: Alembic for schema version control

## Next Steps

1. **Additional Agents**:
   - Product Sourcing Agent
   - Content Creation Agents (copy, image, video)
   - Marketing Agent
   - Fulfillment Agent

2. **Integrations**:
   - Shopify API for product management
   - Image generation APIs (DALL-E, Stable Diffusion)
   - Supplier APIs (Alibaba, etc.)
   - Ad platform APIs (Google Ads, Facebook)
   - ✅ Pinecone vector database (completed)

3. **Features**:
   - WebSocket support for real-time updates
   - Background task processing
   - Advanced error handling and retries
   - Metrics and monitoring

## Testing

### Test Structure
```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_celery.py          # Unit tests for Celery configuration
├── services/
│   ├── test_pinecone.py    # Unit tests for Pinecone service
│   └── test_pinecone_integration.py  # Integration tests with Pinecone
└── integration/
    └── test_celery_integration.py  # Integration tests requiring services
```

### Test Categories
- **Unit Tests**: Run with `poetry run pytest -m unit`
  - Celery configuration tests
  - Task decorator tests
  - Mocked service tests
  - Pinecone service unit tests with mocked dependencies
  
- **Integration Tests**: Run with `poetry run pytest -m integration`
  - End-to-end task execution
  - Worker communication tests
  - Pinecone vector operations (requires API key)
  - Requires Redis and Celery worker running

### Running Tests
```bash
# Unit tests only (fast, no dependencies)
PYTHONPATH=. poetry run pytest -m unit -v

# Integration tests (requires Redis + Celery worker)
PYTHONPATH=. poetry run pytest -m integration -v

# All tests
PYTHONPATH=. poetry run pytest -v
```