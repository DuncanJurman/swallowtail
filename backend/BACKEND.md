# Swallowtail Backend Architecture

## Overview
The Swallowtail backend is built using Python with CrewAI (built on LangChain) for multi-agent orchestration, FastAPI for REST APIs, PostgreSQL for data persistence, and Redis for shared state management. The system uses an instance-based architecture where each business/brand has its own isolated configuration and AI agents.

## Directory Structure
```
backend/
├── src/
│   ├── agents/         # AI agents implementation
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Core utilities
│   ├── crews/         # CrewAI crew definitions
│   ├── flows/         # CrewAI Flow orchestrations
│   ├── models/        # Data models
│   ├── services/      # External service integrations
│   ├── tools/         # Agent tools and utilities
│   └── workflows/     # Legacy workflow implementations
├── tests/             # Test files
├── docs/              # Documentation
├── run.py            # Application entry point
└── pyproject.toml    # Poetry configuration
```

## Implemented Files

### Instance Management System (NEW)

#### `src/models/instance.py`
- **Purpose**: Database models for instance-based multi-tenancy
- **Key Models**:
  - `Instance`: Business/brand instance with isolated configuration
  - `InstanceAgent`: Agent configuration specific to an instance
  - `InstanceTask`: User-submitted tasks for processing
  - `InstanceMedia`: Reference images and media files
- **Features**:
  - Support for ECOMMERCE and SOCIAL_MEDIA instance types
  - JSONB fields for flexible configuration storage
  - Proper indexes for performance

#### `src/models/instance_schemas.py`
- **Purpose**: Pydantic schemas for instance API validation
- **Key Schemas**:
  - `InstanceCreate`: Request model for creating instances
  - `InstanceResponse`: Response model with full instance data
  - `TaskSubmission`: Natural language task submission
  - `InstanceTaskResponse`: Task status and results

#### `src/services/instance_service.py`
- **Purpose**: Business logic for instance management
- **Key Methods**:
  - `create_instance()`: Creates instance with default agents
  - `submit_task()`: Submits tasks for AI processing
  - `get_instance_tasks()`: Retrieves tasks with filtering
- **Features**:
  - Automatic agent creation based on instance type
  - User isolation and ownership validation

#### `src/api/instances.py`
- **Purpose**: RESTful API endpoints for instance management
- **Endpoints**:
  - `POST /instances/`: Create new instance
  - `GET /instances/`: List user's instances
  - `GET /instances/{id}`: Get specific instance
  - `PATCH /instances/{id}`: Update instance
  - `POST /instances/{id}/tasks`: Submit task
  - `GET /instances/{id}/tasks`: List tasks
- **Features**:
  - Full CRUD operations with user authentication
  - Task submission and status tracking

### Core Infrastructure

#### `src/core/config.py`
- **Purpose**: Centralized configuration management using Pydantic Settings
- **Key Features**:
  - Environment variable support with `.env` file loading
  - Type-safe configuration with validation
  - Settings for OpenAI, Redis, API server, and external services
  - Caching with `@lru_cache` for performance
  - Flexible CORS origins parsing (supports JSON array or comma-separated string)
- **Key Settings**: `openai_api_key`, `redis_url`, `api_host/port`, `cors_origins_list` (property)

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

#### `src/models/user.py` (NEW)
- **Purpose**: Simple user model for MVP authentication
- **Model**: `User`
  - Basic fields: id (UUID), email, name, is_active, created_at, updated_at
  - Relationship: One-to-many with instances
- **Notes**: 
  - Minimal implementation for MVP
  - No password storage (future OAuth integration planned)
  - Foreign key relationship with Instance model

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
  - CORS middleware configuration (uses `cors_origins_list` property)
  - Router registration
  - Debug mode with auto-docs
  - API versioning setup
  - Socket.io integration for WebSocket support

#### `src/api/deps.py` (NEW)
- **Purpose**: Common dependencies for API routes
- **Functions**:
  - `get_db()`: Async database session dependency
  - `get_current_user()`: 🔄 DUMMY - Returns mock user for testing
