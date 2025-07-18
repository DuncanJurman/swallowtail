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

#### `src/services/storage.py`
- **Purpose**: Manage file storage for product images and videos using Supabase Storage
- **Key Features**:
  - Product-based partitioning (`products/{product_id}/...`)
  - Automatic image optimization (WebP conversion, resizing)
  - Three storage buckets: product-images (public), product-videos (public), reference-images (private)
  - Metadata tracking in PostgreSQL
  - Support for different image types: reference, generated, temp
  - Support for different video types: demo, ad, raw
- **Main Class**: `SupabaseStorageService`
  - `upload_image()`: Upload images with automatic optimization and metadata storage
  - `upload_video()`: Upload videos with size validation
  - `list_product_images()`: Get all images for a product
  - `delete_product_assets()`: Clean up all assets for a product
  - `get_signed_url()`: Generate temporary access URLs for private content
- **Image Optimization**:
  - Max dimension: 2048px (maintains aspect ratio)
  - Format: WebP for generated images
  - Quality: 85% for good balance
  - Size reduction: Typically 70-90%
- **Path Structure**:
  - Reference: `products/{id}/reference/{timestamp}_{filename}`
  - Generated: `products/{id}/generated/{subtype}/{session}_final.webp`
  - Temp: `products/{id}/temp/{session}/{image_id}.webp`
  - Videos: `products/{id}/{type}/...`

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
  - `DATABASE_URL`: PostgreSQL connection string (pooled) - Use this for application connections
  - `DATABASE_DIRECT_URL`: Direct connection for migrations (may not be available on all Supabase plans)
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_ANON_KEY`: Public API key
  - `SUPABASE_SERVICE_KEY`: Service role key for backend

#### Database Connection Notes
- **pgBouncer Compatibility**: Supabase uses pgBouncer for connection pooling. When using asyncpg directly:
  - Set `statement_cache_size=0` to disable prepared statements
  - Use the pooled DATABASE_URL for connections (not DIRECT_URL)
  - See `src/utils/db_helper.py` for proper connection setup

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
11. **Image Generation**: AI-powered product image generation with quality evaluation

## Research Workshop

### Overview
The Research Workshop is a continuous discovery engine that operates independently from product instances, constantly scanning for trends and opportunities.

### Components

#### Research Workshop Tables
- **trend_snapshots**: Raw trend data from various sources (Google Trends, social media, marketplaces)
- **research_metrics**: Performance tracking for research agents
- **market_opportunities**: Enhanced with scoring, review workflow, and detailed analysis fields

#### Research Agents (Planned)
1. **TrendScannerAgent**: Monitors multiple data sources for emerging trends
2. **MarketAnalyzerAgent**: Deep dives into specific opportunities 
3. **SourcingScoutAgent**: Identifies potential suppliers and pricing
4. **OpportunityEvaluatorAgent**: Scores and ranks opportunities using ML

### Database Schema Updates
```sql
-- New tables for Research Workshop
CREATE TABLE trend_snapshots (
    id UUID PRIMARY KEY,
    source VARCHAR(100),
    keywords TEXT[],
    metrics JSONB,
    geographic_data JSONB,
    captured_at TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

CREATE TABLE research_metrics (
    id UUID PRIMARY KEY,
    agent_name VARCHAR(100),
    execution_date DATE,
    opportunities_found INTEGER,
    opportunities_approved INTEGER,
    success_rate NUMERIC(3,2),
    average_score NUMERIC(3,2)
);

-- Enhanced market_opportunities table
ALTER TABLE market_opportunities ADD:
    - status VARCHAR(50) -- pending, reviewed, approved, rejected, promoted
    - score NUMERIC(3,2) -- 0.00-1.00 scoring
    - market_analysis JSONB
    - sourcing_options JSONB
    - discovery_date TIMESTAMP
    - review tracking fields
```

## Image Generation System

### Overview
The image generation system uses OpenAI's gpt-image-1 model to create high-quality product images based on reference images. It includes automatic quality evaluation using structured outputs and iterative improvement through feedback loops.

### Key Features
- **Structured Output Integration**: Uses OpenAI's structured output feature with Pydantic models for type-safe, consistent evaluation results
- **Detailed Scoring System**: Breaks down evaluation into visual fidelity, prompt accuracy, technical quality, and product accuracy
- **Metadata Propagation**: Detailed scores flow through the entire system from evaluation to API responses
- **Automatic Refinement**: Feedback-driven regeneration based on specific improvement suggestions

### Components

#### Services

##### `src/services/openai_image_service.py`
- **Purpose**: OpenAI API integration for image generation and structured evaluation
- **Key Features**:
  - Image generation using `images.edit` endpoint with gpt-image-1 model
  - Structured image evaluation using GPT-4 vision with `client.chat.completions.parse()`
  - Type-safe evaluation responses using Pydantic models
  - Automatic image preparation and optimization
- **Key Models**:
  - `ImageEvaluationResponse`: Pydantic model defining structured evaluation output
    - `overall_score`: Overall quality score (0-100)
    - `visual_fidelity_score`: How well it matches the reference (0-100)
    - `prompt_accuracy_score`: How well it follows the prompt (0-100)
    - `technical_quality_score`: Sharpness, lighting, composition (0-100)
    - `product_accuracy_score`: Product detail accuracy (0-100)
    - `issues`: List of specific issues found
    - `improvements`: List of suggested improvements
- **Main Methods**:
  - `generate_image()`: Create product images from references
  - `evaluate_images()`: Structured evaluation with detailed scoring breakdown
  - `prepare_image()`: Optimize images for API constraints

#### Agents

##### `src/agents/image_generation.py`
- **Purpose**: CrewAI agent for product image generation
- **Key Features**:
  - Reference-based image generation
  - Feedback-based regeneration
  - CrewAI task integration
- **Main Methods**:
  - `execute()`: CrewAI execution interface
  - `_generate_from_reference()`: Initial image generation
  - `_regenerate_with_feedback()`: Improved generation with feedback

##### `src/agents/image_evaluator.py`
- **Purpose**: CrewAI agent for image quality evaluation with structured output support
- **Key Features**:
  - Visual fidelity assessment using structured evaluation
  - Prompt adherence checking with detailed scoring
  - Specific improvement suggestions from structured feedback
  - Metadata propagation through `AgentResult`
- **Main Methods**:
  - `execute()`: CrewAI execution interface with metadata support
  - `_evaluate_generated_image()`: Structured quality scoring using Pydantic models
- **Metadata Propagation**:
  - Extracts detailed scores from structured evaluation
  - Passes scores through `AgentResult.metadata` field
  - Includes: visual_fidelity_score, prompt_accuracy_score, technical_quality_score, product_accuracy_score, issues

#### Workflows

##### `src/workflows/image_generation_workflow.py`
- **Purpose**: Orchestrates the complete image generation pipeline with structured output support
- **Key Features**:
  - Automatic retry with feedback loop using structured improvement suggestions
  - Configurable quality thresholds with detailed score tracking
  - Enhanced logging of all evaluation scores
  - CrewAI Crew integration option
- **Main Methods**:
  - `generate_product_image()`: Main workflow with automatic refinement and detailed score logging
  - `generate_with_crew()`: Alternative CrewAI Crew-based approach
- **Enhanced Features**:
  - Logs detailed evaluation scores for each attempt
  - Propagates metadata through to API responses
  - Tracks issues found during evaluation
  - Returns comprehensive detailed_scores in response

#### API Endpoints

##### `src/api/routes/image_generation.py`
- **Endpoints**:
  - `POST /api/v1/images/generate`: Synchronous image generation with detailed scoring
  - `POST /api/v1/images/generate-async`: Asynchronous generation (placeholder)
  - `GET /api/v1/images/status/{task_id}`: Check async task status
- **Request Model**:
  ```python
  {
    "product_id": "string",
    "reference_image_url": "string",
    "product_name": "string", 
    "product_features": ["string"],
    "style_requirements": {"key": "value"},
    "approval_threshold": 0.85,
    "max_attempts": 3
  }
  ```
- **Response Model with Detailed Scores**:
  ```python
  {
    "success": bool,
    "image_url": "string",  # URL of approved image
    "score": float,         # Overall score (0-1)
    "attempts": int,        # Number of attempts made
    "prompt": "string",     # Final prompt used
    "detailed_scores": {    # Breakdown of evaluation scores
      "visual_fidelity": int,    # 0-100
      "prompt_accuracy": int,    # 0-100
      "technical_quality": int,  # 0-100
      "product_accuracy": int    # 0-100
    }
  }
  ```

### Image Generation Flow

1. **Input**: Reference image URL + product details
2. **Generation**: Use gpt-image-1 to create product image
3. **Structured Evaluation**: GPT-4 vision with structured output:
   - Uses `client.chat.completions.parse()` with Pydantic model
   - Returns type-safe evaluation with detailed scores
   - Provides specific issues and improvement suggestions
4. **Decision**:
   - If overall_score >= threshold: Approve and store with metadata
   - If overall_score < threshold: Use structured feedback for regeneration
5. **Iteration**: Up to max_attempts tries with targeted improvements
6. **Output**: Final approved image URL with detailed scoring breakdown

### Configuration

- **Environment Variables**:
  - `OPENAI_API_KEY`: Required for image generation
  - `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`: For image storage

### Testing

- **File**: `tests/workflows/test_image_generation_workflow.py`
- **Coverage**:
  - Successful first-attempt generation
  - Regeneration with feedback
  - Max attempts handling
  - Error scenarios
  - Structured output parsing and validation
  - Metadata propagation through workflow

### Structured Output Implementation Details

#### Benefits
1. **Type Safety**: Pydantic models ensure consistent evaluation structure
2. **Reliable Parsing**: No more regex or string parsing for scores
3. **Rich Feedback**: Detailed breakdown helps targeted improvements
4. **Better Observability**: Granular scores for debugging and analytics

#### Technical Implementation
- Uses OpenAI's `response_format` parameter with Pydantic models
- Requires GPT-4o-2024-08-06 or later for structured output support
- Evaluation prompt crafted for consistent structured responses
- Metadata flows through: Service → Agent → Workflow → API

#### Example Structured Evaluation Response
```json
{
  "overall_score": 88,
  "visual_fidelity_score": 92,
  "prompt_accuracy_score": 85,
  "technical_quality_score": 90,
  "product_accuracy_score": 86,
  "issues": ["Slight color mismatch in product finish"],
  "improvements": ["Adjust color temperature to match reference warmth"]
}
```

## Next Steps

1. **Research Workshop Implementation**:
   - ResearchWorkshop orchestrator with continuous discovery cycle
   - TrendScannerAgent implementation
   - MarketAnalyzerAgent implementation
   - SourcingScoutAgent implementation
   - OpportunityEvaluatorAgent with ML scoring
   - API endpoints for opportunity management
   - Frontend dashboard for opportunity review

2. **Additional Agents**:
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