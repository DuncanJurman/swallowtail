# Task Queue System Implementation Plan

## Strategic Rationale

Building the task queue first makes sense because:

1. **User Validation**: You can test the UX of task submission and tracking before AI complexity
2. **Foundation First**: The Manager Agent needs a robust queue to work with
3. **Incremental Development**: You can add simple task processors before full AI agents
4. **Early Feedback**: Users can start submitting tasks and you can analyze patterns
5. **Risk Reduction**: Separates infrastructure concerns from AI implementation challenges

## Core Features for MVP

### Backend Requirements

#### 1. Task Queue Infrastructure
- **Real-time Updates**: WebSocket or Server-Sent Events for live status updates
- **Task Persistence**: All tasks stored in PostgreSQL with full history
- **Queue Management**: Redis for fast queue operations
- **Background Processing**: Celery or similar for async task execution
- **Retry Logic**: Automatic retries with exponential backoff
- **Priority System**: Handle urgent tasks first

#### 2. Task Status Lifecycle
```
SUBMITTED → QUEUED → PLANNING → ASSIGNED → IN_PROGRESS → REVIEW → COMPLETED
                ↓           ↓          ↓           ↓          ↓
              FAILED      FAILED    FAILED     FAILED    REJECTED
```

#### 3. Task Data Model Enhancements
- **Structured Input**: Parse natural language into structured format
- **Execution Plan**: Store step-by-step plan (even if manual initially)
- **Progress Tracking**: Percentage complete and current step
- **Result Storage**: Structured output with media attachments
- **Audit Trail**: Who did what and when

### Frontend Requirements

#### 1. Task Submission Interface
- **Natural Language Input**: Large text area with examples
- **Media Attachments**: Drag-and-drop for reference images (Would be nice to also load existing uploaded photos for a given instance that the user can select to reference)
- **Priority Selection**: Urgent, normal, low
- **Schedule Option**: "Do now", "Do this at X time" or "recurring at X time"

#### 2. Task Dashboard
- **Kanban View**: Columns for each status
- **List View**: Sortable table with filters
- **Timeline View**: Gantt-style for scheduled tasks
- **Quick Actions**: One-click retry, cancel, duplicate

#### 3. Task Detail View
- **Live Status Updates**: Real-time progress indicator
- **Execution Plan**: See planned steps (even if manual)
- **Activity Log**: Detailed timeline of actions
- **Results Display**: Rich media output with downloads (would be the output of the ai agents, mock for now)
- **Feedback Options**: Approve, reject, request changes

## Implementation Plan

### Phase 1: Core Backend Infrastructure

#### Day 1-2: Enhanced Task Model
```python
# Additional fields for task model
class InstanceTask:
    # Existing fields...
    
    # New fields
    priority = Column(Enum(Priority), default=Priority.NORMAL)
    scheduled_for = Column(DateTime, nullable=True)
    recurring_pattern = Column(JSONB, nullable=True)  # RRULE format
    
    # Structured data
    parsed_intent = Column(JSONB)  # {intent, entities, parameters}
    execution_steps = Column(JSONB)  # [{step, status, output}]
    progress_percentage = Column(Integer, default=0)
    
    # Results
    output_format = Column(String)  # text, json, media
    output_data = Column(JSONB)
    output_media_ids = Column(JSONB)  # Generated media
    
    # Metadata
    processing_started_at = Column(DateTime)
    processing_ended_at = Column(DateTime)
    retry_count = Column(Integer, default=0)
    parent_task_id = Column(UUID)  # For subtasks
```

#### Day 3-4: Queue Infrastructure
- Set up Celery with Redis broker
- Create task processor base class
- Implement retry mechanisms
- Add task routing by priority

#### Day 5: WebSocket
- Real-time status updates
- Progress notifications
- Result delivery

### Phase 2: Core API Endpoints 