- **Implementation**:
  - Returns User model with UUID: "00000000-0000-0000-0000-000000000000"
  - Email: "test@example.com", Name: "Test User"
  - TODO: Implement proper JWT authentication
  - Required for instance access control

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

#### `src/services/tiktok/`
- **Purpose**: TikTok API integration for OAuth and content posting
- **Key Features**:
  - OAuth 2.0 flow with CSRF protection
  - Token management with automatic refresh
  - Content posting API (sandbox mode)
  - Encrypted credential storage
  - Support for multiple TikTok accounts per instance
  - Account naming for easy identification
- **Main Components**:
  - `oauth.py`: OAuth flow implementation
    - `generate_auth_url()`: Create authorization URL with state (includes instance_id and optional account_name)
    - `exchange_code_for_token()`: Exchange auth code for tokens
    - `refresh_access_token()`: Refresh expired tokens
    - `get_user_info()`: Fetch TikTok user profile
    - `save_credentials()`: Store encrypted tokens in database with account name
    - State format: `instance_id:csrf_token:account_name` (account_name optional)
  - `content_api.py`: Content posting functionality
    - `query_creator_info()`: Get creator permissions and limits
    - `post_video_sandbox()`: Post videos (PULL_FROM_URL or FILE_UPLOAD)
    - `check_post_status()`: Monitor post processing status
  - `models.py`: Pydantic models for API data
  - `config.py`: TikTok API configuration
- **Environment Variables**:
  - `TIKTOK_CLIENT_KEY`: TikTok app client key
  - `TIKTOK_CLIENT_SECRET`: TikTok app client secret
  - `TIKTOK_REDIRECT_URI`: OAuth callback URL
  - `TIKTOK_SANDBOX_MODE`: Enable sandbox mode (default: true)

#### `src/models/tiktok_credentials.py`
- **Purpose**: Database model for storing TikTok OAuth credentials
- **Key Features**:
  - Encrypted storage of access and refresh tokens
  - Automatic token expiration checking
  - Support for multiple TikTok accounts per instance
  - Optional account naming for easy identification
  - Token refresh tracking
- **Model**: `InstanceTikTokCredentials`
  - Links to Instance via foreign key (no unique constraint - allows multiple accounts)
  - Stores TikTok user info and granted scopes
  - Tracks token expiration times
  - Provides encryption/decryption properties
  - Fields: id, instance_id, account_name, tiktok_open_id, display_name, avatar_url, access_token (encrypted), refresh_token (encrypted), scopes, user_info (JSONB)

#### `src/api/routes/tiktok.py`
- **Purpose**: REST API endpoints for TikTok integration
- **Endpoints**:
  - `POST /api/v1/tiktok/auth`: Generate TikTok OAuth URL
    - Request: `{ instance_id: UUID, account_name?: string, scopes?: string[] }`
    - Response: `{ auth_url: string, state: string }`
  - `GET /api/v1/tiktok/callback`: Handle OAuth callback
    - Query params: code, state, error?, error_description?
    - Exchanges code for tokens and saves credentials
  - `GET /api/v1/tiktok/accounts/{instance_id}`: List all TikTok accounts
    - Returns array of connected accounts with token status
    - Automatically refreshes expired tokens
  - `POST /api/v1/tiktok/post`: Post content to TikTok
    - Request: TikTokPostRequest with video_url, title, privacy settings
    - Supports account selection for multi-account instances
  - `DELETE /api/v1/tiktok/disconnect/{instance_id}/{account_id}`: Disconnect account
    - Revokes token and removes from database

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
- **Latest Migration**: `18815335c350_add_user_table_and_instance_fk`
  - Creates users table with basic fields
  - Adds foreign key from instances to users
  - Creates default user for existing data
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
- Auto-generated from Poetry for deployment
- Core packages: crewai, langchain, fastapi, redis
- Used by Railway/Docker deployments

#### `.env.example`
- Template for environment variables
- API keys placeholders (OpenAI, Serper, Shopify, Pinecone)
- Configuration examples
- Pinecone settings for vector database
- Supabase database connection strings
- Service authentication keys

## Deployment Configuration

#### `railway.json`
- Railway platform configuration
- Uses Nixpacks builder
- Start command: `python run.py`
- Configured for automatic restarts

