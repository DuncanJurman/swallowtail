# Agents

> Detailed guide on creating and managing agents within the CrewAI framework.

## Overview of an Agent

In the CrewAI framework, an `Agent` is an autonomous unit that can:

* Perform specific tasks
* Make decisions based on its role and goal
* Use tools to accomplish objectives
* Communicate and collaborate with other agents
* Maintain memory of interactions
* Delegate tasks when allowed

<Tip>
  Think of an agent as a specialized team member with specific skills, expertise, and responsibilities. For example, a `Researcher` agent might excel at gathering and analyzing information, while a `Writer` agent might be better at creating content.
</Tip>

<Note type="info" title="Enterprise Enhancement: Visual Agent Builder">
  CrewAI Enterprise includes a Visual Agent Builder that simplifies agent creation and configuration without writing code. Design your agents visually and test them in real-time.

  ![Visual Agent Builder Screenshot](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/enterprise/crew-studio-interface.png)

  The Visual Agent Builder enables:

  * Intuitive agent configuration with form-based interfaces
  * Real-time testing and validation
  * Template library with pre-configured agent types
  * Easy customization of agent attributes and behaviors
</Note>

## Agent Attributes

| Attribute                               | Parameter                | Type                                  | Description                                                                                              |
| :-------------------------------------- | :----------------------- | :------------------------------------ | :------------------------------------------------------------------------------------------------------- |
| **Role**                                | `role`                   | `str`                                 | Defines the agent's function and expertise within the crew.                                              |
| **Goal**                                | `goal`                   | `str`                                 | The individual objective that guides the agent's decision-making.                                        |
| **Backstory**                           | `backstory`              | `str`                                 | Provides context and personality to the agent, enriching interactions.                                   |
| **LLM** *(optional)*                    | `llm`                    | `Union[str, LLM, Any]`                | Language model that powers the agent. Defaults to the model specified in `OPENAI_MODEL_NAME` or "gpt-4". |
| **Tools** *(optional)*                  | `tools`                  | `List[BaseTool]`                      | Capabilities or functions available to the agent. Defaults to an empty list.                             |
| **Function Calling LLM** *(optional)*   | `function_calling_llm`   | `Optional[Any]`                       | Language model for tool calling, overrides crew's LLM if specified.                                      |
| **Max Iterations** *(optional)*         | `max_iter`               | `int`                                 | Maximum iterations before the agent must provide its best answer. Default is 20.                         |
| **Max RPM** *(optional)*                | `max_rpm`                | `Optional[int]`                       | Maximum requests per minute to avoid rate limits.                                                        |
| **Max Execution Time** *(optional)*     | `max_execution_time`     | `Optional[int]`                       | Maximum time (in seconds) for task execution.                                                            |
| **Verbose** *(optional)*                | `verbose`                | `bool`                                | Enable detailed execution logs for debugging. Default is False.                                          |
| **Allow Delegation** *(optional)*       | `allow_delegation`       | `bool`                                | Allow the agent to delegate tasks to other agents. Default is False.                                     |
| **Step Callback** *(optional)*          | `step_callback`          | `Optional[Any]`                       | Function called after each agent step, overrides crew callback.                                          |
| **Cache** *(optional)*                  | `cache`                  | `bool`                                | Enable caching for tool usage. Default is True.                                                          |
| **System Template** *(optional)*        | `system_template`        | `Optional[str]`                       | Custom system prompt template for the agent.                                                             |
| **Prompt Template** *(optional)*        | `prompt_template`        | `Optional[str]`                       | Custom prompt template for the agent.                                                                    |
| **Response Template** *(optional)*      | `response_template`      | `Optional[str]`                       | Custom response template for the agent.                                                                  |
| **Allow Code Execution** *(optional)*   | `allow_code_execution`   | `Optional[bool]`                      | Enable code execution for the agent. Default is False.                                                   |
| **Max Retry Limit** *(optional)*        | `max_retry_limit`        | `int`                                 | Maximum number of retries when an error occurs. Default is 2.                                            |
| **Respect Context Window** *(optional)* | `respect_context_window` | `bool`                                | Keep messages under context window size by summarizing. Default is True.                                 |
| **Code Execution Mode** *(optional)*    | `code_execution_mode`    | `Literal["safe", "unsafe"]`           | Mode for code execution: 'safe' (using Docker) or 'unsafe' (direct). Default is 'safe'.                  |
| **Multimodal** *(optional)*             | `multimodal`             | `bool`                                | Whether the agent supports multimodal capabilities. Default is False.                                    |
| **Inject Date** *(optional)*            | `inject_date`            | `bool`                                | Whether to automatically inject the current date into tasks. Default is False.                           |
| **Date Format** *(optional)*            | `date_format`            | `str`                                 | Format string for date when inject\_date is enabled. Default is "%Y-%m-%d" (ISO format).                 |
| **Reasoning** *(optional)*              | `reasoning`              | `bool`                                | Whether the agent should reflect and create a plan before executing a task. Default is False.            |
| **Max Reasoning Attempts** *(optional)* | `max_reasoning_attempts` | `Optional[int]`                       | Maximum number of reasoning attempts before executing the task. If None, will try until ready.           |
| **Embedder** *(optional)*               | `embedder`               | `Optional[Dict[str, Any]]`            | Configuration for the embedder used by the agent.                                                        |
| **Knowledge Sources** *(optional)*      | `knowledge_sources`      | `Optional[List[BaseKnowledgeSource]]` | Knowledge sources available to the agent.                                                                |
| **Use System Prompt** *(optional)*      | `use_system_prompt`      | `Optional[bool]`                      | Whether to use system prompt (for o1 model support). Default is True.                                    |

## Creating Agents

There are two ways to create agents in CrewAI: using **YAML configuration (recommended)** or defining them **directly in code**.

### YAML Configuration (Recommended)

Using YAML configuration provides a cleaner, more maintainable way to define agents. We strongly recommend using this approach in your CrewAI projects.

After creating your CrewAI project as outlined in the [Installation](/en/installation) section, navigate to the `src/latest_ai_development/config/agents.yaml` file and modify the template to match your requirements.

<Note>
  Variables in your YAML files (like `{topic}`) will be replaced with values from your inputs when running the crew:

  ```python Code
  crew.kickoff(inputs={'topic': 'AI Agents'})
  ```
</Note>

Here's an example of how to configure agents using YAML:

```yaml agents.yaml
# src/latest_ai_development/config/agents.yaml
researcher:
  role: >
    {topic} Senior Data Researcher
  goal: >
    Uncover cutting-edge developments in {topic}
  backstory: >
    You're a seasoned researcher with a knack for uncovering the latest
    developments in {topic}. Known for your ability to find the most relevant
    information and present it in a clear and concise manner.

reporting_analyst:
  role: >
    {topic} Reporting Analyst
  goal: >
    Create detailed reports based on {topic} data analysis and research findings
  backstory: >
    You're a meticulous analyst with a keen eye for detail. You're known for
    your ability to turn complex data into clear and concise reports, making
    it easy for others to understand and act on the information you provide.
```

To use this YAML configuration in your code, create a crew class that inherits from `CrewBase`:

```python Code
# src/latest_ai_development/crew.py
from crewai import Agent, Crew, Process
from crewai.project import CrewBase, agent, crew
from crewai_tools import SerperDevTool

@CrewBase
class LatestAiDevelopmentCrew():
  """LatestAiDevelopment crew"""

  agents_config = "config/agents.yaml"

  @agent
  def researcher(self) -> Agent:
    return Agent(
      config=self.agents_config['researcher'], # type: ignore[index]
      verbose=True,
      tools=[SerperDevTool()]
    )

  @agent
  def reporting_analyst(self) -> Agent:
    return Agent(
      config=self.agents_config['reporting_analyst'], # type: ignore[index]
      verbose=True
    )
```

<Note>
  The names you use in your YAML files (`agents.yaml`) should match the method names in your Python code.
</Note>

### Direct Code Definition

You can create agents directly in code by instantiating the `Agent` class. Here's a comprehensive example showing all available parameters:

```python Code
from crewai import Agent
from crewai_tools import SerperDevTool

# Create an agent with all available parameters
agent = Agent(
    role="Senior Data Scientist",
    goal="Analyze and interpret complex datasets to provide actionable insights",
    backstory="With over 10 years of experience in data science and machine learning, "
              "you excel at finding patterns in complex datasets.",
    llm="gpt-4",  # Default: OPENAI_MODEL_NAME or "gpt-4"
    function_calling_llm=None,  # Optional: Separate LLM for tool calling
    verbose=False,  # Default: False
    allow_delegation=False,  # Default: False
    max_iter=20,  # Default: 20 iterations
    max_rpm=None,  # Optional: Rate limit for API calls
    max_execution_time=None,  # Optional: Maximum execution time in seconds
    max_retry_limit=2,  # Default: 2 retries on error
    allow_code_execution=False,  # Default: False
    code_execution_mode="safe",  # Default: "safe" (options: "safe", "unsafe")
    respect_context_window=True,  # Default: True
    use_system_prompt=True,  # Default: True
    multimodal=False,  # Default: False
    inject_date=False,  # Default: False
    date_format="%Y-%m-%d",  # Default: ISO format
    reasoning=False,  # Default: False
    max_reasoning_attempts=None,  # Default: None
    tools=[SerperDevTool()],  # Optional: List of tools
    knowledge_sources=None,  # Optional: List of knowledge sources
    embedder=None,  # Optional: Custom embedder configuration
    system_template=None,  # Optional: Custom system prompt template
    prompt_template=None,  # Optional: Custom prompt template
    response_template=None,  # Optional: Custom response template
    step_callback=None,  # Optional: Callback function for monitoring
)
```

Let's break down some key parameter combinations for common use cases:

#### Basic Research Agent

```python Code
research_agent = Agent(
    role="Research Analyst",
    goal="Find and summarize information about specific topics",
    backstory="You are an experienced researcher with attention to detail",
    tools=[SerperDevTool()],
    verbose=True  # Enable logging for debugging
)
```

#### Code Development Agent

```python Code
dev_agent = Agent(
    role="Senior Python Developer",
    goal="Write and debug Python code",
    backstory="Expert Python developer with 10 years of experience",
    allow_code_execution=True,
    code_execution_mode="safe",  # Uses Docker for safety
    max_execution_time=300,  # 5-minute timeout
    max_retry_limit=3  # More retries for complex code tasks
)
```

#### Long-Running Analysis Agent

```python Code
analysis_agent = Agent(
    role="Data Analyst",
    goal="Perform deep analysis of large datasets",
    backstory="Specialized in big data analysis and pattern recognition",
    memory=True,
    respect_context_window=True,
    max_rpm=10,  # Limit API calls
    function_calling_llm="gpt-4o-mini"  # Cheaper model for tool calls
)
```

#### Custom Template Agent

```python Code
custom_agent = Agent(
    role="Customer Service Representative",
    goal="Assist customers with their inquiries",
    backstory="Experienced in customer support with a focus on satisfaction",
    system_template="""<|start_header_id|>system<|end_header_id|>
                        {{ .System }}<|eot_id|>""",
    prompt_template="""<|start_header_id|>user<|end_header_id|>
                        {{ .Prompt }}<|eot_id|>""",
    response_template="""<|start_header_id|>assistant<|end_header_id|>
                        {{ .Response }}<|eot_id|>""",
)
```

#### Date-Aware Agent with Reasoning

```python Code
strategic_agent = Agent(
    role="Market Analyst",
    goal="Track market movements with precise date references and strategic planning",
    backstory="Expert in time-sensitive financial analysis and strategic reporting",
    inject_date=True,  # Automatically inject current date into tasks
    date_format="%B %d, %Y",  # Format as "May 21, 2025"
    reasoning=True,  # Enable strategic planning
    max_reasoning_attempts=2,  # Limit planning iterations
    verbose=True
)
```

#### Reasoning Agent

```python Code
reasoning_agent = Agent(
    role="Strategic Planner",
    goal="Analyze complex problems and create detailed execution plans",
    backstory="Expert strategic planner who methodically breaks down complex challenges",
    reasoning=True,  # Enable reasoning and planning
    max_reasoning_attempts=3,  # Limit reasoning attempts
    max_iter=30,  # Allow more iterations for complex planning
    verbose=True
)
```

#### Multimodal Agent

```python Code
multimodal_agent = Agent(
    role="Visual Content Analyst",
    goal="Analyze and process both text and visual content",
    backstory="Specialized in multimodal analysis combining text and image understanding",
    multimodal=True,  # Enable multimodal capabilities
    verbose=True
)
```

### Parameter Details

#### Critical Parameters