#### Essential Task Endpoints
```python
# Core task operations
POST   /instances/{id}/tasks          # Submit task
GET    /instances/{id}/tasks          # List tasks with filters
GET    /instances/{id}/tasks/{tid}    # Get task details
PATCH  /instances/{id}/tasks/{tid}    # Update task (cancel, retry)
DELETE /instances/{id}/tasks/{tid}    # Delete task

# Real-time updates
WS     /instances/{id}/tasks/stream   # WebSocket for live updates
```

### Phase 3: Frontend Task Management 

#### Component Structure
```
frontend/src/
├── components/
│   ├── tasks/
│   │   ├── TaskSubmissionForm.tsx
│   │   ├── TaskTemplateGallery.tsx
│   │   ├── TaskQueue.tsx
│   │   ├── TaskCard.tsx
│   │   └── TaskDetail.tsx
│   └── shared/
│       ├── MediaUploader.tsx
│       └── RealtimeStatus.tsx
├── hooks/
│   ├── useTaskQueue.ts
│   ├── useTaskTemplates.ts
│   └── useRealtimeUpdates.ts
└── stores/
    └── taskStore.ts
```

### Phase 4: Simple Task Processors 

#### Dummy Processors for Testing
1. **Echo Processor**: Returns formatted version of input
2. **Mock Content Generator**: Returns Lorem Ipsum style content
3. **Delay Processor**: Simulates long-running tasks
4. **Random Failure**: Tests retry logic

This allows full system testing before AI integration.

## Key Technical Decisions

### 1. Queue Technology
**Recommendation**: Celery + Redis
- **Why**: Battle-tested, great Python support, scales well

### 2. Real-time Updates
**Recommendation**: WebSockets with fallback to SSE
- **Why**: Best user experience, broad browser support
- **Implementation**: Socket.io 

### 3. Task Storage
**Recommendation**: PostgreSQL + Redis cache
- **PostgreSQL**: Full task history and search
- **Redis**: Active queue and real-time status

### 4. Frontend Framework
**Recommendation**: React with Zustand for state
- **Why**: You likely already use React, Zustand is simple
- **UI Library**: Shadcn/ui or MUI for rapid development

## MVP Feature Set

### Must Have
1. Submit tasks via natural language
2. View task queue with real-time updates
3. See task details and results
4. Basic retry/cancel functionality
5. Simple priority system

### Nice to Have
1. Task templates
2. Recurring tasks
3. Batch operations
4. Export functionality

### Post-MVP
1. Task dependencies
2. Conditional workflows
3. Advanced scheduling
4. Team collaboration
5. API access for external systems

## Success Metrics

1. **Task Submission Rate**: >10 tasks/day/instance
2. **Queue Performance**: <100ms to queue a task
3. **Update Latency**: <500ms for status updates
4. **UI Responsiveness**: <200ms for all interactions
5. **System Reliability**: >99.9% uptime

## Migration Path to AI

The beautiful part of this approach is that once the queue system is working:

1. **Phase 1**: Replace dummy processors with simple AI agents
2. **Phase 2**: Add the Manager Agent to analyze and route tasks
3. **Phase 3**: Implement full CrewAI orchestration
4. **Phase 4**: Add learning and optimization

Each phase can be rolled out gradually without disrupting the user experience.

## Risk Mitigation

1. **Scalability**: Design for 1000x current load from day one
2. **Reliability**: Implement circuit breakers and fallbacks
3. **Security**: Rate limiting and input validation
4. **Monitoring**: Comprehensive logging and alerting
5. **Testing**: Unit, integration, and load tests

This approach gives you a solid foundation that users can start using immediately, while providing a clear path to the full AI-powered vision.