#### `Procfile`
- Web process definition for Railway
- Command: `web: python run.py`

#### `runtime.txt`
- Python version specification: `python-3.12`
- Used by Railway for runtime selection

#### Port Configuration
- Application binds to `0.0.0.0` (all interfaces)
- Uses `PORT` environment variable if available (Railway requirement)
- Falls back to configured `api_port` for local development

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
12. **File Storage**: Supabase Storage integration for images and videos

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

##### `src/services/openai_client.py`
- **Purpose**: Centralized OpenAI client management
- **Features**:
  - Singleton pattern for client reuse
  - Automatic API key validation
  - Shared client instance across services

#### Tools

##### `src/tools/image_generation_tool.py`
- **Purpose**: CrewAI tool for generating images using OpenAI API
- **Key Features**:
  - Handles async operations in synchronous context
  - Uses nest-asyncio for event loop management
  - Accepts file:// URLs for local reference images
  - Returns temporary image path for further processing
- **Main Method**: `_run()` - Synchronous interface for CrewAI

##### `src/tools/image_storage_tool.py`
- **Purpose**: CrewAI tool for storing images to Supabase
- **Key Features**:
  - Handles async storage operations
  - Manages product-based file organization
  - Returns public URLs for stored images
- **Main Method**: `_run()` - Stores images and returns URLs

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
  - `POST /api/v1/images/generate-async`: Asynchronous generation (🔄 DUMMY: returns placeholder - TODO: implement queue integration)
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

### Implementation Status

✅ **Completed**:
- ImageGenerationTool with async/sync handling using nest-asyncio
- ImageStorageTool for Supabase integration
- ImageGenerationCrew using CrewAI @CrewBase pattern
- Multimodal agents with vision capabilities
- Output parsing for extracting generated image paths
- Comprehensive test suite:
  - Unit tests for state models and crews
  - Integration tests with real API calls
  - Direct tool testing for faster validation
  - End-to-end crew execution tests
- Successfully generates product images (e.g., LED Squirtle in dorm room)
- Images saved to `/output/generated_images/` for validation

✅ **Completed**:
- ImageEvaluationCrew implementation with structured outputs
- Flow-based orchestration with feedback loops
- Image generation and evaluation integration

🚧 **Pending**:
- API endpoint integration
- Supabase storage integration (currently saves locally)

### Configuration

- **Environment Variables**:
  - `OPENAI_API_KEY`: Required for image generation
  - `SUPABASE_URL` & `SUPABASE_SERVICE_KEY`: For image storage

### Testing

#### Unit Tests
- **File**: `tests/unit/test_image_generation_state.py`
  - ImageGenerationState model validation
  - State serialization/deserialization
  - Default value handling

- **File**: `tests/unit/test_image_generation_crew.py`
  - Crew initialization
  - Agent configuration
  - Task creation

#### Integration Tests
- **File**: `tests/integration/test_image_tool_direct.py`
  - Direct ImageGenerationTool testing
  - Multiple size generation
  - Error handling
  - Real API calls with timeout handling

- **File**: `tests/integration/test_image_generation_workflow.py`
  - End-to-end crew execution
  - Flow integration with feedback loops
  - Error handling scenarios
  - Real image generation and storage

- **File**: `tests/workflows/test_image_generation_workflow.py`
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

## Task Management System (Enhanced with CrewAI)

### Overview
The Task Management System allows users to create natural language tasks for their products, which are then interpreted and executed by specialized agents through CrewAI's native orchestration capabilities. The system now leverages CrewAI's hierarchical processing, planning, reasoning, and delegation features.

### Architecture Changes

#### Enhanced Base Agent (`src/agents/base.py`)
- **Major Enhancements**:
  - Full CrewAI feature support (delegation, reasoning, planning, memory)
  - Configurable parameters for all CrewAI capabilities
  - Support for YAML configuration loading
  - Enhanced task creation with guardrails, async execution, and structured outputs
  - `from_config` class method for creating agents from YAML

#### CrewAI Integration (`src/crews/`)
- **New CrewBase** (`src/crews/base.py`):
  - Base class using CrewAI's native patterns
  - YAML configuration loading
  - Before/after kickoff hooks
  - Shared state integration
  - Standardized crew creation