* `role`, `goal`, and `backstory` are required and shape the agent's behavior
* `llm` determines the language model used (default: OpenAI's GPT-4)

#### Memory and Context

* `memory`: Enable to maintain conversation history
* `respect_context_window`: Prevents token limit issues
* `knowledge_sources`: Add domain-specific knowledge bases

#### Execution Control

* `max_iter`: Maximum attempts before giving best answer
* `max_execution_time`: Timeout in seconds
* `max_rpm`: Rate limiting for API calls
* `max_retry_limit`: Retries on error

#### Code Execution

* `allow_code_execution`: Must be True to run code
* `code_execution_mode`:
  * `"safe"`: Uses Docker (recommended for production)
  * `"unsafe"`: Direct execution (use only in trusted environments)

<Note>
  This runs a default Docker image. If you want to configure the docker image, the checkout the Code Interpreter Tool in the tools section.
  Add the code interpreter tool as a tool in the agent as a tool parameter.
</Note>

#### Advanced Features

* `multimodal`: Enable multimodal capabilities for processing text and visual content
* `reasoning`: Enable agent to reflect and create plans before executing tasks
* `inject_date`: Automatically inject current date into task descriptions

#### Templates

* `system_template`: Defines agent's core behavior
* `prompt_template`: Structures input format
* `response_template`: Formats agent responses

<Note>
  When using custom templates, ensure that both `system_template` and `prompt_template` are defined. The `response_template` is optional but recommended for consistent output formatting.
</Note>

<Note>
  When using custom templates, you can use variables like `{role}`, `{goal}`, and `{backstory}` in your templates. These will be automatically populated during execution.
</Note>

## Agent Tools

Agents can be equipped with various tools to enhance their capabilities. CrewAI supports tools from:

* [CrewAI Toolkit](https://github.com/joaomdmoura/crewai-tools)
* [LangChain Tools](https://python.langchain.com/docs/integrations/tools)

Here's how to add tools to an agent:

```python Code
from crewai import Agent
from crewai_tools import SerperDevTool, WikipediaTools

# Create tools
search_tool = SerperDevTool()
wiki_tool = WikipediaTools()

# Add tools to agent
researcher = Agent(
    role="AI Technology Researcher",
    goal="Research the latest AI developments",
    tools=[search_tool, wiki_tool],
    verbose=True
)
```

## Agent Memory and Context

Agents can maintain memory of their interactions and use context from previous tasks. This is particularly useful for complex workflows where information needs to be retained across multiple tasks.

```python Code
from crewai import Agent

analyst = Agent(
    role="Data Analyst",
    goal="Analyze and remember complex data patterns",
    memory=True,  # Enable memory
    verbose=True
)
```

<Note>
  When `memory` is enabled, the agent will maintain context across multiple interactions, improving its ability to handle complex, multi-step tasks.
</Note>

## Context Window Management

CrewAI includes sophisticated automatic context window management to handle situations where conversations exceed the language model's token limits. This powerful feature is controlled by the `respect_context_window` parameter.

### How Context Window Management Works

When an agent's conversation history grows too large for the LLM's context window, CrewAI automatically detects this situation and can either:

1. **Automatically summarize content** (when `respect_context_window=True`)
2. **Stop execution with an error** (when `respect_context_window=False`)

### Automatic Context Handling (`respect_context_window=True`)

This is the **default and recommended setting** for most use cases. When enabled, CrewAI will:

```python Code
# Agent with automatic context management (default)
smart_agent = Agent(
    role="Research Analyst",
    goal="Analyze large documents and datasets",
    backstory="Expert at processing extensive information",
    respect_context_window=True,  # 🔑 Default: auto-handle context limits
    verbose=True
)
```

**What happens when context limits are exceeded:**

* ⚠️ **Warning message**: `"Context length exceeded. Summarizing content to fit the model context window."`
* 🔄 **Automatic summarization**: CrewAI intelligently summarizes the conversation history
* ✅ **Continued execution**: Task execution continues seamlessly with the summarized context
* 📝 **Preserved information**: Key information is retained while reducing token count

### Strict Context Limits (`respect_context_window=False`)

When you need precise control and prefer execution to stop rather than lose any information:

```python Code
# Agent with strict context limits
strict_agent = Agent(
    role="Legal Document Reviewer",
    goal="Provide precise legal analysis without information loss",
    backstory="Legal expert requiring complete context for accurate analysis",
    respect_context_window=False,  # ❌ Stop execution on context limit
    verbose=True
)
```

**What happens when context limits are exceeded:**

* ❌ **Error message**: `"Context length exceeded. Consider using smaller text or RAG tools from crewai_tools."`
* 🛑 **Execution stops**: Task execution halts immediately
* 🔧 **Manual intervention required**: You need to modify your approach

### Choosing the Right Setting

#### Use `respect_context_window=True` (Default) when:

* **Processing large documents** that might exceed context limits
* **Long-running conversations** where some summarization is acceptable
* **Research tasks** where general context is more important than exact details
* **Prototyping and development** where you want robust execution

```python Code
# Perfect for document processing
document_processor = Agent(
    role="Document Analyst",
    goal="Extract insights from large research papers",
    backstory="Expert at analyzing extensive documentation",
    respect_context_window=True,  # Handle large documents gracefully
    max_iter=50,  # Allow more iterations for complex analysis
    verbose=True
)
```

#### Use `respect_context_window=False` when:

* **Precision is critical** and information loss is unacceptable
* **Legal or medical tasks** requiring complete context
* **Code review** where missing details could introduce bugs
* **Financial analysis** where accuracy is paramount

```python Code
# Perfect for precision tasks
precision_agent = Agent(
    role="Code Security Auditor",
    goal="Identify security vulnerabilities in code",
    backstory="Security expert requiring complete code context",
    respect_context_window=False,  # Prefer failure over incomplete analysis
    max_retry_limit=1,  # Fail fast on context issues
    verbose=True
)
```

### Alternative Approaches for Large Data

When dealing with very large datasets, consider these strategies:

#### 1. Use RAG Tools

```python Code
from crewai_tools import RagTool

# Create RAG tool for large document processing
rag_tool = RagTool()

rag_agent = Agent(
    role="Research Assistant",
    goal="Query large knowledge bases efficiently",
    backstory="Expert at using RAG tools for information retrieval",
    tools=[rag_tool],  # Use RAG instead of large context windows
    respect_context_window=True,
    verbose=True
)
```

#### 2. Use Knowledge Sources

```python Code
# Use knowledge sources instead of large prompts
knowledge_agent = Agent(
    role="Knowledge Expert",
    goal="Answer questions using curated knowledge",
    backstory="Expert at leveraging structured knowledge sources",
    knowledge_sources=[your_knowledge_sources],  # Pre-processed knowledge
    respect_context_window=True,
    verbose=True
)
```

### Context Window Best Practices

1. **Monitor Context Usage**: Enable `verbose=True` to see context management in action
2. **Design for Efficiency**: Structure tasks to minimize context accumulation
3. **Use Appropriate Models**: Choose LLMs with context windows suitable for your tasks
4. **Test Both Settings**: Try both `True` and `False` to see which works better for your use case
5. **Combine with RAG**: Use RAG tools for very large datasets instead of relying solely on context windows

### Troubleshooting Context Issues

**If you're getting context limit errors:**

```python Code
# Quick fix: Enable automatic handling
agent.respect_context_window = True

# Better solution: Use RAG tools for large data
from crewai_tools import RagTool
agent.tools = [RagTool()]

# Alternative: Break tasks into smaller pieces
# Or use knowledge sources instead of large prompts
```

**If automatic summarization loses important information:**

```python Code
# Disable auto-summarization and use RAG instead
agent = Agent(
    role="Detailed Analyst",
    goal="Maintain complete information accuracy",
    backstory="Expert requiring full context",
    respect_context_window=False,  # No summarization
    tools=[RagTool()],  # Use RAG for large data
    verbose=True
)
```

<Note>
  The context window management feature works automatically in the background. You don't need to call any special functions - just set `respect_context_window` to your preferred behavior and CrewAI handles the rest!
</Note>

## Direct Agent Interaction with `kickoff()`

Agents can be used directly without going through a task or crew workflow using the `kickoff()` method. This provides a simpler way to interact with an agent when you don't need the full crew orchestration capabilities.

### How `kickoff()` Works

The `kickoff()` method allows you to send messages directly to an agent and get a response, similar to how you would interact with an LLM but with all the agent's capabilities (tools, reasoning, etc.).

```python Code
from crewai import Agent
from crewai_tools import SerperDevTool

# Create an agent
researcher = Agent(
    role="AI Technology Researcher",
    goal="Research the latest AI developments",
    tools=[SerperDevTool()],
    verbose=True
)

# Use kickoff() to interact directly with the agent
result = researcher.kickoff("What are the latest developments in language models?")

# Access the raw response
print(result.raw)
```

### Parameters and Return Values

| Parameter         | Type                               | Description                                                               |
| :---------------- | :--------------------------------- | :------------------------------------------------------------------------ |
| `messages`        | `Union[str, List[Dict[str, str]]]` | Either a string query or a list of message dictionaries with role/content |
| `response_format` | `Optional[Type[Any]]`              | Optional Pydantic model for structured output                             |

The method returns a `LiteAgentOutput` object with the following properties:

* `raw`: String containing the raw output text
* `pydantic`: Parsed Pydantic model (if a `response_format` was provided)
* `agent_role`: Role of the agent that produced the output
* `usage_metrics`: Token usage metrics for the execution

### Structured Output

You can get structured output by providing a Pydantic model as the `response_format`:

```python Code
from pydantic import BaseModel
from typing import List

class ResearchFindings(BaseModel):
    main_points: List[str]
    key_technologies: List[str]
    future_predictions: str

# Get structured output
result = researcher.kickoff(
    "Summarize the latest developments in AI for 2025",
    response_format=ResearchFindings
)

# Access structured data
print(result.pydantic.main_points)
print(result.pydantic.future_predictions)
```

### Multiple Messages

You can also provide a conversation history as a list of message dictionaries:

```python Code
messages = [
    {"role": "user", "content": "I need information about large language models"},
    {"role": "assistant", "content": "I'd be happy to help with that! What specifically would you like to know?"},
    {"role": "user", "content": "What are the latest developments in 2025?"}
]

result = researcher.kickoff(messages)
```

### Async Support

An asynchronous version is available via `kickoff_async()` with the same parameters:

```python Code
import asyncio

async def main():
    result = await researcher.kickoff_async("What are the latest developments in AI?")
    print(result.raw)

asyncio.run(main())
```

<Note>
  The `kickoff()` method uses a `LiteAgent` internally, which provides a simpler execution flow while preserving all of the agent's configuration (role, goal, backstory, tools, etc.).
</Note>

## Important Considerations and Best Practices

### Security and Code Execution

* When using `allow_code_execution`, be cautious with user input and always validate it
* Use `code_execution_mode: "safe"` (Docker) in production environments
* Consider setting appropriate `max_execution_time` limits to prevent infinite loops

### Performance Optimization

* Use `respect_context_window: true` to prevent token limit issues
* Set appropriate `max_rpm` to avoid rate limiting
* Enable `cache: true` to improve performance for repetitive tasks
* Adjust `max_iter` and `max_retry_limit` based on task complexity

### Memory and Context Management

* Leverage `knowledge_sources` for domain-specific information
* Configure `embedder` when using custom embedding models
* Use custom templates (`system_template`, `prompt_template`, `response_template`) for fine-grained control over agent behavior

### Advanced Features

* Enable `reasoning: true` for agents that need to plan and reflect before executing complex tasks
* Set appropriate `max_reasoning_attempts` to control planning iterations (None for unlimited attempts)
* Use `inject_date: true` to provide agents with current date awareness for time-sensitive tasks
* Customize the date format with `date_format` using standard Python datetime format codes
* Enable `multimodal: true` for agents that need to process both text and visual content

### Agent Collaboration

* Enable `allow_delegation: true` when agents need to work together
* Use `step_callback` to monitor and log agent interactions
* Consider using different LLMs for different purposes:
  * Main `llm` for complex reasoning
  * `function_calling_llm` for efficient tool usage

### Date Awareness and Reasoning

* Use `inject_date: true` to provide agents with current date awareness for time-sensitive tasks
* Customize the date format with `date_format` using standard Python datetime format codes
* Valid format codes include: %Y (year), %m (month), %d (day), %B (full month name), etc.
* Invalid date formats will be logged as warnings and will not modify the task description
* Enable `reasoning: true` for complex tasks that benefit from upfront planning and reflection

### Model Compatibility

* Set `use_system_prompt: false` for older models that don't support system messages
* Ensure your chosen `llm` supports the features you need (like function calling)

## Troubleshooting Common Issues

1. **Rate Limiting**: If you're hitting API rate limits:
   * Implement appropriate `max_rpm`
   * Use caching for repetitive operations
   * Consider batching requests

2. **Context Window Errors**: If you're exceeding context limits:
   * Enable `respect_context_window`
   * Use more efficient prompts
   * Clear agent memory periodically

3. **Code Execution Issues**: If code execution fails:
   * Verify Docker is installed for safe mode
   * Check execution permissions
   * Review code sandbox settings

4. **Memory Issues**: If agent responses seem inconsistent:
   * Check knowledge source configuration
   * Review conversation history management

Remember that agents are most effective when configured according to their specific use case. Take time to understand your requirements and adjust these parameters accordingly.





# Crews

> Understanding and utilizing crews in the crewAI framework with comprehensive attributes and functionalities.

## Overview

A crew in crewAI represents a collaborative group of agents working together to achieve a set of tasks. Each crew defines the strategy for task execution, agent collaboration, and the overall workflow.

## Crew Attributes

| Attribute                             | Parameters             | Description                                                                                                                                                                                           |
| :------------------------------------ | :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tasks**                             | `tasks`                | A list of tasks assigned to the crew.                                                                                                                                                                 |
| **Agents**                            | `agents`               | A list of agents that are part of the crew.                                                                                                                                                           |
| **Process** *(optional)*              | `process`              | The process flow (e.g., sequential, hierarchical) the crew follows. Default is `sequential`.                                                                                                          |
| **Verbose** *(optional)*              | `verbose`              | The verbosity level for logging during execution. Defaults to `False`.                                                                                                                                |
| **Manager LLM** *(optional)*          | `manager_llm`          | The language model used by the manager agent in a hierarchical process. **Required when using a hierarchical process.**                                                                               |
| **Function Calling LLM** *(optional)* | `function_calling_llm` | If passed, the crew will use this LLM to do function calling for tools for all agents in the crew. Each agent can have its own LLM, which overrides the crew's LLM for function calling.              |
| **Config** *(optional)*               | `config`               | Optional configuration settings for the crew, in `Json` or `Dict[str, Any]` format.                                                                                                                   |
| **Max RPM** *(optional)*              | `max_rpm`              | Maximum requests per minute the crew adheres to during execution. Defaults to `None`.                                                                                                                 |
| **Memory** *(optional)*               | `memory`               | Utilized for storing execution memories (short-term, long-term, entity memory).                                                                                                                       |
| **Memory Config** *(optional)*        | `memory_config`        | Configuration for the memory provider to be used by the crew.                                                                                                                                         |
| **Cache** *(optional)*                | `cache`                | Specifies whether to use a cache for storing the results of tools' execution. Defaults to `True`.                                                                                                     |
| **Embedder** *(optional)*             | `embedder`             | Configuration for the embedder to be used by the crew. Mostly used by memory for now. Default is `{"provider": "openai"}`.                                                                            |
| **Step Callback** *(optional)*        | `step_callback`        | A function that is called after each step of every agent. This can be used to log the agent's actions or to perform other operations; it won't override the agent-specific `step_callback`.           |
| **Task Callback** *(optional)*        | `task_callback`        | A function that is called after the completion of each task. Useful for monitoring or additional operations post-task execution.                                                                      |
| **Share Crew** *(optional)*           | `share_crew`           | Whether you want to share the complete crew information and execution with the crewAI team to make the library better, and allow us to train models.                                                  |
| **Output Log File** *(optional)*      | `output_log_file`      | Set to True to save logs as logs.txt in the current directory or provide a file path. Logs will be in JSON format if the filename ends in .json, otherwise .txt. Defaults to `None`.                  |
| **Manager Agent** *(optional)*        | `manager_agent`        | `manager` sets a custom agent that will be used as a manager.                                                                                                                                         |
| **Prompt File** *(optional)*          | `prompt_file`          | Path to the prompt JSON file to be used for the crew.                                                                                                                                                 |
| **Planning** *(optional)*             | `planning`             | Adds planning ability to the Crew. When activated before each Crew iteration, all Crew data is sent to an AgentPlanner that will plan the tasks and this plan will be added to each task description. |
| **Planning LLM** *(optional)*         | `planning_llm`         | The language model used by the AgentPlanner in a planning process.                                                                                                                                    |
| **Knowledge Sources** *(optional)*    | `knowledge_sources`    | Knowledge sources available at the crew level, accessible to all the agents.                                                                                                                          |

<Tip>
  **Crew Max RPM**: The `max_rpm` attribute sets the maximum number of requests per minute the crew can perform to avoid rate limits and will override individual agents' `max_rpm` settings if you set it.
</Tip>

## Creating Crews

There are two ways to create crews in CrewAI: using **YAML configuration (recommended)** or defining them **directly in code**.

### YAML Configuration (Recommended)

Using YAML configuration provides a cleaner, more maintainable way to define crews and is consistent with how agents and tasks are defined in CrewAI projects.

After creating your CrewAI project as outlined in the [Installation](/en/installation) section, you can define your crew in a class that inherits from `CrewBase` and uses decorators to define agents, tasks, and the crew itself.

#### Example Crew Class with Decorators

```python code
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class YourCrewName:
    """Description of your crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Paths to your YAML configuration files
    # To see an example agent and task defined in YAML, checkout the following:
    # - Task: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    # - Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @before_kickoff
    def prepare_inputs(self, inputs):
        # Modify inputs before the crew starts
        inputs['additional_data'] = "Some extra information"
        return inputs

    @after_kickoff
    def process_output(self, output):
        # Modify output after the crew finishes
        output.raw += "\nProcessed after kickoff."
        return output

    @agent
    def agent_one(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_one'], # type: ignore[index]
            verbose=True
        )

    @agent
    def agent_two(self) -> Agent:
        return Agent(
            config=self.agents_config['agent_two'], # type: ignore[index]
            verbose=True
        )

    @task
    def task_one(self) -> Task:
        return Task(
            config=self.tasks_config['task_one'] # type: ignore[index]
        )

    @task
    def task_two(self) -> Task:
        return Task(
            config=self.tasks_config['task_two'] # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically collected by the @agent decorator
            tasks=self.tasks,    # Automatically collected by the @task decorator.
            process=Process.sequential,
            verbose=True,
        )
```

How to run the above code:

```python code
YourCrewName().crew().kickoff(inputs={"any": "input here"})
```

<Note>
  Tasks will be executed in the order they are defined.
</Note>

The `CrewBase` class, along with these decorators, automates the collection of agents and tasks, reducing the need for manual management.

#### Decorators overview from `annotations.py`

CrewAI provides several decorators in the `annotations.py` file that are used to mark methods within your crew class for special handling:

* `@CrewBase`: Marks the class as a crew base class.
* `@agent`: Denotes a method that returns an `Agent` object.
* `@task`: Denotes a method that returns a `Task` object.
* `@crew`: Denotes the method that returns the `Crew` object.
* `@before_kickoff`: (Optional) Marks a method to be executed before the crew starts.
* `@after_kickoff`: (Optional) Marks a method to be executed after the crew finishes.

These decorators help in organizing your crew's structure and automatically collecting agents and tasks without manually listing them.

### Direct Code Definition (Alternative)

Alternatively, you can define the crew directly in code without using YAML configuration files.

```python code
from crewai import Agent, Crew, Task, Process
from crewai_tools import YourCustomTool

class YourCrewName:
    def agent_one(self) -> Agent:
        return Agent(
            role="Data Analyst",
            goal="Analyze data trends in the market",
            backstory="An experienced data analyst with a background in economics",
            verbose=True,
            tools=[YourCustomTool()]
        )

    def agent_two(self) -> Agent:
        return Agent(
            role="Market Researcher",
            goal="Gather information on market dynamics",
            backstory="A diligent researcher with a keen eye for detail",
            verbose=True
        )

    def task_one(self) -> Task:
        return Task(
            description="Collect recent market data and identify trends.",
            expected_output="A report summarizing key trends in the market.",
            agent=self.agent_one()
        )

    def task_two(self) -> Task:
        return Task(
            description="Research factors affecting market dynamics.",
            expected_output="An analysis of factors influencing the market.",
            agent=self.agent_two()
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.agent_one(), self.agent_two()],
            tasks=[self.task_one(), self.task_two()],
            process=Process.sequential,
            verbose=True
        )
```

How to run the above code:

```python code
YourCrewName().crew().kickoff(inputs={})
```

In this example:

* Agents and tasks are defined directly within the class without decorators.
* We manually create and manage the list of agents and tasks.
* This approach provides more control but can be less maintainable for larger projects.

## Crew Output

The output of a crew in the CrewAI framework is encapsulated within the `CrewOutput` class.
This class provides a structured way to access results of the crew's execution, including various formats such as raw strings, JSON, and Pydantic models.
The `CrewOutput` includes the results from the final task output, token usage, and individual task outputs.

### Crew Output Attributes

| Attribute        | Parameters     | Type                       | Description                                                                                          |
| :--------------- | :------------- | :------------------------- | :--------------------------------------------------------------------------------------------------- |
| **Raw**          | `raw`          | `str`                      | The raw output of the crew. This is the default format for the output.                               |
| **Pydantic**     | `pydantic`     | `Optional[BaseModel]`      | A Pydantic model object representing the structured output of the crew.                              |
| **JSON Dict**    | `json_dict`    | `Optional[Dict[str, Any]]` | A dictionary representing the JSON output of the crew.                                               |
| **Tasks Output** | `tasks_output` | `List[TaskOutput]`         | A list of `TaskOutput` objects, each representing the output of a task in the crew.                  |
| **Token Usage**  | `token_usage`  | `Dict[str, Any]`           | A summary of token usage, providing insights into the language model's performance during execution. |

### Crew Output Methods and Properties

| Method/Property | Description                                                                                       |
| :-------------- | :------------------------------------------------------------------------------------------------ |
| **json**        | Returns the JSON string representation of the crew output if the output format is JSON.           |
| **to\_dict**    | Converts the JSON and Pydantic outputs to a dictionary.                                           |
| \***\*str\*\*** | Returns the string representation of the crew output, prioritizing Pydantic, then JSON, then raw. |

### Accessing Crew Outputs

Once a crew has been executed, its output can be accessed through the `output` attribute of the `Crew` object. The `CrewOutput` class provides various ways to interact with and present this output.

#### Example

```python Code
# Example crew execution
crew = Crew(
    agents=[research_agent, writer_agent],
    tasks=[research_task, write_article_task],
    verbose=True
)

crew_output = crew.kickoff()

# Accessing the crew output
print(f"Raw Output: {crew_output.raw}")
if crew_output.json_dict:
    print(f"JSON Output: {json.dumps(crew_output.json_dict, indent=2)}")
if crew_output.pydantic:
    print(f"Pydantic Output: {crew_output.pydantic}")
print(f"Tasks Output: {crew_output.tasks_output}")
print(f"Token Usage: {crew_output.token_usage}")
```

## Accessing Crew Logs

You can see real time log of the crew execution, by setting `output_log_file` as a `True(Boolean)` or a `file_name(str)`. Supports logging of events as both `file_name.txt` and `file_name.json`.
In case of `True(Boolean)` will save as `logs.txt`.

In case of `output_log_file` is set as `False(Boolean)` or `None`, the logs will not be populated.

```python Code
# Save crew logs
crew = Crew(output_log_file = True)  # Logs will be saved as logs.txt
crew = Crew(output_log_file = file_name)  # Logs will be saved as file_name.txt
crew = Crew(output_log_file = file_name.txt)  # Logs will be saved as file_name.txt
crew = Crew(output_log_file = file_name.json)  # Logs will be saved as file_name.json
```

## Memory Utilization

Crews can utilize memory (short-term, long-term, and entity memory) to enhance their execution and learning over time. This feature allows crews to store and recall execution memories, aiding in decision-making and task execution strategies.

## Cache Utilization

Caches can be employed to store the results of tools' execution, making the process more efficient by reducing the need to re-execute identical tasks.

## Crew Usage Metrics

After the crew execution, you can access the `usage_metrics` attribute to view the language model (LLM) usage metrics for all tasks executed by the crew. This provides insights into operational efficiency and areas for improvement.

```python Code
# Access the crew's usage metrics
crew = Crew(agents=[agent1, agent2], tasks=[task1, task2])
crew.kickoff()
print(crew.usage_metrics)
```

## Crew Execution Process

* **Sequential Process**: Tasks are executed one after another, allowing for a linear flow of work.
* **Hierarchical Process**: A manager agent coordinates the crew, delegating tasks and validating outcomes before proceeding. **Note**: A `manager_llm` or `manager_agent` is required for this process and it's essential for validating the process flow.

### Kicking Off a Crew

Once your crew is assembled, initiate the workflow with the `kickoff()` method. This starts the execution process according to the defined process flow.

```python Code
# Start the crew's task execution
result = my_crew.kickoff()
print(result)
```

### Different Ways to Kick Off a Crew

Once your crew is assembled, initiate the workflow with the appropriate kickoff method. CrewAI provides several methods for better control over the kickoff process: `kickoff()`, `kickoff_for_each()`, `kickoff_async()`, and `kickoff_for_each_async()`.

* `kickoff()`: Starts the execution process according to the defined process flow.
* `kickoff_for_each()`: Executes tasks sequentially for each provided input event or item in the collection.
* `kickoff_async()`: Initiates the workflow asynchronously.
* `kickoff_for_each_async()`: Executes tasks concurrently for each provided input event or item, leveraging asynchronous processing.

```python Code
# Start the crew's task execution
result = my_crew.kickoff()
print(result)

# Example of using kickoff_for_each
inputs_array = [{'topic': 'AI in healthcare'}, {'topic': 'AI in finance'}]
results = my_crew.kickoff_for_each(inputs=inputs_array)
for result in results:
    print(result)

# Example of using kickoff_async
inputs = {'topic': 'AI in healthcare'}
async_result = await my_crew.kickoff_async(inputs=inputs)
print(async_result)

# Example of using kickoff_for_each_async
inputs_array = [{'topic': 'AI in healthcare'}, {'topic': 'AI in finance'}]
async_results = await my_crew.kickoff_for_each_async(inputs=inputs_array)
for async_result in async_results:
    print(async_result)
```

These methods provide flexibility in how you manage and execute tasks within your crew, allowing for both synchronous and asynchronous workflows tailored to your needs.

### Replaying from a Specific Task

You can now replay from a specific task using our CLI command `replay`.

The replay feature in CrewAI allows you to replay from a specific task using the command-line interface (CLI). By running the command `crewai replay -t <task_id>`, you can specify the `task_id` for the replay process.

Kickoffs will now save the latest kickoffs returned task outputs locally for you to be able to replay from.

### Replaying from a Specific Task Using the CLI

To use the replay feature, follow these steps:

1. Open your terminal or command prompt.
2. Navigate to the directory where your CrewAI project is located.
3. Run the following command:

To view the latest kickoff task IDs, use:

```shell
crewai log-tasks-outputs
```

Then, to replay from a specific task, use:

```shell
crewai replay -t <task_id>
```

These commands let you replay from your latest kickoff tasks, still retaining context from previously executed tasks.


# Tasks

> Detailed guide on managing and creating tasks within the CrewAI framework.

## Overview

In the CrewAI framework, a `Task` is a specific assignment completed by an `Agent`.

Tasks provide all necessary details for execution, such as a description, the agent responsible, required tools, and more, facilitating a wide range of action complexities.

Tasks within CrewAI can be collaborative, requiring multiple agents to work together. This is managed through the task properties and orchestrated by the Crew's process, enhancing teamwork and efficiency.

<Note type="info" title="Enterprise Enhancement: Visual Task Builder">
  CrewAI Enterprise includes a Visual Task Builder in Crew Studio that simplifies complex task creation and chaining. Design your task flows visually and test them in real-time without writing code.

  ![Task Builder Screenshot](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/enterprise/crew-studio-interface.png)

  The Visual Task Builder enables:

  * Drag-and-drop task creation
  * Visual task dependencies and flow
  * Real-time testing and validation
  * Easy sharing and collaboration
</Note>

### Task Execution Flow

Tasks can be executed in two ways:

* **Sequential**: Tasks are executed in the order they are defined
* **Hierarchical**: Tasks are assigned to agents based on their roles and expertise

The execution flow is defined when creating the crew:

```python Code
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    process=Process.sequential  # or Process.hierarchical
)
```

## Task Attributes

| Attribute                        | Parameters        | Type                             | Description                                                                                                     |
| :------------------------------- | :---------------- | :------------------------------- | :-------------------------------------------------------------------------------------------------------------- |
| **Description**                  | `description`     | `str`                            | A clear, concise statement of what the task entails.                                                            |
| **Expected Output**              | `expected_output` | `str`                            | A detailed description of what the task's completion looks like.                                                |
| **Name** *(optional)*            | `name`            | `Optional[str]`                  | A name identifier for the task.                                                                                 |
| **Agent** *(optional)*           | `agent`           | `Optional[BaseAgent]`            | The agent responsible for executing the task.                                                                   |
| **Tools** *(optional)*           | `tools`           | `List[BaseTool]`                 | The tools/resources the agent is limited to use for this task.                                                  |
| **Context** *(optional)*         | `context`         | `Optional[List["Task"]]`         | Other tasks whose outputs will be used as context for this task.                                                |
| **Async Execution** *(optional)* | `async_execution` | `Optional[bool]`                 | Whether the task should be executed asynchronously. Defaults to False.                                          |
| **Human Input** *(optional)*     | `human_input`     | `Optional[bool]`                 | Whether the task should have a human review the final answer of the agent. Defaults to False.                   |
| **Markdown** *(optional)*        | `markdown`        | `Optional[bool]`                 | Whether the task should instruct the agent to return the final answer formatted in Markdown. Defaults to False. |
| **Config** *(optional)*          | `config`          | `Optional[Dict[str, Any]]`       | Task-specific configuration parameters.                                                                         |
| **Output File** *(optional)*     | `output_file`     | `Optional[str]`                  | File path for storing the task output.                                                                          |
| **Output JSON** *(optional)*     | `output_json`     | `Optional[Type[BaseModel]]`      | A Pydantic model to structure the JSON output.                                                                  |
| **Output Pydantic** *(optional)* | `output_pydantic` | `Optional[Type[BaseModel]]`      | A Pydantic model for task output.                                                                               |
| **Callback** *(optional)*        | `callback`        | `Optional[Any]`                  | Function/object to be executed after task completion.                                                           |
| **Guardrail** *(optional)*       | `guardrail`       | `Optional[Union[Callable, str]]` | Function or string description to validate task output before proceeding to next task.                          |

## Creating Tasks

There are two ways to create tasks in CrewAI: using **YAML configuration (recommended)** or defining them **directly in code**.

### YAML Configuration (Recommended)

Using YAML configuration provides a cleaner, more maintainable way to define tasks. We strongly recommend using this approach to define tasks in your CrewAI projects.

After creating your CrewAI project as outlined in the [Installation](/en/installation) section, navigate to the `src/latest_ai_development/config/tasks.yaml` file and modify the template to match your specific task requirements.

<Note>
  Variables in your YAML files (like `{topic}`) will be replaced with values from your inputs when running the crew:

  ```python Code
  crew.kickoff(inputs={'topic': 'AI Agents'})
  ```
</Note>

Here's an example of how to configure tasks using YAML:

````yaml tasks.yaml
research_task:
  description: >
    Conduct a thorough research about {topic}
    Make sure you find any interesting and relevant information given
    the current year is 2025.
  expected_output: >
    A list with 10 bullet points of the most relevant information about {topic}
  agent: researcher
  guardrail: ensure each bullet contains a minimum of 100 words

reporting_task:
  description: >
    Review the context you got and expand each topic into a full section for a report.
    Make sure the report is detailed and contains any and all relevant information.
  expected_output: >
    A fully fledge reports with the mains topics, each with a full section of information.
    Formatted as markdown without '```'
  agent: reporting_analyst
  markdown: true
  output_file: report.md
````

To use this YAML configuration in your code, create a crew class that inherits from `CrewBase`:

```python crew.py
# src/latest_ai_development/crew.py

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

@CrewBase
class LatestAiDevelopmentCrew():
  """LatestAiDevelopment crew"""

  @agent
  def researcher(self) -> Agent:
    return Agent(
      config=self.agents_config['researcher'], # type: ignore[index]
      verbose=True,
      tools=[SerperDevTool()]
    )

  @agent
  def reporting_analyst(self) -> Agent:
    return Agent(
      config=self.agents_config['reporting_analyst'], # type: ignore[index]
      verbose=True
    )

  @task
  def research_task(self) -> Task:
    return Task(
      config=self.tasks_config['research_task'] # type: ignore[index]
    )

  @task
  def reporting_task(self) -> Task:
    return Task(
      config=self.tasks_config['reporting_task'] # type: ignore[index]
    )

  @crew
  def crew(self) -> Crew:
    return Crew(
      agents=[
        self.researcher(),
        self.reporting_analyst()
      ],
      tasks=[
        self.research_task(),
        self.reporting_task()
      ],
      process=Process.sequential
    )
```

<Note>
  The names you use in your YAML files (`agents.yaml` and `tasks.yaml`) should match the method names in your Python code.
</Note>

### Direct Code Definition (Alternative)

Alternatively, you can define tasks directly in your code without using YAML configuration:

```python task.py
from crewai import Task

research_task = Task(
    description="""
        Conduct a thorough research about AI Agents.
        Make sure you find any interesting and relevant information given
        the current year is 2025.
    """,
    expected_output="""
        A list with 10 bullet points of the most relevant information about AI Agents
    """,
    agent=researcher
)

reporting_task = Task(
    description="""
        Review the context you got and expand each topic into a full section for a report.
        Make sure the report is detailed and contains any and all relevant information.
    """,
    expected_output="""
        A fully fledge reports with the mains topics, each with a full section of information.
    """,
    agent=reporting_analyst,
    markdown=True,  # Enable markdown formatting for the final output
    output_file="report.md"
)
```

<Tip>
  Directly specify an `agent` for assignment or let the `hierarchical` CrewAI's process decide based on roles, availability, etc.
</Tip>

## Task Output

Understanding task outputs is crucial for building effective AI workflows. CrewAI provides a structured way to handle task results through the `TaskOutput` class, which supports multiple output formats and can be easily passed between tasks.

The output of a task in CrewAI framework is encapsulated within the `TaskOutput` class. This class provides a structured way to access results of a task, including various formats such as raw output, JSON, and Pydantic models.

By default, the `TaskOutput` will only include the `raw` output. A `TaskOutput` will only include the `pydantic` or `json_dict` output if the original `Task` object was configured with `output_pydantic` or `output_json`, respectively.

### Task Output Attributes

| Attribute         | Parameters      | Type                       | Description                                                                                        |
| :---------------- | :-------------- | :------------------------- | :------------------------------------------------------------------------------------------------- |
| **Description**   | `description`   | `str`                      | Description of the task.                                                                           |
| **Summary**       | `summary`       | `Optional[str]`            | Summary of the task, auto-generated from the first 10 words of the description.                    |
| **Raw**           | `raw`           | `str`                      | The raw output of the task. This is the default format for the output.                             |
| **Pydantic**      | `pydantic`      | `Optional[BaseModel]`      | A Pydantic model object representing the structured output of the task.                            |
| **JSON Dict**     | `json_dict`     | `Optional[Dict[str, Any]]` | A dictionary representing the JSON output of the task.                                             |
| **Agent**         | `agent`         | `str`                      | The agent that executed the task.                                                                  |
| **Output Format** | `output_format` | `OutputFormat`             | The format of the task output, with options including RAW, JSON, and Pydantic. The default is RAW. |

### Task Methods and Properties

| Method/Property | Description                                                                                       |
| :-------------- | :------------------------------------------------------------------------------------------------ |
| **json**        | Returns the JSON string representation of the task output if the output format is JSON.           |
| **to\_dict**    | Converts the JSON and Pydantic outputs to a dictionary.                                           |
| **str**         | Returns the string representation of the task output, prioritizing Pydantic, then JSON, then raw. |

### Accessing Task Outputs

Once a task has been executed, its output can be accessed through the `output` attribute of the `Task` object. The `TaskOutput` class provides various ways to interact with and present this output.

#### Example

```python Code
# Example task
task = Task(
    description='Find and summarize the latest AI news',
    expected_output='A bullet list summary of the top 5 most important AI news',
    agent=research_agent,
    tools=[search_tool]
)

# Execute the crew
crew = Crew(
    agents=[research_agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()

# Accessing the task output
task_output = task.output

print(f"Task Description: {task_output.description}")
print(f"Task Summary: {task_output.summary}")
print(f"Raw Output: {task_output.raw}")
if task_output.json_dict:
    print(f"JSON Output: {json.dumps(task_output.json_dict, indent=2)}")
if task_output.pydantic:
    print(f"Pydantic Output: {task_output.pydantic}")
```

## Markdown Output Formatting

The `markdown` parameter enables automatic markdown formatting for task outputs. When set to `True`, the task will instruct the agent to format the final answer using proper Markdown syntax.

### Using Markdown Formatting

```python Code
# Example task with markdown formatting enabled
formatted_task = Task(
    description="Create a comprehensive report on AI trends",
    expected_output="A well-structured report with headers, sections, and bullet points",
    agent=reporter_agent,
    markdown=True  # Enable automatic markdown formatting
)
```

When `markdown=True`, the agent will receive additional instructions to format the output using:

* `#` for headers
* `**text**` for bold text
* `*text*` for italic text
* `-` or `*` for bullet points
* `` `code` `` for inline code
* ` `language \`\`\` for code blocks

### YAML Configuration with Markdown

```yaml tasks.yaml
analysis_task:
  description: >
    Analyze the market data and create a detailed report
  expected_output: >
    A comprehensive analysis with charts and key findings
  agent: analyst
  markdown: true  # Enable markdown formatting
  output_file: analysis.md
```

### Benefits of Markdown Output

* **Consistent Formatting**: Ensures all outputs follow proper markdown conventions
* **Better Readability**: Structured content with headers, lists, and emphasis
* **Documentation Ready**: Output can be directly used in documentation systems
* **Cross-Platform Compatibility**: Markdown is universally supported

<Note>
  The markdown formatting instructions are automatically added to the task prompt when `markdown=True`, so you don't need to specify formatting requirements in your task description.
</Note>

## Task Dependencies and Context

Tasks can depend on the output of other tasks using the `context` attribute. For example:

```python Code
research_task = Task(
    description="Research the latest developments in AI",
    expected_output="A list of recent AI developments",
    agent=researcher
)

analysis_task = Task(
    description="Analyze the research findings and identify key trends",
    expected_output="Analysis report of AI trends",
    agent=analyst,
    context=[research_task]  # This task will wait for research_task to complete
)
```

## Task Guardrails

Task guardrails provide a way to validate and transform task outputs before they
are passed to the next task. This feature helps ensure data quality and provides
feedback to agents when their output doesn't meet specific criteria.

**Guardrails can be defined in two ways:**

1. **Function-based guardrails**: Python functions that implement custom validation logic
2. **String-based guardrails**: Natural language descriptions that are automatically converted to LLM-powered validation

### Function-Based Guardrails

To add a function-based guardrail to a task, provide a validation function through the `guardrail` parameter:

```python Code
from typing import Tuple, Union, Dict, Any
from crewai import TaskOutput

def validate_blog_content(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate blog content meets requirements."""
    try:
        # Check word count
        word_count = len(result.split())
        if word_count > 200:
            return (False, "Blog content exceeds 200 words")

        # Additional validation logic here
        return (True, result.strip())
    except Exception as e:
        return (False, "Unexpected error during validation")

blog_task = Task(
    description="Write a blog post about AI",
    expected_output="A blog post under 200 words",
    agent=blog_agent,
    guardrail=validate_blog_content  # Add the guardrail function
)
```

### Guardrail Function Requirements

1. **Function Signature**:
   * Must accept exactly one parameter (the task output)
   * Should return a tuple of `(bool, Any)`
   * Type hints are recommended but optional

2. **Return Values**:
   * On success: it returns a tuple of `(bool, Any)`. For example: `(True, validated_result)`
   * On Failure: it returns a tuple of `(bool, str)`. For example: `(False, "Error message explain the failure")`

### String-Based Guardrails

String-based guardrails allow you to describe validation criteria in natural language. When you provide a string instead of a function, CrewAI automatically converts it to an `LLMGuardrail` that uses an AI agent to validate the task output.

#### Using String Guardrails in Python

```python Code
from crewai import Task

# Simple string-based guardrail
blog_task = Task(
    description="Write a blog post about AI",
    expected_output="A blog post under 200 words",
    agent=blog_agent,
    guardrail="Ensure the blog post is under 200 words and includes practical examples"
)

# More complex validation criteria
research_task = Task(
    description="Research AI trends for 2025",
    expected_output="A comprehensive research report",
    agent=research_agent,
    guardrail="Ensure each finding includes a credible source and is backed by recent data from 2024-2025"
)
```

#### Using String Guardrails in YAML

```yaml
research_task:
  description: Research the latest AI developments
  expected_output: A list of 10 bullet points about AI
  agent: researcher
  guardrail: ensure each bullet contains a minimum of 100 words

validation_task:
  description: Validate the research findings
  expected_output: A validation report
  agent: validator
  guardrail: confirm all sources are from reputable publications and published within the last 2 years
```

#### How String Guardrails Work

When you provide a string guardrail, CrewAI automatically:

1. Creates an `LLMGuardrail` instance using the string as validation criteria
2. Uses the task's agent LLM to power the validation
3. Creates a temporary validation agent that checks the output against your criteria
4. Returns detailed feedback if validation fails

This approach is ideal when you want to use natural language to describe validation rules without writing custom validation functions.

### LLMGuardrail Class

The `LLMGuardrail` class is the underlying mechanism that powers string-based guardrails. You can also use it directly for more advanced control:

```python Code
from crewai import Task
from crewai.tasks.llm_guardrail import LLMGuardrail
from crewai.llm import LLM

# Create a custom LLMGuardrail with specific LLM
custom_guardrail = LLMGuardrail(
    description="Ensure the response contains exactly 5 bullet points with proper citations",
    llm=LLM(model="gpt-4o-mini")
)

task = Task(
    description="Research AI safety measures",
    expected_output="A detailed analysis with bullet points",
    agent=research_agent,
    guardrail=custom_guardrail
)
```

**Note**: When you use a string guardrail, CrewAI automatically creates an `LLMGuardrail` instance using your task's agent LLM. Using `LLMGuardrail` directly gives you more control over the validation process and LLM selection.

### Error Handling Best Practices

1. **Structured Error Responses**:

```python Code
from crewai import TaskOutput, LLMGuardrail

def validate_with_context(result: TaskOutput) -> Tuple[bool, Any]:
    try:
        # Main validation logic
        validated_data = perform_validation(result)
        return (True, validated_data)
    except ValidationError as e:
        return (False, f"VALIDATION_ERROR: {str(e)}")
    except Exception as e:
        return (False, str(e))
```

2. **Error Categories**:
   * Use specific error codes
   * Include relevant context
   * Provide actionable feedback

3. **Validation Chain**:

```python Code
from typing import Any, Dict, List, Tuple, Union
from crewai import TaskOutput

def complex_validation(result: TaskOutput) -> Tuple[bool, Any]:
    """Chain multiple validation steps."""
    # Step 1: Basic validation
    if not result:
        return (False, "Empty result")

    # Step 2: Content validation
    try:
        validated = validate_content(result)
        if not validated:
            return (False, "Invalid content")

        # Step 3: Format validation
        formatted = format_output(validated)
        return (True, formatted)
    except Exception as e:
        return (False, str(e))
```

### Handling Guardrail Results

When a guardrail returns `(False, error)`:

1. The error is sent back to the agent
2. The agent attempts to fix the issue
3. The process repeats until:
   * The guardrail returns `(True, result)`
   * Maximum retries are reached

Example with retry handling:

```python Code
from typing import Optional, Tuple, Union
from crewai import TaskOutput, Task

def validate_json_output(result: TaskOutput) -> Tuple[bool, Any]:
    """Validate and parse JSON output."""
    try:
        # Try to parse as JSON
        data = json.loads(result)
        return (True, data)
    except json.JSONDecodeError as e:
        return (False, "Invalid JSON format")

task = Task(
    description="Generate a JSON report",
    expected_output="A valid JSON object",
    agent=analyst,
    guardrail=validate_json_output,
    max_retries=3  # Limit retry attempts
)
```

## Getting Structured Consistent Outputs from Tasks

<Note>
  It's also important to note that the output of the final task of a crew becomes the final output of the actual crew itself.
</Note>

### Using `output_pydantic`

The `output_pydantic` property allows you to define a Pydantic model that the task output should conform to. This ensures that the output is not only structured but also validated according to the Pydantic model.

Here's an example demonstrating how to use output\_pydantic:

```python Code
import json

from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel


class Blog(BaseModel):
    title: str
    content: str


blog_agent = Agent(
    role="Blog Content Generator Agent",
    goal="Generate a blog title and content",
    backstory="""You are an expert content creator, skilled in crafting engaging and informative blog posts.""",
    verbose=False,
    allow_delegation=False,
    llm="gpt-4o",
)

task1 = Task(
    description="""Create a blog title and content on a given topic. Make sure the content is under 200 words.""",
    expected_output="A compelling blog title and well-written content.",
    agent=blog_agent,
    output_pydantic=Blog,
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[blog_agent],
    tasks=[task1],
    verbose=True,
    process=Process.sequential,
)

result = crew.kickoff()

# Option 1: Accessing Properties Using Dictionary-Style Indexing
print("Accessing Properties - Option 1")
title = result["title"]
content = result["content"]
print("Title:", title)
print("Content:", content)

# Option 2: Accessing Properties Directly from the Pydantic Model
print("Accessing Properties - Option 2")
title = result.pydantic.title
content = result.pydantic.content
print("Title:", title)
print("Content:", content)

# Option 3: Accessing Properties Using the to_dict() Method
print("Accessing Properties - Option 3")
output_dict = result.to_dict()
title = output_dict["title"]
content = output_dict["content"]
print("Title:", title)
print("Content:", content)

# Option 4: Printing the Entire Blog Object
print("Accessing Properties - Option 5")
print("Blog:", result)

```

In this example:

* A Pydantic model Blog is defined with title and content fields.
* The task task1 uses the output\_pydantic property to specify that its output should conform to the Blog model.
* After executing the crew, you can access the structured output in multiple ways as shown.

#### Explanation of Accessing the Output

1. Dictionary-Style Indexing: You can directly access the fields using result\["field\_name"]. This works because the CrewOutput class implements the **getitem** method.
2. Directly from Pydantic Model: Access the attributes directly from the result.pydantic object.
3. Using to\_dict() Method: Convert the output to a dictionary and access the fields.
4. Printing the Entire Object: Simply print the result object to see the structured output.

### Using `output_json`

The `output_json` property allows you to define the expected output in JSON format. This ensures that the task's output is a valid JSON structure that can be easily parsed and used in your application.

Here's an example demonstrating how to use `output_json`:

```python Code
import json

from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel


# Define the Pydantic model for the blog
class Blog(BaseModel):
    title: str
    content: str


# Define the agent
blog_agent = Agent(
    role="Blog Content Generator Agent",
    goal="Generate a blog title and content",
    backstory="""You are an expert content creator, skilled in crafting engaging and informative blog posts.""",
    verbose=False,
    allow_delegation=False,
    llm="gpt-4o",
)

# Define the task with output_json set to the Blog model
task1 = Task(
    description="""Create a blog title and content on a given topic. Make sure the content is under 200 words.""",
    expected_output="A JSON object with 'title' and 'content' fields.",
    agent=blog_agent,
    output_json=Blog,
)

# Instantiate the crew with a sequential process
crew = Crew(
    agents=[blog_agent],
    tasks=[task1],
    verbose=True,
    process=Process.sequential,
)

# Kickoff the crew to execute the task
result = crew.kickoff()

# Option 1: Accessing Properties Using Dictionary-Style Indexing
print("Accessing Properties - Option 1")
title = result["title"]
content = result["content"]
print("Title:", title)
print("Content:", content)

# Option 2: Printing the Entire Blog Object
print("Accessing Properties - Option 2")
print("Blog:", result)
```

In this example:

* A Pydantic model Blog is defined with title and content fields, which is used to specify the structure of the JSON output.
* The task task1 uses the output\_json property to indicate that it expects a JSON output conforming to the Blog model.
* After executing the crew, you can access the structured JSON output in two ways as shown.

#### Explanation of Accessing the Output

1. Accessing Properties Using Dictionary-Style Indexing: You can access the fields directly using result\["field\_name"]. This is possible because the CrewOutput class implements the **getitem** method, allowing you to treat the output like a dictionary. In this option, we're retrieving the title and content from the result.
2. Printing the Entire Blog Object: By printing result, you get the string representation of the CrewOutput object. Since the **str** method is implemented to return the JSON output, this will display the entire output as a formatted string representing the Blog object.

***

By using output\_pydantic or output\_json, you ensure that your tasks produce outputs in a consistent and structured format, making it easier to process and utilize the data within your application or across multiple tasks.

## Integrating Tools with Tasks

Leverage tools from the [CrewAI Toolkit](https://github.com/joaomdmoura/crewai-tools) and [LangChain Tools](https://python.langchain.com/docs/integrations/tools) for enhanced task performance and agent interaction.

## Creating a Task with Tools

```python Code
import os
os.environ["OPENAI_API_KEY"] = "Your Key"
os.environ["SERPER_API_KEY"] = "Your Key" # serper.dev API key

from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

research_agent = Agent(
  role='Researcher',
  goal='Find and summarize the latest AI news',
  backstory="""You're a researcher at a large company.
  You're responsible for analyzing data and providing insights
  to the business.""",
  verbose=True
)

# to perform a semantic search for a specified query from a text's content across the internet
search_tool = SerperDevTool()

task = Task(
  description='Find and summarize the latest AI news',
  expected_output='A bullet list summary of the top 5 most important AI news',
  agent=research_agent,
  tools=[search_tool]
)

crew = Crew(
    agents=[research_agent],
    tasks=[task],
    verbose=True
)

result = crew.kickoff()
print(result)
```

This demonstrates how tasks with specific tools can override an agent's default set for tailored task execution.

## Referring to Other Tasks

In CrewAI, the output of one task is automatically relayed into the next one, but you can specifically define what tasks' output, including multiple, should be used as context for another task.

This is useful when you have a task that depends on the output of another task that is not performed immediately after it. This is done through the `context` attribute of the task:

```python Code
# ...

research_ai_task = Task(
    description="Research the latest developments in AI",
    expected_output="A list of recent AI developments",
    async_execution=True,
    agent=research_agent,
    tools=[search_tool]
)

research_ops_task = Task(
    description="Research the latest developments in AI Ops",
    expected_output="A list of recent AI Ops developments",
    async_execution=True,
    agent=research_agent,
    tools=[search_tool]
)

write_blog_task = Task(
    description="Write a full blog post about the importance of AI and its latest news",
    expected_output="Full blog post that is 4 paragraphs long",
    agent=writer_agent,
    context=[research_ai_task, research_ops_task]
)

#...
```

## Asynchronous Execution

You can define a task to be executed asynchronously. This means that the crew will not wait for it to be completed to continue with the next task. This is useful for tasks that take a long time to be completed, or that are not crucial for the next tasks to be performed.

You can then use the `context` attribute to define in a future task that it should wait for the output of the asynchronous task to be completed.

```python Code
#...

list_ideas = Task(
    description="List of 5 interesting ideas to explore for an article about AI.",
    expected_output="Bullet point list of 5 ideas for an article.",
    agent=researcher,
    async_execution=True # Will be executed asynchronously
)

list_important_history = Task(
    description="Research the history of AI and give me the 5 most important events.",
    expected_output="Bullet point list of 5 important events.",
    agent=researcher,
    async_execution=True # Will be executed asynchronously
)

write_article = Task(
    description="Write an article about AI, its history, and interesting ideas.",
    expected_output="A 4 paragraph article about AI.",
    agent=writer,
    context=[list_ideas, list_important_history] # Will wait for the output of the two tasks to be completed
)

#...
```

## Callback Mechanism

The callback function is executed after the task is completed, allowing for actions or notifications to be triggered based on the task's outcome.

```python Code
# ...

def callback_function(output: TaskOutput):
    # Do something after the task is completed
    # Example: Send an email to the manager
    print(f"""
        Task completed!
        Task: {output.description}
        Output: {output.raw}
    """)

research_task = Task(
    description='Find and summarize the latest AI news',
    expected_output='A bullet list summary of the top 5 most important AI news',
    agent=research_agent,
    tools=[search_tool],
    callback=callback_function
)

#...
```

## Accessing a Specific Task Output

Once a crew finishes running, you can access the output of a specific task by using the `output` attribute of the task object:

```python Code
# ...
task1 = Task(
    description='Find and summarize the latest AI news',
    expected_output='A bullet list summary of the top 5 most important AI news',
    agent=research_agent,
    tools=[search_tool]
)

#...

crew = Crew(
    agents=[research_agent],
    tasks=[task1, task2, task3],
    verbose=True
)

result = crew.kickoff()

# Returns a TaskOutput object with the description and results of the task
print(f"""
    Task completed!
    Task: {task1.output.description}
    Output: {task1.output.raw}
""")
```

## Tool Override Mechanism

Specifying tools in a task allows for dynamic adaptation of agent capabilities, emphasizing CrewAI's flexibility.

## Error Handling and Validation Mechanisms

While creating and executing tasks, certain validation mechanisms are in place to ensure the robustness and reliability of task attributes. These include but are not limited to:

* Ensuring only one output type is set per task to maintain clear output expectations.
* Preventing the manual assignment of the `id` attribute to uphold the integrity of the unique identifier system.

These validations help in maintaining the consistency and reliability of task executions within the crewAI framework.

## Creating Directories when Saving Files

You can now specify if a task should create directories when saving its output to a file. This is particularly useful for organizing outputs and ensuring that file paths are correctly structured.

```python Code
# ...

save_output_task = Task(
    description='Save the summarized AI news to a file',
    expected_output='File saved successfully',
    agent=research_agent,
    tools=[file_save_tool],
    output_file='outputs/ai_news_summary.txt',
    create_directory=True
)

#...
```

Check out the video below to see how to use structured outputs in CrewAI:

<iframe width="560" height="315" src="https://www.youtube.com/embed/dNpKQk5uxHw" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen />

## Conclusion

Tasks are the driving force behind the actions of agents in CrewAI.
By properly defining tasks and their outcomes, you set the stage for your AI agents to work effectively, either independently or as a collaborative unit.
Equipping tasks with appropriate tools, understanding the execution process, and following robust validation practices are crucial for maximizing CrewAI's potential,
ensuring agents are effectively prepared for their assignments and that tasks are executed as intended.


# LLMs

> A comprehensive guide to configuring and using Large Language Models (LLMs) in your CrewAI projects

## Overview

CrewAI integrates with multiple LLM providers through LiteLLM, giving you the flexibility to choose the right model for your specific use case. This guide will help you understand how to configure and use different LLM providers in your CrewAI projects.

## What are LLMs?

Large Language Models (LLMs) are the core intelligence behind CrewAI agents. They enable agents to understand context, make decisions, and generate human-like responses. Here's what you need to know:

<CardGroup cols={2}>
  <Card title="LLM Basics" icon="brain">
    Large Language Models are AI systems trained on vast amounts of text data. They power the intelligence of your CrewAI agents, enabling them to understand and generate human-like text.
  </Card>

  <Card title="Context Window" icon="window">
    The context window determines how much text an LLM can process at once. Larger windows (e.g., 128K tokens) allow for more context but may be more expensive and slower.
  </Card>

  <Card title="Temperature" icon="temperature-three-quarters">
    Temperature (0.0 to 1.0) controls response randomness. Lower values (e.g., 0.2) produce more focused, deterministic outputs, while higher values (e.g., 0.8) increase creativity and variability.
  </Card>

  <Card title="Provider Selection" icon="server">
    Each LLM provider (e.g., OpenAI, Anthropic, Google) offers different models with varying capabilities, pricing, and features. Choose based on your needs for accuracy, speed, and cost.
  </Card>
</CardGroup>

## Setting up your LLM

There are different places in CrewAI code where you can specify the model to use. Once you specify the model you are using, you will need to provide the configuration (like an API key) for each of the model providers you use. See the [provider configuration examples](#provider-configuration-examples) section for your provider.

<Tabs>
  <Tab title="1. Environment Variables">
    The simplest way to get started. Set the model in your environment directly, through an `.env` file or in your app code. If you used `crewai create` to bootstrap your project, it will be set already.

    ```bash .env
    MODEL=model-id  # e.g. gpt-4o, gemini-2.0-flash, claude-3-sonnet-...

    # Be sure to set your API keys here too. See the Provider
    # section below.
    ```

    <Warning>
      Never commit API keys to version control. Use environment files (.env) or your system's secret management.
    </Warning>
  </Tab>

  <Tab title="2. YAML Configuration">
    Create a YAML file to define your agent configurations. This method is great for version control and team collaboration:

    ```yaml agents.yaml {6}
    researcher:
        role: Research Specialist
        goal: Conduct comprehensive research and analysis
        backstory: A dedicated research professional with years of experience
        verbose: true
        llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...
        # (see provider configuration examples below for more)
    ```

    <Info>
      The YAML configuration allows you to:

      * Version control your agent settings
      * Easily switch between different models
      * Share configurations across team members
      * Document model choices and their purposes
    </Info>
  </Tab>

  <Tab title="3. Direct Code">
    For maximum flexibility, configure LLMs directly in your Python code:

    ```python {4,8}
    from crewai import LLM

    # Basic configuration
    llm = LLM(model="model-id-here")  # gpt-4o, gemini-2.0-flash, anthropic/claude...

    # Advanced configuration with detailed parameters
    llm = LLM(
        model="model-id-here",  # gpt-4o, gemini-2.0-flash, anthropic/claude...
        temperature=0.7,        # Higher for more creative outputs
        timeout=120,            # Seconds to wait for response
        max_tokens=4000,        # Maximum length of response
        top_p=0.9,              # Nucleus sampling parameter
        frequency_penalty=0.1 , # Reduce repetition
        presence_penalty=0.1,   # Encourage topic diversity
        response_format={"type": "json"},  # For structured outputs
        seed=42                 # For reproducible results
    )
    ```

    <Info>
      Parameter explanations:

      * `temperature`: Controls randomness (0.0-1.0)
      * `timeout`: Maximum wait time for response
      * `max_tokens`: Limits response length
      * `top_p`: Alternative to temperature for sampling
      * `frequency_penalty`: Reduces word repetition
      * `presence_penalty`: Encourages new topics
      * `response_format`: Specifies output structure
      * `seed`: Ensures consistent outputs
    </Info>
  </Tab>
</Tabs>

## Provider Configuration Examples

CrewAI supports a multitude of LLM providers, each offering unique features, authentication methods, and model capabilities.
In this section, you'll find detailed examples that help you select, configure, and optimize the LLM that best fits your project's needs.

<AccordionGroup>
  <Accordion title="OpenAI">
    Set the following environment variables in your `.env` file:

    ```toml Code
    # Required
    OPENAI_API_KEY=sk-...

    # Optional
    OPENAI_API_BASE=<custom-base-url>
    OPENAI_ORGANIZATION=<your-org-id>
    ```

    Example usage in your CrewAI project:

    ```python Code
    from crewai import LLM

    llm = LLM(
        model="openai/gpt-4", # call model by provider/model_name
        temperature=0.8,
        max_tokens=150,
        top_p=0.9,
        frequency_penalty=0.1,
        presence_penalty=0.1,
        stop=["END"],
        seed=42
    )
    ```

    OpenAI is one of the leading providers of LLMs with a wide range of models and features.

    | Model                | Context Window | Best For                                |
    | -------------------- | -------------- | --------------------------------------- |
    | GPT-4                | 8,192 tokens   | High-accuracy tasks, complex reasoning  |
    | GPT-4 Turbo          | 128,000 tokens | Long-form content, document analysis    |
    | GPT-4o & GPT-4o-mini | 128,000 tokens | Cost-effective large context processing |
    | o3-mini              | 200,000 tokens | Fast reasoning, complex reasoning       |
    | o1-mini              | 128,000 tokens | Fast reasoning, complex reasoning       |
    | o1-preview           | 128,000 tokens | Fast reasoning, complex reasoning       |
    | o1                   | 200,000 tokens | Fast reasoning, complex reasoning       |
  </Accordion>

  <Accordion title="Meta-Llama">
    Meta's Llama API provides access to Meta's family of large language models.
    The API is available through the [Meta Llama API](https://llama.developer.meta.com?utm_source=partner-crewai\&utm_medium=website).
    Set the following environment variables in your `.env` file:

    ```toml Code
    # Meta Llama API Key Configuration
    LLAMA_API_KEY=LLM|your_api_key_here
    ```

    Example usage in your CrewAI project:

    ```python Code
    from crewai import LLM

    # Initialize Meta Llama LLM
    llm = LLM(
        model="meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8",
        temperature=0.8,
        stop=["END"],
        seed=42
    )
    ```

    All models listed here [https://llama.developer.meta.com/docs/models/](https://llama.developer.meta.com/docs/models/) are supported.

    | Model ID                                            | Input context length | Output context length | Input Modalities | Output Modalities |
    | --------------------------------------------------- | -------------------- | --------------------- | ---------------- | ----------------- |
    | `meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8`     | 128k                 | 4028                  | Text, Image      | Text              |
    | `meta_llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 128k                 | 4028                  | Text, Image      | Text              |
    | `meta_llama/Llama-3.3-70B-Instruct`                 | 128k                 | 4028                  | Text             | Text              |
    | `meta_llama/Llama-3.3-8B-Instruct`                  | 128k                 | 4028                  | Text             | Text              |
  </Accordion>

  <Accordion title="Anthropic">
    ```toml Code
    # Required
    ANTHROPIC_API_KEY=sk-ant-...

    # Optional
    ANTHROPIC_API_BASE=<custom-base-url>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="anthropic/claude-3-sonnet-20240229-v1:0",
        temperature=0.7
    )
    ```
  </Accordion>

  <Accordion title="Google (Gemini API)">
    Set your API key in your `.env` file. If you need a key, or need to find an
    existing key, check [AI Studio](https://aistudio.google.com/apikey).

    ```toml .env
    # https://ai.google.dev/gemini-api/docs/api-key
    GEMINI_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    from crewai import LLM

    llm = LLM(
        model="gemini/gemini-2.0-flash",
        temperature=0.7,
    )
    ```

    ### Gemini models

    Google offers a range of powerful models optimized for different use cases.

    | Model                          | Context Window | Best For                                                                                                         |
    | ------------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------------- |
    | gemini-2.5-flash-preview-04-17 | 1M tokens      | Adaptive thinking, cost efficiency                                                                               |
    | gemini-2.5-pro-preview-05-06   | 1M tokens      | Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more                             |
    | gemini-2.0-flash               | 1M tokens      | Next generation features, speed, thinking, and realtime streaming                                                |
    | gemini-2.0-flash-lite          | 1M tokens      | Cost efficiency and low latency                                                                                  |
    | gemini-1.5-flash               | 1M tokens      | Balanced multimodal model, good for most tasks                                                                   |
    | gemini-1.5-flash-8B            | 1M tokens      | Fastest, most cost-efficient, good for high-frequency tasks                                                      |
    | gemini-1.5-pro                 | 2M tokens      | Best performing, wide variety of reasoning tasks including logical reasoning, coding, and creative collaboration |

    The full list of models is available in the [Gemini model docs](https://ai.google.dev/gemini-api/docs/models).

    ### Gemma

    The Gemini API also allows you to use your API key to access [Gemma models](https://ai.google.dev/gemma/docs) hosted on Google infrastructure.

    | Model          | Context Window |
    | -------------- | -------------- |
    | gemma-3-1b-it  | 32k tokens     |
    | gemma-3-4b-it  | 32k tokens     |
    | gemma-3-12b-it | 32k tokens     |
    | gemma-3-27b-it | 128k tokens    |
  </Accordion>

  <Accordion title="Google (Vertex AI)">
    Get credentials from your Google Cloud Console and save it to a JSON file, then load it with the following code:

    ```python Code
    import json

    file_path = 'path/to/vertex_ai_service_account.json'

    # Load the JSON file
    with open(file_path, 'r') as file:
        vertex_credentials = json.load(file)

    # Convert the credentials to a JSON string
    vertex_credentials_json = json.dumps(vertex_credentials)
    ```

    Example usage in your CrewAI project:

    ```python Code
    from crewai import LLM

    llm = LLM(
        model="gemini/gemini-1.5-pro-latest",
        temperature=0.7,
        vertex_credentials=vertex_credentials_json
    )
    ```

    Google offers a range of powerful models optimized for different use cases:

    | Model                          | Context Window | Best For                                                                                                         |
    | ------------------------------ | -------------- | ---------------------------------------------------------------------------------------------------------------- |
    | gemini-2.5-flash-preview-04-17 | 1M tokens      | Adaptive thinking, cost efficiency                                                                               |
    | gemini-2.5-pro-preview-05-06   | 1M tokens      | Enhanced thinking and reasoning, multimodal understanding, advanced coding, and more                             |
    | gemini-2.0-flash               | 1M tokens      | Next generation features, speed, thinking, and realtime streaming                                                |
    | gemini-2.0-flash-lite          | 1M tokens      | Cost efficiency and low latency                                                                                  |
    | gemini-1.5-flash               | 1M tokens      | Balanced multimodal model, good for most tasks                                                                   |
    | gemini-1.5-flash-8B            | 1M tokens      | Fastest, most cost-efficient, good for high-frequency tasks                                                      |
    | gemini-1.5-pro                 | 2M tokens      | Best performing, wide variety of reasoning tasks including logical reasoning, coding, and creative collaboration |
  </Accordion>

  <Accordion title="Azure">
    ```toml Code
    # Required
    AZURE_API_KEY=<your-api-key>
    AZURE_API_BASE=<your-resource-url>
    AZURE_API_VERSION=<api-version>

    # Optional
    AZURE_AD_TOKEN=<your-azure-ad-token>
    AZURE_API_TYPE=<your-azure-api-type>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="azure/gpt-4",
        api_version="2023-05-15"
    )
    ```
  </Accordion>

  <Accordion title="AWS Bedrock">
    ```toml Code
    AWS_ACCESS_KEY_ID=<your-access-key>
    AWS_SECRET_ACCESS_KEY=<your-secret-key>
    AWS_DEFAULT_REGION=<your-region>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="bedrock/anthropic.claude-3-sonnet-20240229-v1:0"
    )
    ```

    Before using Amazon Bedrock, make sure you have boto3 installed in your environment

    [Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html) is a managed service that provides access to multiple foundation models from top AI companies through a unified API, enabling secure and responsible AI application development.

    | Model                   | Context Window     | Best For                                                                                                                              |
    | ----------------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------------- |
    | Amazon Nova Pro         | Up to 300k tokens  | High-performance, model balancing accuracy, speed, and cost-effectiveness across diverse tasks.                                       |
    | Amazon Nova Micro       | Up to 128k tokens  | High-performance, cost-effective text-only model optimized for lowest latency responses.                                              |
    | Amazon Nova Lite        | Up to 300k tokens  | High-performance, affordable multimodal processing for images, video, and text with real-time capabilities.                           |
    | Claude 3.7 Sonnet       | Up to 128k tokens  | High-performance, best for complex reasoning, coding & AI agents                                                                      |
    | Claude 3.5 Sonnet v2    | Up to 200k tokens  | State-of-the-art model specialized in software engineering, agentic capabilities, and computer interaction at optimized cost.         |
    | Claude 3.5 Sonnet       | Up to 200k tokens  | High-performance model delivering superior intelligence and reasoning across diverse tasks with optimal speed-cost balance.           |
    | Claude 3.5 Haiku        | Up to 200k tokens  | Fast, compact multimodal model optimized for quick responses and seamless human-like interactions                                     |
    | Claude 3 Sonnet         | Up to 200k tokens  | Multimodal model balancing intelligence and speed for high-volume deployments.                                                        |
    | Claude 3 Haiku          | Up to 200k tokens  | Compact, high-speed multimodal model optimized for quick responses and natural conversational interactions                            |
    | Claude 3 Opus           | Up to 200k tokens  | Most advanced multimodal model exceling at complex tasks with human-like reasoning and superior contextual understanding.             |
    | Claude 2.1              | Up to 200k tokens  | Enhanced version with expanded context window, improved reliability, and reduced hallucinations for long-form and RAG applications    |
    | Claude                  | Up to 100k tokens  | Versatile model excelling in sophisticated dialogue, creative content, and precise instruction following.                             |
    | Claude Instant          | Up to 100k tokens  | Fast, cost-effective model for everyday tasks like dialogue, analysis, summarization, and document Q\&A                               |
    | Llama 3.1 405B Instruct | Up to 128k tokens  | Advanced LLM for synthetic data generation, distillation, and inference for chatbots, coding, and domain-specific tasks.              |
    | Llama 3.1 70B Instruct  | Up to 128k tokens  | Powers complex conversations with superior contextual understanding, reasoning and text generation.                                   |
    | Llama 3.1 8B Instruct   | Up to 128k tokens  | Advanced state-of-the-art model with language understanding, superior reasoning, and text generation.                                 |
    | Llama 3 70B Instruct    | Up to 8k tokens    | Powers complex conversations with superior contextual understanding, reasoning and text generation.                                   |
    | Llama 3 8B Instruct     | Up to 8k tokens    | Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.                                   |
    | Titan Text G1 - Lite    | Up to 4k tokens    | Lightweight, cost-effective model optimized for English tasks and fine-tuning with focus on summarization and content generation.     |
    | Titan Text G1 - Express | Up to 8k tokens    | Versatile model for general language tasks, chat, and RAG applications with support for English and 100+ languages.                   |
    | Cohere Command          | Up to 4k tokens    | Model specialized in following user commands and delivering practical enterprise solutions.                                           |
    | Jurassic-2 Mid          | Up to 8,191 tokens | Cost-effective model balancing quality and affordability for diverse language tasks like Q\&A, summarization, and content generation. |
    | Jurassic-2 Ultra        | Up to 8,191 tokens | Model for advanced text generation and comprehension, excelling in complex tasks like analysis and content creation.                  |
    | Jamba-Instruct          | Up to 256k tokens  | Model with extended context window optimized for cost-effective text generation, summarization, and Q\&A.                             |
    | Mistral 7B Instruct     | Up to 32k tokens   | This LLM follows instructions, completes requests, and generates creative text.                                                       |
    | Mistral 8x7B Instruct   | Up to 32k tokens   | An MOE LLM that follows instructions, completes requests, and generates creative text.                                                |
  </Accordion>

  <Accordion title="Amazon SageMaker">
    ```toml Code
    AWS_ACCESS_KEY_ID=<your-access-key>
    AWS_SECRET_ACCESS_KEY=<your-secret-key>
    AWS_DEFAULT_REGION=<your-region>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="sagemaker/<my-endpoint>"
    )
    ```
  </Accordion>

  <Accordion title="Mistral">
    Set the following environment variables in your `.env` file:

    ```toml Code
    MISTRAL_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="mistral/mistral-large-latest",
        temperature=0.7
    )
    ```
  </Accordion>

  <Accordion title="Nvidia NIM">
    Set the following environment variables in your `.env` file:

    ```toml Code
    NVIDIA_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="nvidia_nim/meta/llama3-70b-instruct",
        temperature=0.7
    )
    ```

    Nvidia NIM provides a comprehensive suite of models for various use cases, from general-purpose tasks to specialized applications.

    | Model                                       | Context Window | Best For                                                                                                                    |
    | ------------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------------------------------- |
    | nvidia/mistral-nemo-minitron-8b-8k-instruct | 8,192 tokens   | State-of-the-art small language model delivering superior accuracy for chatbot, virtual assistants, and content generation. |
    | nvidia/nemotron-4-mini-hindi-4b-instruct    | 4,096 tokens   | A bilingual Hindi-English SLM for on-device inference, tailored specifically for Hindi Language.                            |
    | nvidia/llama-3.1-nemotron-70b-instruct      | 128k tokens    | Customized for enhanced helpfulness in responses                                                                            |
    | nvidia/llama3-chatqa-1.5-8b                 | 128k tokens    | Advanced LLM to generate high-quality, context-aware responses for chatbots and search engines.                             |
    | nvidia/llama3-chatqa-1.5-70b                | 128k tokens    | Advanced LLM to generate high-quality, context-aware responses for chatbots and search engines.                             |
    | nvidia/vila                                 | 128k tokens    | Multi-modal vision-language model that understands text/img/video and creates informative responses                         |
    | nvidia/neva-22                              | 4,096 tokens   | Multi-modal vision-language model that understands text/images and generates informative responses                          |
    | nvidia/nemotron-mini-4b-instruct            | 8,192 tokens   | General-purpose tasks                                                                                                       |
    | nvidia/usdcode-llama3-70b-instruct          | 128k tokens    | State-of-the-art LLM that answers OpenUSD knowledge queries and generates USD-Python code.                                  |
    | nvidia/nemotron-4-340b-instruct             | 4,096 tokens   | Creates diverse synthetic data that mimics the characteristics of real-world data.                                          |
    | meta/codellama-70b                          | 100k tokens    | LLM capable of generating code from natural language and vice versa.                                                        |
    | meta/llama2-70b                             | 4,096 tokens   | Cutting-edge large language AI model capable of generating text and code in response to prompts.                            |
    | meta/llama3-8b-instruct                     | 8,192 tokens   | Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.                         |
    | meta/llama3-70b-instruct                    | 8,192 tokens   | Powers complex conversations with superior contextual understanding, reasoning and text generation.                         |
    | meta/llama-3.1-8b-instruct                  | 128k tokens    | Advanced state-of-the-art model with language understanding, superior reasoning, and text generation.                       |
    | meta/llama-3.1-70b-instruct                 | 128k tokens    | Powers complex conversations with superior contextual understanding, reasoning and text generation.                         |
    | meta/llama-3.1-405b-instruct                | 128k tokens    | Advanced LLM for synthetic data generation, distillation, and inference for chatbots, coding, and domain-specific tasks.    |
    | meta/llama-3.2-1b-instruct                  | 128k tokens    | Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.        |
    | meta/llama-3.2-3b-instruct                  | 128k tokens    | Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.        |
    | meta/llama-3.2-11b-vision-instruct          | 128k tokens    | Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.        |
    | meta/llama-3.2-90b-vision-instruct          | 128k tokens    | Advanced state-of-the-art small language model with language understanding, superior reasoning, and text generation.        |
    | google/gemma-7b                             | 8,192 tokens   | Cutting-edge text generation model text understanding, transformation, and code generation.                                 |
    | google/gemma-2b                             | 8,192 tokens   | Cutting-edge text generation model text understanding, transformation, and code generation.                                 |
    | google/codegemma-7b                         | 8,192 tokens   | Cutting-edge model built on Google's Gemma-7B specialized for code generation and code completion.                          |
    | google/codegemma-1.1-7b                     | 8,192 tokens   | Advanced programming model for code generation, completion, reasoning, and instruction following.                           |
    | google/recurrentgemma-2b                    | 8,192 tokens   | Novel recurrent architecture based language model for faster inference when generating long sequences.                      |
    | google/gemma-2-9b-it                        | 8,192 tokens   | Cutting-edge text generation model text understanding, transformation, and code generation.                                 |
    | google/gemma-2-27b-it                       | 8,192 tokens   | Cutting-edge text generation model text understanding, transformation, and code generation.                                 |
    | google/gemma-2-2b-it                        | 8,192 tokens   | Cutting-edge text generation model text understanding, transformation, and code generation.                                 |
    | google/deplot                               | 512 tokens     | One-shot visual language understanding model that translates images of plots into tables.                                   |
    | google/paligemma                            | 8,192 tokens   | Vision language model adept at comprehending text and visual inputs to produce informative responses.                       |
    | mistralai/mistral-7b-instruct-v0.2          | 32k tokens     | This LLM follows instructions, completes requests, and generates creative text.                                             |
    | mistralai/mixtral-8x7b-instruct-v0.1        | 8,192 tokens   | An MOE LLM that follows instructions, completes requests, and generates creative text.                                      |
    | mistralai/mistral-large                     | 4,096 tokens   | Creates diverse synthetic data that mimics the characteristics of real-world data.                                          |
    | mistralai/mixtral-8x22b-instruct-v0.1       | 8,192 tokens   | Creates diverse synthetic data that mimics the characteristics of real-world data.                                          |
    | mistralai/mistral-7b-instruct-v0.3          | 32k tokens     | This LLM follows instructions, completes requests, and generates creative text.                                             |
    | nv-mistralai/mistral-nemo-12b-instruct      | 128k tokens    | Most advanced language model for reasoning, code, multilingual tasks; runs on a single GPU.                                 |
    | mistralai/mamba-codestral-7b-v0.1           | 256k tokens    | Model for writing and interacting with code across a wide range of programming languages and tasks.                         |
    | microsoft/phi-3-mini-128k-instruct          | 128K tokens    | Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.                                       |
    | microsoft/phi-3-mini-4k-instruct            | 4,096 tokens   | Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.                                       |
    | microsoft/phi-3-small-8k-instruct           | 8,192 tokens   | Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.                                       |
    | microsoft/phi-3-small-128k-instruct         | 128K tokens    | Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.                                       |
    | microsoft/phi-3-medium-4k-instruct          | 4,096 tokens   | Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.                                       |
    | microsoft/phi-3-medium-128k-instruct        | 128K tokens    | Lightweight, state-of-the-art open LLM with strong math and logical reasoning skills.                                       |
    | microsoft/phi-3.5-mini-instruct             | 128K tokens    | Lightweight multilingual LLM powering AI applications in latency bound, memory/compute constrained environments             |
    | microsoft/phi-3.5-moe-instruct              | 128K tokens    | Advanced LLM based on Mixture of Experts architecture to deliver compute efficient content generation                       |
    | microsoft/kosmos-2                          | 1,024 tokens   | Groundbreaking multimodal model designed to understand and reason about visual elements in images.                          |
    | microsoft/phi-3-vision-128k-instruct        | 128k tokens    | Cutting-edge open multimodal model exceling in high-quality reasoning from images.                                          |
    | microsoft/phi-3.5-vision-instruct           | 128k tokens    | Cutting-edge open multimodal model exceling in high-quality reasoning from images.                                          |
    | databricks/dbrx-instruct                    | 12k tokens     | A general-purpose LLM with state-of-the-art performance in language understanding, coding, and RAG.                         |
    | snowflake/arctic                            | 1,024 tokens   | Delivers high efficiency inference for enterprise applications focused on SQL generation and coding.                        |
    | aisingapore/sea-lion-7b-instruct            | 4,096 tokens   | LLM to represent and serve the linguistic and cultural diversity of Southeast Asia                                          |
    | ibm/granite-8b-code-instruct                | 4,096 tokens   | Software programming LLM for code generation, completion, explanation, and multi-turn conversion.                           |
    | ibm/granite-34b-code-instruct               | 8,192 tokens   | Software programming LLM for code generation, completion, explanation, and multi-turn conversion.                           |
    | ibm/granite-3.0-8b-instruct                 | 4,096 tokens   | Advanced Small Language Model supporting RAG, summarization, classification, code, and agentic AI                           |
    | ibm/granite-3.0-3b-a800m-instruct           | 4,096 tokens   | Highly efficient Mixture of Experts model for RAG, summarization, entity extraction, and classification                     |
    | mediatek/breeze-7b-instruct                 | 4,096 tokens   | Creates diverse synthetic data that mimics the characteristics of real-world data.                                          |
    | upstage/solar-10.7b-instruct                | 4,096 tokens   | Excels in NLP tasks, particularly in instruction-following, reasoning, and mathematics.                                     |
    | writer/palmyra-med-70b-32k                  | 32k tokens     | Leading LLM for accurate, contextually relevant responses in the medical domain.                                            |
    | writer/palmyra-med-70b                      | 32k tokens     | Leading LLM for accurate, contextually relevant responses in the medical domain.                                            |
    | writer/palmyra-fin-70b-32k                  | 32k tokens     | Specialized LLM for financial analysis, reporting, and data processing                                                      |
    | 01-ai/yi-large                              | 32k tokens     | Powerful model trained on English and Chinese for diverse tasks including chatbot and creative writing.                     |
    | deepseek-ai/deepseek-coder-6.7b-instruct    | 2k tokens      | Powerful coding model offering advanced capabilities in code generation, completion, and infilling                          |
    | rakuten/rakutenai-7b-instruct               | 1,024 tokens   | Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.                         |
    | rakuten/rakutenai-7b-chat                   | 1,024 tokens   | Advanced state-of-the-art LLM with language understanding, superior reasoning, and text generation.                         |
    | baichuan-inc/baichuan2-13b-chat             | 4,096 tokens   | Support Chinese and English chat, coding, math, instruction following, solving quizzes                                      |
  </Accordion>

  <Accordion title="Local NVIDIA NIM Deployed using WSL2">
    NVIDIA NIM enables you to run powerful LLMs locally on your Windows machine using WSL2 (Windows Subsystem for Linux).
    This approach allows you to leverage your NVIDIA GPU for private, secure, and cost-effective AI inference without relying on cloud services.
    Perfect for development, testing, or production scenarios where data privacy or offline capabilities are required.

    Here is a step-by-step guide to setting up a local NVIDIA NIM model:

    1. Follow installation instructions from [NVIDIA Website](https://docs.nvidia.com/nim/wsl2/latest/getting-started.html)

    2. Install the local model. For Llama 3.1-8b follow [instructions](https://build.nvidia.com/meta/llama-3_1-8b-instruct/deploy)

    3. Configure your crewai local models:

    ```python Code
    from crewai.llm import LLM

    local_nvidia_nim_llm = LLM(
        model="openai/meta/llama-3.1-8b-instruct", # it's an openai-api compatible model
        base_url="http://localhost:8000/v1",
        api_key="<your_api_key|any text if you have not configured it>", # api_key is required, but you can use any text
    )

    # Then you can use it in your crew:

    @CrewBase
    class MyCrew():
        # ...

        @agent
        def researcher(self) -> Agent:
            return Agent(
                config=self.agents_config['researcher'], # type: ignore[index]
                llm=local_nvidia_nim_llm
            )

        # ...
    ```
  </Accordion>

  <Accordion title="Groq">
    Set the following environment variables in your `.env` file:

    ```toml Code
    GROQ_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="groq/llama-3.2-90b-text-preview",
        temperature=0.7
    )
    ```

    | Model            | Context Window | Best For                              |
    | ---------------- | -------------- | ------------------------------------- |
    | Llama 3.1 70B/8B | 131,072 tokens | High-performance, large context tasks |
    | Llama 3.2 Series | 8,192 tokens   | General-purpose tasks                 |
    | Mixtral 8x7B     | 32,768 tokens  | Balanced performance and context      |
  </Accordion>

  <Accordion title="IBM watsonx.ai">
    Set the following environment variables in your `.env` file:

    ```toml Code
    # Required
    WATSONX_URL=<your-url>
    WATSONX_APIKEY=<your-apikey>
    WATSONX_PROJECT_ID=<your-project-id>

    # Optional
    WATSONX_TOKEN=<your-token>
    WATSONX_DEPLOYMENT_SPACE_ID=<your-space-id>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="watsonx/meta-llama/llama-3-1-70b-instruct",
        base_url="https://api.watsonx.ai/v1"
    )
    ```
  </Accordion>

  <Accordion title="Ollama (Local LLMs)">
    1. Install Ollama: [ollama.ai](https://ollama.ai/)
    2. Run a model: `ollama run llama3`
    3. Configure:

    ```python Code
    llm = LLM(
        model="ollama/llama3:70b",
        base_url="http://localhost:11434"
    )
    ```
  </Accordion>

  <Accordion title="Fireworks AI">
    Set the following environment variables in your `.env` file:

    ```toml Code
    FIREWORKS_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="fireworks_ai/accounts/fireworks/models/llama-v3-70b-instruct",
        temperature=0.7
    )
    ```
  </Accordion>

  <Accordion title="Perplexity AI">
    Set the following environment variables in your `.env` file:

    ```toml Code
    PERPLEXITY_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="llama-3.1-sonar-large-128k-online",
        base_url="https://api.perplexity.ai/"
    )
    ```
  </Accordion>

  <Accordion title="Hugging Face">
    Set the following environment variables in your `.env` file:

    ```toml Code
    HF_TOKEN=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="huggingface/meta-llama/Meta-Llama-3.1-8B-Instruct"
    )
    ```
  </Accordion>

  <Accordion title="SambaNova">
    Set the following environment variables in your `.env` file:

    ```toml Code
    SAMBANOVA_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="sambanova/Meta-Llama-3.1-8B-Instruct",
        temperature=0.7
    )
    ```

    | Model            | Context Window       | Best For                              |
    | ---------------- | -------------------- | ------------------------------------- |
    | Llama 3.1 70B/8B | Up to 131,072 tokens | High-performance, large context tasks |
    | Llama 3.1 405B   | 8,192 tokens         | High-performance and output quality   |
    | Llama 3.2 Series | 8,192 tokens         | General-purpose, multimodal tasks     |
    | Llama 3.3 70B    | Up to 131,072 tokens | High-performance and output quality   |
    | Qwen2 familly    | 8,192 tokens         | High-performance and output quality   |
  </Accordion>

  <Accordion title="Cerebras">
    Set the following environment variables in your `.env` file:

    ```toml Code
    # Required
    CEREBRAS_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="cerebras/llama3.1-70b",
        temperature=0.7,
        max_tokens=8192
    )
    ```

    <Info>
      Cerebras features:

      * Fast inference speeds
      * Competitive pricing
      * Good balance of speed and quality
      * Support for long context windows
    </Info>
  </Accordion>

  <Accordion title="Open Router">
    Set the following environment variables in your `.env` file:

    ```toml Code
    OPENROUTER_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="openrouter/deepseek/deepseek-r1",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    ```

    <Info>
      Open Router models:

      * openrouter/deepseek/deepseek-r1
      * openrouter/deepseek/deepseek-chat
    </Info>
  </Accordion>

  <Accordion title="Nebius AI Studio">
    Set the following environment variables in your `.env` file:

    ```toml Code
    NEBIUS_API_KEY=<your-api-key>
    ```

    Example usage in your CrewAI project:

    ```python Code
    llm = LLM(
        model="nebius/Qwen/Qwen3-30B-A3B"
    )
    ```

    <Info>
      Nebius AI Studio features:

      * Large collection of open source models
      * Higher rate limits
      * Competitive pricing
      * Good balance of speed and quality
    </Info>
  </Accordion>
</AccordionGroup>

## Streaming Responses

CrewAI supports streaming responses from LLMs, allowing your application to receive and process outputs in real-time as they're generated.

<Tabs>
  <Tab title="Basic Setup">
    Enable streaming by setting the `stream` parameter to `True` when initializing your LLM:

    ```python
    from crewai import LLM

    # Create an LLM with streaming enabled
    llm = LLM(
        model="openai/gpt-4o",
        stream=True  # Enable streaming
    )
    ```

    When streaming is enabled, responses are delivered in chunks as they're generated, creating a more responsive user experience.
  </Tab>

  <Tab title="Event Handling">
    CrewAI emits events for each chunk received during streaming:

    ```python
    from crewai.utilities.events import (
      LLMStreamChunkEvent
    )
    from crewai.utilities.events.base_event_listener import BaseEventListener

    class MyCustomListener(BaseEventListener):
        def setup_listeners(self, crewai_event_bus):
            @crewai_event_bus.on(LLMStreamChunkEvent)
            def on_llm_stream_chunk(self, event: LLMStreamChunkEvent):
              # Process each chunk as it arrives
              print(f"Received chunk: {event.chunk}")

    my_listener = MyCustomListener()
    ```

    <Tip>
      [Click here](https://docs.crewai.com/concepts/event-listener#event-listeners) for more details
    </Tip>
  </Tab>

  <Tab title="Agent & Task Tracking">
    All LLM events in CrewAI include agent and task information, allowing you to track and filter LLM interactions by specific agents or tasks:

    ```python
    from crewai import LLM, Agent, Task, Crew
    from crewai.utilities.events import LLMStreamChunkEvent
    from crewai.utilities.events.base_event_listener import BaseEventListener

    class MyCustomListener(BaseEventListener):
        def setup_listeners(self, crewai_event_bus):
            @crewai_event_bus.on(LLMStreamChunkEvent)
            def on_llm_stream_chunk(source, event):
                if researcher.id == event.agent_id:
                    print("\n==============\n Got event:", event, "\n==============\n")


    my_listener = MyCustomListener()

    llm = LLM(model="gpt-4o-mini", temperature=0, stream=True)

    researcher = Agent(
        role="About User",
        goal="You know everything about the user.",
        backstory="""You are a master at understanding people and their preferences.""",
        llm=llm,
    )

    search = Task(
        description="Answer the following questions about the user: {question}",
        expected_output="An answer to the question.",
        agent=researcher,
    )

    crew = Crew(agents=[researcher], tasks=[search])

    result = crew.kickoff(
        inputs={"question": "..."}
    )
    ```

    <Info>
      This feature is particularly useful for:

      * Debugging specific agent behaviors
      * Logging LLM usage by task type
      * Auditing which agents are making what types of LLM calls
      * Performance monitoring of specific tasks
    </Info>
  </Tab>
</Tabs>

## Structured LLM Calls

CrewAI supports structured responses from LLM calls by allowing you to define a `response_format` using a Pydantic model. This enables the framework to automatically parse and validate the output, making it easier to integrate the response into your application without manual post-processing.

For example, you can define a Pydantic model to represent the expected response structure and pass it as the `response_format` when instantiating the LLM. The model will then be used to convert the LLM output into a structured Python object.

```python Code
from crewai import LLM

class Dog(BaseModel):
    name: str
    age: int
    breed: str


llm = LLM(model="gpt-4o", response_format=Dog)

response = llm.call(
    "Analyze the following messages and return the name, age, and breed. "
    "Meet Kona! She is 3 years old and is a black german shepherd."
)
print(response)

# Output:
# Dog(name='Kona', age=3, breed='black german shepherd')
```

## Advanced Features and Optimization

Learn how to get the most out of your LLM configuration:

<AccordionGroup>
  <Accordion title="Context Window Management">
    CrewAI includes smart context management features:

    ```python
    from crewai import LLM

    # CrewAI automatically handles:
    # 1. Token counting and tracking
    # 2. Content summarization when needed
    # 3. Task splitting for large contexts

    llm = LLM(
        model="gpt-4",
        max_tokens=4000,  # Limit response length
    )
    ```

    <Info>
      Best practices for context management:

      1. Choose models with appropriate context windows
      2. Pre-process long inputs when possible
      3. Use chunking for large documents
      4. Monitor token usage to optimize costs
    </Info>
  </Accordion>

  <Accordion title="Performance Optimization">
    <Steps>
      <Step title="Token Usage Optimization">
        Choose the right context window for your task:

        * Small tasks (up to 4K tokens): Standard models
        * Medium tasks (between 4K-32K): Enhanced models
        * Large tasks (over 32K): Large context models

        ```python
        # Configure model with appropriate settings
        llm = LLM(
            model="openai/gpt-4-turbo-preview",
            temperature=0.7,    # Adjust based on task
            max_tokens=4096,    # Set based on output needs
            timeout=300        # Longer timeout for complex tasks
        )
        ```

        <Tip>
          * Lower temperature (0.1 to 0.3) for factual responses
          * Higher temperature (0.7 to 0.9) for creative tasks
        </Tip>
      </Step>

      <Step title="Best Practices">
        1. Monitor token usage
        2. Implement rate limiting
        3. Use caching when possible
        4. Set appropriate max\_tokens limits
      </Step>
    </Steps>

    <Info>
      Remember to regularly monitor your token usage and adjust your configuration as needed to optimize costs and performance.
    </Info>
  </Accordion>

  <Accordion title="Drop Additional Parameters">
    CrewAI internally uses Litellm for LLM calls, which allows you to drop additional parameters that are not needed for your specific use case. This can help simplify your code and reduce the complexity of your LLM configuration.
    For example, if you don't need to send the <code>stop</code> parameter, you can simply omit it from your LLM call:

    ```python
    from crewai import LLM
    import os

    os.environ["OPENAI_API_KEY"] = "<api-key>"

    o3_llm = LLM(
        model="o3",
        drop_params=True,
        additional_drop_params=["stop"]
    )
    ```
  </Accordion>
</AccordionGroup>

## Common Issues and Solutions

<Tabs>
  <Tab title="Authentication">
    <Warning>
      Most authentication issues can be resolved by checking API key format and environment variable names.
    </Warning>

    ```bash
    # OpenAI
    OPENAI_API_KEY=sk-...

    # Anthropic
    ANTHROPIC_API_KEY=sk-ant-...
    ```
  </Tab>

  <Tab title="Model Names">
    <Check>
      Always include the provider prefix in model names
    </Check>

    ```python
    # Correct
    llm = LLM(model="openai/gpt-4")

    # Incorrect
    llm = LLM(model="gpt-4")
    ```
  </Tab>

  <Tab title="Context Length">
    <Tip>
      Use larger context models for extensive tasks
    </Tip>

    ```python
    # Large context model
    llm = LLM(model="openai/gpt-4o")  # 128K tokens
    ```
  </Tab>
</Tabs>


# Processes

> Detailed guide on workflow management through processes in CrewAI, with updated implementation details.

## Overview

<Tip>
  Processes orchestrate the execution of tasks by agents, akin to project management in human teams.
  These processes ensure tasks are distributed and executed efficiently, in alignment with a predefined strategy.
</Tip>

## Process Implementations

* **Sequential**: Executes tasks sequentially, ensuring tasks are completed in an orderly progression.
* **Hierarchical**: Organizes tasks in a managerial hierarchy, where tasks are delegated and executed based on a structured chain of command. A manager language model (`manager_llm`) or a custom manager agent (`manager_agent`) must be specified in the crew to enable the hierarchical process, facilitating the creation and management of tasks by the manager.
* **Consensual Process (Planned)**: Aiming for collaborative decision-making among agents on task execution, this process type introduces a democratic approach to task management within CrewAI. It is planned for future development and is not currently implemented in the codebase.

## The Role of Processes in Teamwork

Processes enable individual agents to operate as a cohesive unit, streamlining their efforts to achieve common objectives with efficiency and coherence.

## Assigning Processes to a Crew

To assign a process to a crew, specify the process type upon crew creation to set the execution strategy. For a hierarchical process, ensure to define `manager_llm` or `manager_agent` for the manager agent.

```python
from crewai import Crew, Process

# Example: Creating a crew with a sequential process
crew = Crew(
    agents=my_agents,
    tasks=my_tasks,
    process=Process.sequential
)

# Example: Creating a crew with a hierarchical process
# Ensure to provide a manager_llm or manager_agent
crew = Crew(
    agents=my_agents,
    tasks=my_tasks,
    process=Process.hierarchical,
    manager_llm="gpt-4o"
    # or
    # manager_agent=my_manager_agent
)
```

**Note:** Ensure `my_agents` and `my_tasks` are defined prior to creating a `Crew` object, and for the hierarchical process, either `manager_llm` or `manager_agent` is also required.

## Sequential Process

This method mirrors dynamic team workflows, progressing through tasks in a thoughtful and systematic manner. Task execution follows the predefined order in the task list, with the output of one task serving as context for the next.

To customize task context, utilize the `context` parameter in the `Task` class to specify outputs that should be used as context for subsequent tasks.

## Hierarchical Process

Emulates a corporate hierarchy, CrewAI allows specifying a custom manager agent or automatically creates one, requiring the specification of a manager language model (`manager_llm`). This agent oversees task execution, including planning, delegation, and validation. Tasks are not pre-assigned; the manager allocates tasks to agents based on their capabilities, reviews outputs, and assesses task completion.

## Process Class: Detailed Overview

The `Process` class is implemented as an enumeration (`Enum`), ensuring type safety and restricting process values to the defined types (`sequential`, `hierarchical`). The consensual process is planned for future inclusion, emphasizing our commitment to continuous development and innovation.

## Conclusion

The structured collaboration facilitated by processes within CrewAI is crucial for enabling systematic teamwork among agents.
This documentation has been updated to reflect the latest features, enhancements, and the planned integration of the Consensual Process, ensuring users have access to the most current and comprehensive information.


# Collaboration

> How to enable agents to work together, delegate tasks, and communicate effectively within CrewAI teams.

## Overview

Collaboration in CrewAI enables agents to work together as a team by delegating tasks and asking questions to leverage each other's expertise. When `allow_delegation=True`, agents automatically gain access to powerful collaboration tools.

## Quick Start: Enable Collaboration

```python
from crewai import Agent, Crew, Task

# Enable collaboration for agents
researcher = Agent(
    role="Research Specialist",
    goal="Conduct thorough research on any topic",
    backstory="Expert researcher with access to various sources",
    allow_delegation=True,  # 🔑 Key setting for collaboration
    verbose=True
)

writer = Agent(
    role="Content Writer", 
    goal="Create engaging content based on research",
    backstory="Skilled writer who transforms research into compelling content",
    allow_delegation=True,  # 🔑 Enables asking questions to other agents
    verbose=True
)

# Agents can now collaborate automatically
crew = Crew(
    agents=[researcher, writer],
    tasks=[...],
    verbose=True
)
```

## How Agent Collaboration Works

When `allow_delegation=True`, CrewAI automatically provides agents with two powerful tools:

### 1. **Delegate Work Tool**

Allows agents to assign tasks to teammates with specific expertise.

```python
# Agent automatically gets this tool:
# Delegate work to coworker(task: str, context: str, coworker: str)
```

### 2. **Ask Question Tool**

Enables agents to ask specific questions to gather information from colleagues.

```python
# Agent automatically gets this tool:
# Ask question to coworker(question: str, context: str, coworker: str)
```

## Collaboration in Action

Here's a complete example showing agents collaborating on a content creation task:

```python
from crewai import Agent, Crew, Task, Process

# Create collaborative agents
researcher = Agent(
    role="Research Specialist",
    goal="Find accurate, up-to-date information on any topic",
    backstory="""You're a meticulous researcher with expertise in finding 
    reliable sources and fact-checking information across various domains.""",
    allow_delegation=True,
    verbose=True
)

writer = Agent(
    role="Content Writer",
    goal="Create engaging, well-structured content",
    backstory="""You're a skilled content writer who excels at transforming 
    research into compelling, readable content for different audiences.""",
    allow_delegation=True,
    verbose=True
)

editor = Agent(
    role="Content Editor",
    goal="Ensure content quality and consistency",
    backstory="""You're an experienced editor with an eye for detail, 
    ensuring content meets high standards for clarity and accuracy.""",
    allow_delegation=True,
    verbose=True
)

# Create a task that encourages collaboration
article_task = Task(
    description="""Write a comprehensive 1000-word article about 'The Future of AI in Healthcare'.
    
    The article should include:
    - Current AI applications in healthcare
    - Emerging trends and technologies  
    - Potential challenges and ethical considerations
    - Expert predictions for the next 5 years
    
    Collaborate with your teammates to ensure accuracy and quality.""",
    expected_output="A well-researched, engaging 1000-word article with proper structure and citations",
    agent=writer  # Writer leads, but can delegate research to researcher
)

# Create collaborative crew
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[article_task],
    process=Process.sequential,
    verbose=True
)

result = crew.kickoff()
```

## Collaboration Patterns

### Pattern 1: Research → Write → Edit

```python
research_task = Task(
    description="Research the latest developments in quantum computing",
    expected_output="Comprehensive research summary with key findings and sources",
    agent=researcher
)

writing_task = Task(
    description="Write an article based on the research findings",
    expected_output="Engaging 800-word article about quantum computing",
    agent=writer,
    context=[research_task]  # Gets research output as context
)

editing_task = Task(
    description="Edit and polish the article for publication",
    expected_output="Publication-ready article with improved clarity and flow",
    agent=editor,
    context=[writing_task]  # Gets article draft as context
)
```

### Pattern 2: Collaborative Single Task

```python
collaborative_task = Task(
    description="""Create a marketing strategy for a new AI product.
    
    Writer: Focus on messaging and content strategy
    Researcher: Provide market analysis and competitor insights
    
    Work together to create a comprehensive strategy.""",
    expected_output="Complete marketing strategy with research backing",
    agent=writer  # Lead agent, but can delegate to researcher
)
```

## Hierarchical Collaboration

For complex projects, use a hierarchical process with a manager agent:

```python
from crewai import Agent, Crew, Task, Process

# Manager agent coordinates the team
manager = Agent(
    role="Project Manager",
    goal="Coordinate team efforts and ensure project success",
    backstory="Experienced project manager skilled at delegation and quality control",
    allow_delegation=True,
    verbose=True
)

# Specialist agents
researcher = Agent(
    role="Researcher",
    goal="Provide accurate research and analysis",
    backstory="Expert researcher with deep analytical skills",
    allow_delegation=False,  # Specialists focus on their expertise
    verbose=True
)

writer = Agent(
    role="Writer", 
    goal="Create compelling content",
    backstory="Skilled writer who creates engaging content",
    allow_delegation=False,
    verbose=True
)

# Manager-led task
project_task = Task(
    description="Create a comprehensive market analysis report with recommendations",
    expected_output="Executive summary, detailed analysis, and strategic recommendations",
    agent=manager  # Manager will delegate to specialists
)

# Hierarchical crew
crew = Crew(
    agents=[manager, researcher, writer],
    tasks=[project_task],
    process=Process.hierarchical,  # Manager coordinates everything
    manager_llm="gpt-4o",  # Specify LLM for manager
    verbose=True
)
```

## Best Practices for Collaboration

### 1. **Clear Role Definition**

```python
# ✅ Good: Specific, complementary roles
researcher = Agent(role="Market Research Analyst", ...)
writer = Agent(role="Technical Content Writer", ...)

# ❌ Avoid: Overlapping or vague roles  
agent1 = Agent(role="General Assistant", ...)
agent2 = Agent(role="Helper", ...)
```

### 2. **Strategic Delegation Enabling**

```python
# ✅ Enable delegation for coordinators and generalists
lead_agent = Agent(
    role="Content Lead",
    allow_delegation=True,  # Can delegate to specialists
    ...
)

# ✅ Disable for focused specialists (optional)
specialist_agent = Agent(
    role="Data Analyst", 
    allow_delegation=False,  # Focuses on core expertise
    ...
)
```

### 3. **Context Sharing**

```python
# ✅ Use context parameter for task dependencies
writing_task = Task(
    description="Write article based on research",
    agent=writer,
    context=[research_task],  # Shares research results
    ...
)
```

### 4. **Clear Task Descriptions**

```python
# ✅ Specific, actionable descriptions
Task(
    description="""Research competitors in the AI chatbot space.
    Focus on: pricing models, key features, target markets.
    Provide data in a structured format.""",
    ...
)

# ❌ Vague descriptions that don't guide collaboration
Task(description="Do some research about chatbots", ...)
```

## Troubleshooting Collaboration

### Issue: Agents Not Collaborating

**Symptoms:** Agents work in isolation, no delegation occurs

```python
# ✅ Solution: Ensure delegation is enabled
agent = Agent(
    role="...",
    allow_delegation=True,  # This is required!
    ...
)
```

### Issue: Too Much Back-and-Forth

**Symptoms:** Agents ask excessive questions, slow progress

```python
# ✅ Solution: Provide better context and specific roles
Task(
    description="""Write a technical blog post about machine learning.
    
    Context: Target audience is software developers with basic ML knowledge.
    Length: 1200 words
    Include: code examples, practical applications, best practices
    
    If you need specific technical details, delegate research to the researcher.""",
    ...
)
```

### Issue: Delegation Loops

**Symptoms:** Agents delegate back and forth indefinitely

```python
# ✅ Solution: Clear hierarchy and responsibilities
manager = Agent(role="Manager", allow_delegation=True)
specialist1 = Agent(role="Specialist A", allow_delegation=False)  # No re-delegation
specialist2 = Agent(role="Specialist B", allow_delegation=False)
```

## Advanced Collaboration Features

### Custom Collaboration Rules

```python
# Set specific collaboration guidelines in agent backstory
agent = Agent(
    role="Senior Developer",
    backstory="""You lead development projects and coordinate with team members.
    
    Collaboration guidelines:
    - Delegate research tasks to the Research Analyst
    - Ask the Designer for UI/UX guidance  
    - Consult the QA Engineer for testing strategies
    - Only escalate blocking issues to the Project Manager""",
    allow_delegation=True
)
```

### Monitoring Collaboration

```python
def track_collaboration(output):
    """Track collaboration patterns"""
    if "Delegate work to coworker" in output.raw:
        print("🤝 Delegation occurred")
    if "Ask question to coworker" in output.raw:
        print("❓ Question asked")

crew = Crew(
    agents=[...],
    tasks=[...],
    step_callback=track_collaboration,  # Monitor collaboration
    verbose=True
)
```

## Memory and Learning

Enable agents to remember past collaborations:

```python
agent = Agent(
    role="Content Lead",
    memory=True,  # Remembers past interactions
    allow_delegation=True,
    verbose=True
)
```

With memory enabled, agents learn from previous collaborations and improve their delegation decisions over time.

## Next Steps

* **Try the examples**: Start with the basic collaboration example
* **Experiment with roles**: Test different agent role combinations
* **Monitor interactions**: Use `verbose=True` to see collaboration in action
* **Optimize task descriptions**: Clear tasks lead to better collaboration
* **Scale up**: Try hierarchical processes for complex projects

Collaboration transforms individual AI agents into powerful teams that can tackle complex, multi-faceted challenges together.














# Reasoning

> Learn how to enable and use agent reasoning to improve task execution.

## Overview

Agent reasoning is a feature that allows agents to reflect on a task and create a plan before execution. This helps agents approach tasks more methodically and ensures they're ready to perform the assigned work.

## Usage

To enable reasoning for an agent, simply set `reasoning=True` when creating the agent:

```python
from crewai import Agent

agent = Agent(
    role="Data Analyst",
    goal="Analyze complex datasets and provide insights",
    backstory="You are an experienced data analyst with expertise in finding patterns in complex data.",
    reasoning=True,  # Enable reasoning
    max_reasoning_attempts=3  # Optional: Set a maximum number of reasoning attempts
)
```

## How It Works

When reasoning is enabled, before executing a task, the agent will:

1. Reflect on the task and create a detailed plan
2. Evaluate whether it's ready to execute the task
3. Refine the plan as necessary until it's ready or max\_reasoning\_attempts is reached
4. Inject the reasoning plan into the task description before execution

This process helps the agent break down complex tasks into manageable steps and identify potential challenges before starting.

## Configuration Options

<ParamField body="reasoning" type="bool" default="False">
  Enable or disable reasoning
</ParamField>

<ParamField body="max_reasoning_attempts" type="int" default="None">
  Maximum number of attempts to refine the plan before proceeding with execution. If None (default), the agent will continue refining until it's ready.
</ParamField>

## Example

Here's a complete example:

```python
from crewai import Agent, Task, Crew

# Create an agent with reasoning enabled
analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="You are an expert data analyst.",
    reasoning=True,
    max_reasoning_attempts=3  # Optional: Set a limit on reasoning attempts
)

# Create a task
analysis_task = Task(
    description="Analyze the provided sales data and identify key trends.",
    expected_output="A report highlighting the top 3 sales trends.",
    agent=analyst
)

# Create a crew and run the task
crew = Crew(agents=[analyst], tasks=[analysis_task])
result = crew.kickoff()

print(result)
```

## Error Handling

The reasoning process is designed to be robust, with error handling built in. If an error occurs during reasoning, the agent will proceed with executing the task without the reasoning plan. This ensures that tasks can still be executed even if the reasoning process fails.

Here's how to handle potential errors in your code:

```python
from crewai import Agent, Task
import logging

# Set up logging to capture any reasoning errors
logging.basicConfig(level=logging.INFO)

# Create an agent with reasoning enabled
agent = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    reasoning=True,
    max_reasoning_attempts=3
)

# Create a task
task = Task(
    description="Analyze the provided sales data and identify key trends.",
    expected_output="A report highlighting the top 3 sales trends.",
    agent=agent
)

# Execute the task
# If an error occurs during reasoning, it will be logged and execution will continue
result = agent.execute_task(task)
```

## Example Reasoning Output

Here's an example of what a reasoning plan might look like for a data analysis task:

```
Task: Analyze the provided sales data and identify key trends.

Reasoning Plan:
I'll analyze the sales data to identify the top 3 trends.

1. Understanding of the task:
   I need to analyze sales data to identify key trends that would be valuable for business decision-making.

2. Key steps I'll take:
   - First, I'll examine the data structure to understand what fields are available
   - Then I'll perform exploratory data analysis to identify patterns
   - Next, I'll analyze sales by time periods to identify temporal trends
   - I'll also analyze sales by product categories and customer segments
   - Finally, I'll identify the top 3 most significant trends

3. Approach to challenges:
   - If the data has missing values, I'll decide whether to fill or filter them
   - If the data has outliers, I'll investigate whether they're valid data points or errors
   - If trends aren't immediately obvious, I'll apply statistical methods to uncover patterns

4. Use of available tools:
   - I'll use data analysis tools to explore and visualize the data
   - I'll use statistical tools to identify significant patterns
   - I'll use knowledge retrieval to access relevant information about sales analysis

5. Expected outcome:
   A concise report highlighting the top 3 sales trends with supporting evidence from the data.

READY: I am ready to execute the task.
```

This reasoning plan helps the agent organize its approach to the task, consider potential challenges, and ensure it delivers the expected output.



# Planning

> Learn how to add planning to your CrewAI Crew and improve their performance.

## Overview

The planning feature in CrewAI allows you to add planning capability to your crew. When enabled, before each Crew iteration,
all Crew information is sent to an AgentPlanner that will plan the tasks step by step, and this plan will be added to each task description.

### Using the Planning Feature

Getting started with the planning feature is very easy, the only step required is to add `planning=True` to your Crew:

<CodeGroup>
  ```python Code
  from crewai import Crew, Agent, Task, Process

  # Assemble your crew with planning capabilities
  my_crew = Crew(
      agents=self.agents,
      tasks=self.tasks,
      process=Process.sequential,
      planning=True,
  )
  ```
</CodeGroup>

From this point on, your crew will have planning enabled, and the tasks will be planned before each iteration.

<Warning>
  When planning is enabled, crewAI will use `gpt-4o-mini` as the default LLM for planning, which requires a valid OpenAI API key. Since your agents might be using different LLMs, this could cause confusion if you don't have an OpenAI API key configured or if you're experiencing unexpected behavior related to LLM API calls.
</Warning>

#### Planning LLM

Now you can define the LLM that will be used to plan the tasks.

When running the base case example, you will see something like the output below, which represents the output of the `AgentPlanner`
responsible for creating the step-by-step logic to add to the Agents' tasks.

<CodeGroup>
  ```python Code
  from crewai import Crew, Agent, Task, Process

  # Assemble your crew with planning capabilities and custom LLM
  my_crew = Crew(
      agents=self.agents,
      tasks=self.tasks,
      process=Process.sequential,
      planning=True,
      planning_llm="gpt-4o"
  )

  # Run the crew
  my_crew.kickoff()
  ```

  ````markdown Result
  [2024-07-15 16:49:11][INFO]: Planning the crew execution
  **Step-by-Step Plan for Task Execution**

  **Task Number 1: Conduct a thorough research about AI LLMs**

  **Agent:** AI LLMs Senior Data Researcher

  **Agent Goal:** Uncover cutting-edge developments in AI LLMs

  **Task Expected Output:** A list with 10 bullet points of the most relevant information about AI LLMs

  **Task Tools:** None specified

  **Agent Tools:** None specified

  **Step-by-Step Plan:**

  1. **Define Research Scope:**

     - Determine the specific areas of AI LLMs to focus on, such as advancements in architecture, use cases, ethical considerations, and performance metrics.

  2. **Identify Reliable Sources:**

     - List reputable sources for AI research, including academic journals, industry reports, conferences (e.g., NeurIPS, ACL), AI research labs (e.g., OpenAI, Google AI), and online databases (e.g., IEEE Xplore, arXiv).

  3. **Collect Data:**

     - Search for the latest papers, articles, and reports published in 2024 and early 2025.
     - Use keywords like "Large Language Models 2025", "AI LLM advancements", "AI ethics 2025", etc.

  4. **Analyze Findings:**

     - Read and summarize the key points from each source.
     - Highlight new techniques, models, and applications introduced in the past year.

  5. **Organize Information:**

     - Categorize the information into relevant topics (e.g., new architectures, ethical implications, real-world applications).
     - Ensure each bullet point is concise but informative.

  6. **Create the List:**

     - Compile the 10 most relevant pieces of information into a bullet point list.
     - Review the list to ensure clarity and relevance.

  **Expected Output:**

  A list with 10 bullet points of the most relevant information about AI LLMs.

  ---

  **Task Number 2: Review the context you got and expand each topic into a full section for a report**

  **Agent:** AI LLMs Reporting Analyst

  **Agent Goal:** Create detailed reports based on AI LLMs data analysis and research findings

  **Task Expected Output:** A fully fledged report with the main topics, each with a full section of information. Formatted as markdown without '```'

  **Task Tools:** None specified

  **Agent Tools:** None specified

  **Step-by-Step Plan:**

  1. **Review the Bullet Points:**
     - Carefully read through the list of 10 bullet points provided by the AI LLMs Senior Data Researcher.

  2. **Outline the Report:**
     - Create an outline with each bullet point as a main section heading.
     - Plan sub-sections under each main heading to cover different aspects of the topic.

  3. **Research Further Details:**
     - For each bullet point, conduct additional research if necessary to gather more detailed information.
     - Look for case studies, examples, and statistical data to support each section.

  4. **Write Detailed Sections:**
     - Expand each bullet point into a comprehensive section.
     - Ensure each section includes an introduction, detailed explanation, examples, and a conclusion.
     - Use markdown formatting for headings, subheadings, lists, and emphasis.

  5. **Review and Edit:**
     - Proofread the report for clarity, coherence, and correctness.
     - Make sure the report flows logically from one section to the next.
     - Format the report according to markdown standards.

  6. **Finalize the Report:**
     - Ensure the report is complete with all sections expanded and detailed.
     - Double-check formatting and make any necessary adjustments.

  **Expected Output:**
  A fully fledged report with the main topics, each with a full section of information. Formatted as markdown without '```'.
  ````
</CodeGroup>


# Using Annotations in crew.py

> Learn how to use annotations to properly structure agents, tasks, and components in CrewAI

This guide explains how to use annotations to properly reference **agents**, **tasks**, and other components in the `crew.py` file.

## Introduction

Annotations in the CrewAI framework are used to decorate classes and methods, providing metadata and functionality to various components of your crew. These annotations help in organizing and structuring your code, making it more readable and maintainable.

## Available Annotations

The CrewAI framework provides the following annotations:

* `@CrewBase`: Used to decorate the main crew class.
* `@agent`: Decorates methods that define and return Agent objects.
* `@task`: Decorates methods that define and return Task objects.
* `@crew`: Decorates the method that creates and returns the Crew object.
* `@llm`: Decorates methods that initialize and return Language Model objects.
* `@tool`: Decorates methods that initialize and return Tool objects.
* `@callback`: Used for defining callback methods.
* `@output_json`: Used for methods that output JSON data.
* `@output_pydantic`: Used for methods that output Pydantic models.
* `@cache_handler`: Used for defining cache handling methods.

## Usage Examples

Let's go through examples of how to use these annotations:

### 1. Crew Base Class

```python
@CrewBase
class LinkedinProfileCrew():
    """LinkedinProfile crew"""
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
```

The `@CrewBase` annotation is used to decorate the main crew class. This class typically contains configurations and methods for creating agents, tasks, and the crew itself.

### 2. Tool Definition

```python
@tool
def myLinkedInProfileTool(self):
    return LinkedInProfileTool()
```

The `@tool` annotation is used to decorate methods that return tool objects. These tools can be used by agents to perform specific tasks.

### 3. LLM Definition

```python
@llm
def groq_llm(self):
    api_key = os.getenv('api_key')
    return ChatGroq(api_key=api_key, temperature=0, model_name="mixtral-8x7b-32768")
```

The `@llm` annotation is used to decorate methods that initialize and return Language Model objects. These LLMs are used by agents for natural language processing tasks.

### 4. Agent Definition

```python
@agent
def researcher(self) -> Agent:
    return Agent(
        config=self.agents_config['researcher']
    )
```

The `@agent` annotation is used to decorate methods that define and return Agent objects.

### 5. Task Definition

```python
@task
def research_task(self) -> Task:
    return Task(
        config=self.tasks_config['research_linkedin_task'],
        agent=self.researcher()
    )
```

The `@task` annotation is used to decorate methods that define and return Task objects. These methods specify the task configuration and the agent responsible for the task.

### 6. Crew Creation

```python
@crew
def crew(self) -> Crew:
    """Creates the LinkedinProfile crew"""
    return Crew(
        agents=self.agents,
        tasks=self.tasks,
        process=Process.sequential,
        verbose=True
    )
```

The `@crew` annotation is used to decorate the method that creates and returns the `Crew` object. This method assembles all the components (agents and tasks) into a functional crew.

## YAML Configuration

The agent configurations are typically stored in a YAML file. Here's an example of how the `agents.yaml` file might look for the researcher agent:

```yaml
researcher:
    role: >
        LinkedIn Profile Senior Data Researcher
    goal: >
        Uncover detailed LinkedIn profiles based on provided name {name} and domain {domain}
        Generate a Dall-E image based on domain {domain}
    backstory: >
        You're a seasoned researcher with a knack for uncovering the most relevant LinkedIn profiles.
        Known for your ability to navigate LinkedIn efficiently, you excel at gathering and presenting
        professional information clearly and concisely.
    allow_delegation: False
    verbose: True
    llm: groq_llm
    tools:
        - myLinkedInProfileTool
        - mySerperDevTool
        - myDallETool
```

This YAML configuration corresponds to the researcher agent defined in the `LinkedinProfileCrew` class. The configuration specifies the agent's role, goal, backstory, and other properties such as the LLM and tools it uses.

Note how the `llm` and `tools` in the YAML file correspond to the methods decorated with `@llm` and `@tool` in the Python class.

## Best Practices

* **Consistent Naming**: Use clear and consistent naming conventions for your methods. For example, agent methods could be named after their roles (e.g., researcher, reporting\_analyst).
* **Environment Variables**: Use environment variables for sensitive information like API keys.
* **Flexibility**: Design your crew to be flexible by allowing easy addition or removal of agents and tasks.
* **YAML-Code Correspondence**: Ensure that the names and structures in your YAML files correspond correctly to the decorated methods in your Python code.

By following these guidelines and properly using annotations, you can create well-structured and maintainable crews using the CrewAI framework.


# Connect to any LLM

> Comprehensive guide on integrating CrewAI with various Large Language Models (LLMs) using LiteLLM, including supported providers and configuration options.

## Connect CrewAI to LLMs

CrewAI uses LiteLLM to connect to a wide variety of Language Models (LLMs). This integration provides extensive versatility, allowing you to use models from numerous providers with a simple, unified interface.

<Note>
  By default, CrewAI uses the `gpt-4o-mini` model. This is determined by the `OPENAI_MODEL_NAME` environment variable, which defaults to "gpt-4o-mini" if not set.
  You can easily configure your agents to use a different model or provider as described in this guide.
</Note>

## Supported Providers

LiteLLM supports a wide range of providers, including but not limited to:

* OpenAI
* Anthropic
* Google (Vertex AI, Gemini)
* Azure OpenAI
* AWS (Bedrock, SageMaker)
* Cohere
* VoyageAI
* Hugging Face
* Ollama
* Mistral AI
* Replicate
* Together AI
* AI21
* Cloudflare Workers AI
* DeepInfra
* Groq
* SambaNova
* Nebius AI Studio
* [NVIDIA NIMs](https://docs.api.nvidia.com/nim/reference/models-1)
* And many more!

For a complete and up-to-date list of supported providers, please refer to the [LiteLLM Providers documentation](https://docs.litellm.ai/docs/providers).

## Changing the LLM

To use a different LLM with your CrewAI agents, you have several options:

<Tabs>
  <Tab title="Using a String Identifier">
    Pass the model name as a string when initializing the agent:

    <CodeGroup>
      ```python Code
      from crewai import Agent

      # Using OpenAI's GPT-4
      openai_agent = Agent(
          role='OpenAI Expert',
          goal='Provide insights using GPT-4',
          backstory="An AI assistant powered by OpenAI's latest model.",
          llm='gpt-4'
      )

      # Using Anthropic's Claude
      claude_agent = Agent(
          role='Anthropic Expert',
          goal='Analyze data using Claude',
          backstory="An AI assistant leveraging Anthropic's language model.",
          llm='claude-2'
      )
      ```
    </CodeGroup>
  </Tab>

  <Tab title="Using the LLM Class">
    For more detailed configuration, use the LLM class:

    <CodeGroup>
      ```python Code
      from crewai import Agent, LLM

      llm = LLM(
          model="gpt-4",
          temperature=0.7,
          base_url="https://api.openai.com/v1",
          api_key="your-api-key-here"
      )

      agent = Agent(
          role='Customized LLM Expert',
          goal='Provide tailored responses',
          backstory="An AI assistant with custom LLM settings.",
          llm=llm
      )
      ```
    </CodeGroup>
  </Tab>
</Tabs>

## Configuration Options

When configuring an LLM for your agent, you have access to a wide range of parameters:

| Parameter              |        Type        | Description                                                      |
| :--------------------- | :----------------: | :--------------------------------------------------------------- |
| **model**              |        `str`       | The name of the model to use (e.g., "gpt-4", "claude-2")         |
| **temperature**        |       `float`      | Controls randomness in output (0.0 to 1.0)                       |
| **max\_tokens**        |        `int`       | Maximum number of tokens to generate                             |
| **top\_p**             |       `float`      | Controls diversity of output (0.0 to 1.0)                        |
| **frequency\_penalty** |       `float`      | Penalizes new tokens based on their frequency in the text so far |
| **presence\_penalty**  |       `float`      | Penalizes new tokens based on their presence in the text so far  |
| **stop**               | `str`, `List[str]` | Sequence(s) to stop generation                                   |
| **base\_url**          |        `str`       | The base URL for the API endpoint                                |
| **api\_key**           |        `str`       | Your API key for authentication                                  |

For a complete list of parameters and their descriptions, refer to the LLM class documentation.

## Connecting to OpenAI-Compatible LLMs

You can connect to OpenAI-compatible LLMs using either environment variables or by setting specific attributes on the LLM class:

<Tabs>
  <Tab title="Using Environment Variables">
    <CodeGroup>
      ```python Generic
      import os

      os.environ["OPENAI_API_KEY"] = "your-api-key"
      os.environ["OPENAI_API_BASE"] = "https://api.your-provider.com/v1"
      os.environ["OPENAI_MODEL_NAME"] = "your-model-name"
      ```

      ```python Google
      import os

      # Example using Gemini's OpenAI-compatible API.
      os.environ["OPENAI_API_KEY"] = "your-gemini-key"  # Should start with AIza...
      os.environ["OPENAI_API_BASE"] = "https://generativelanguage.googleapis.com/v1beta/openai/"
      os.environ["OPENAI_MODEL_NAME"] = "openai/gemini-2.0-flash"  # Add your Gemini model here, under openai/
      ```
    </CodeGroup>
  </Tab>

  <Tab title="Using LLM Class Attributes">
    <CodeGroup>
      ```python Generic
      llm = LLM(
          model="custom-model-name",
          api_key="your-api-key",
          base_url="https://api.your-provider.com/v1"
      )
      agent = Agent(llm=llm, ...)
      ```

      ```python Google
      # Example using Gemini's OpenAI-compatible API
      llm = LLM(
          model="openai/gemini-2.0-flash",
          base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
          api_key="your-gemini-key",  # Should start with AIza...
      )
      agent = Agent(llm=llm, ...)
      ```
    </CodeGroup>
  </Tab>
</Tabs>

## Using Local Models with Ollama

For local models like those provided by Ollama:

<Steps>
  <Step title="Download and install Ollama">
    [Click here to download and install Ollama](https://ollama.com/download)
  </Step>

  <Step title="Pull the desired model">
    For example, run `ollama pull llama3.2` to download the model.
  </Step>

  <Step title="Configure your agent">
    <CodeGroup>
      ```python Code
          agent = Agent(
              role='Local AI Expert',
              goal='Process information using a local model',
              backstory="An AI assistant running on local hardware.",
              llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
          )
      ```
    </CodeGroup>
  </Step>
</Steps>

## Changing the Base API URL

You can change the base API URL for any LLM provider by setting the `base_url` parameter:

```python Code
llm = LLM(
    model="custom-model-name",
    base_url="https://api.your-provider.com/v1",
    api_key="your-api-key"
)
agent = Agent(llm=llm, ...)
```

This is particularly useful when working with OpenAI-compatible APIs or when you need to specify a different endpoint for your chosen provider.

## Conclusion

By leveraging LiteLLM, CrewAI offers seamless integration with a vast array of LLMs. This flexibility allows you to choose the most suitable model for your specific needs, whether you prioritize performance, cost-efficiency, or local deployment. Remember to consult the [LiteLLM documentation](https://docs.litellm.ai/docs/) for the most up-to-date information on supported models and configuration options.


# Using Multimodal Agents

> Learn how to enable and use multimodal capabilities in your agents for processing images and other non-text content within the CrewAI framework.

## Using Multimodal Agents

CrewAI supports multimodal agents that can process both text and non-text content like images. This guide will show you how to enable and use multimodal capabilities in your agents.

### Enabling Multimodal Capabilities

To create a multimodal agent, simply set the `multimodal` parameter to `True` when initializing your agent:

```python
from crewai import Agent

agent = Agent(
    role="Image Analyst",
    goal="Analyze and extract insights from images",
    backstory="An expert in visual content interpretation with years of experience in image analysis",
    multimodal=True  # This enables multimodal capabilities
)
```

When you set `multimodal=True`, the agent is automatically configured with the necessary tools for handling non-text content, including the `AddImageTool`.

### Working with Images

The multimodal agent comes pre-configured with the `AddImageTool`, which allows it to process images. You don't need to manually add this tool - it's automatically included when you enable multimodal capabilities.

Here's a complete example showing how to use a multimodal agent to analyze an image:

```python
from crewai import Agent, Task, Crew

# Create a multimodal agent
image_analyst = Agent(
    role="Product Analyst",
    goal="Analyze product images and provide detailed descriptions",
    backstory="Expert in visual product analysis with deep knowledge of design and features",
    multimodal=True
)

# Create a task for image analysis
task = Task(
    description="Analyze the product image at https://example.com/product.jpg and provide a detailed description",
    expected_output="A detailed description of the product image",
    agent=image_analyst
)

# Create and run the crew
crew = Crew(
    agents=[image_analyst],
    tasks=[task]
)

result = crew.kickoff()
```

### Advanced Usage with Context

You can provide additional context or specific questions about the image when creating tasks for multimodal agents. The task description can include specific aspects you want the agent to focus on:

```python
from crewai import Agent, Task, Crew

# Create a multimodal agent for detailed analysis
expert_analyst = Agent(
    role="Visual Quality Inspector",
    goal="Perform detailed quality analysis of product images",
    backstory="Senior quality control expert with expertise in visual inspection",
    multimodal=True  # AddImageTool is automatically included
)

# Create a task with specific analysis requirements
inspection_task = Task(
    description="""
    Analyze the product image at https://example.com/product.jpg with focus on:
    1. Quality of materials
    2. Manufacturing defects
    3. Compliance with standards
    Provide a detailed report highlighting any issues found.
    """,
    expected_output="A detailed report highlighting any issues found",
    agent=expert_analyst
)

# Create and run the crew
crew = Crew(
    agents=[expert_analyst],
    tasks=[inspection_task]
)

result = crew.kickoff()
```

### Tool Details

When working with multimodal agents, the `AddImageTool` is automatically configured with the following schema:

```python
class AddImageToolSchema:
    image_url: str  # Required: The URL or path of the image to process
    action: Optional[str] = None  # Optional: Additional context or specific questions about the image
```

The multimodal agent will automatically handle the image processing through its built-in tools, allowing it to:

* Access images via URLs or local file paths
* Process image content with optional context or specific questions
* Provide analysis and insights based on the visual information and task requirements

### Best Practices

When working with multimodal agents, keep these best practices in mind:

1. **Image Access**
   * Ensure your images are accessible via URLs that the agent can reach
   * For local images, consider hosting them temporarily or using absolute file paths
   * Verify that image URLs are valid and accessible before running tasks

2. **Task Description**
   * Be specific about what aspects of the image you want the agent to analyze
   * Include clear questions or requirements in the task description
   * Consider using the optional `action` parameter for focused analysis

3. **Resource Management**
   * Image processing may require more computational resources than text-only tasks
   * Some language models may require base64 encoding for image data
   * Consider batch processing for multiple images to optimize performance

4. **Environment Setup**
   * Verify that your environment has the necessary dependencies for image processing
   * Ensure your language model supports multimodal capabilities
   * Test with small images first to validate your setup

5. **Error Handling**
   * Implement proper error handling for image loading failures
   * Have fallback strategies for when image processing fails
   * Monitor and log image processing operations for debugging


# Hierarchical Process

> A comprehensive guide to understanding and applying the hierarchical process within your CrewAI projects, updated to reflect the latest coding practices and functionalities.

## Introduction

The hierarchical process in CrewAI introduces a structured approach to task management, simulating traditional organizational hierarchies for efficient task delegation and execution.
This systematic workflow enhances project outcomes by ensuring tasks are handled with optimal efficiency and accuracy.

<Tip>
  The hierarchical process is designed to leverage advanced models like GPT-4, optimizing token usage while handling complex tasks with greater efficiency.
</Tip>

## Hierarchical Process Overview

By default, tasks in CrewAI are managed through a sequential process. However, adopting a hierarchical approach allows for a clear hierarchy in task management,
where a 'manager' agent coordinates the workflow, delegates tasks, and validates outcomes for streamlined and effective execution. This manager agent can now be either
automatically created by CrewAI or explicitly set by the user.

### Key Features

* **Task Delegation**: A manager agent allocates tasks among crew members based on their roles and capabilities.
* **Result Validation**: The manager evaluates outcomes to ensure they meet the required standards.
* **Efficient Workflow**: Emulates corporate structures, providing an organized approach to task management.
* **System Prompt Handling**: Optionally specify whether the system should use predefined prompts.
* **Stop Words Control**: Optionally specify whether stop words should be used, supporting various models including the o1 models.
* **Context Window Respect**: Prioritize important context by enabling respect of the context window, which is now the default behavior.
* **Delegation Control**: Delegation is now disabled by default to give users explicit control.
* **Max Requests Per Minute**: Configurable option to set the maximum number of requests per minute.
* **Max Iterations**: Limit the maximum number of iterations for obtaining a final answer.

## Implementing the Hierarchical Process

To utilize the hierarchical process, it's essential to explicitly set the process attribute to `Process.hierarchical`, as the default behavior is `Process.sequential`.
Define a crew with a designated manager and establish a clear chain of command.

<Tip>
  Assign tools at the agent level to facilitate task delegation and execution by the designated agents under the manager's guidance.
  Tools can also be specified at the task level for precise control over tool availability during task execution.
</Tip>

<Tip>
  Configuring the `manager_llm` parameter is crucial for the hierarchical process.
  The system requires a manager LLM to be set up for proper function, ensuring tailored decision-making.
</Tip>

```python Code
from crewai import Crew, Process, Agent

# Agents are defined with attributes for backstory, cache, and verbose mode
researcher = Agent(
    role='Researcher',
    goal='Conduct in-depth analysis',
    backstory='Experienced data analyst with a knack for uncovering hidden trends.',
)
writer = Agent(
    role='Writer',
    goal='Create engaging content',
    backstory='Creative writer passionate about storytelling in technical domains.',
)

# Establishing the crew with a hierarchical process and additional configurations
project_crew = Crew(
    tasks=[...],  # Tasks to be delegated and executed under the manager's supervision
    agents=[researcher, writer],
    manager_llm="gpt-4o",  # Specify which LLM the manager should use
    process=Process.hierarchical,  
    planning=True, 
)
```

### Using a Custom Manager Agent

Alternatively, you can create a custom manager agent with specific attributes tailored to your project's management needs. This gives you more control over the manager's behavior and capabilities.

```python
# Define a custom manager agent
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success.",
    allow_delegation=True,
)

# Use the custom manager in your crew
project_crew = Crew(
    tasks=[...],
    agents=[researcher, writer],
    manager_agent=manager,  # Use your custom manager agent
    process=Process.hierarchical,
    planning=True,
)
```

<Tip>
  For more details on creating and customizing a manager agent, check out the [Custom Manager Agent documentation](https://docs.crewai.com/how-to/custom-manager-agent#custom-manager-agent).
</Tip>

### Workflow in Action

1. **Task Assignment**: The manager assigns tasks strategically, considering each agent's capabilities and available tools.
2. **Execution and Review**: Agents complete their tasks with the option for asynchronous execution and callback functions for streamlined workflows.
3. **Sequential Task Progression**: Despite being a hierarchical process, tasks follow a logical order for smooth progression, facilitated by the manager's oversight.

## Conclusion

Adopting the hierarchical process in CrewAI, with the correct configurations and understanding of the system's capabilities, facilitates an organized and efficient approach to project management.
Utilize the advanced features and customizations to tailor the workflow to your specific needs, ensuring optimal task execution and project success.


# Human Input on Execution

> Integrating CrewAI with human input during execution in complex decision-making processes and leveraging the full capabilities of the agent's attributes and tools.

## Human input in agent execution

Human input is critical in several agent execution scenarios, allowing agents to request additional information or clarification when necessary.
This feature is especially useful in complex decision-making processes or when agents require more details to complete a task effectively.

## Using human input with CrewAI

To integrate human input into agent execution, set the `human_input` flag in the task definition. When enabled, the agent prompts the user for input before delivering its final answer.
This input can provide extra context, clarify ambiguities, or validate the agent's output.

### Example:

```shell
pip install crewai
```

```python Code
import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

os.environ["SERPER_API_KEY"] = "Your Key"  # serper.dev API key
os.environ["OPENAI_API_KEY"] = "Your Key"

# Loading Tools
search_tool = SerperDevTool()

# Define your agents with roles, goals, tools, and additional attributes
researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover cutting-edge developments in AI and data science',
    backstory=(
        "You are a Senior Research Analyst at a leading tech think tank. "
        "Your expertise lies in identifying emerging trends and technologies in AI and data science. "
        "You have a knack for dissecting complex data and presenting actionable insights."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)
writer = Agent(
    role='Tech Content Strategist',
    goal='Craft compelling content on tech advancements',
    backstory=(
        "You are a renowned Tech Content Strategist, known for your insightful and engaging articles on technology and innovation. "
        "With a deep understanding of the tech industry, you transform complex concepts into compelling narratives."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    cache=False,  # Disable cache for this agent
)

# Create tasks for your agents
task1 = Task(
    description=(
        "Conduct a comprehensive analysis of the latest advancements in AI in 2025. "
        "Identify key trends, breakthrough technologies, and potential industry impacts. "
        "Compile your findings in a detailed report. "
        "Make sure to check with a human if the draft is good before finalizing your answer."
    ),
    expected_output='A comprehensive full report on the latest AI advancements in 2025, leave nothing out',
    agent=researcher,
    human_input=True
)

task2 = Task(
    description=(
        "Using the insights from the researcher\'s report, develop an engaging blog post that highlights the most significant AI advancements. "
        "Your post should be informative yet accessible, catering to a tech-savvy audience. "
        "Aim for a narrative that captures the essence of these breakthroughs and their implications for the future."
    ),
    expected_output='A compelling 3 paragraphs blog post formatted as markdown about the latest AI advancements in 2025',
    agent=writer,
    human_input=True
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=True,
    memory=True,
    planning=True  # Enable planning feature for the crew
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
```


# Flows

> Learn how to create and manage AI workflows using CrewAI Flows.

## Overview

CrewAI Flows is a powerful feature designed to streamline the creation and management of AI workflows. Flows allow developers to combine and coordinate coding tasks and Crews efficiently, providing a robust framework for building sophisticated AI automations.

Flows allow you to create structured, event-driven workflows. They provide a seamless way to connect multiple tasks, manage state, and control the flow of execution in your AI applications. With Flows, you can easily design and implement multi-step processes that leverage the full potential of CrewAI's capabilities.

1. **Simplified Workflow Creation**: Easily chain together multiple Crews and tasks to create complex AI workflows.

2. **State Management**: Flows make it super easy to manage and share state between different tasks in your workflow.

3. **Event-Driven Architecture**: Built on an event-driven model, allowing for dynamic and responsive workflows.

4. **Flexible Control Flow**: Implement conditional logic, loops, and branching within your workflows.

## Getting Started

Let's create a simple Flow where you will use OpenAI to generate a random city in one task and then use that city to generate a fun fact in another task.

```python Code

from crewai.flow.flow import Flow, listen, start
from dotenv import load_dotenv
from litellm import completion


class ExampleFlow(Flow):
    model = "gpt-4o-mini"

    @start()
    def generate_city(self):
        print("Starting flow")
        # Each flow state automatically gets a unique ID
        print(f"Flow State ID: {self.state['id']}")

        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": "Return the name of a random city in the world.",
                },
            ],
        )

        random_city = response["choices"][0]["message"]["content"]
        # Store the city in our state
        self.state["city"] = random_city
        print(f"Random City: {random_city}")

        return random_city

    @listen(generate_city)
    def generate_fun_fact(self, random_city):
        response = completion(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": f"Tell me a fun fact about {random_city}",
                },
            ],
        )

        fun_fact = response["choices"][0]["message"]["content"]
        # Store the fun fact in our state
        self.state["fun_fact"] = fun_fact
        return fun_fact



flow = ExampleFlow()
flow.plot()
result = flow.kickoff()

print(f"Generated fun fact: {result}")
```

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-1.png)
In the above example, we have created a simple Flow that generates a random city using OpenAI and then generates a fun fact about that city. The Flow consists of two tasks: `generate_city` and `generate_fun_fact`. The `generate_city` task is the starting point of the Flow, and the `generate_fun_fact` task listens for the output of the `generate_city` task.

Each Flow instance automatically receives a unique identifier (UUID) in its state, which helps track and manage flow executions. The state can also store additional data (like the generated city and fun fact) that persists throughout the flow's execution.

When you run the Flow, it will:

1. Generate a unique ID for the flow state
2. Generate a random city and store it in the state
3. Generate a fun fact about that city and store it in the state
4. Print the results to the console

The state's unique ID and stored data can be useful for tracking flow executions and maintaining context between tasks.

**Note:** Ensure you have set up your `.env` file to store your `OPENAI_API_KEY`. This key is necessary for authenticating requests to the OpenAI API.

### @start()

The `@start()` decorator is used to mark a method as the starting point of a Flow. When a Flow is started, all the methods decorated with `@start()` are executed in parallel. You can have multiple start methods in a Flow, and they will all be executed when the Flow is started.

### @listen()

The `@listen()` decorator is used to mark a method as a listener for the output of another task in the Flow. The method decorated with `@listen()` will be executed when the specified task emits an output. The method can access the output of the task it is listening to as an argument.

#### Usage

The `@listen()` decorator can be used in several ways:

1. **Listening to a Method by Name**: You can pass the name of the method you want to listen to as a string. When that method completes, the listener method will be triggered.

   ```python Code
   @listen("generate_city")
   def generate_fun_fact(self, random_city):
       # Implementation
   ```

2. **Listening to a Method Directly**: You can pass the method itself. When that method completes, the listener method will be triggered.
   ```python Code
   @listen(generate_city)
   def generate_fun_fact(self, random_city):
       # Implementation
   ```

### Flow Output

Accessing and handling the output of a Flow is essential for integrating your AI workflows into larger applications or systems. CrewAI Flows provide straightforward mechanisms to retrieve the final output, access intermediate results, and manage the overall state of your Flow.

#### Retrieving the Final Output

When you run a Flow, the final output is determined by the last method that completes. The `kickoff()` method returns the output of this final method.

Here's how you can access the final output:

<CodeGroup>
  ```python Code
  from crewai.flow.flow import Flow, listen, start

  class OutputExampleFlow(Flow):
      @start()
      def first_method(self):
          return "Output from first_method"

      @listen(first_method)
      def second_method(self, first_output):
          return f"Second method received: {first_output}"


  flow = OutputExampleFlow()
  flow.plot("my_flow_plot")
  final_output = flow.kickoff()

  print("---- Final Output ----")
  print(final_output)
  ```

  ```text Output
  ---- Final Output ----
  Second method received: Output from first_method
  ```
</CodeGroup>

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-2.png)

In this example, the `second_method` is the last method to complete, so its output will be the final output of the Flow.
The `kickoff()` method will return the final output, which is then printed to the console. The `plot()` method will generate the HTML file, which will help you understand the flow.

#### Accessing and Updating State

In addition to retrieving the final output, you can also access and update the state within your Flow. The state can be used to store and share data between different methods in the Flow. After the Flow has run, you can access the state to retrieve any information that was added or updated during the execution.

Here's an example of how to update and access the state:

<CodeGroup>
  ```python Code
  from crewai.flow.flow import Flow, listen, start
  from pydantic import BaseModel

  class ExampleState(BaseModel):
      counter: int = 0
      message: str = ""

  class StateExampleFlow(Flow[ExampleState]):

      @start()
      def first_method(self):
          self.state.message = "Hello from first_method"
          self.state.counter += 1

      @listen(first_method)
      def second_method(self):
          self.state.message += " - updated by second_method"
          self.state.counter += 1
          return self.state.message

  flow = StateExampleFlow()
  flow.plot("my_flow_plot")
  final_output = flow.kickoff()
  print(f"Final Output: {final_output}")
  print("Final State:")
  print(flow.state)
  ```

  ```text Output
  Final Output: Hello from first_method - updated by second_method
  Final State:
  counter=2 message='Hello from first_method - updated by second_method'
  ```
</CodeGroup>

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-2.png)

In this example, the state is updated by both `first_method` and `second_method`.
After the Flow has run, you can access the final state to see the updates made by these methods.

By ensuring that the final method's output is returned and providing access to the state, CrewAI Flows make it easy to integrate the results of your AI workflows into larger applications or systems,
while also maintaining and accessing the state throughout the Flow's execution.

## Flow State Management

Managing state effectively is crucial for building reliable and maintainable AI workflows. CrewAI Flows provides robust mechanisms for both unstructured and structured state management,
allowing developers to choose the approach that best fits their application's needs.

### Unstructured State Management

In unstructured state management, all state is stored in the `state` attribute of the `Flow` class.
This approach offers flexibility, enabling developers to add or modify state attributes on the fly without defining a strict schema.
Even with unstructured states, CrewAI Flows automatically generates and maintains a unique identifier (UUID) for each state instance.

```python Code
from crewai.flow.flow import Flow, listen, start

class UnstructuredExampleFlow(Flow):

    @start()
    def first_method(self):
        # The state automatically includes an 'id' field
        print(f"State ID: {self.state['id']}")
        self.state['counter'] = 0
        self.state['message'] = "Hello from structured flow"

    @listen(first_method)
    def second_method(self):
        self.state['counter'] += 1
        self.state['message'] += " - updated"

    @listen(second_method)
    def third_method(self):
        self.state['counter'] += 1
        self.state['message'] += " - updated again"

        print(f"State after third_method: {self.state}")


flow = UnstructuredExampleFlow()
flow.plot("my_flow_plot")
flow.kickoff()
```

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-3.png)

**Note:** The `id` field is automatically generated and preserved throughout the flow's execution. You don't need to manage or set it manually, and it will be maintained even when updating the state with new data.

**Key Points:**

* **Flexibility:** You can dynamically add attributes to `self.state` without predefined constraints.
* **Simplicity:** Ideal for straightforward workflows where state structure is minimal or varies significantly.

### Structured State Management

Structured state management leverages predefined schemas to ensure consistency and type safety across the workflow.
By using models like Pydantic's `BaseModel`, developers can define the exact shape of the state, enabling better validation and auto-completion in development environments.

Each state in CrewAI Flows automatically receives a unique identifier (UUID) to help track and manage state instances. This ID is automatically generated and managed by the Flow system.

```python Code
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel


class ExampleState(BaseModel):
    # Note: 'id' field is automatically added to all states
    counter: int = 0
    message: str = ""


class StructuredExampleFlow(Flow[ExampleState]):

    @start()
    def first_method(self):
        # Access the auto-generated ID if needed
        print(f"State ID: {self.state.id}")
        self.state.message = "Hello from structured flow"

    @listen(first_method)
    def second_method(self):
        self.state.counter += 1
        self.state.message += " - updated"

    @listen(second_method)
    def third_method(self):
        self.state.counter += 1
        self.state.message += " - updated again"

        print(f"State after third_method: {self.state}")


flow = StructuredExampleFlow()
flow.kickoff()
```

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-3.png)

**Key Points:**

* **Defined Schema:** `ExampleState` clearly outlines the state structure, enhancing code readability and maintainability.
* **Type Safety:** Leveraging Pydantic ensures that state attributes adhere to the specified types, reducing runtime errors.
* **Auto-Completion:** IDEs can provide better auto-completion and error checking based on the defined state model.

### Choosing Between Unstructured and Structured State Management

* **Use Unstructured State Management when:**

  * The workflow's state is simple or highly dynamic.
  * Flexibility is prioritized over strict state definitions.
  * Rapid prototyping is required without the overhead of defining schemas.

* **Use Structured State Management when:**
  * The workflow requires a well-defined and consistent state structure.
  * Type safety and validation are important for your application's reliability.
  * You want to leverage IDE features like auto-completion and type checking for better developer experience.

By providing both unstructured and structured state management options, CrewAI Flows empowers developers to build AI workflows that are both flexible and robust, catering to a wide range of application requirements.

## Flow Persistence

The @persist decorator enables automatic state persistence in CrewAI Flows, allowing you to maintain flow state across restarts or different workflow executions. This decorator can be applied at either the class level or method level, providing flexibility in how you manage state persistence.

### Class-Level Persistence

When applied at the class level, the @persist decorator automatically persists all flow method states:

```python
@persist  # Using SQLiteFlowPersistence by default
class MyFlow(Flow[MyState]):
    @start()
    def initialize_flow(self):
        # This method will automatically have its state persisted
        self.state.counter = 1
        print("Initialized flow. State ID:", self.state.id)

    @listen(initialize_flow)
    def next_step(self):
        # The state (including self.state.id) is automatically reloaded
        self.state.counter += 1
        print("Flow state is persisted. Counter:", self.state.counter)
```

### Method-Level Persistence

For more granular control, you can apply @persist to specific methods:

```python
class AnotherFlow(Flow[dict]):
    @persist  # Persists only this method's state
    @start()
    def begin(self):
        if "runs" not in self.state:
            self.state["runs"] = 0
        self.state["runs"] += 1
        print("Method-level persisted runs:", self.state["runs"])
```

### How It Works

1. **Unique State Identification**
   * Each flow state automatically receives a unique UUID
   * The ID is preserved across state updates and method calls
   * Supports both structured (Pydantic BaseModel) and unstructured (dictionary) states

2. **Default SQLite Backend**
   * SQLiteFlowPersistence is the default storage backend
   * States are automatically saved to a local SQLite database
   * Robust error handling ensures clear messages if database operations fail

3. **Error Handling**
   * Comprehensive error messages for database operations
   * Automatic state validation during save and load
   * Clear feedback when persistence operations encounter issues

### Important Considerations

* **State Types**: Both structured (Pydantic BaseModel) and unstructured (dictionary) states are supported
* **Automatic ID**: The `id` field is automatically added if not present
* **State Recovery**: Failed or restarted flows can automatically reload their previous state
* **Custom Implementation**: You can provide your own FlowPersistence implementation for specialized storage needs

### Technical Advantages

1. **Precise Control Through Low-Level Access**
   * Direct access to persistence operations for advanced use cases
   * Fine-grained control via method-level persistence decorators
   * Built-in state inspection and debugging capabilities
   * Full visibility into state changes and persistence operations

2. **Enhanced Reliability**
   * Automatic state recovery after system failures or restarts
   * Transaction-based state updates for data integrity
   * Comprehensive error handling with clear error messages
   * Robust validation during state save and load operations

3. **Extensible Architecture**
   * Customizable persistence backend through FlowPersistence interface
   * Support for specialized storage solutions beyond SQLite
   * Compatible with both structured (Pydantic) and unstructured (dict) states
   * Seamless integration with existing CrewAI flow patterns

The persistence system's architecture emphasizes technical precision and customization options, allowing developers to maintain full control over state management while benefiting from built-in reliability features.

## Flow Control

### Conditional Logic: `or`

The `or_` function in Flows allows you to listen to multiple methods and trigger the listener method when any of the specified methods emit an output.

<CodeGroup>
  ```python Code
  from crewai.flow.flow import Flow, listen, or_, start

  class OrExampleFlow(Flow):

      @start()
      def start_method(self):
          return "Hello from the start method"

      @listen(start_method)
      def second_method(self):
          return "Hello from the second method"

      @listen(or_(start_method, second_method))
      def logger(self, result):
          print(f"Logger: {result}")



  flow = OrExampleFlow()
  flow.plot("my_flow_plot")
  flow.kickoff()
  ```

  ```text Output
  Logger: Hello from the start method
  Logger: Hello from the second method
  ```
</CodeGroup>

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-4.png)

When you run this Flow, the `logger` method will be triggered by the output of either the `start_method` or the `second_method`.
The `or_` function is used to listen to multiple methods and trigger the listener method when any of the specified methods emit an output.

### Conditional Logic: `and`

The `and_` function in Flows allows you to listen to multiple methods and trigger the listener method only when all the specified methods emit an output.

<CodeGroup>
  ```python Code
  from crewai.flow.flow import Flow, and_, listen, start

  class AndExampleFlow(Flow):

      @start()
      def start_method(self):
          self.state["greeting"] = "Hello from the start method"

      @listen(start_method)
      def second_method(self):
          self.state["joke"] = "What do computers eat? Microchips."

      @listen(and_(start_method, second_method))
      def logger(self):
          print("---- Logger ----")
          print(self.state)

  flow = AndExampleFlow()
  flow.plot()
  flow.kickoff()
  ```

  ```text Output
  ---- Logger ----
  {'greeting': 'Hello from the start method', 'joke': 'What do computers eat? Microchips.'}
  ```
</CodeGroup>

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-5.png)

When you run this Flow, the `logger` method will be triggered only when both the `start_method` and the `second_method` emit an output.
The `and_` function is used to listen to multiple methods and trigger the listener method only when all the specified methods emit an output.

### Router

The `@router()` decorator in Flows allows you to define conditional routing logic based on the output of a method.
You can specify different routes based on the output of the method, allowing you to control the flow of execution dynamically.

<CodeGroup>
  ```python Code
  import random
  from crewai.flow.flow import Flow, listen, router, start
  from pydantic import BaseModel

  class ExampleState(BaseModel):
      success_flag: bool = False

  class RouterFlow(Flow[ExampleState]):

      @start()
      def start_method(self):
          print("Starting the structured flow")
          random_boolean = random.choice([True, False])
          self.state.success_flag = random_boolean

      @router(start_method)
      def second_method(self):
          if self.state.success_flag:
              return "success"
          else:
              return "failed"

      @listen("success")
      def third_method(self):
          print("Third method running")

      @listen("failed")
      def fourth_method(self):
          print("Fourth method running")


  flow = RouterFlow()
  flow.plot("my_flow_plot")
  flow.kickoff()
  ```

  ```text Output
  Starting the structured flow
  Third method running
  Fourth method running
  ```
</CodeGroup>

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-6.png)

In the above example, the `start_method` generates a random boolean value and sets it in the state.
The `second_method` uses the `@router()` decorator to define conditional routing logic based on the value of the boolean.
If the boolean is `True`, the method returns `"success"`, and if it is `False`, the method returns `"failed"`.
The `third_method` and `fourth_method` listen to the output of the `second_method` and execute based on the returned value.

When you run this Flow, the output will change based on the random boolean value generated by the `start_method`.

## Adding Agents to Flows

Agents can be seamlessly integrated into your flows, providing a lightweight alternative to full Crews when you need simpler, focused task execution. Here's an example of how to use an Agent within a flow to perform market research:

```python
import asyncio
from typing import Any, Dict, List

from crewai_tools import SerperDevTool
from pydantic import BaseModel, Field

from crewai.agent import Agent
from crewai.flow.flow import Flow, listen, start


# Define a structured output format
class MarketAnalysis(BaseModel):
    key_trends: List[str] = Field(description="List of identified market trends")
    market_size: str = Field(description="Estimated market size")
    competitors: List[str] = Field(description="Major competitors in the space")


# Define flow state
class MarketResearchState(BaseModel):
    product: str = ""
    analysis: MarketAnalysis | None = None


# Create a flow class
class MarketResearchFlow(Flow[MarketResearchState]):
    @start()
    def initialize_research(self) -> Dict[str, Any]:
        print(f"Starting market research for {self.state.product}")
        return {"product": self.state.product}

    @listen(initialize_research)
    async def analyze_market(self) -> Dict[str, Any]:
        # Create an Agent for market research
        analyst = Agent(
            role="Market Research Analyst",
            goal=f"Analyze the market for {self.state.product}",
            backstory="You are an experienced market analyst with expertise in "
            "identifying market trends and opportunities.",
            tools=[SerperDevTool()],
            verbose=True,
        )

        # Define the research query
        query = f"""
        Research the market for {self.state.product}. Include:
        1. Key market trends
        2. Market size
        3. Major competitors

        Format your response according to the specified structure.
        """

        # Execute the analysis with structured output format
        result = await analyst.kickoff_async(query, response_format=MarketAnalysis)
        if result.pydantic:
            print("result", result.pydantic)
        else:
            print("result", result)

        # Return the analysis to update the state
        return {"analysis": result.pydantic}

    @listen(analyze_market)
    def present_results(self, analysis) -> None:
        print("\nMarket Analysis Results")
        print("=====================")

        if isinstance(analysis, dict):
            # If we got a dict with 'analysis' key, extract the actual analysis object
            market_analysis = analysis.get("analysis")
        else:
            market_analysis = analysis

        if market_analysis and isinstance(market_analysis, MarketAnalysis):
            print("\nKey Market Trends:")
            for trend in market_analysis.key_trends:
                print(f"- {trend}")

            print(f"\nMarket Size: {market_analysis.market_size}")

            print("\nMajor Competitors:")
            for competitor in market_analysis.competitors:
                print(f"- {competitor}")
        else:
            print("No structured analysis data available.")
            print("Raw analysis:", analysis)


# Usage example
async def run_flow():
    flow = MarketResearchFlow()
    flow.plot("MarketResearchFlowPlot")
    result = await flow.kickoff_async(inputs={"product": "AI-powered chatbots"})
    return result


# Run the flow
if __name__ == "__main__":
    asyncio.run(run_flow())
```

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-7.png)

This example demonstrates several key features of using Agents in flows:

1. **Structured Output**: Using Pydantic models to define the expected output format (`MarketAnalysis`) ensures type safety and structured data throughout the flow.

2. **State Management**: The flow state (`MarketResearchState`) maintains context between steps and stores both inputs and outputs.

3. **Tool Integration**: Agents can use tools (like `WebsiteSearchTool`) to enhance their capabilities.

## Adding Crews to Flows

Creating a flow with multiple crews in CrewAI is straightforward.

You can generate a new CrewAI project that includes all the scaffolding needed to create a flow with multiple crews by running the following command:

```bash
crewai create flow name_of_flow
```

This command will generate a new CrewAI project with the necessary folder structure. The generated project includes a prebuilt crew called `poem_crew` that is already working. You can use this crew as a template by copying, pasting, and editing it to create other crews.

### Folder Structure

After running the `crewai create flow name_of_flow` command, you will see a folder structure similar to the following:

| Directory/File         | Description                                                         |
| :--------------------- | :------------------------------------------------------------------ |
| `name_of_flow/`        | Root directory for the flow.                                        |
| ├── `crews/`           | Contains directories for specific crews.                            |
| │ └── `poem_crew/`     | Directory for the "poem\_crew" with its configurations and scripts. |
| │ ├── `config/`        | Configuration files directory for the "poem\_crew".                 |
| │ │ ├── `agents.yaml`  | YAML file defining the agents for "poem\_crew".                     |
| │ │ └── `tasks.yaml`   | YAML file defining the tasks for "poem\_crew".                      |
| │ ├── `poem_crew.py`   | Script for "poem\_crew" functionality.                              |
| ├── `tools/`           | Directory for additional tools used in the flow.                    |
| │ └── `custom_tool.py` | Custom tool implementation.                                         |
| ├── `main.py`          | Main script for running the flow.                                   |
| ├── `README.md`        | Project description and instructions.                               |
| ├── `pyproject.toml`   | Configuration file for project dependencies and settings.           |
| └── `.gitignore`       | Specifies files and directories to ignore in version control.       |

### Building Your Crews

In the `crews` folder, you can define multiple crews. Each crew will have its own folder containing configuration files and the crew definition file. For example, the `poem_crew` folder contains:

* `config/agents.yaml`: Defines the agents for the crew.
* `config/tasks.yaml`: Defines the tasks for the crew.
* `poem_crew.py`: Contains the crew definition, including agents, tasks, and the crew itself.

You can copy, paste, and edit the `poem_crew` to create other crews.

### Connecting Crews in `main.py`

The `main.py` file is where you create your flow and connect the crews together. You can define your flow by using the `Flow` class and the decorators `@start` and `@listen` to specify the flow of execution.

Here's an example of how you can connect the `poem_crew` in the `main.py` file:

```python Code
#!/usr/bin/env python
from random import randint

from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from .crews.poem_crew.poem_crew import PoemCrew

class PoemState(BaseModel):
    sentence_count: int = 1
    poem: str = ""

class PoemFlow(Flow[PoemState]):

    @start()
    def generate_sentence_count(self):
        print("Generating sentence count")
        self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        result = PoemCrew().crew().kickoff(inputs={"sentence_count": self.state.sentence_count})

        print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)

def kickoff():
    poem_flow = PoemFlow()
    poem_flow.kickoff()


def plot():
    poem_flow = PoemFlow()
    poem_flow.plot("PoemFlowPlot")

if __name__ == "__main__":
    kickoff()
    plot()
```

In this example, the `PoemFlow` class defines a flow that generates a sentence count, uses the `PoemCrew` to generate a poem, and then saves the poem to a file. The flow is kicked off by calling the `kickoff()` method. The PoemFlowPlot will be generated by `plot()` method.

![Flow Visual image](https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/crewai-flow-8.png)

### Running the Flow

(Optional) Before running the flow, you can install the dependencies by running:

```bash
crewai install
```

Once all of the dependencies are installed, you need to activate the virtual environment by running:

```bash
source .venv/bin/activate
```

After activating the virtual environment, you can run the flow by executing one of the following commands:

```bash
crewai flow kickoff
```

or

```bash
uv run kickoff
```

The flow will execute, and you should see the output in the console.

## Plot Flows

Visualizing your AI workflows can provide valuable insights into the structure and execution paths of your flows. CrewAI offers a powerful visualization tool that allows you to generate interactive plots of your flows, making it easier to understand and optimize your AI workflows.

### What are Plots?

Plots in CrewAI are graphical representations of your AI workflows. They display the various tasks, their connections, and the flow of data between them. This visualization helps in understanding the sequence of operations, identifying bottlenecks, and ensuring that the workflow logic aligns with your expectations.

### How to Generate a Plot

CrewAI provides two convenient methods to generate plots of your flows:

#### Option 1: Using the `plot()` Method

If you are working directly with a flow instance, you can generate a plot by calling the `plot()` method on your flow object. This method will create an HTML file containing the interactive plot of your flow.

```python Code
# Assuming you have a flow instance
flow.plot("my_flow_plot")
```

This will generate a file named `my_flow_plot.html` in your current directory. You can open this file in a web browser to view the interactive plot.

#### Option 2: Using the Command Line

If you are working within a structured CrewAI project, you can generate a plot using the command line. This is particularly useful for larger projects where you want to visualize the entire flow setup.

```bash
crewai flow plot
```

This command will generate an HTML file with the plot of your flow, similar to the `plot()` method. The file will be saved in your project directory, and you can open it in a web browser to explore the flow.

### Understanding the Plot

The generated plot will display nodes representing the tasks in your flow, with directed edges indicating the flow of execution. The plot is interactive, allowing you to zoom in and out, and hover over nodes to see additional details.

By visualizing your flows, you can gain a clearer understanding of the workflow's structure, making it easier to debug, optimize, and communicate your AI processes to others.

### Conclusion

Plotting your flows is a powerful feature of CrewAI that enhances your ability to design and manage complex AI workflows. Whether you choose to use the `plot()` method or the command line, generating plots will provide you with a visual representation of your workflows, aiding in both development and presentation.

## Next Steps

If you're interested in exploring additional examples of flows, we have a variety of recommendations in our examples repository. Here are four specific flow examples, each showcasing unique use cases to help you match your current problem type to a specific example:

1. **Email Auto Responder Flow**: This example demonstrates an infinite loop where a background job continually runs to automate email responses. It's a great use case for tasks that need to be performed repeatedly without manual intervention. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/email_auto_responder_flow)

2. **Lead Score Flow**: This flow showcases adding human-in-the-loop feedback and handling different conditional branches using the router. It's an excellent example of how to incorporate dynamic decision-making and human oversight into your workflows. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/lead-score-flow)

3. **Write a Book Flow**: This example excels at chaining multiple crews together, where the output of one crew is used by another. Specifically, one crew outlines an entire book, and another crew generates chapters based on the outline. Eventually, everything is connected to produce a complete book. This flow is perfect for complex, multi-step processes that require coordination between different tasks. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/write_a_book_with_flows)

4. **Meeting Assistant Flow**: This flow demonstrates how to broadcast one event to trigger multiple follow-up actions. For instance, after a meeting is completed, the flow can update a Trello board, send a Slack message, and save the results. It's a great example of handling multiple outcomes from a single event, making it ideal for comprehensive task management and notification systems. [View Example](https://github.com/crewAIInc/crewAI-examples/tree/main/meeting_assistant_flow)

By exploring these examples, you can gain insights into how to leverage CrewAI Flows for various use cases, from automating repetitive tasks to managing complex, multi-step processes with dynamic decision-making and human feedback.

Also, check out our YouTube video on how to use flows in CrewAI below!

<iframe width="560" height="315" src="https://www.youtube.com/embed/MTb5my6VOT8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen />

## Running Flows

There are two ways to run a flow:

### Using the Flow API

You can run a flow programmatically by creating an instance of your flow class and calling the `kickoff()` method:

```python
flow = ExampleFlow()
result = flow.kickoff()
```

### Using the CLI

Starting from version 0.103.0, you can run flows using the `crewai run` command:

```shell
crewai run
```

This command automatically detects if your project is a flow (based on the `type = "flow"` setting in your pyproject.toml) and runs it accordingly. This is the recommended way to run flows from the command line.

For backward compatibility, you can also use:

```shell
crewai flow kickoff
```

However, the `crewai run` command is now the preferred method as it works for both crews and flows.



# Mastering Flow State Management

> A comprehensive guide to managing, persisting, and leveraging state in CrewAI Flows for building robust AI applications.

## Understanding the Power of State in Flows

State management is the backbone of any sophisticated AI workflow. In CrewAI Flows, the state system allows you to maintain context, share data between steps, and build complex application logic. Mastering state management is essential for creating reliable, maintainable, and powerful AI applications.

This guide will walk you through everything you need to know about managing state in CrewAI Flows, from basic concepts to advanced techniques, with practical code examples along the way.

### Why State Management Matters

Effective state management enables you to:

1. **Maintain context across execution steps** - Pass information seamlessly between different stages of your workflow
2. **Build complex conditional logic** - Make decisions based on accumulated data
3. **Create persistent applications** - Save and restore workflow progress
4. **Handle errors gracefully** - Implement recovery patterns for more robust applications
5. **Scale your applications** - Support complex workflows with proper data organization
6. **Enable conversational applications** - Store and access conversation history for context-aware AI interactions

Let's explore how to leverage these capabilities effectively.

## State Management Fundamentals

### The Flow State Lifecycle

In CrewAI Flows, the state follows a predictable lifecycle:

1. **Initialization** - When a flow is created, its state is initialized (either as an empty dictionary or a Pydantic model instance)
2. **Modification** - Flow methods access and modify the state as they execute
3. **Transmission** - State is passed automatically between flow methods
4. **Persistence** (optional) - State can be saved to storage and later retrieved
5. **Completion** - The final state reflects the cumulative changes from all executed methods

Understanding this lifecycle is crucial for designing effective flows.

### Two Approaches to State Management

CrewAI offers two ways to manage state in your flows:

1. **Unstructured State** - Using dictionary-like objects for flexibility
2. **Structured State** - Using Pydantic models for type safety and validation

Let's examine each approach in detail.

## Unstructured State Management

Unstructured state uses a dictionary-like approach, offering flexibility and simplicity for straightforward applications.

### How It Works

With unstructured state:

* You access state via `self.state` which behaves like a dictionary
* You can freely add, modify, or remove keys at any point
* All state is automatically available to all flow methods

### Basic Example

Here's a simple example of unstructured state management:

```python
from crewai.flow.flow import Flow, listen, start

class UnstructuredStateFlow(Flow):
    @start()
    def initialize_data(self):
        print("Initializing flow data")
        # Add key-value pairs to state
        self.state["user_name"] = "Alex"
        self.state["preferences"] = {
            "theme": "dark",
            "language": "English"
        }
        self.state["items"] = []

        # The flow state automatically gets a unique ID
        print(f"Flow ID: {self.state['id']}")

        return "Initialized"

    @listen(initialize_data)
    def process_data(self, previous_result):
        print(f"Previous step returned: {previous_result}")

        # Access and modify state
        user = self.state["user_name"]
        print(f"Processing data for {user}")

        # Add items to a list in state
        self.state["items"].append("item1")
        self.state["items"].append("item2")

        # Add a new key-value pair
        self.state["processed"] = True

        return "Processed"

    @listen(process_data)
    def generate_summary(self, previous_result):
        # Access multiple state values
        user = self.state["user_name"]
        theme = self.state["preferences"]["theme"]
        items = self.state["items"]
        processed = self.state.get("processed", False)

        summary = f"User {user} has {len(items)} items with {theme} theme. "
        summary += "Data is processed." if processed else "Data is not processed."

        return summary

# Run the flow
flow = UnstructuredStateFlow()
result = flow.kickoff()
print(f"Final result: {result}")
print(f"Final state: {flow.state}")
```

### When to Use Unstructured State

Unstructured state is ideal for:

* Quick prototyping and simple flows
* Dynamically evolving state needs
* Cases where the structure may not be known in advance
* Flows with simple state requirements

While flexible, unstructured state lacks type checking and schema validation, which can lead to errors in complex applications.

## Structured State Management

Structured state uses Pydantic models to define a schema for your flow's state, providing type safety, validation, and better developer experience.

### How It Works

With structured state:

* You define a Pydantic model that represents your state structure
* You pass this model type to your Flow class as a type parameter
* You access state via `self.state`, which behaves like a Pydantic model instance
* All fields are validated according to their defined types
* You get IDE autocompletion and type checking support

### Basic Example

Here's how to implement structured state management:

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

# Define your state model
class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "English"

class AppState(BaseModel):
    user_name: str = ""
    preferences: UserPreferences = UserPreferences()
    items: List[str] = []
    processed: bool = False
    completion_percentage: float = 0.0

# Create a flow with typed state
class StructuredStateFlow(Flow[AppState]):
    @start()
    def initialize_data(self):
        print("Initializing flow data")
        # Set state values (type-checked)
        self.state.user_name = "Taylor"
        self.state.preferences.theme = "dark"

        # The ID field is automatically available
        print(f"Flow ID: {self.state.id}")

        return "Initialized"

    @listen(initialize_data)
    def process_data(self, previous_result):
        print(f"Processing data for {self.state.user_name}")

        # Modify state (with type checking)
        self.state.items.append("item1")
        self.state.items.append("item2")
        self.state.processed = True
        self.state.completion_percentage = 50.0

        return "Processed"

    @listen(process_data)
    def generate_summary(self, previous_result):
        # Access state (with autocompletion)
        summary = f"User {self.state.user_name} has {len(self.state.items)} items "
        summary += f"with {self.state.preferences.theme} theme. "
        summary += "Data is processed." if self.state.processed else "Data is not processed."
        summary += f" Completion: {self.state.completion_percentage}%"

        return summary

# Run the flow
flow = StructuredStateFlow()
result = flow.kickoff()
print(f"Final result: {result}")
print(f"Final state: {flow.state}")
```

### Benefits of Structured State

Using structured state provides several advantages:

1. **Type Safety** - Catch type errors at development time
2. **Self-Documentation** - The state model clearly documents what data is available
3. **Validation** - Automatic validation of data types and constraints
4. **IDE Support** - Get autocomplete and inline documentation
5. **Default Values** - Easily define fallbacks for missing data

### When to Use Structured State

Structured state is recommended for:

* Complex flows with well-defined data schemas
* Team projects where multiple developers work on the same code
* Applications where data validation is important
* Flows that need to enforce specific data types and constraints

## The Automatic State ID

Both unstructured and structured states automatically receive a unique identifier (UUID) to help track and manage state instances.

### How It Works

* For unstructured state, the ID is accessible as `self.state["id"]`
* For structured state, the ID is accessible as `self.state.id`
* This ID is generated automatically when the flow is created
* The ID remains the same throughout the flow's lifecycle
* The ID can be used for tracking, logging, and retrieving persisted states

This UUID is particularly valuable when implementing persistence or tracking multiple flow executions.

## Dynamic State Updates

Regardless of whether you're using structured or unstructured state, you can update state dynamically throughout your flow's execution.

### Passing Data Between Steps

Flow methods can return values that are then passed as arguments to listening methods:

```python
from crewai.flow.flow import Flow, listen, start

class DataPassingFlow(Flow):
    @start()
    def generate_data(self):
        # This return value will be passed to listening methods
        return "Generated data"

    @listen(generate_data)
    def process_data(self, data_from_previous_step):
        print(f"Received: {data_from_previous_step}")
        # You can modify the data and pass it along
        processed_data = f"{data_from_previous_step} - processed"
        # Also update state
        self.state["last_processed"] = processed_data
        return processed_data

    @listen(process_data)
    def finalize_data(self, processed_data):
        print(f"Received processed data: {processed_data}")
        # Access both the passed data and state
        last_processed = self.state.get("last_processed", "")
        return f"Final: {processed_data} (from state: {last_processed})"
```

This pattern allows you to combine direct data passing with state updates for maximum flexibility.

## Persisting Flow State

One of CrewAI's most powerful features is the ability to persist flow state across executions. This enables workflows that can be paused, resumed, and even recovered after failures.

### The @persist() Decorator

The `@persist()` decorator automates state persistence, saving your flow's state at key points in execution.

#### Class-Level Persistence

When applied at the class level, `@persist()` saves state after every method execution:

```python
from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence import persist
from pydantic import BaseModel

class CounterState(BaseModel):
    value: int = 0

@persist()  # Apply to the entire flow class
class PersistentCounterFlow(Flow[CounterState]):
    @start()
    def increment(self):
        self.state.value += 1
        print(f"Incremented to {self.state.value}")
        return self.state.value

    @listen(increment)
    def double(self, value):
        self.state.value = value * 2
        print(f"Doubled to {self.state.value}")
        return self.state.value

# First run
flow1 = PersistentCounterFlow()
result1 = flow1.kickoff()
print(f"First run result: {result1}")

# Second run - state is automatically loaded
flow2 = PersistentCounterFlow()
result2 = flow2.kickoff()
print(f"Second run result: {result2}")  # Will be higher due to persisted state
```

#### Method-Level Persistence

For more granular control, you can apply `@persist()` to specific methods:

```python
from crewai.flow.flow import Flow, listen, start
from crewai.flow.persistence import persist

class SelectivePersistFlow(Flow):
    @start()
    def first_step(self):
        self.state["count"] = 1
        return "First step"

    @persist()  # Only persist after this method
    @listen(first_step)
    def important_step(self, prev_result):
        self.state["count"] += 1
        self.state["important_data"] = "This will be persisted"
        return "Important step completed"

    @listen(important_step)
    def final_step(self, prev_result):
        self.state["count"] += 1
        return f"Complete with count {self.state['count']}"
```

## Advanced State Patterns

### State-Based Conditional Logic

You can use state to implement complex conditional logic in your flows:

```python
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel

class PaymentState(BaseModel):
    amount: float = 0.0
    is_approved: bool = False
    retry_count: int = 0

class PaymentFlow(Flow[PaymentState]):
    @start()
    def process_payment(self):
        # Simulate payment processing
        self.state.amount = 100.0
        self.state.is_approved = self.state.amount < 1000
        return "Payment processed"

    @router(process_payment)
    def check_approval(self, previous_result):
        if self.state.is_approved:
            return "approved"
        elif self.state.retry_count < 3:
            return "retry"
        else:
            return "rejected"

    @listen("approved")
    def handle_approval(self):
        return f"Payment of ${self.state.amount} approved!"

    @listen("retry")
    def handle_retry(self):
        self.state.retry_count += 1
        print(f"Retrying payment (attempt {self.state.retry_count})...")
        # Could implement retry logic here
        return "Retry initiated"

    @listen("rejected")
    def handle_rejection(self):
        return f"Payment of ${self.state.amount} rejected after {self.state.retry_count} retries."
```

### Handling Complex State Transformations

For complex state transformations, you can create dedicated methods:

```python
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel
from typing import List, Dict

class UserData(BaseModel):
    name: str
    active: bool = True
    login_count: int = 0

class ComplexState(BaseModel):
    users: Dict[str, UserData] = {}
    active_user_count: int = 0

class TransformationFlow(Flow[ComplexState]):
    @start()
    def initialize(self):
        # Add some users
        self.add_user("alice", "Alice")
        self.add_user("bob", "Bob")
        self.add_user("charlie", "Charlie")
        return "Initialized"

    @listen(initialize)
    def process_users(self, _):
        # Increment login counts
        for user_id in self.state.users:
            self.increment_login(user_id)

        # Deactivate one user
        self.deactivate_user("bob")

        # Update active count
        self.update_active_count()

        return f"Processed {len(self.state.users)} users"

    # Helper methods for state transformations
    def add_user(self, user_id: str, name: str):
        self.state.users[user_id] = UserData(name=name)
        self.update_active_count()

    def increment_login(self, user_id: str):
        if user_id in self.state.users:
            self.state.users[user_id].login_count += 1

    def deactivate_user(self, user_id: str):
        if user_id in self.state.users:
            self.state.users[user_id].active = False
            self.update_active_count()

    def update_active_count(self):
        self.state.active_user_count = sum(
            1 for user in self.state.users.values() if user.active
        )
```

This pattern of creating helper methods keeps your flow methods clean while enabling complex state manipulations.

## State Management with Crews

One of the most powerful patterns in CrewAI is combining flow state management with crew execution.

### Passing State to Crews

You can use flow state to parameterize crews:

```python
from crewai.flow.flow import Flow, listen, start
from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel

class ResearchState(BaseModel):
    topic: str = ""
    depth: str = "medium"
    results: str = ""

class ResearchFlow(Flow[ResearchState]):
    @start()
    def get_parameters(self):
        # In a real app, this might come from user input
        self.state.topic = "Artificial Intelligence Ethics"
        self.state.depth = "deep"
        return "Parameters set"

    @listen(get_parameters)
    def execute_research(self, _):
        # Create agents
        researcher = Agent(
            role="Research Specialist",
            goal=f"Research {self.state.topic} in {self.state.depth} detail",
            backstory="You are an expert researcher with a talent for finding accurate information."
        )

        writer = Agent(
            role="Content Writer",
            goal="Transform research into clear, engaging content",
            backstory="You excel at communicating complex ideas clearly and concisely."
        )

        # Create tasks
        research_task = Task(
            description=f"Research {self.state.topic} with {self.state.depth} analysis",
            expected_output="Comprehensive research notes in markdown format",
            agent=researcher
        )

        writing_task = Task(
            description=f"Create a summary on {self.state.topic} based on the research",
            expected_output="Well-written article in markdown format",
            agent=writer,
            context=[research_task]
        )

        # Create and run crew
        research_crew = Crew(
            agents=[researcher, writer],
            tasks=[research_task, writing_task],
            process=Process.sequential,
            verbose=True
        )

        # Run crew and store result in state
        result = research_crew.kickoff()
        self.state.results = result.raw

        return "Research completed"

    @listen(execute_research)
    def summarize_results(self, _):
        # Access the stored results
        result_length = len(self.state.results)
        return f"Research on {self.state.topic} completed with {result_length} characters of results."
```

### Handling Crew Outputs in State

When a crew completes, you can process its output and store it in your flow state:

```python
@listen(execute_crew)
def process_crew_results(self, _):
    # Parse the raw results (assuming JSON output)
    import json
    try:
        results_dict = json.loads(self.state.raw_results)
        self.state.processed_results = {
            "title": results_dict.get("title", ""),
            "main_points": results_dict.get("main_points", []),
            "conclusion": results_dict.get("conclusion", "")
        }
        return "Results processed successfully"
    except json.JSONDecodeError:
        self.state.error = "Failed to parse crew results as JSON"
        return "Error processing results"
```

## Best Practices for State Management

### 1. Keep State Focused

Design your state to contain only what's necessary:

```python
# Too broad
class BloatedState(BaseModel):
    user_data: Dict = {}
    system_settings: Dict = {}
    temporary_calculations: List = []
    debug_info: Dict = {}
    # ...many more fields

# Better: Focused state
class FocusedState(BaseModel):
    user_id: str
    preferences: Dict[str, str]
    completion_status: Dict[str, bool]
```

### 2. Use Structured State for Complex Flows

As your flows grow in complexity, structured state becomes increasingly valuable:

```python
# Simple flow can use unstructured state
class SimpleGreetingFlow(Flow):
    @start()
    def greet(self):
        self.state["name"] = "World"
        return f"Hello, {self.state['name']}!"

# Complex flow benefits from structured state
class UserRegistrationState(BaseModel):
    username: str
    email: str
    verification_status: bool = False
    registration_date: datetime = Field(default_factory=datetime.now)
    last_login: Optional[datetime] = None

class RegistrationFlow(Flow[UserRegistrationState]):
    # Methods with strongly-typed state access
```

### 3. Document State Transitions

For complex flows, document how state changes throughout the execution:

```python
@start()
def initialize_order(self):
    """
    Initialize order state with empty values.

    State before: {}
    State after: {order_id: str, items: [], status: 'new'}
    """
    self.state.order_id = str(uuid.uuid4())
    self.state.items = []
    self.state.status = "new"
    return "Order initialized"
```

### 4. Handle State Errors Gracefully

Implement error handling for state access:

```python
@listen(previous_step)
def process_data(self, _):
    try:
        # Try to access a value that might not exist
        user_preference = self.state.preferences.get("theme", "default")
    except (AttributeError, KeyError):
        # Handle the error gracefully
        self.state.errors = self.state.get("errors", [])
        self.state.errors.append("Failed to access preferences")
        user_preference = "default"

    return f"Used preference: {user_preference}"
```

### 5. Use State for Progress Tracking

Leverage state to track progress in long-running flows:

```python
class ProgressTrackingFlow(Flow):
    @start()
    def initialize(self):
        self.state["total_steps"] = 3
        self.state["current_step"] = 0
        self.state["progress"] = 0.0
        self.update_progress()
        return "Initialized"

    def update_progress(self):
        """Helper method to calculate and update progress"""
        if self.state.get("total_steps", 0) > 0:
            self.state["progress"] = (self.state.get("current_step", 0) /
                                    self.state["total_steps"]) * 100
            print(f"Progress: {self.state['progress']:.1f}%")

    @listen(initialize)
    def step_one(self, _):
        # Do work...
        self.state["current_step"] = 1
        self.update_progress()
        return "Step 1 complete"

    # Additional steps...
```

### 6. Use Immutable Operations When Possible

Especially with structured state, prefer immutable operations for clarity:

```python
# Instead of modifying lists in place:
self.state.items.append(new_item)  # Mutable operation

# Consider creating new state:
from pydantic import BaseModel
from typing import List

class ItemState(BaseModel):
    items: List[str] = []

class ImmutableFlow(Flow[ItemState]):
    @start()
    def add_item(self):
        # Create new list with the added item
        self.state.items = [*self.state.items, "new item"]
        return "Item added"
```

## Debugging Flow State

### Logging State Changes

When developing, add logging to track state changes:

```python
import logging
logging.basicConfig(level=logging.INFO)

class LoggingFlow(Flow):
    def log_state(self, step_name):
        logging.info(f"State after {step_name}: {self.state}")

    @start()
    def initialize(self):
        self.state["counter"] = 0
        self.log_state("initialize")
        return "Initialized"

    @listen(initialize)
    def increment(self, _):
        self.state["counter"] += 1
        self.log_state("increment")
        return f"Incremented to {self.state['counter']}"
```

### State Visualization

You can add methods to visualize your state for debugging:

```python
def visualize_state(self):
    """Create a simple visualization of the current state"""
    import json
    from rich.console import Console
    from rich.panel import Panel

    console = Console()

    if hasattr(self.state, "model_dump"):
        # Pydantic v2
        state_dict = self.state.model_dump()
    elif hasattr(self.state, "dict"):
        # Pydantic v1
        state_dict = self.state.dict()
    else:
        # Unstructured state
        state_dict = dict(self.state)

    # Remove id for cleaner output
    if "id" in state_dict:
        state_dict.pop("id")

    state_json = json.dumps(state_dict, indent=2, default=str)
    console.print(Panel(state_json, title="Current Flow State"))
```

## Conclusion

Mastering state management in CrewAI Flows gives you the power to build sophisticated, robust AI applications that maintain context, make complex decisions, and deliver consistent results.

Whether you choose unstructured or structured state, implementing proper state management practices will help you create flows that are maintainable, extensible, and effective at solving real-world problems.

As you develop more complex flows, remember that good state management is about finding the right balance between flexibility and structure, making your code both powerful and easy to understand.

<Check>
  You've now mastered the concepts and practices of state management in CrewAI Flows! With this knowledge, you can create robust AI workflows that effectively maintain context, share data between steps, and build sophisticated application logic.
</Check>

## Next Steps

* Experiment with both structured and unstructured state in your flows
* Try implementing state persistence for long-running workflows
* Explore [building your first crew](/en/guides/crews/first-crew) to see how crews and flows can work together
* Check out the [Flow reference documentation](/en/concepts/flows) for more advanced features



# Evaluating Use Cases for CrewAI

> Learn how to assess your AI application needs and choose the right approach between Crews and Flows based on complexity and precision requirements.

## Understanding the Decision Framework

When building AI applications with CrewAI, one of the most important decisions you'll make is choosing the right approach for your specific use case. Should you use a Crew? A Flow? A combination of both? This guide will help you evaluate your requirements and make informed architectural decisions.

At the heart of this decision is understanding the relationship between **complexity** and **precision** in your application:

<Frame caption="Complexity vs. Precision Matrix for CrewAI Applications">
  <img src="https://mintlify.s3.us-west-1.amazonaws.com/crewai/images/complexity_precision.png" alt="Complexity vs. Precision Matrix" />
</Frame>

This matrix helps visualize how different approaches align with varying requirements for complexity and precision. Let's explore what each quadrant means and how it guides your architectural choices.

## The Complexity-Precision Matrix Explained

### What is Complexity?

In the context of CrewAI applications, **complexity** refers to:

* The number of distinct steps or operations required
* The diversity of tasks that need to be performed
* The interdependencies between different components
* The need for conditional logic and branching
* The sophistication of the overall workflow

### What is Precision?

**Precision** in this context refers to:

* The accuracy required in the final output
* The need for structured, predictable results
* The importance of reproducibility
* The level of control needed over each step
* The tolerance for variation in outputs

### The Four Quadrants

#### 1. Low Complexity, Low Precision

**Characteristics:**

* Simple, straightforward tasks
* Tolerance for some variation in outputs
* Limited number of steps
* Creative or exploratory applications

**Recommended Approach:** Simple Crews with minimal agents

**Example Use Cases:**

* Basic content generation
* Idea brainstorming
* Simple summarization tasks
* Creative writing assistance

#### 2. Low Complexity, High Precision

**Characteristics:**

* Simple workflows that require exact, structured outputs
* Need for reproducible results
* Limited steps but high accuracy requirements
* Often involves data processing or transformation

**Recommended Approach:** Flows with direct LLM calls or simple Crews with structured outputs

**Example Use Cases:**

* Data extraction and transformation
* Form filling and validation
* Structured content generation (JSON, XML)
* Simple classification tasks

#### 3. High Complexity, Low Precision

**Characteristics:**

* Multi-stage processes with many steps
* Creative or exploratory outputs
* Complex interactions between components
* Tolerance for variation in final results

**Recommended Approach:** Complex Crews with multiple specialized agents

**Example Use Cases:**

* Research and analysis
* Content creation pipelines
* Exploratory data analysis
* Creative problem-solving

#### 4. High Complexity, High Precision

**Characteristics:**

* Complex workflows requiring structured outputs
* Multiple interdependent steps with strict accuracy requirements
* Need for both sophisticated processing and precise results
* Often mission-critical applications

**Recommended Approach:** Flows orchestrating multiple Crews with validation steps

**Example Use Cases:**

* Enterprise decision support systems
* Complex data processing pipelines
* Multi-stage document processing
* Regulated industry applications

## Choosing Between Crews and Flows

### When to Choose Crews

Crews are ideal when:

1. **You need collaborative intelligence** - Multiple agents with different specializations need to work together
2. **The problem requires emergent thinking** - The solution benefits from different perspectives and approaches
3. **The task is primarily creative or analytical** - The work involves research, content creation, or analysis
4. **You value adaptability over strict structure** - The workflow can benefit from agent autonomy
5. **The output format can be somewhat flexible** - Some variation in output structure is acceptable

```python
# Example: Research Crew for market analysis
from crewai import Agent, Crew, Process, Task

# Create specialized agents
researcher = Agent(
    role="Market Research Specialist",
    goal="Find comprehensive market data on emerging technologies",
    backstory="You are an expert at discovering market trends and gathering data."
)

analyst = Agent(
    role="Market Analyst",
    goal="Analyze market data and identify key opportunities",
    backstory="You excel at interpreting market data and spotting valuable insights."
)

# Define their tasks
research_task = Task(
    description="Research the current market landscape for AI-powered healthcare solutions",
    expected_output="Comprehensive market data including key players, market size, and growth trends",
    agent=researcher
)

analysis_task = Task(
    description="Analyze the market data and identify the top 3 investment opportunities",
    expected_output="Analysis report with 3 recommended investment opportunities and rationale",
    agent=analyst,
    context=[research_task]
)

# Create the crew
market_analysis_crew = Crew(
    agents=[researcher, analyst],
    tasks=[research_task, analysis_task],
    process=Process.sequential,
    verbose=True
)

# Run the crew
result = market_analysis_crew.kickoff()
```

### When to Choose Flows

Flows are ideal when:

1. **You need precise control over execution** - The workflow requires exact sequencing and state management
2. **The application has complex state requirements** - You need to maintain and transform state across multiple steps
3. **You need structured, predictable outputs** - The application requires consistent, formatted results
4. **The workflow involves conditional logic** - Different paths need to be taken based on intermediate results
5. **You need to combine AI with procedural code** - The solution requires both AI capabilities and traditional programming

```python
# Example: Customer Support Flow with structured processing
from crewai.flow.flow import Flow, listen, router, start
from pydantic import BaseModel
from typing import List, Dict

# Define structured state
class SupportTicketState(BaseModel):
    ticket_id: str = ""
    customer_name: str = ""
    issue_description: str = ""
    category: str = ""
    priority: str = "medium"
    resolution: str = ""
    satisfaction_score: int = 0

class CustomerSupportFlow(Flow[SupportTicketState]):
    @start()
    def receive_ticket(self):
        # In a real app, this might come from an API
        self.state.ticket_id = "TKT-12345"
        self.state.customer_name = "Alex Johnson"
        self.state.issue_description = "Unable to access premium features after payment"
        return "Ticket received"

    @listen(receive_ticket)
    def categorize_ticket(self, _):
        # Use a direct LLM call for categorization
        from crewai import LLM
        llm = LLM(model="openai/gpt-4o-mini")

        prompt = f"""
        Categorize the following customer support issue into one of these categories:
        - Billing
        - Account Access
        - Technical Issue
        - Feature Request
        - Other

        Issue: {self.state.issue_description}

        Return only the category name.
        """

        self.state.category = llm.call(prompt).strip()
        return self.state.category

    @router(categorize_ticket)
    def route_by_category(self, category):
        # Route to different handlers based on category
        return category.lower().replace(" ", "_")

    @listen("billing")
    def handle_billing_issue(self):
        # Handle billing-specific logic
        self.state.priority = "high"
        # More billing-specific processing...
        return "Billing issue handled"

    @listen("account_access")
    def handle_access_issue(self):
        # Handle access-specific logic
        self.state.priority = "high"
        # More access-specific processing...
        return "Access issue handled"

    # Additional category handlers...

    @listen("billing", "account_access", "technical_issue", "feature_request", "other")
    def resolve_ticket(self, resolution_info):
        # Final resolution step
        self.state.resolution = f"Issue resolved: {resolution_info}"
        return self.state.resolution

# Run the flow
support_flow = CustomerSupportFlow()
result = support_flow.kickoff()
```

### When to Combine Crews and Flows

The most sophisticated applications often benefit from combining Crews and Flows:

1. **Complex multi-stage processes** - Use Flows to orchestrate the overall process and Crews for complex subtasks
2. **Applications requiring both creativity and structure** - Use Crews for creative tasks and Flows for structured processing
3. **Enterprise-grade AI applications** - Use Flows to manage state and process flow while leveraging Crews for specialized work

```python
# Example: Content Production Pipeline combining Crews and Flows
from crewai.flow.flow import Flow, listen, start
from crewai import Agent, Crew, Process, Task
from pydantic import BaseModel
from typing import List, Dict

class ContentState(BaseModel):
    topic: str = ""
    target_audience: str = ""
    content_type: str = ""
    outline: Dict = {}
    draft_content: str = ""
    final_content: str = ""
    seo_score: int = 0

class ContentProductionFlow(Flow[ContentState]):
    @start()
    def initialize_project(self):
        # Set initial parameters
        self.state.topic = "Sustainable Investing"
        self.state.target_audience = "Millennial Investors"
        self.state.content_type = "Blog Post"
        return "Project initialized"

    @listen(initialize_project)
    def create_outline(self, _):
        # Use a research crew to create an outline
        researcher = Agent(
            role="Content Researcher",
            goal=f"Research {self.state.topic} for {self.state.target_audience}",
            backstory="You are an expert researcher with deep knowledge of content creation."
        )

        outliner = Agent(
            role="Content Strategist",
            goal=f"Create an engaging outline for a {self.state.content_type}",
            backstory="You excel at structuring content for maximum engagement."
        )

        research_task = Task(
            description=f"Research {self.state.topic} focusing on what would interest {self.state.target_audience}",
            expected_output="Comprehensive research notes with key points and statistics",
            agent=researcher
        )

        outline_task = Task(
            description=f"Create an outline for a {self.state.content_type} about {self.state.topic}",
            expected_output="Detailed content outline with sections and key points",
            agent=outliner,
            context=[research_task]
        )

        outline_crew = Crew(
            agents=[researcher, outliner],
            tasks=[research_task, outline_task],
            process=Process.sequential,
            verbose=True
        )

        # Run the crew and store the result
        result = outline_crew.kickoff()

        # Parse the outline (in a real app, you might use a more robust parsing approach)
        import json
        try:
            self.state.outline = json.loads(result.raw)
        except:
            # Fallback if not valid JSON
            self.state.outline = {"sections": result.raw}

        return "Outline created"

    @listen(create_outline)
    def write_content(self, _):
        # Use a writing crew to create the content
        writer = Agent(
            role="Content Writer",
            goal=f"Write engaging content for {self.state.target_audience}",
            backstory="You are a skilled writer who creates compelling content."
        )

        editor = Agent(
            role="Content Editor",
            goal="Ensure content is polished, accurate, and engaging",
            backstory="You have a keen eye for detail and a talent for improving content."
        )

        writing_task = Task(
            description=f"Write a {self.state.content_type} about {self.state.topic} following this outline: {self.state.outline}",
            expected_output="Complete draft content in markdown format",
            agent=writer
        )

        editing_task = Task(
            description="Edit and improve the draft content for clarity, engagement, and accuracy",
            expected_output="Polished final content in markdown format",
            agent=editor,
            context=[writing_task]
        )

        writing_crew = Crew(
            agents=[writer, editor],
            tasks=[writing_task, editing_task],
            process=Process.sequential,
            verbose=True
        )

        # Run the crew and store the result
        result = writing_crew.kickoff()
        self.state.final_content = result.raw

        return "Content created"

    @listen(write_content)
    def optimize_for_seo(self, _):
        # Use a direct LLM call for SEO optimization
        from crewai import LLM
        llm = LLM(model="openai/gpt-4o-mini")

        prompt = f"""
        Analyze this content for SEO effectiveness for the keyword "{self.state.topic}".
        Rate it on a scale of 1-100 and provide 3 specific recommendations for improvement.

        Content: {self.state.final_content[:1000]}... (truncated for brevity)

        Format your response as JSON with the following structure:
        {{
            "score": 85,
            "recommendations": [
                "Recommendation 1",
                "Recommendation 2",
                "Recommendation 3"
            ]
        }}
        """

        seo_analysis = llm.call(prompt)

        # Parse the SEO analysis
        import json
        try:
            analysis = json.loads(seo_analysis)
            self.state.seo_score = analysis.get("score", 0)
            return analysis
        except:
            self.state.seo_score = 50
            return {"score": 50, "recommendations": ["Unable to parse SEO analysis"]}

# Run the flow
content_flow = ContentProductionFlow()
result = content_flow.kickoff()
```

## Practical Evaluation Framework

To determine the right approach for your specific use case, follow this step-by-step evaluation framework:

### Step 1: Assess Complexity

Rate your application's complexity on a scale of 1-10 by considering:

1. **Number of steps**: How many distinct operations are required?
   * 1-3 steps: Low complexity (1-3)
   * 4-7 steps: Medium complexity (4-7)
   * 8+ steps: High complexity (8-10)

2. **Interdependencies**: How interconnected are the different parts?
   * Few dependencies: Low complexity (1-3)
   * Some dependencies: Medium complexity (4-7)
   * Many complex dependencies: High complexity (8-10)

3. **Conditional logic**: How much branching and decision-making is needed?
   * Linear process: Low complexity (1-3)
   * Some branching: Medium complexity (4-7)
   * Complex decision trees: High complexity (8-10)

4. **Domain knowledge**: How specialized is the knowledge required?
   * General knowledge: Low complexity (1-3)
   * Some specialized knowledge: Medium complexity (4-7)
   * Deep expertise in multiple domains: High complexity (8-10)

Calculate your average score to determine overall complexity.

### Step 2: Assess Precision Requirements

Rate your precision requirements on a scale of 1-10 by considering:

1. **Output structure**: How structured must the output be?
   * Free-form text: Low precision (1-3)
   * Semi-structured: Medium precision (4-7)
   * Strictly formatted (JSON, XML): High precision (8-10)

2. **Accuracy needs**: How important is factual accuracy?
   * Creative content: Low precision (1-3)
   * Informational content: Medium precision (4-7)
   * Critical information: High precision (8-10)

3. **Reproducibility**: How consistent must results be across runs?
   * Variation acceptable: Low precision (1-3)
   * Some consistency needed: Medium precision (4-7)
   * Exact reproducibility required: High precision (8-10)

4. **Error tolerance**: What is the impact of errors?
   * Low impact: Low precision (1-3)
   * Moderate impact: Medium precision (4-7)
   * High impact: High precision (8-10)

Calculate your average score to determine overall precision requirements.

### Step 3: Map to the Matrix

Plot your complexity and precision scores on the matrix:

* **Low Complexity (1-4), Low Precision (1-4)**: Simple Crews
* **Low Complexity (1-4), High Precision (5-10)**: Flows with direct LLM calls
* **High Complexity (5-10), Low Precision (1-4)**: Complex Crews
* **High Complexity (5-10), High Precision (5-10)**: Flows orchestrating Crews

### Step 4: Consider Additional Factors

Beyond complexity and precision, consider:

1. **Development time**: Crews are often faster to prototype
2. **Maintenance needs**: Flows provide better long-term maintainability
3. **Team expertise**: Consider your team's familiarity with different approaches
4. **Scalability requirements**: Flows typically scale better for complex applications
5. **Integration needs**: Consider how the solution will integrate with existing systems

## Conclusion

Choosing between Crews and Flows—or combining them—is a critical architectural decision that impacts the effectiveness, maintainability, and scalability of your CrewAI application. By evaluating your use case along the dimensions of complexity and precision, you can make informed decisions that align with your specific requirements.

Remember that the best approach often evolves as your application matures. Start with the simplest solution that meets your needs, and be prepared to refine your architecture as you gain experience and your requirements become clearer.

<Check>
  You now have a framework for evaluating CrewAI use cases and choosing the right approach based on complexity and precision requirements. This will help you build more effective, maintainable, and scalable AI applications.
</Check>

## Next Steps

* Learn more about [crafting effective agents](/en/guides/agents/crafting-effective-agents)
* Explore [building your first crew](/en/guides/crews/first-crew)
* Dive into [mastering flow state management](/en/guides/flows/mastering-flow-state)
* Check out the [core concepts](/en/concepts/agents) for deeper understanding


# Vision Tool

> The `VisionTool` is designed to extract text from images.

# `VisionTool`

## Description

This tool is used to extract text from images. When passed to the agent it will extract the text from the image and then use it to generate a response, report or any other output.
The URL or the PATH of the image should be passed to the Agent.

## Installation

Install the crewai\_tools package

```shell
pip install 'crewai[tools]'
```

## Usage

In order to use the VisionTool, the OpenAI API key should be set in the environment variable `OPENAI_API_KEY`.

```python Code
from crewai_tools import VisionTool

vision_tool = VisionTool()

@agent
def researcher(self) -> Agent:
    '''
    This agent uses the VisionTool to extract text from images.
    '''
    return Agent(
        config=self.agents_config["researcher"],
        allow_delegation=False,
        tools=[vision_tool]
    )
```

## Arguments

The VisionTool requires the following arguments:

| Argument             | Type     | Description                                                                      |
| :------------------- | :------- | :------------------------------------------------------------------------------- |
| **image\_path\_url** | `string` | **Mandatory**. The path to the image file from which text needs to be extracted. |


# Conditional Tasks

> Learn how to use conditional tasks in a crewAI kickoff

## Introduction

Conditional Tasks in crewAI allow for dynamic workflow adaptation based on the outcomes of previous tasks.
This powerful feature enables crews to make decisions and execute tasks selectively, enhancing the flexibility and efficiency of your AI-driven processes.

## Example Usage

```python Code
from typing import List
from pydantic import BaseModel
from crewai import Agent, Crew
from crewai.tasks.conditional_task import ConditionalTask
from crewai.tasks.task_output import TaskOutput
from crewai.task import Task
from crewai_tools import SerperDevTool

# Define a condition function for the conditional task
# If false, the task will be skipped, if true, then execute the task.
def is_data_missing(output: TaskOutput) -> bool:
    return len(output.pydantic.events) < 10  # this will skip this task

# Define the agents
data_fetcher_agent = Agent(
    role="Data Fetcher",
    goal="Fetch data online using Serper tool",
    backstory="Backstory 1",
    verbose=True,
    tools=[SerperDevTool()]
)

data_processor_agent = Agent(
    role="Data Processor",
    goal="Process fetched data",
    backstory="Backstory 2",
    verbose=True
)

summary_generator_agent = Agent(
    role="Summary Generator",
    goal="Generate summary from fetched data",
    backstory="Backstory 3",
    verbose=True
)

class EventOutput(BaseModel):
    events: List[str]

task1 = Task(
    description="Fetch data about events in San Francisco using Serper tool",
    expected_output="List of 10 things to do in SF this week",
    agent=data_fetcher_agent,
    output_pydantic=EventOutput,
)

conditional_task = ConditionalTask(
    description="""
        Check if data is missing. If we have less than 10 events,
        fetch more events using Serper tool so that
        we have a total of 10 events in SF this week..
        """,
    expected_output="List of 10 Things to do in SF this week",
    condition=is_data_missing,
    agent=data_processor_agent,
)

task3 = Task(
    description="Generate summary of events in San Francisco from fetched data",
    expected_output="A complete report on the customer and their customers and competitors, including their demographics, preferences, market positioning and audience engagement.",
    agent=summary_generator_agent,
)

# Create a crew with the tasks
crew = Crew(
    agents=[data_fetcher_agent, data_processor_agent, summary_generator_agent],
    tasks=[task1, conditional_task, task3],
    verbose=True,
    planning=True
)

# Run the crew
result = crew.kickoff()
print("results", result)
```


# Create Custom Tools

> Comprehensive guide on crafting, using, and managing custom tools within the CrewAI framework, including new functionalities and error handling.

## Creating and Utilizing Tools in CrewAI

This guide provides detailed instructions on creating custom tools for the CrewAI framework and how to efficiently manage and utilize these tools,
incorporating the latest functionalities such as tool delegation, error handling, and dynamic tool calling. It also highlights the importance of collaboration tools,
enabling agents to perform a wide range of actions.

### Subclassing `BaseTool`

To create a personalized tool, inherit from `BaseTool` and define the necessary attributes, including the `args_schema` for input validation, and the `_run` method.

```python Code
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = "What this tool does. It's vital for effective utilization."
    args_schema: Type[BaseModel] = MyToolInput

    def _run(self, argument: str) -> str:
        # Your tool's logic here
        return "Tool's result"
```

### Using the `tool` Decorator

Alternatively, you can use the tool decorator `@tool`. This approach allows you to define the tool's attributes and functionality directly within a function,
offering a concise and efficient way to create specialized tools tailored to your needs.

```python Code
from crewai.tools import tool

@tool("Tool Name")
def my_simple_tool(question: str) -> str:
    """Tool description for clarity."""
    # Tool logic here
    return "Tool output"
```

### Defining a Cache Function for the Tool

To optimize tool performance with caching, define custom caching strategies using the `cache_function` attribute.

```python Code
@tool("Tool with Caching")
def cached_tool(argument: str) -> str:
    """Tool functionality description."""
    return "Cacheable result"

def my_cache_strategy(arguments: dict, result: str) -> bool:
    # Define custom caching logic
    return True if some_condition else False

cached_tool.cache_function = my_cache_strategy
```

By adhering to these guidelines and incorporating new functionalities and collaboration tools into your tool creation and management processes,
you can leverage the full capabilities of the CrewAI framework, enhancing both the development experience and the efficiency of your AI agents.


# Kickoff Crew Asynchronously

> Kickoff a Crew Asynchronously

## Introduction

CrewAI provides the ability to kickoff a crew asynchronously, allowing you to start the crew execution in a non-blocking manner.
This feature is particularly useful when you want to run multiple crews concurrently or when you need to perform other tasks while the crew is executing.

## Asynchronous Crew Execution

To kickoff a crew asynchronously, use the `kickoff_async()` method. This method initiates the crew execution in a separate thread, allowing the main thread to continue executing other tasks.

### Method Signature

```python Code
def kickoff_async(self, inputs: dict) -> CrewOutput:
```

### Parameters

* `inputs` (dict): A dictionary containing the input data required for the tasks.

### Returns

* `CrewOutput`: An object representing the result of the crew execution.

## Potential Use Cases

* **Parallel Content Generation**: Kickoff multiple independent crews asynchronously, each responsible for generating content on different topics. For example, one crew might research and draft an article on AI trends, while another crew generates social media posts about a new product launch. Each crew operates independently, allowing content production to scale efficiently.

* **Concurrent Market Research Tasks**: Launch multiple crews asynchronously to conduct market research in parallel. One crew might analyze industry trends, while another examines competitor strategies, and yet another evaluates consumer sentiment. Each crew independently completes its task, enabling faster and more comprehensive insights.

* **Independent Travel Planning Modules**: Execute separate crews to independently plan different aspects of a trip. One crew might handle flight options, another handles accommodation, and a third plans activities. Each crew works asynchronously, allowing various components of the trip to be planned simultaneously and independently for faster results.

## Example: Single Asynchronous Crew Execution

Here's an example of how to kickoff a crew asynchronously using asyncio and awaiting the result:

```python Code
import asyncio
from crewai import Crew, Agent, Task

# Create an agent with code execution enabled
coding_agent = Agent(
    role="Python Data Analyst",
    goal="Analyze data and provide insights using Python",
    backstory="You are an experienced data analyst with strong Python skills.",
    allow_code_execution=True
)

# Create a task that requires code execution
data_analysis_task = Task(
    description="Analyze the given dataset and calculate the average age of participants. Ages: {ages}",
    agent=coding_agent,
    expected_output="The average age of the participants."
)

# Create a crew and add the task
analysis_crew = Crew(
    agents=[coding_agent],
    tasks=[data_analysis_task]
)

# Async function to kickoff the crew asynchronously
async def async_crew_execution():
    result = await analysis_crew.kickoff_async(inputs={"ages": [25, 30, 35, 40, 45]})
    print("Crew Result:", result)

# Run the async function
asyncio.run(async_crew_execution())
```

## Example: Multiple Asynchronous Crew Executions

In this example, we'll show how to kickoff multiple crews asynchronously and wait for all of them to complete using `asyncio.gather()`:

```python Code
import asyncio
from crewai import Crew, Agent, Task

# Create an agent with code execution enabled
coding_agent = Agent(
    role="Python Data Analyst",
    goal="Analyze data and provide insights using Python",
    backstory="You are an experienced data analyst with strong Python skills.",
    allow_code_execution=True
)

# Create tasks that require code execution
task_1 = Task(
    description="Analyze the first dataset and calculate the average age of participants. Ages: {ages}",
    agent=coding_agent,
    expected_output="The average age of the participants."
)

task_2 = Task(
    description="Analyze the second dataset and calculate the average age of participants. Ages: {ages}",
    agent=coding_agent,
    expected_output="The average age of the participants."
)

# Create two crews and add tasks
crew_1 = Crew(agents=[coding_agent], tasks=[task_1])
crew_2 = Crew(agents=[coding_agent], tasks=[task_2])

# Async function to kickoff multiple crews asynchronously and wait for all to finish
async def async_multiple_crews():
    # Create coroutines for concurrent execution
    result_1 = crew_1.kickoff_async(inputs={"ages": [25, 30, 35, 40, 45]})
    result_2 = crew_2.kickoff_async(inputs={"ages": [20, 22, 24, 28, 30]})

    # Wait for both crews to finish
    results = await asyncio.gather(result_1, result_2)

    for i, result in enumerate(results, 1):
        print(f"Crew {i} Result:", result)

# Run the async function
asyncio.run(async_multiple_crews())
```


# Kickoff Crew for Each

> Kickoff Crew for Each Item in a List

## Introduction

CrewAI provides the ability to kickoff a crew for each item in a list, allowing you to execute the crew for each item in the list.
This feature is particularly useful when you need to perform the same set of tasks for multiple items.

## Kicking Off a Crew for Each Item

To kickoff a crew for each item in a list, use the `kickoff_for_each()` method.
This method executes the crew for each item in the list, allowing you to process multiple items efficiently.

Here's an example of how to kickoff a crew for each item in a list:

```python Code
from crewai import Crew, Agent, Task

# Create an agent with code execution enabled
coding_agent = Agent(
    role="Python Data Analyst",
    goal="Analyze data and provide insights using Python",
    backstory="You are an experienced data analyst with strong Python skills.",
    allow_code_execution=True
)

# Create a task that requires code execution
data_analysis_task = Task(
    description="Analyze the given dataset and calculate the average age of participants. Ages: {ages}",
    agent=coding_agent,
    expected_output="The average age calculated from the dataset"
)

# Create a crew and add the task
analysis_crew = Crew(
    agents=[coding_agent],
    tasks=[data_analysis_task],
    verbose=True,
    memory=False
)

datasets = [
  { "ages": [25, 30, 35, 40, 45] },
  { "ages": [20, 25, 30, 35, 40] },
  { "ages": [30, 35, 40, 45, 50] }
]

# Execute the crew
result = analysis_crew.kickoff_for_each(inputs=datasets)
```
# Human Input on Execution

> Integrating CrewAI with human input during execution in complex decision-making processes and leveraging the full capabilities of the agent's attributes and tools.

## Human input in agent execution

Human input is critical in several agent execution scenarios, allowing agents to request additional information or clarification when necessary.
This feature is especially useful in complex decision-making processes or when agents require more details to complete a task effectively.

## Using human input with CrewAI

To integrate human input into agent execution, set the `human_input` flag in the task definition. When enabled, the agent prompts the user for input before delivering its final answer.
This input can provide extra context, clarify ambiguities, or validate the agent's output.

### Example:

```shell
pip install crewai
```

```python Code
import os
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool

os.environ["SERPER_API_KEY"] = "Your Key"  # serper.dev API key
os.environ["OPENAI_API_KEY"] = "Your Key"

# Loading Tools
search_tool = SerperDevTool()

# Define your agents with roles, goals, tools, and additional attributes
researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover cutting-edge developments in AI and data science',
    backstory=(
        "You are a Senior Research Analyst at a leading tech think tank. "
        "Your expertise lies in identifying emerging trends and technologies in AI and data science. "
        "You have a knack for dissecting complex data and presenting actionable insights."
    ),
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)
writer = Agent(
    role='Tech Content Strategist',
    goal='Craft compelling content on tech advancements',
    backstory=(
        "You are a renowned Tech Content Strategist, known for your insightful and engaging articles on technology and innovation. "
        "With a deep understanding of the tech industry, you transform complex concepts into compelling narratives."
    ),
    verbose=True,
    allow_delegation=True,
    tools=[search_tool],
    cache=False,  # Disable cache for this agent
)

# Create tasks for your agents
task1 = Task(
    description=(
        "Conduct a comprehensive analysis of the latest advancements in AI in 2025. "
        "Identify key trends, breakthrough technologies, and potential industry impacts. "
        "Compile your findings in a detailed report. "
        "Make sure to check with a human if the draft is good before finalizing your answer."
    ),
    expected_output='A comprehensive full report on the latest AI advancements in 2025, leave nothing out',
    agent=researcher,
    human_input=True
)

task2 = Task(
    description=(
        "Using the insights from the researcher\'s report, develop an engaging blog post that highlights the most significant AI advancements. "
        "Your post should be informative yet accessible, catering to a tech-savvy audience. "
        "Aim for a narrative that captures the essence of these breakthroughs and their implications for the future."
    ),
    expected_output='A compelling 3 paragraphs blog post formatted as markdown about the latest AI advancements in 2025',
    agent=writer,
    human_input=True
)

# Instantiate your crew with a sequential process
crew = Crew(
    agents=[researcher, writer],
    tasks=[task1, task2],
    verbose=True,
    memory=True,
    planning=True  # Enable planning feature for the crew
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)
```


# Custom Manager Agent

> Learn how to set a custom agent as the manager in CrewAI, providing more control over task management and coordination.

# Setting a Specific Agent as Manager in CrewAI

CrewAI allows users to set a specific agent as the manager of the crew, providing more control over the management and coordination of tasks.
This feature enables the customization of the managerial role to better fit your project's requirements.

## Using the `manager_agent` Attribute

### Custom Manager Agent

The `manager_agent` attribute allows you to define a custom agent to manage the crew. This agent will oversee the entire process, ensuring that tasks are completed efficiently and to the highest standard.

### Example

```python Code
import os
from crewai import Agent, Task, Crew, Process

# Define your agents
researcher = Agent(
    role="Researcher",
    goal="Conduct thorough research and analysis on AI and AI agents",
    backstory="You're an expert researcher, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently researching for a new client.",
    allow_delegation=False,
)

writer = Agent(
    role="Senior Writer",
    goal="Create compelling content about AI and AI agents",
    backstory="You're a senior writer, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently writing content for a new client.",
    allow_delegation=False,
)

# Define your task
task = Task(
    description="Generate a list of 5 interesting ideas for an article, then write one captivating paragraph for each idea that showcases the potential of a full article on this topic. Return the list of ideas with their paragraphs and your notes.",
    expected_output="5 bullet points, each with a paragraph and accompanying notes.",
)

# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
    allow_delegation=True,
)

# Instantiate your crew with a custom manager
crew = Crew(
    agents=[researcher, writer],
    tasks=[task],
    manager_agent=manager,
    process=Process.hierarchical,
)

# Start the crew's work
result = crew.kickoff()
```

## Benefits of a Custom Manager Agent

* **Enhanced Control**: Tailor the management approach to fit the specific needs of your project.
* **Improved Coordination**: Ensure efficient task coordination and management by an experienced agent.
* **Customizable Management**: Define managerial roles and responsibilities that align with your project's goals.

## Setting a Manager LLM

If you're using the hierarchical process and don't want to set a custom manager agent, you can specify the language model for the manager:

```python Code
from crewai import LLM

manager_llm = LLM(model="gpt-4o")

crew = Crew(
    agents=[researcher, writer],
    tasks=[task],
    process=Process.hierarchical,
    manager_llm=manager_llm
)
```

<Note>
  Either `manager_agent` or `manager_llm` must be set when using the hierarchical process.
</Note>


# Testing

> Learn how to test your CrewAI Crew and evaluate their performance.

## Overview

Testing is a crucial part of the development process, and it is essential to ensure that your crew is performing as expected. With crewAI, you can easily test your crew and evaluate its performance using the built-in testing capabilities.

### Using the Testing Feature

We added the CLI command `crewai test` to make it easy to test your crew. This command will run your crew for a specified number of iterations and provide detailed performance metrics. The parameters are `n_iterations` and `model`, which are optional and default to 2 and `gpt-4o-mini` respectively. For now, the only provider available is OpenAI.

```bash
crewai test
```

If you want to run more iterations or use a different model, you can specify the parameters like this:

```bash
crewai test --n_iterations 5 --model gpt-4o
```

or using the short forms:

```bash
crewai test -n 5 -m gpt-4o
```

When you run the `crewai test` command, the crew will be executed for the specified number of iterations, and the performance metrics will be displayed at the end of the run.

A table of scores at the end will show the performance of the crew in terms of the following metrics:

<center>**Tasks Scores (1-10 Higher is better)**</center>

| Tasks/Crew/Agents  | Run 1 | Run 2 | Avg. Total |            Agents            | Additional Info                |
| :----------------- | :---: | :---: | :--------: | :--------------------------: | :----------------------------- |
| Task 1             |  9.0  |  9.5  |   **9.2**  |     Professional Insights    |                                |
|                    |       |       |            |          Researcher          |                                |
| Task 2             |  9.0  |  10.0 |   **9.5**  | Company Profile Investigator |                                |
| Task 3             |  9.0  |  9.0  |   **9.0**  |      Automation Insights     |                                |
|                    |       |       |            |          Specialist          |                                |
| Task 4             |  9.0  |  9.0  |   **9.0**  |     Final Report Compiler    | Automation Insights Specialist |
| Crew               |  9.00 |  9.38 |   **9.2**  |                              |                                |
| Execution Time (s) |  126  |  145  |   **135**  |                              |                                |

The example above shows the test results for two runs of the crew with two tasks, with the average total score for each task and the crew as a whole.
