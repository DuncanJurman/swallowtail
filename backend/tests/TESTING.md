# Swallowtail Backend Testing Documentation

## Overview
This document describes the testing structure and files in the Swallowtail backend test suite. Tests are organized by category and purpose to ensure comprehensive coverage of all components.

## Directory Structure

```
tests/
├── agents/              # Individual agent tests
├── crews/               # CrewAI crew implementations
├── e2e/                 # End-to-end tests
├── fixtures/            # Test fixtures and data
├── flows/               # CrewAI flow tests
├── infrastructure/      # Infrastructure component tests
├── integration/         # Integration tests
├── performance/         # Performance and load tests
├── reference_images/    # Test images for evaluation
├── services/            # External service tests
├── unit/                # Unit tests
├── workflows/           # Legacy workflow tests
└── conftest.py          # Pytest configuration
```

## Test Categories

### 1. Unit Tests (`unit/`)
Fast, isolated tests for individual components.

- **`test_image_generation_state.py`**: Tests for the ImageGenerationState Pydantic model
  - State initialization and validation
  - JSON serialization/deserialization
  - Default value handling

- **`test_image_generation_crew.py`**: Unit tests for ImageGenerationCrew
  - Crew initialization
  - Agent and task creation
  - Configuration validation

### 2. Integration Tests (`integration/`)
Tests that verify component interactions with real services.

- **`test_image_evaluation_crew.py`**: Tests ImageEvaluationCrew with real images
  - Evaluates identical images (should approve with high scores)
  - Evaluates different images (should reject with feedback)
  - Tests score parsing and structured output
  - Validates error handling for invalid images
  - Checks evaluation consistency across runs

- **`test_image_generation_workflow.py`**: Tests complete image generation workflow
  - API endpoint integration
  - Workflow execution with real services
  - Error handling and retries

- **`test_image_tool_direct.py`**: Direct testing of image generation tools
  - Tests ImageGenerationTool functionality
  - Validates tool parameters and outputs

- **`test_celery_integration.py`**: Celery task queue integration
  - Task execution and monitoring
  - Queue management
  - Worker communication

- **`test_manager_agent_flow.py`**: Product manager agent workflow
  - Multi-agent coordination
  - Task delegation and results

### 3. Crew Tests (`crews/`)
Tests for CrewAI crew implementations.

- **`test_evaluation_crew.py`**: Basic evaluation crew functionality
  - Crew component creation
  - Configuration validation
  - Does not execute full evaluation

- **`test_image_generation_crew.py`**: Image generation crew tests
  - Tests crew initialization and configuration
  - Validates agent and task setup
  - Tests execution with mock services

- **`test_crew_execution.py`**: General crew execution tests
  - Tests crew kickoff and task flow
  - Validates result handling

- **`test_direct_crew_execution.py`**: Direct crew execution without flows
  - Tests synchronous crew execution
  - Validates immediate result handling

### 4. Flow Tests (`flows/`)
Tests for CrewAI flow implementations.

- **`test_flow_models.py`**: Flow state model tests
  - Tests ImageGenerationState and other flow models
  - Validates state transitions
  - Tests serialization

- **`test_flow_tools.py`**: Flow tool integration tests
  - Tests ImageGenerationFlowTool
  - Tests ImageGenerationFlowStatusTool
  - Validates tool-flow communication

- **`test_image_generation_flow.py`**: Complete flow execution tests
  - Tests flow with quality control loop
  - Validates retry logic with feedback
  - Tests approval/rejection paths

### 5. Infrastructure Tests (`infrastructure/`)
Tests for core infrastructure components.

- **`test_database_setup.py`**: Database connectivity and schema
  - Verifies database connection
  - Checks table existence and structure
  - Validates migrations

- **`test_storage_complete.py`**: Supabase storage integration
  - Tests image upload/download
  - Validates storage URLs
  - Tests optimization features

- **`test_celery.py`**: Basic Celery configuration
  - Tests worker connectivity
  - Validates queue configuration
  - Basic task execution

### 6. Service Tests (`services/`)
Tests for external service integrations.

- **`test_pinecone.py`**: Basic Pinecone vector DB tests
  - Connection validation
  - Basic operations

- **`test_pinecone_integration.py`**: Advanced Pinecone features
  - Vector operations
  - Search functionality
  - Index management

### 7. Agent Tests (`agents/`)
Tests for individual agent implementations.

- **`test_research_workshop.py`**: Research workshop agent tests
- **`test_trend_scanner.py`**: Trend scanner agent tests

### 8. End-to-End Tests (`e2e/`)
Complete user journey tests.

- **`test_led_squirtle_dorm_room.py`**: Full product image generation
  - Tests complete flow from request to final image
  - Validates all stages of generation and evaluation
  - Tests with specific product scenario

### 9. Workflow Tests (`workflows/`)
Legacy workflow implementation tests.

- **`test_image_generation_workflow.py`**: Legacy workflow tests
  - Kept for backward compatibility
  - Tests older workflow patterns

## Test Images (`reference_images/`)

The reference images directory contains test images for evaluation:

- **`led-squirtle.jpg`**: Primary reference image of LED Squirtle product
- **`led-squirtle2.jpg`**: Identical product image for testing matching
- **`led-mew.jpg`**: Different product for testing rejection logic

These images are used to test:
- Product matching accuracy
- Image quality evaluation
- Multimodal agent capabilities

## Running Tests

### Run all tests
```bash
poetry run pytest
```

### Run specific test category
```bash
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/crews/
```

### Run with coverage
```bash
poetry run pytest --cov=src --cov-report=html
```

### Run specific test file
```bash
poetry run pytest tests/integration/test_image_evaluation_crew.py -v
```

### Run tests matching pattern
```bash
poetry run pytest -k "evaluation" -v
```

## Test Configuration

### Environment Variables
Tests require the following environment variables:
- `OPENAI_API_KEY`: For AI model access
- `SUPABASE_URL`: For storage tests
- `SUPABASE_SERVICE_KEY`: For storage tests
- `DATABASE_URL`: For database tests
- `REDIS_URL`: For Celery tests

### Pytest Configuration (`conftest.py`)
Contains shared fixtures and test configuration:
- Database session fixtures
- Mock service fixtures
- Test data generators
- Cleanup utilities

## Best Practices

1. **Test Organization**
   - Place tests in the appropriate category directory
   - Use descriptive test names that explain what is being tested
   - Group related tests in classes

2. **Test Independence**
   - Tests should not depend on each other
   - Clean up resources after each test
   - Use fixtures for shared setup

3. **Mocking**
   - Mock external services in unit tests
   - Use real services only in integration tests
   - Provide clear mock behaviors

4. **Assertions**
   - Use specific assertions over generic ones
   - Test both success and failure cases
   - Validate all important outputs

5. **Performance**
   - Keep unit tests fast (< 1 second)
   - Mark slow tests with `@pytest.mark.slow`
   - Use `@pytest.mark.timeout()` for tests that might hang

## Maintenance

### Adding New Tests
1. Determine the appropriate category
2. Create test file with `test_` prefix
3. Follow existing patterns in that category
4. Update this documentation

### Removing Tests
1. Ensure functionality is covered elsewhere
2. Remove test file
3. Update this documentation

### Test Data
- Keep test data minimal and focused
- Use fixtures for reusable test data
- Store large test files in `fixtures/`