- **Product Task Crew** (`src/crews/product_task_crew.py`):
  - Hierarchical crew implementation
  - Dynamic task generation based on execution plans
  - Automatic agent selection
  - Planning and reasoning enabled
  - Real-time task status updates

#### Configuration System (`src/config/`)
- **Agent Configurations** (`src/config/agents.yaml`):
  - All agents defined in YAML format
  - Consistent role, goal, and backstory definitions
  - CrewAI-specific settings (delegation, reasoning, etc.)
  - Includes: product_orchestrator, image_generator, image_evaluator, market_researcher, content_writer, pricing_analyst, seo_specialist

- **Task Templates** (`src/config/tasks.yaml`):
  - Predefined task configurations
  - Expected outputs with guardrails
  - Context dependencies
  - Support for structured output formats

### Components

#### Models

##### `src/models/task.py`
- **Purpose**: Task-related data structures
- **Models**:
  - `TaskPriority`: Enum for priority levels (URGENT=1, HIGH=3, MEDIUM=5, LOW=7, TRIVIAL=9)
  - `TaskCreateRequest`: Request model for creating tasks
  - `TaskUpdateRequest`: Request model for updating tasks
  - `TaskStatusUpdate`: Simplified status update model
  - `ProductTask`: Complete task model with all fields
  - `TaskResponse`: API response model
  - `TaskListResponse`: Paginated response model

#### Database

##### Task Table (`product_tasks`)
- **Purpose**: Store user-created tasks for products
- **Fields**:
  - `id`: UUID primary key
  - `product_id`: Foreign key to products table
  - `task_description`: Natural language task description
  - `status`: TaskStatus enum (PENDING, IN_PROGRESS, COMPLETED, FAILED, CANCELLED)
  - `priority`: Integer (1-9, lower is higher priority)
  - `assigned_agent`: Agent type handling the task
  - `result_data`: JSONB field for execution results
  - `error_message`: Error details if failed
  - Timestamps: created_at, started_at, completed_at
  - `created_by`: User who created the task

#### API Endpoints

##### `src/api/routes/tasks.py`
- **Endpoints**:
  - `POST /api/v1/products/{product_id}/tasks`: Create new task (with auto_execute option)
  - `GET /api/v1/products/{product_id}/tasks`: List product tasks (with pagination/filtering)
  - `GET /api/v1/tasks/{task_id}`: Get task details
  - `PUT /api/v1/tasks/{task_id}`: Update task
  - `PUT /api/v1/tasks/{task_id}/status`: Update task status only
  - `DELETE /api/v1/tasks/{task_id}`: Delete task (only if PENDING)
  - `POST /api/v1/tasks/{task_id}/execute`: Execute a specific task
- **New Features**:
  - Auto-execute option when creating tasks
  - Background task execution
  - Integration with new orchestrator

##### `src/api/routes/tiktok.py` (NEW)
- **Endpoints**:
  - `POST /api/v1/tiktok/auth`: Generate TikTok OAuth URL (with optional account name)
  - `GET /api/v1/tiktok/callback`: Handle OAuth callback and save credentials
  - `GET /api/v1/tiktok/accounts/{instance_id}`: Get all connected TikTok accounts
  - `POST /api/v1/tiktok/post`: Post content to TikTok (with account selection)
  - `DELETE /api/v1/tiktok/disconnect/{instance_id}/{account_id}`: Disconnect specific account
- **Features**:
  - OAuth 2.0 flow with state validation
  - Automatic token refresh when expired
  - Multiple TikTok accounts per instance
  - Account selection for content posting
  - Sandbox mode content posting

#### Agents

##### Product Orchestrator (`src/agents/product_orchestrator.py`)
- **Complete Rewrite**:
  - Lightweight wrapper that delegates to CrewAI crews
  - Creates ProductTaskCrew for each task
  - No manual orchestration logic
  - Leverages CrewAI's hierarchical process

##### Specialized Agents (Configured in YAML)
- **All agents now support**:
  - Delegation capabilities (configurable)
  - Reasoning and planning
  - Memory and context management
  - Custom LLM configurations
  - Tool assignments