Task Queue Implementation TODO List

  Phase 1: Backend Infrastructure Foundation

  Goal: Establish core task model and queue 
  system that CrewAI agents can easily 
  integrate with

  1. Enhanced Task Model (2 days)

  - Update InstanceTask model with new
  fields
    - Add priority enum (URGENT, NORMAL,
  LOW)
    - Add scheduled_for and
  recurring_pattern fields
    - Add parsed_intent JSONB field for
  structured task data
    - Add execution_steps JSONB field for
  tracking agent actions
    - Add progress_percentage integer field
    - Add output fields (format, data,
  media_ids)
    - Add processing timestamps and
  retry_count
    - Add parent_task_id for future subtask
  support
  - Create Alembic migration for task model
  updates
  - Update Pydantic schemas
    - Enhance TaskSubmission with priority
  and scheduling
    - Create TaskUpdateRequest for progress
  updates
    - Create TaskExecutionStep schema for
  agent reporting
  - Write unit tests for new model fields

  2. Queue Infrastructure Setup (2 days)

  - Install and configure Celery with Redis
  broker
    - Add Celery to poetry dependencies
    - Create celery_app.py configuration
    - Configure Redis connection for queue
  - Create base task processor class
    - BaseTaskProcessor with standard
  interface
    - Progress reporting mechanism
    - Error handling and logging
    - CrewAI agent integration points
  - Implement retry mechanism
    - Exponential backoff configuration
    - Max retry limits by task type
    - Dead letter queue for failed tasks
  - Add priority-based task routing
    - Configure Celery priority queues
    - Route urgent tasks to dedicated
  workers

  3. WebSocket Infrastructure (1 day)

  - Set up Socket.io server
    - Add python-socketio to dependencies
    - Create WebSocket namespace for tasks
    - Configure CORS for frontend
  - Implement real-time events
    - Task status change notifications
    - Progress update events
    - Result delivery events
  - Create WebSocket authentication
    - Instance-based room management
    - User authentication via tokens

  Phase 2: API Development

  Goal: RESTful + WebSocket APIs that 
  support natural language tasks and CrewAI 
  integration

  4. Core Task API Endpoints (2 days)

  - Enhance existing task submission
  endpoint
    - Parse natural language into structured
   intent
    - Handle priority and scheduling options
    - Validate media attachments
    - Queue task with Celery
  - Implement task listing with filters
    - Filter by status, priority, date range
    - Pagination support
    - Sort by created_at, priority
  - Create task detail endpoint
    - Include execution steps
    - Show current progress
    - Return results when complete
  - Add task update endpoint
    - Cancel running tasks
    - Retry failed tasks
    - Update priority
  - Implement task deletion
    - Soft delete with status
    - Clean up associated media

  5. WebSocket API (1 day)

  - Create Socket.io event handlers
    - Connection management
    - Subscribe to instance tasks
    - Unsubscribe on disconnect
  - Implement task event emitters
    - Emit from Celery tasks
    - Emit from API updates
    - Handle connection failures

  Phase 3: Task Processing System

  Goal: Dummy processors that simulate 
  CrewAI agent behavior for testing

  6. Task Processor Framework (2 days)

  - Create processor registry system
    - Register processors by task intent
    - Dynamic processor loading
    - Processor capability declaration
  - Implement dummy processors
    - EchoProcessor - formats and returns
  input
    - MockContentProcessor - generates
  sample content
    - DelayProcessor - simulates long tasks
    - RandomFailureProcessor - tests retry
  logic
  - Add progress reporting
    - Update task progress in database
    - Emit WebSocket events
    - Log execution steps

  7. Task Intent Parser (1 day)

  - Create basic NLP intent parser
    - Identify task type (content, social,
  research)
    - Extract platforms mentioned
    - Parse scheduling requirements
    - Identify referenced media
  - Map intents to processors
    - Intent to processor mapping
    - Default processor fallback
    - Future CrewAI agent mapping

  Phase 4: Frontend Implementation

  Goal: User interface for natural language 
  task submission and monitoring

  8. Task Submission Interface (2 days)

  - Create TaskSubmissionForm component
    - Natural language textarea with
  placeholder examples
    - Priority selector (urgent/normal/low)
    - Schedule selector (now/specific
  time/recurring)
    - Media attachment area
  - Implement media selection
    - Show existing instance media gallery
    - Drag-and-drop for new uploads
    - Multiple selection support
    
  9. Task Dashboard Views (2 days)

  - Create TaskQueue component
    - Kanban view by status
    - List view with sorting
    - Real-time status updates
  - Implement TaskCard component
    - Show task summary
    - Display current status
    - Quick action buttons
    - Progress indicator
  - Build TaskDetail modal
    - Full task information
    - Execution steps timeline
    - Results display area
    - Action buttons (retry/cancel)

  10. Real-time Integration (1 day)

  - Create useRealtimeUpdates hook
    - Socket.io connection management
    - Auto-reconnection logic
    - Event subscription
  - Implement task store with Zustand
    - Task list state
    - Real-time updates
    - Optimistic UI updates
  - Add notifications
    - Task completion alerts
    - Error notifications
    - Progress milestones

  Phase 5: Integration & Testing

  Goal: Ensure system is ready for CrewAI 
  agent integration

  11. Integration Preparation (1 day)

  - Create CrewAI integration points
    - Agent result formatter
    - Execution step transformer
    - Media output handler
  - Add task result schemas
    - Text content results
    - Generated media results
    - Analytics results
  - Document processor interface
    - Required methods
    - Progress reporting
    - Result format

  12. Testing & Validation (2 days)

  - Write integration tests
    - Full task lifecycle tests
    - WebSocket event tests
    - Retry mechanism tests
  - Load testing
    - Queue performance with 100+ tasks
    - WebSocket with multiple connections
    - Database query optimization
  - User acceptance testing
    - Task submission flow
    - Real-time updates
    - Error scenarios

  Success Criteria for MVP

  1. Users can submit natural language tasks
  2. Tasks are queued and processed by dummy
   processors
  3. Real-time status updates via WebSocket
  4. Basic retry and cancellation
  functionality
  5. Results displayed in UI (mocked AI
  output)
  6. System architecture ready for CrewAI
  integration

  Notes for CrewAI Integration

  - Task parsed_intent field will store
  Manager Agent's analysis
  - execution_steps will track each agent's
  actions
  - Processors will be replaced with CrewAI
  crews
  - WebSocket events will report agent
  progress
  - Result format supports multi-agent
  outputs

  This implementation provides a solid
  foundation that users can interact with
  immediately, while being designed from the
   ground up to support the full CrewAI
  multi-agent system described in
  Project-Overview.md.



  I've successfully implemented the core MVP
   functionality for the Task Queue System:

  ✅ Completed:

  1. Enhanced Task Model - Added priority,
  scheduling, execution tracking
  2. Database Migration - Updated schema
  with new fields
  3. Pydantic Schemas - Full validation for
  task operations
  4. Celery Integration - Reused existing
  infrastructure with retry mechanisms
  5. Base Task Processor - Abstract class
  with CrewAI integration points
  6. Queue Service - Complete task lifecycle
   management
  7. Dummy Processors - Default and Content
  Creation for testing
  8. WebSocket Support - Real-time updates
  via Socket.io
  9. Enhanced API - Comprehensive task
  endpoints with filtering
  10. Scheduled Runner - Celery Beat for
  periodic task processing
  11. Comprehensive Tests - Unit,
  integration, and API tests
  12. Documentation - WebSocket guide and
  updated backend.md

  🔄 Dummy Implementations (marked in 
  backend.md):

  - Task Processors: Return mock data, ready
   for real agent integration
  - Intent Parsing: Basic keyword matching,
  ready for NLP/LLM
  - Async Image Generation: Placeholder
  endpoint

  Key Features:

  - Priority-based routing: Urgent → agents
  queue, Normal → default, Low → background
  - Real-time updates: WebSocket broadcasts
  for progress and status
  - Advanced filtering: By status, priority,
   dates with pagination
  - Retry mechanism: Exponential backoff
  with jitter
  - Scheduled tasks: Support for future and
  recurring tasks

  The system is now ready for:
  1. Integration with the Manager Agent and
  CrewAI hierarchical processing
  2. Real agent implementations to replace
  dummy processors
  3. Frontend development for task
  submission and monitoring
  4. Production deployment with proper
  authentication