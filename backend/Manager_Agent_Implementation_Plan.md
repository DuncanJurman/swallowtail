# Manager Agent Implementation Plan for Swallowtail

## Overview
The Manager Agent will be the central coordinator for each instance, using CrewAI's hierarchical process to analyze natural language tasks, create execution plans, and delegate to specialist agents. The system will be modular and extensible, allowing easy addition of new agents, tools, and workflows.

## Architecture Design

### 1. Manager Agent Structure
- **Base Manager Agent Class**: Extends CrewAI Agent with instance-specific configuration
- **Task Analysis**: Natural language processing to understand user intent
- **Plan Generation**: Creates structured execution plans
- **Delegation**: Assigns tasks to appropriate specialist agents
- **Progress Monitoring**: Tracks task execution and handles failures

### 2. Agent Registry System
- **Dynamic Agent Loading**: Load agents based on instance type and configuration
- **Agent Capabilities**: Each agent declares its capabilities and required tools
- **Agent Templates**: YAML-based configuration for easy customization

### 3. Flow Integration
- **Task Execution Flow**: Main flow that orchestrates task processing
- **Modular Sub-flows**: Reusable flows for common operations
- **State Management**: Shared state between flow steps

### 4. Tool Management
- **Tool Registry**: Centralized tool management
- **Instance-Scoped Tools**: Tools with instance-specific configuration
- **Tool Validation**: Ensure agents have required tools

## Implementation Plan

### Phase 1: Core Manager Agent (Week 1)
1. **Create Base Manager Agent**
   - `ManagerAgent` class with instance configuration
   - Task analysis capabilities using LLM
   - Plan generation with structured output

2. **Agent Registry**
   - `AgentRegistry` class for dynamic agent management
   - Agent capability declaration system
   - Instance-specific agent configuration

3. **Update Agent Configurations**
   - Convert existing agents.yaml to instance-aware format
   - Add manager agent configuration
   - Define agent capabilities

### Phase 2: Task Execution Flow (Week 1-2)
1. **Main Task Flow**
   - `TaskExecutionFlow` using CrewAI Flow
   - Task state management
   - Error handling and retry logic

2. **Integration Points**
   - Connect to instance task queue
   - Update task status in database
   - Result storage and formatting

3. **Sub-flows**
   - Content generation flow
   - Social media posting flow
   - Analytics flow

### Phase 3: Specialist Agents (Week 2)
1. **Content Creator Agent**
   - Multi-platform content generation
   - Brand voice customization
   - Image integration

2. **Social Media Manager Agent**
   - Platform API integration
   - Scheduling capabilities
   - Engagement tracking

3. **Placeholder Agents**
   - Marketing Analyst Agent
   - Customer Service Agent
   - Product Researcher Agent

### Phase 4: Tools and Integration (Week 2-3)
1. **Platform Tools**
   - Instagram posting tool
   - TikTok integration tool
   - Analytics retrieval tool

2. **Instance Tools**
   - Media library access
   - Brand profile retrieval
   - Configuration management

3. **Utility Tools**
   - Text formatting tool
   - Image processing tool
   - Data analysis tool

## File Structure

```
backend/src/
├── agents/
│   ├── manager/
│   │   ├── __init__.py
│   │   ├── manager_agent.py      # Main manager agent
│   │   ├── task_analyzer.py      # Task analysis logic
│   │   └── plan_generator.py     # Execution plan generation
│   ├── specialists/
│   │   ├── content_creator.py
│   │   ├── social_media_manager.py
│   │   └── marketing_analyst.py  # Placeholder
│   └── registry.py               # Agent registry system
├── config/
│   ├── agents/
│   │   ├── manager.yaml         # Manager agent config
│   │   ├── content_creator.yaml
│   │   └── social_media.yaml
│   └── tools/
│       ├── platform_tools.yaml
│       └── instance_tools.yaml
├── flows/
│   ├── task_execution_flow.py   # Main task processing flow
│   ├── content_flow.py          # Content generation sub-flow
│   └── social_media_flow.py     # Social posting sub-flow
├── tools/
│   ├── platform/
│   │   ├── instagram_tool.py
│   │   └── tiktok_tool.py
│   ├── instance/
│   │   ├── media_library_tool.py
│   │   └── brand_profile_tool.py
│   └── registry.py              # Tool registry system
└── crews/
    ├── instance_crew.py         # Instance-specific crew
    └── task_crew.py            # Task execution crew
```

## Key Implementation Details

### 1. Manager Agent Task Analysis
```python
# Example task analysis structure
{
    "intent": "content_creation",
    "platforms": ["instagram", "tiktok"],
    "content_type": "product_launch",
    "requirements": {
        "tone": "excited",
        "include_images": true,
        "hashtag_strategy": "trending"
    },
    "delegations": [
        {
            "agent": "content_creator",
            "task": "Generate launch announcement"
        },
        {
            "agent": "social_media_manager",
            "task": "Schedule and post content"
        }
    ]
}
```

### 2. Agent Capability System
```yaml
# Example agent capability declaration
content_creator:
  capabilities:
    - content_generation
    - copywriting
    - seo_optimization
  supported_platforms:
    - instagram
    - tiktok
    - facebook
  required_tools:
    - text_generation
    - image_analysis
    - brand_profile_access
```

### 3. Flow State Management
- Task ID tracking
- Execution progress
- Agent outputs
- Error logs
- Final results

## Testing Strategy

1. **Unit Tests**
   - Manager agent task analysis
   - Plan generation logic
   - Agent registry operations

2. **Integration Tests**
   - Full task execution flow
   - Multi-agent collaboration
   - Database updates

3. **End-to-End Tests**
   - Complete task submission to result
   - Error handling scenarios
   - Performance benchmarks

## TODO List Implementation

1. [ ] Create ManagerAgent base class with instance configuration
2. [ ] Implement task analysis using structured output
3. [ ] Build plan generation system with delegation logic
4. [ ] Create AgentRegistry for dynamic agent management
5. [ ] Implement TaskExecutionFlow using CrewAI Flow
6. [ ] Connect flow to instance task queue
7. [ ] Create ContentCreatorAgent with brand voice customization
8. [ ] Create SocialMediaManagerAgent with platform integration
9. [ ] Add placeholder agents (MarketingAnalyst, CustomerService)
10. [ ] Build tool registry system
11. [ ] Create instance-specific tools (media library, brand profile)
12. [ ] Add platform integration tools (Instagram, TikTok)
13. [ ] Write comprehensive tests
14. [ ] Create agent configuration templates
15. [ ] Document agent customization process

## Next Steps
After implementing this plan:
1. Add more specialist agents based on user needs
2. Expand platform integrations
3. Implement learning mechanisms
4. Add advanced analytics and reporting