##### Dummy Agent Implementations
- **Status**: 🔄 DUMMY IMPLEMENTATIONS
- **Files**:
  - `market_research.py`: 
    - **Current**: Returns hardcoded market data
    - **TODO**: Integrate with real market research APIs and web scraping
  - `content_writer.py`: 
    - **Current**: Returns template-based content
    - **TODO**: Integrate with GPT-4 for actual content generation
  - `pricing_analyst.py`: 
    - **Current**: Returns random pricing suggestions
    - **TODO**: Implement real pricing analysis with competitor data
  - `seo_specialist.py`: 
    - **Current**: Returns generic SEO tips
    - **TODO**: Integrate with SEO analysis tools and keyword research

### CrewAI Task Execution Flow

1. **Task Creation**: User creates task via API
2. **Orchestrator Initialization**: ProductOrchestrator creates ProductTaskCrew
3. **Task Interpretation**: Orchestrator agent analyzes task using reasoning
4. **Execution Planning**: Creates structured plan with subtasks
5. **Dynamic Crew Assembly**: Builds crew with required agents
6. **Hierarchical Execution**: Manager LLM coordinates agent collaboration
7. **Delegation & Collaboration**: Agents can delegate and ask questions
8. **Status Updates**: Real-time updates via SharedState
9. **Result Aggregation**: Final output stored in database

### Key Improvements

1. **Native CrewAI Features**:
   - Hierarchical processing with manager LLM
   - Built-in planning capabilities
   - Agent reasoning before execution
   - Automatic delegation handling

2. **Configuration-Driven**:
   - Agents defined in YAML
   - Tasks templates for consistency
   - Easy to add new agents/tasks

3. **Better Orchestration**:
   - No manual delegation logic
   - CrewAI handles agent coordination
   - Structured execution plans

4. **Enhanced Capabilities**:
   - Context window management
   - Memory across executions
   - Structured output support
   - Human-in-the-loop options

### Example Tasks

- "Research competitor pricing for this product"
- "Generate new product images with white background"
- "Write an SEO-optimized product description"

### CrewAI Flows (`src/flows/`)

#### Overview
CrewAI Flows provide a more sophisticated way to orchestrate complex workflows with conditional logic, feedback loops, and state management. This is the recommended approach for workflows that require:
- Multiple evaluation steps
- Retry logic with feedback
- Complex routing decisions
- State persistence across steps

#### Flow Architecture

##### Base Components
- **Flow State Models** (`src/flows/models.py`):
  - `ImageGenerationState`: Pydantic model tracking generation attempts, feedback, and results
  - Ensures type safety and serialization support
  - Tracks errors, attempts, and approval status

##### Image Generation Flow (`src/flows/image_generation_flow.py`)
- **Purpose**: Orchestrates image generation with automatic quality control
- **Key Features**:
  - Uses `@start`, `@router`, and `@listen` decorators for flow control
  - Automatic retry with feedback incorporation
  - State management throughout the process
  - Temporary file cleanup
- **Flow Steps**:
  1. `generate_initial_image()`: Starts generation process
  2. `evaluate_generated_image()`: Routes to evaluation crew
  3. `regenerate_with_feedback()`: Handles retry logic
  4. `finalize_image()`: Stores approved images
  5. `handle_failure()`: Manages error cases
- **Public API**:
  - `generate_image_for_product()`: Async method for external callers
  - `get_generation_status()`: Check current flow status

##### Supporting Crews
- **ImageGenerationCrew** (`src/crews/image_generation_crew.py`):
  - Uses CrewAI's @CrewBase decorator pattern
  - Multimodal agents with vision capabilities
  - Integrated with ImageGenerationTool and ImageStorageTool
  - Accepts feedback from previous attempts
  - Enhanced parsing for extracting generated image paths
  
