# Image Generation Flow Documentation

## Overview

The Image Generation Flow is a CrewAI Flow-based implementation that orchestrates the complete image generation pipeline with automatic quality control and feedback loops. This architecture replaces the previous single-crew approach with a more modular and maintainable solution.

## Architecture

### Key Components

1. **ImageGenerationFlow** (`src/flows/image_generation_flow.py`)
   - Main orchestrator using CrewAI Flow decorators
   - Manages state throughout the generation process
   - Handles routing between generation and evaluation steps
   - Implements retry logic with feedback incorporation

2. **ImageGenerationCrewV2** (`src/crews/image_generation_crew_v2.py`)
   - Focused solely on image generation
   - Accepts feedback from previous attempts
   - Uses multimodal agents for better understanding

3. **ImageEvaluationCrew** (`src/crews/image_evaluation_crew.py`)
   - Dedicated to quality assessment
   - Compares generated images against reference
   - Provides structured feedback for improvements

4. **ImageGenerationState** (`src/flows/models.py`)
   - Pydantic model for flow state management
   - Tracks attempts, feedback, and results
   - Ensures type safety throughout the flow

## Flow Diagram

```
[Start] → Generate Initial Image → Evaluate Image
   ↑                                      ↓
   ↑                              [Quality Check]
   ↑                                ↙         ↘
   ↑                          Approved      Needs Work
   ↑                              ↓              ↓
   ↑                        Store & Return   [Retry?]
   ↑                                        ↙      ↘
   ↑                                    Yes        No
   ↑                                     ↓          ↓
   ←←←← Regenerate with Feedback ←←←←←←←←      Failed
```

## Integration Patterns

### 1. Direct API Usage

```python
from src.flows.image_generation_flow import ImageGenerationFlow
from uuid import UUID

# Create flow instance
flow = ImageGenerationFlow()

# Execute generation
result = await flow.generate_image_for_product(
    product_id=UUID("..."),
    reference_url="https://...",
    product_info={
        "name": "Product Name",
        "features": ["feature1", "feature2"],
        "style": {"background": "white"},
        "threshold": 0.85
    }
)

# Check result
if result["success"]:
    print(f"Image URL: {result['image_url']}")
    print(f"Attempts: {result['attempts']}")
```

### 2. Agent Tool Integration

```python
from src.tools.flow_tools import create_flow_tools
from crewai import Agent

# Create tools
generation_tool, status_tool = create_flow_tools()

# Create agent with tools
agent = Agent(
    role="Product Manager",
    tools=[generation_tool, status_tool],
    # ... other config
)

# Agent can now use tools in tasks
```

### 3. REST API Endpoints

```bash
# Generate image using flow
POST /api/v1/images/generate-flow
{
    "product_id": "uuid-here",
    "reference_image_url": "https://...",
    "product_name": "Product Name",
    "product_features": ["feature1", "feature2"],
    "style_requirements": {"background": "white"},
    "approval_threshold": 0.85
}

# Check status (requires persistent storage implementation)
GET /api/v1/images/flow-status/{product_id}
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for image generation and evaluation
- `OPENAI_MODEL`: Model for evaluation (default: gpt-4o)
- `OPENAI_IMAGE_MODEL`: Model for generation (default: gpt-image-1)

### Flow Parameters

- `max_attempts`: Maximum generation attempts (default: 3)
- `approval_threshold`: Quality threshold 0-1 (default: 0.85)
- `style_requirements`: Custom style preferences
- `product_features`: Key features to emphasize

## Error Handling

The flow implements comprehensive error handling:

1. **Generation Failures**: Logged and stored in state
2. **Evaluation Errors**: Graceful fallback to failed state
3. **API Errors**: Proper error propagation with context
4. **File I/O Errors**: Automatic cleanup of temporary files

## Best Practices

### 1. State Management
- Always check flow state before operations
- Use structured feedback format
- Clean up temporary resources

### 2. Integration
- Reuse flow instances for the same product when possible
- Implement proper status tracking for async operations
- Use appropriate approval thresholds for different product types

### 3. Performance
- Set reasonable max_attempts based on cost/quality trade-offs
- Implement caching for reference images
- Consider batch processing for multiple products

## Extending the Flow

### Adding Custom Evaluation Criteria

```python
class CustomEvaluationCrew(ImageEvaluationCrew):
    def evaluate(self):
        result = super().evaluate()
        # Add custom criteria
        result["custom_score"] = self.evaluate_custom_criteria()
        return result
```

### Implementing Persistent State

```python
# Example Redis-based persistence
class PersistentImageGenerationFlow(ImageGenerationFlow):
    def __init__(self, redis_client):
        super().__init__()
        self.redis = redis_client
    
    async def generate_image_for_product(self, ...):
        # Save state to Redis
        self.redis.set(f"flow:{product_id}", self.state.json())
        # ... rest of implementation
```

## Troubleshooting

### Common Issues

1. **"No module named 'flows'"**
   - Ensure PYTHONPATH includes project root
   - Check imports use relative paths

2. **Token Limit Errors**
   - Flow passes file paths, not base64 data
   - Check image sizes aren't excessive

3. **Evaluation Always Fails**
   - Verify reference image is accessible
   - Check approval threshold isn't too high
   - Review evaluation crew prompts

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger("ImageGenerationFlow").setLevel(logging.DEBUG)
```

## Migration from V1

If migrating from the previous single-crew approach:

1. Replace `ImageGenerationCrew` with `ImageGenerationFlow`
2. Update API calls to use flow endpoints
3. Adjust error handling for flow-specific responses
4. Update monitoring to track flow states

## Future Enhancements

- **Distributed Execution**: Support for running crews on different workers
- **A/B Testing**: Compare different generation strategies
- **Analytics**: Track success rates and optimization opportunities
- **Template System**: Predefined styles for common product categories