- **ImageEvaluationCrew** (`src/crews/image_evaluation_crew.py`):
  - Dedicated quality assessment crew with multimodal vision capabilities
  - Compares generated vs reference images using GPT-4o
  - Uses structured output with Pydantic model (`ImageEvaluationOutput`)
  - Provides type-safe evaluation results including:
    - Individual category scores (0-100): visual fidelity, product accuracy, technical quality, professional appearance, e-commerce suitability
    - Overall score (weighted average)
    - Approval decision based on configurable threshold
    - Specific actionable feedback items
    - Strengths and weaknesses analysis
    - Confidence level (High/Medium/Low)
  - Configurable approval thresholds
  - Strict product matching - different products automatically fail
  - No regex parsing needed - leverages CrewAI's `output_pydantic` parameter
  - Handles local file paths by removing file:// prefix for compatibility

#### Flow Tools (`src/tools/flow_tools.py`)

##### ImageGenerationFlowTool
- **Purpose**: Allows agents to trigger image generation flows
- **Features**:
  - Wraps complex flow logic in simple tool interface
  - Manages flow instances per product
  - Handles async execution in sync contexts
- **Integration**: Can be added to any agent's toolset

##### ImageGenerationFlowStatusTool
- **Purpose**: Check status of ongoing generations
- **Returns**: Current state, attempts, approval status, etc.

#### API Integration

##### Flow-Based Endpoints (`src/api/routes/image_generation.py`)
- `POST /images/generate-flow`: Trigger flow-based generation
- `GET /images/flow-status/{product_id}`: Check generation status
- **Models**:
  - `FlowImageGenerationRequest`: Input validation
  - `FlowImageGenerationResponse`: Structured output

#### Integration Patterns

1. **Direct Flow Usage**:
   ```python
   flow = ImageGenerationFlow()
   result = await flow.generate_image_for_product(...)
   ```

2. **Agent Tool Integration**:
   ```python
   from src.tools.flow_tools import create_flow_tools
   generation_tool, status_tool = create_flow_tools()
   agent = Agent(tools=[generation_tool, status_tool])
   ```

3. **Manager Agent Pattern**: See `tests/integration/test_manager_agent_flow.py`

#### Benefits of Flow Architecture

1. **Separation of Concerns**: Each crew focuses on one responsibility
2. **Automatic Orchestration**: Flow handles routing and retries
3. **State Persistence**: Can resume interrupted workflows
4. **Better Error Handling**: Structured error states and recovery
5. **Modularity**: Easy to add new steps or modify flow logic
6. **Testability**: Each component can be tested independently

#### When to Use Flows vs Single Crews

**Use Flows when**:
- Multiple evaluation/decision points
- Retry logic with feedback loops
- Complex conditional routing
- Need to persist state across steps
- Long-running workflows

**Use Single Crews when**:
- Simple, linear workflows
- Single-shot operations
- No retry/feedback needed
- Stateless operations

## Task Queue System (NEW)

### Overview
The task queue system provides scalable background task processing using Celery with Redis as the broker. It supports priority-based routing, retry mechanisms with exponential backoff, and real-time task tracking.

### Components

#### Enhanced Task Model (`src/models/instance.py`)
- **Status**: ✅ Implemented
- **Enhancements**:
  - `TaskPriority` enum: URGENT, NORMAL, LOW
  - Extended `InstanceTaskStatus`: SUBMITTED, QUEUED, PLANNING, ASSIGNED, IN_PROGRESS, REVIEW, COMPLETED, FAILED, CANCELLED, REJECTED
  - New fields: priority, scheduled_for, recurring_pattern, parsed_intent, execution_steps, progress_percentage
  - Output tracking: output_format, output_data, output_media_ids
  - Processing metadata: processing_started_at, processing_ended_at, retry_count, parent_task_id

#### Task Schemas (`src/models/instance_schemas.py`)
- **Status**: ✅ Implemented
- **New Schemas**:
  - `TaskSubmission`: Natural language task submission with priority and scheduling
  - `TaskUpdateRequest`: Update task status and progress
  - `TaskExecutionStep`: Track individual execution steps
  - `TaskListFilters`: Advanced filtering for task queries

#### Base Task Processor (`src/tasks/base_processor.py`)
- **Status**: ✅ Implemented
- **Features**:
  - Abstract base class for all task processors
  - Context manager pattern for database session management
  - Progress tracking and status updates
  - Execution step management
  - CrewAI integration points (ready for implementation)
  - Intent parsing placeholder (to be enhanced with NLP/LLM)

#### Queue Service (`src/tasks/queue_service.py`)
- **Status**: ✅ Implemented
- **Features**:
  - Task submission and lifecycle management
  - Priority-based queue routing (urgent → agents, normal → default, low → background)
  - Intent parsing (🔄 DUMMY: basic keyword matching - TODO: NLP/LLM integration)
  - Processor registration system
  - Task cancellation and retry logic
  - Scheduled task processing

#### Task Processors

##### Default Task Processor (`src/tasks/processors/default_processor.py`)
- **Status**: 🔄 DUMMY IMPLEMENTATION
- **Current**: Simulates task processing with 2-second delay
- **TODO**: Replace with actual task delegation to Manager Agent

##### Content Creation Processor (`src/tasks/processors/content_creation_processor.py`)
- **Status**: 🔄 DUMMY IMPLEMENTATION
- **Current**: 
  - Simulates content creation workflow
  - Returns mock social media content
  - Fake platform optimization
  - Dummy media generation
- **TODO**: 
  - Integrate with real content creation agents
  - Connect to actual image/video generation services
  - Implement real platform-specific optimization
  - Add actual hashtag research

### Celery Integration
- **Status**: ✅ Implemented (reusing existing infrastructure)
- **Configuration**: Three queues with priority routing
- **Retry mechanism**: Exponential backoff with jitter

### Testing
- **Status**: ✅ Comprehensive test suite
- **Coverage**:
  - Base processor unit tests
  - Queue service tests
  - Processor tests (including dummy implementations)
  - WebSocket tests
  - API endpoint tests

### WebSocket Support (`src/core/websocket.py`)
- **Status**: ✅ Implemented
- **Features**:
  - Socket.io integration with FastAPI
  - Real-time task updates (progress, status, execution steps)
  - Instance-based rooms for targeted broadcasts
  - Client subscription management
  - Automatic reconnection handling
- **Events**:
  - Client → Server: `subscribe_instance`, `unsubscribe_instance`
  - Server → Client: `task_update`, `execution_step`, `error`

### Enhanced Task API (`src/api/routes/tasks.py`)
- **Status**: ✅ Implemented
- **Endpoints**:
  - `POST /tasks/instances/{id}/tasks`: Submit task with priority and scheduling
  - `GET /tasks/instances/{id}/tasks`: List tasks with advanced filtering
  - `GET /tasks/tasks/{id}`: Get task details
  - `GET /tasks/tasks/{id}/status`: Get detailed status including Celery info
  - `PATCH /tasks/tasks/{id}`: Update task properties
  - `POST /tasks/tasks/{id}/cancel`: Cancel pending/running task
  - `POST /tasks/tasks/{id}/retry`: Retry failed task
- **Filtering Options**:
  - By status, priority, creation date, scheduled date
  - Pagination with limit/offset
  - Combines database and Celery status

### Scheduled Task Runner (`src/tasks/scheduled_runner.py`)
- **Status**: ✅ Implemented
- **Features**:
  - Celery Beat integration for periodic execution
  - Processes scheduled tasks every 5 minutes
  - Automatic retry on failure

## Dummy Implementations

The following components have placeholder/dummy implementations that need to be replaced:

### Authentication & Authorization
- **`src/api/deps.py`**: 
  - `get_current_user()` returns hardcoded test user (UUID: "00000000-0000-0000-0000-000000000000")
  - TODO: Implement JWT-based authentication or OAuth
  - Used by all protected endpoints (instances, tasks, TikTok)

### Task Processing
- **`src/tasks/processors/default_processor.py`**:
  - Simulates processing with 2-second delay
  - TODO: Integrate with Manager Agent for real task execution
  
- **`src/tasks/processors/content_creation_processor.py`**:
  - Returns mock social media content
  - TODO: Integrate with real content creation agents and image/video generation

### Agent Implementations
- **`src/agents/market_research.py`**:
  - Returns hardcoded market data
  - TODO: Integrate with market research APIs and web scraping
  
- **`src/agents/content_writer.py`**:
  - Returns template-based content
  - TODO: Integrate with GPT-4 for content generation
  
- **`src/agents/pricing_analyst.py`**:
  - Returns random pricing suggestions
  - TODO: Implement real pricing analysis with competitor data
  
- **`src/agents/seo_specialist.py`**:
  - Returns generic SEO tips
  - TODO: Integrate with SEO tools and keyword research

### Intent Parsing
- **`src/tasks/queue_service.py`**:
  - Basic keyword matching for intent detection
  - TODO: Integrate NLP/LLM for sophisticated intent parsing

### Async Image Generation
- **`src/api/routes/image_generation.py`**:
  - `/api/v1/images/generate-async` returns placeholder response
  - TODO: Implement queue-based async image generation

## Next Steps

1. **Authentication Implementation**:
   - JWT token generation and validation
   - OAuth integration (Google, GitHub)
   - User registration and login endpoints
   - Protected route middleware

2. **Research Workshop Implementation**:
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
   - ✅ Task Management System (completed)

## Deployment

### Railway Production Deployment
- **Platform**: Railway.app
- **URL**: https://swallowtail-production.up.railway.app
- **Configuration**:
  - Root directory: `/backend`
  - Build: Nixpacks with Python 3.11
  - Start command: `python run.py`
  - Port binding: Railway's PORT environment variable
  - Database migrations: Automatic via Alembic
- **Environment Variables**:
  - All sensitive credentials stored in Railway dashboard
  - CORS_ORIGINS configured for production frontend
  - Redis automatically provisioned
- **See**: `railway_deployment.md` for detailed setup guide

## Testing

### Test Runner
A convenient test runner script is provided:
```bash
# List available test categories
python run_tests.py --list

# Run all tests
python run_tests.py all

# Run specific category
python run_tests.py unit          # Unit tests only
python run_tests.py integration   # Integration tests only
python run_tests.py crews         # Crew tests only

# Run with options
python run_tests.py unit -v       # Verbose output
python run_tests.py all -c        # With coverage report
python run_tests.py crews -k "evaluation"  # Match pattern
```

### Test Structure
```
tests/
├── TESTING.md               # Comprehensive testing documentation
├── run_tests.py            # Test runner script
├── conftest.py             # Pytest configuration and fixtures
├── agents/                 # Individual agent tests
├── crews/                  # CrewAI crew implementation tests
├── e2e/                    # End-to-end tests
├── fixtures/               # Test fixtures and data
├── flows/                  # CrewAI flow tests
├── infrastructure/         # Database, storage, Celery tests
├── integration/            # Component interaction tests
├── performance/            # Performance and load tests
├── reference_images/       # Test images for evaluation
├── services/               # External service tests
├── unit/                   # Fast, isolated component tests
└── workflows/              # Legacy workflow tests
```

### Test Categories
- **Unit Tests**: Fast, isolated component tests
  - Model validation tests
  - Crew initialization tests
  - Configuration tests
  
- **Integration Tests**: Component interaction with real services
  - Image evaluation with real images
  - Workflow execution tests
  - Service integration tests
  
- **Crew Tests**: CrewAI crew implementations
  - Evaluation crew tests
  - Generation crew tests
  - Direct execution tests
  
- **Flow Tests**: CrewAI flow orchestrations
  - Flow model tests
  - Flow tool integration
  - Complete flow execution
  
- **Infrastructure Tests**: Core components
  - Database connectivity
  - Storage integration
  - Celery task queue

### Key Test Files

#### Image Evaluation Tests
- `tests/integration/test_image_evaluation_crew.py`: Comprehensive evaluation tests
  - Tests with identical images (high scores expected)
  - Tests with different products (should fail)
  - Structured output validation
  - Error handling for invalid images

#### Reference Images
- `tests/reference_images/`: Test images for evaluation
  - `led-squirtle.jpg`: Primary reference image
  - `led-squirtle2.jpg`: Identical product for matching tests
  - `led-mew.jpg`: Different product for rejection tests

### Running Tests
```bash
# Unit tests only (fast, no dependencies)
poetry run pytest tests/unit/ -v

# Integration tests (requires Redis + Celery worker)
PYTHONPATH=. poetry run pytest -m integration -v

# All tests
PYTHONPATH=. poetry run pytest -v
```