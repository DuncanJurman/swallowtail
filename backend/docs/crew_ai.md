TITLE: Running Crew with Inputs (Python)
DESCRIPTION: This snippet demonstrates how to initiate a CrewAI workflow by calling the `crew.kickoff()` method. It shows how to pass a dictionary of `inputs` to the crew, which allows dynamic population of variables (e.g., `{topic}`) within task descriptions defined in YAML files.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/tasks.mdx#_snippet_1

LANGUAGE: python
CODE:
```
crew.kickoff(inputs={'topic': 'AI Agents'})
```

----------------------------------------

TITLE: Full Example of Collaborative Agents in CrewAI
DESCRIPTION: This comprehensive example demonstrates a multi-agent system where a researcher, writer, and editor collaborate on an article creation task. All agents have `allow_delegation=True`, enabling the lead agent (writer) to delegate research to the researcher and the editor to refine the content, showcasing a complete collaborative workflow.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/collaboration.mdx#_snippet_3

LANGUAGE: Python
CODE:
```
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

----------------------------------------

TITLE: Adding Tools to CrewAI Agent in Python
DESCRIPTION: This snippet illustrates how to import specific tools from the `crewai_tools` library and assign them to a CrewAI agent. It demonstrates the inclusion of `FileReadTool` and `SerperDevTool` as examples, which are then passed as a list to the `tools` parameter during the agent's initialization, enabling the agent to utilize these functionalities.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/tools/overview.mdx#_snippet_0

LANGUAGE: Python
CODE:
```
from crewai_tools import FileReadTool, SerperDevTool

# Add tools to your agent
agent = Agent(
    role="Research Analyst",
    tools=[FileReadTool(), SerperDevTool()],
    # ... other configuration
)
```

----------------------------------------

TITLE: Using output_pydantic with CrewAI Tasks (Python)
DESCRIPTION: This snippet demonstrates how to use the `output_pydantic` property in a CrewAI task to ensure the output conforms to a specified Pydantic model. It defines a `Blog` model, an `Agent`, and a `Task` that uses `output_pydantic=Blog`. It also shows multiple ways to access the structured output: dictionary-style indexing, direct Pydantic attribute access, `to_dict()` method, and printing the entire object.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/tasks.mdx#_snippet_13

LANGUAGE: Python
CODE:
```
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

----------------------------------------

TITLE: Install CrewAI Python Framework
DESCRIPTION: This snippet demonstrates how to install the CrewAI framework using pip. The base installation provides core functionalities, while the '[tools]' extra installs additional utilities for enhanced agent capabilities, such as integration with various external tools.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/README.md#_snippet_29

LANGUAGE: Shell
CODE:
```
pip install crewai
```

LANGUAGE: Shell
CODE:
```
pip install 'crewai[tools]'
```

----------------------------------------

TITLE: Define and Run a Trip Planning Crew with crewAI
DESCRIPTION: Defines a `TripCrew` class that orchestrates a trip planning process using `crewAI` agents and tasks. It initializes with origin, cities, date range, and interests, then uses a city selection agent and a local expert agent to identify and gather trip details. The `run` method executes the crew and returns the planning result.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/observability/mlflow.mdx#_snippet_4

LANGUAGE: Python
CODE:
```
class TripCrew:
    def __init__(self, origin, cities, date_range, interests):
        self.cities = cities
        self.origin = origin
        self.interests = interests
        self.date_range = date_range

    def run(self):
        agents = TripAgents()
        tasks = TripTasks()

        city_selector_agent = agents.city_selection_agent()
        local_expert_agent = agents.local_expert()

        identify_task = tasks.identify_task(
            city_selector_agent,
            self.origin,
            self.cities,
            self.interests,
            self.date_range,
        )
        gather_task = tasks.gather_task(
            local_expert_agent, self.origin, self.interests, self.date_range
        )

        crew = Crew(
            agents=[city_selector_agent, local_expert_agent],
            tasks=[identify_task, gather_task],
            verbose=True,
            memory=True,
            knowledge={
                "sources": [string_source],
                "metadata": {"preference": "personal"},
            },
        )

        result = crew.kickoff()
        return result


trip_crew = TripCrew("California", "Tokyo", "Dec 12 - Dec 20", "sports")
result = trip_crew.run()

print(result)
```

----------------------------------------

TITLE: Initializing RagTool and Adding Diverse Content in Python
DESCRIPTION: This snippet demonstrates how to initialize the `RagTool` with default settings and then add content from different data sources, including a PDF file and a web page, using the `add` method. It also shows how to define a CrewAI agent that utilizes this `RagTool` to answer questions about the knowledge base.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/tools/ai-ml/ragtool.mdx#_snippet_0

LANGUAGE: Python
CODE:
```
from crewai_tools import RagTool

# Create a RAG tool with default settings
rag_tool = RagTool()

# Add content from a file
rag_tool.add(data_type="file", path="path/to/your/document.pdf")

# Add content from a web page
rag_tool.add(data_type="web_page", url="https://example.com")

# Define an agent with the RagTool
@agent
def knowledge_expert(self) -> Agent:
    '''
    This agent uses the RagTool to answer questions about the knowledge base.
    '''
    return Agent(
        config=self.agents_config["knowledge_expert"],
        allow_delegation=False,
        tools=[rag_tool]
    )
```

----------------------------------------

TITLE: Specifying Structured Output Formats for Tasks
DESCRIPTION: This example demonstrates the best practice of explicitly defining machine-readable output formats, such as JSON, for tasks. This ensures consistency and facilitates automated processing of the agent's deliverables.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/agents/crafting-effective-agents.mdx#_snippet_11

LANGUAGE: yaml
CODE:
```
data_extraction_task:
  description: "Extract key metrics from the quarterly report."
  expected_output: "JSON object with the following keys: revenue, growth_rate, customer_acquisition_cost, and retention_rate."
```

----------------------------------------

TITLE: Prioritizing Function Calling for Tool-Heavy Agents
DESCRIPTION: Function Calling Model Mismatch: Choosing models based on general capabilities while ignoring function calling performance is a pitfall for tool-heavy CrewAI workflows. For example, selecting a creative-focused model for an agent that primarily needs to call APIs or search tools can lead to struggles with tool parameter extraction and reliable function calls. CrewAI's solution is to prioritize function calling capabilities for agents that heavily use tools.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/llm-selection-guide.mdx#_snippet_10

LANGUAGE: python
CODE:
```
# For agents that use many tools
tool_agent = Agent(
    role="API Integration Specialist",
    tools=[search_tool, api_tool, data_tool],
    llm=LLM(model="gpt-4o"),  # Excellent function calling
    # OR
    llm=LLM(model="claude-3-5-sonnet")  # Also strong with tools
)
```

----------------------------------------

TITLE: Troubleshooting: Preventing Agent Delegation Loops (Python)
DESCRIPTION: This snippet addresses the issue of agents delegating tasks back and forth indefinitely. The solution involves establishing a clear hierarchy and responsibilities by enabling delegation for a manager agent and disabling it for specialist agents, preventing them from re-delegating tasks and breaking the loop.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/collaboration.mdx#_snippet_13

LANGUAGE: python
CODE:
```
# ✅ Solution: Clear hierarchy and responsibilities
manager = Agent(role="Manager", allow_delegation=True)
specialist1 = Agent(role="Specialist A", allow_delegation=False)  # No re-delegation
specialist2 = Agent(role="Specialist B", allow_delegation=False)
```

----------------------------------------

TITLE: CrewAI Agent Configuration Parameters Reference
DESCRIPTION: Documents the various optional parameters available when configuring an agent, including their types, default values, and descriptions. These parameters control an agent's capabilities like multimodal support, date injection, reasoning, and knowledge sources.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/agents.mdx#_snippet_1

LANGUAGE: APIDOC
CODE:
```
Agent Configuration Parameters:
  multimodal: bool (optional, default: False)
    Whether the agent supports multimodal capabilities.
  inject_date: bool (optional, default: False)
    Whether to automatically inject the current date into tasks.
  date_format: str (optional, default: "%Y-%m-%d")
    Format string for date when inject_date is enabled.
  reasoning: bool (optional, default: False)
    Whether the agent should reflect and create a plan before executing a task.
  max_reasoning_attempts: Optional[int] (optional)
    Maximum number of reasoning attempts before executing the task. If None, will try until ready.
  embedder: Optional[Dict[str, Any]] (optional)
    Configuration for the embedder used by the agent.
  knowledge_sources: Optional[List[BaseKnowledgeSource]] (optional)
    Knowledge sources available to the agent.
  use_system_prompt: Optional[bool] (optional, default: True)
    Whether to use system prompt (for o1 model support).
```

----------------------------------------

TITLE: Defining Research and Analysis Agents in CrewAI (YAML)
DESCRIPTION: This YAML configuration defines two AI agents, 'researcher' and 'analyst', for a CrewAI application. Each agent is assigned a specific 'role', 'goal', and 'backstory' to guide its behavior and specialization, along with a placeholder for the Large Language Model ('llm') provider and model ID. These definitions are crucial for shaping the agents' approach to tasks and ensuring complementary skills within the crew.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/crews/first-crew.mdx#_snippet_1

LANGUAGE: YAML
CODE:
```
researcher:
  role: >
    Senior Research Specialist for {topic}
  goal: >
    Find comprehensive and accurate information about {topic}
    with a focus on recent developments and key insights
  backstory: >
    You are an experienced research specialist with a talent for
    finding relevant information from various sources. You excel at
    organizing information in a clear and structured manner, making
    complex topics accessible to others.
  llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...

analyst:
  role: >
    Data Analyst and Report Writer for {topic}
  goal: >
    Analyze research findings and create a comprehensive, well-structured
    report that presents insights in a clear and engaging way
  backstory: >
    You are a skilled analyst with a background in data interpretation
    and technical writing. You have a talent for identifying patterns
    and extracting meaningful insights from research data, then
    communicating those insights effectively through well-crafted reports.
  llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...
```

----------------------------------------

TITLE: Install CrewAI Base Package
DESCRIPTION: Installs the core CrewAI package using pip, providing the fundamental framework for multi-agent automation. Ensure Python >=3.10 <3.14 is installed.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/README.md#_snippet_0

LANGUAGE: shell
CODE:
```
pip install crewai
```

----------------------------------------

TITLE: Implementing Asynchronous Task Execution in CrewAI (Python)
DESCRIPTION: This snippet demonstrates how to configure tasks for asynchronous execution using `async_execution=True`. It shows two research tasks (`list_ideas`, `list_important_history`) set to run asynchronously, and a `write_article` task that waits for and uses the context from both asynchronous tasks before proceeding.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/tasks.mdx#_snippet_17

LANGUAGE: Python
CODE:
```
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

----------------------------------------

TITLE: Illustrate Focused vs. Bloated State Design (Python)
DESCRIPTION: This Python example contrasts a 'bloated' state design with a 'focused' one, advocating for keeping flow state minimal and relevant to the the flow's specific purpose. It highlights how a focused state improves clarity and maintainability.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/flows/mastering-flow-state.mdx#_snippet_9

LANGUAGE: python
CODE:
```
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

----------------------------------------

TITLE: Create a Simple CrewAI Application with Agent and Task
DESCRIPTION: Defines a basic CrewAI application where an agent (Writer) is configured with a specific role, goal, backstory, and tools. A task is then assigned to this agent, and a Crew is instantiated to manage the agent and task collaboration.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/observability/langfuse.mdx#_snippet_4

LANGUAGE: Python
CODE:
```
from crewai import Agent, Task, Crew

from crewai_tools import (
    WebsiteSearchTool
)

web_rag_tool = WebsiteSearchTool()

writer = Agent(
        role="Writer",
        goal="You make math engaging and understandable for young children through poetry",
        backstory="You're an expert in writing haikus but you know nothing of math.",
        tools=[web_rag_tool],
    )

task = Task(description=("What is {multiplication}?"),
            expected_output=("Compose a haiku that includes the answer."),
            agent=writer)

crew = Crew(
  agents=[writer],
  tasks=[task],
  share_crew=False
)
```

----------------------------------------

TITLE: Initialize CrewAI Agent with Search Tool and Advanced Settings
DESCRIPTION: This Python example demonstrates how to create a CrewAI Agent, assign a SerperDevTool for search capabilities, and configure advanced settings such as memory, verbosity, request limits (max_rpm), and iteration limits (max_iter). It also shows how to set API keys as environment variables.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/customizing-agents.mdx#_snippet_1

LANGUAGE: python
CODE:
```
import os
from crewai import Agent
from crewai_tools import SerperDevTool

# Set API keys for tool initialization
os.environ["OPENAI_API_KEY"] = "Your Key"
os.environ["SERPER_API_KEY"] = "Your Key"

# Initialize a search tool
search_tool = SerperDevTool()

# Initialize the agent with advanced options
agent = Agent(
  role='Research Analyst',
  goal='Provide up-to-date market analysis',
  backstory='An expert analyst with a keen eye for market trends.',
  tools=[search_tool],
  memory=True, # Enable memory
  verbose=True,
  max_rpm=None, # No limit on requests per minute
  max_iter=25 # Default value for maximum iterations
)
```

----------------------------------------

TITLE: Configuring Custom LLM and Embeddings for `TXTSearchTool`
DESCRIPTION: This example shows how to configure the `TXTSearchTool` to use custom language models (LLM) and embedding providers. The `config` dictionary allows specifying providers like Ollama or Google and their respective model configurations, overriding the default OpenAI settings.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/tools/file-document/txtsearchtool.mdx#_snippet_2

LANGUAGE: python
CODE:
```
tool = TXTSearchTool(
    config=dict(
        llm=dict(
            provider="ollama", # or google, openai, anthropic, llama2, ...
            config=dict(
                model="llama2",
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google", # or openai, ollama, ...
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)
```

----------------------------------------

TITLE: Validating Email Format with a Custom Guardrail in CrewAI
DESCRIPTION: This Python function provides a custom guardrail to validate if a string contains a valid email address using regular expressions. It returns a tuple indicating success or failure, along with the cleaned email or an error message, serving as a practical example of data format validation for task outputs.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/tasks.mdx#_snippet_25

LANGUAGE: Python
CODE:
```
def validate_email_format(result: str) -> Tuple[bool, Union[str, str]]:
    """Ensure the output contains a valid email address."""
    import re
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(email_pattern, result.strip()):
        return (True, result.strip())
    return (False, "Output must be a valid email address")
```

----------------------------------------

TITLE: Agent Design: Specialized Tool User Example
DESCRIPTION: Illustrates how to design an agent specifically to leverage certain tools effectively, such as a Data Analysis Specialist equipped with PythonREPLTool, DataVisualizationTool, and CSVAnalysisTool.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/agents/crafting-effective-agents.mdx#_snippet_20

LANGUAGE: YAML
CODE:
```
role: "Data Analysis Specialist"
goal: "Derive meaningful insights from complex datasets through statistical analysis"
backstory: "With a background in data science, you excel at working with structured and unstructured data..."
tools: [PythonREPLTool, DataVisualizationTool, CSVAnalysisTool]
```

----------------------------------------

TITLE: Execute CrewAI Workflow
DESCRIPTION: Initiates the execution of the defined CrewAI workflow. This method triggers the agents and tasks to begin their operations as per the crew's configuration, leading to the planning and execution of assigned tasks.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/planning.mdx#_snippet_2

LANGUAGE: Python
CODE:
```
my_crew.kickoff()
```

----------------------------------------

TITLE: Designing Focused, Single-Purpose Tasks
DESCRIPTION: This snippet demonstrates how to break down a broad objective into multiple focused tasks, each with a single clear purpose and expected output. This approach improves clarity, enables better agent execution, and facilitates easier evaluation of results.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/agents/crafting-effective-agents.mdx#_snippet_8

LANGUAGE: yaml
CODE:
```
# Task 1
research_task:
  description: "Research the top 5 market trends in the AI industry for 2024."
  expected_output: "A markdown list of the 5 trends with supporting evidence."

# Task 2
analysis_task:
  description: "Analyze the identified trends to determine potential business impacts."
  expected_output: "A structured analysis with impact ratings (High/Medium/Low)."

# Task 3
visualization_task:
  description: "Create a visual representation of the analyzed trends."
  expected_output: "A description of a chart showing trends and their impact ratings."
```

----------------------------------------

TITLE: Writing Clear and Actionable Task Descriptions (Python)
DESCRIPTION: This snippet highlights the importance of providing specific and actionable task descriptions for agents. It contrasts a well-defined task description that includes focus areas, output format, and detailed instructions with a vague one, emphasizing that clear descriptions guide agent collaboration and lead to better outcomes.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/collaboration.mdx#_snippet_10

LANGUAGE: python
CODE:
```
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

----------------------------------------

TITLE: Running a CrewAI Research Crew in Python
DESCRIPTION: This Python script serves as the entry point for executing the `ResearchCrew`. It first ensures an 'output' directory exists, then defines the research topic as input. It instantiates the `ResearchCrew` and uses the `kickoff` method to start the collaborative AI process, finally printing the raw result and confirming the report's save location. This demonstrates the simplicity of initiating complex AI workflows with CrewAI.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/crews/first-crew.mdx#_snippet_4

LANGUAGE: Python
CODE:
```
#!/usr/bin/env python
# src/research_crew/main.py
import os
from research_crew.crew import ResearchCrew

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

def run():
    """
    Run the research crew.
    """
    inputs = {
        'topic': 'Artificial Intelligence in Healthcare'
    }

    # Create and run the crew
    result = ResearchCrew().crew().kickoff(inputs=inputs)

    # Print the result
    print("\n\n=== FINAL REPORT ===\n\n")
    print(result.raw)

    print("\n\nReport has been saved to output/report.md")

if __name__ == "__main__":
    run()
```

----------------------------------------

TITLE: Install CrewAI and Required Tools
DESCRIPTION: This command installs the `crewai` library and `crewai_tools` using pip, which are essential for running the CrewAI examples.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/human-input-on-execution.mdx#_snippet_0

LANGUAGE: shell
CODE:
```
pip install crewai
```

----------------------------------------

TITLE: Setting Up LLM API Keys in .env File
DESCRIPTION: This snippet demonstrates how to configure API keys for various Large Language Models (LLMs) within a `.env` file. It shows examples for OpenAI, Gemini, and Anthropic API keys, which are essential for authenticating requests to these LLM providers. Users should replace placeholder values with their actual keys to enable LLM interactions within the CrewAI application.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/flows/first-flow.mdx#_snippet_12

LANGUAGE: Shell
CODE:
```
OPENAI_API_KEY=your_openai_api_key
# or
GEMINI_API_KEY=your_gemini_api_key
# or
ANTHROPIC_API_KEY=your_anthropic_api_key
```

----------------------------------------

TITLE: Including Purpose and Context in Task Descriptions
DESCRIPTION: This snippet illustrates how adding the 'why' and 'how' a task fits into a larger workflow can significantly improve an agent's understanding and execution. Providing context helps the agent prioritize and focus on the most relevant aspects of the task.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/agents/crafting-effective-agents.mdx#_snippet_10

LANGUAGE: yaml
CODE:
```
competitor_analysis_task:
  description: >
    Analyze our three main competitors' pricing strategies.
    This analysis will inform our upcoming pricing model revision.
    Focus on identifying patterns in how they price premium features
    and how they structure their tiered offerings.
```

----------------------------------------

TITLE: Defining CrewAI Agents for Content Creation - YAML
DESCRIPTION: This snippet defines two core agents for the content creation crew: `content_writer` and `content_reviewer`. Each agent is assigned a specific role, a clear goal, and a backstory to guide its behavior, along with a placeholder for the Large Language Model (LLM) provider and model ID. These definitions establish the specialized perspectives for the AI agents.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/flows/first-flow.mdx#_snippet_3

LANGUAGE: YAML
CODE:
```
content_writer:
  role: >
    Educational Content Writer
  goal: >
    Create engaging, informative content that thoroughly explains the assigned topic
    and provides valuable insights to the reader
  backstory: >
    You are a talented educational writer with expertise in creating clear, engaging
    content. You have a gift for explaining complex concepts in accessible language
    and organizing information in a way that helps readers build their understanding.
  llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...

content_reviewer:
  role: >
    Educational Content Reviewer and Editor
  goal: >
    Ensure content is accurate, comprehensive, well-structured, and maintains
    consistency with previously written sections
  backstory: >
    You are a meticulous editor with years of experience reviewing educational
    content. You have an eye for detail, clarity, and coherence. You excel at
    improving content while maintaining the original author's voice and ensuring
    consistent quality across multiple sections.
  llm: provider/model-id  # e.g. openai/gpt-4o, google/gemini-2.0-flash, anthropic/claude...
```

----------------------------------------

TITLE: Implementing Function Calling Logic for LLMs in Python
DESCRIPTION: This comprehensive snippet details the implementation of function calling capabilities within an LLM integration. It covers parsing tool calls from the LLM's response, executing the corresponding functions, and then re-calling the LLM with the updated message history including the tool's output, enabling multi-turn function execution.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/custom-llm.mdx#_snippet_9

LANGUAGE: python
CODE:
```
import json

def call(self, messages, tools=None, callbacks=None, available_functions=None):
    # Convert string to message format
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    
    # Make API call
    response = self._make_api_call(messages, tools)
    message = response["choices"][0]["message"]
    
    # Check for function calls
    if "tool_calls" in message and available_functions:
        return self._handle_function_calls(
            message["tool_calls"], messages, tools, available_functions
        )
    
    return message["content"]

def _handle_function_calls(self, tool_calls, messages, tools, available_functions):
    """Handle function calling with proper message flow."""
    for tool_call in tool_calls:
        function_name = tool_call["function"]["name"]
        
        if function_name in available_functions:
            # Parse and execute function
            function_args = json.loads(tool_call["function"]["arguments"])
            function_result = available_functions[function_name](**function_args)
            
            # Add function call and result to message history
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": function_name,
                "content": str(function_result)
            })
            
            # Call LLM again with updated context
            return self.call(messages, tools, None, available_functions)
    
    return "Function call failed"
```

----------------------------------------

TITLE: CrewAI Agent Memory and Context Management Configuration
DESCRIPTION: Parameters for managing agent memory, integrating knowledge sources, configuring custom embeddings, and controlling agent behavior with custom templates.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/agents.mdx#_snippet_31

LANGUAGE: APIDOC
CODE:
```
knowledge_sources: list
  Description: Leverages external knowledge sources for domain-specific information.
```

LANGUAGE: APIDOC
CODE:
```
embedder: object
  Description: Configures custom embedding models for context management.
```

LANGUAGE: APIDOC
CODE:
```
system_template: str
  Description: Custom template for the system prompt to fine-tune agent behavior.
```

LANGUAGE: APIDOC
CODE:
```
prompt_template: str
  Description: Custom template for the user prompt to fine-tune agent behavior.
```

LANGUAGE: APIDOC
CODE:
```
response_template: str
  Description: Custom template for the agent's response to fine-tune agent behavior.
```

----------------------------------------

TITLE: CrewAI Agent Configuration with External Knowledge Sources
DESCRIPTION: This agent leverages pre-processed external `knowledge_sources` to answer questions, reducing the need to load large amounts of data into the LLM's context window. This approach is effective for tasks requiring access to curated and structured information, improving efficiency and accuracy.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/agents.mdx#_snippet_27

LANGUAGE: python
CODE:
```
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

----------------------------------------

TITLE: Defining a Research Crew with Agents and Tasks in Python
DESCRIPTION: This Python class, `ResearchCrew`, defines the structure of a collaborative AI system using CrewAI. It sets up a 'researcher' agent equipped with `SerperDevTool` for web search and an 'analyst' agent, along with 'research_task' and 'analysis_task' to guide their workflow. The `crew` method assembles these components into a sequential process, enabling coordinated AI actions.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/crews/first-crew.mdx#_snippet_3

LANGUAGE: Python
CODE:
```
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class ResearchCrew():
    """Research crew for comprehensive topic analysis and reporting"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True,
            tools=[SerperDevTool()]
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'], # type: ignore[index]
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'] # type: ignore[index]
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'], # type: ignore[index]
            output_file='output/report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
```

----------------------------------------

TITLE: Refining Agent Role and Goal for a Research Agent
DESCRIPTION: This snippet demonstrates how to refine an agent's role, goal, and backstory from a generic definition to a highly specialized and detailed one. The 'Before' shows a basic setup, while the 'After' provides a comprehensive and specific persona for an 'Academic Research Specialist in Emerging Technologies'.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/agents/crafting-effective-agents.mdx#_snippet_6

LANGUAGE: yaml
CODE:
```
role: "Researcher"
goal: "Find information"
backstory: "You are good at finding information online."
```

LANGUAGE: yaml
CODE:
```
role: "Academic Research Specialist in Emerging Technologies"
goal: "Discover and synthesize cutting-edge research, identifying key trends, methodologies, and findings while evaluating the quality and reliability of sources"
backstory: "With a background in both computer science and library science, you've mastered the art of digital research. You've worked with research teams at prestigious universities and know how to navigate academic databases, evaluate research quality, and synthesize findings across disciplines. You're methodical in your approach, always cross-referencing information and tracing claims to primary sources before drawing conclusions."
```

----------------------------------------

TITLE: Improving Unclear Task Instructions for Agents
DESCRIPTION: This snippet contrasts a poorly designed task with an improved version, highlighting the importance of detailed and specific instructions. The 'Improved Version' provides comprehensive guidance on scope, focus areas, and expected output structure, enabling more effective agent execution.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/agents/crafting-effective-agents.mdx#_snippet_12

LANGUAGE: yaml
CODE:
```
research_task:
  description: "Research AI trends."
  expected_output: "A report on AI trends."
```

LANGUAGE: yaml
CODE:
```
research_task:
  description: >
    Research the top emerging AI trends for 2024 with a focus on:
    1. Enterprise adoption patterns
    2. Technical breakthroughs in the past 6 months
    3. Regulatory developments affecting implementation

    For each trend, identify key companies, technologies, and potential business impacts.
  expected_output: >
    A comprehensive markdown report with:
    - Executive summary (5 bullet points)
    - 5-7 major trends with supporting evidence
    - For each trend: definition, examples, and business implications
    - References to authoritative sources
```

----------------------------------------

TITLE: Configure Multi-Model Crew in CrewAI
DESCRIPTION: This Python example demonstrates how to configure a CrewAI crew using a multi-model approach. It assigns different Large Language Models (LLMs) to specific agents based on their roles: a high-capability reasoning model for the manager, a creative model for the content writer, and an efficient model for the data processor. This strategy optimizes for both performance and cost by leveraging the strengths of various models for distinct tasks.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/llm-selection-guide.mdx#_snippet_0

LANGUAGE: Python
CODE:
```
from crewai import Agent, Task, Crew, LLM

# High-capability reasoning model for strategic planning
manager_llm = LLM(model="gemini-2.5-flash-preview-05-20", temperature=0.1)

# Creative model for content generation
content_llm = LLM(model="claude-3-5-sonnet-20241022", temperature=0.7)

# Efficient model for data processing
processing_llm = LLM(model="gpt-4o-mini", temperature=0)

research_manager = Agent(
    role="Research Strategy Manager",
    goal="Develop comprehensive research strategies and coordinate team efforts",
    backstory="Expert research strategist with deep analytical capabilities",
    llm=manager_llm,  # High-capability model for complex reasoning
    verbose=True
)

content_writer = Agent(
    role="Research Content Writer",
    goal="Transform research findings into compelling, well-structured reports",
    backstory="Skilled writer who excels at making complex topics accessible",
    llm=content_llm,  # Creative model for engaging content
    verbose=True
)

data_processor = Agent(
    role="Data Analysis Specialist", 
    goal="Extract and organize key data points from research sources",
    backstory="Detail-oriented analyst focused on accuracy and efficiency",
    llm=processing_llm,  # Fast, cost-effective model for routine tasks
    verbose=True
)

crew = Crew(
    agents=[research_manager, content_writer, data_processor],
    tasks=[...],  # Your specific tasks
    manager_llm=manager_llm,  # Manager uses the reasoning model
    verbose=True
)
```

----------------------------------------

TITLE: Automate Documentation Workflows with CrewAI and Enterprise Tools
DESCRIPTION: This Python example illustrates how to set up a CrewAI agent for automating complex documentation workflows. The 'Documentation Automator' agent handles tasks such as identifying outdated content, generating reports, creating weekly updates, and archiving completed project pages, ensuring efficient documentation maintenance.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/enterprise/integrations/notion.mdx#_snippet_20

LANGUAGE: python
CODE:
```
from crewai import Agent, Task, Crew
from crewai_tools import CrewaiEnterpriseTools

enterprise_tools = CrewaiEnterpriseTools(
    enterprise_token="your_enterprise_token"
)

doc_automator = Agent(
    role="Documentation Automator",
    goal="Automate documentation workflows and maintenance",
    backstory="An AI assistant that automates repetitive documentation tasks.",
    tools=[enterprise_tools]
)

# Complex documentation automation task
automation_task = Task(
    description="""
    1. Search for pages that haven't been updated in the last 30 days
    2. Review and update outdated content blocks
    3. Create weekly team update pages with consistent formatting
    4. Add status indicators and progress tracking to project pages
    5. Generate monthly documentation health reports
    6. Archive completed project pages and organize them in archive sections
    """,
    agent=doc_automator,
    expected_output="Documentation automated with updated content, weekly reports, and organized archives"
)

crew = Crew(
    agents=[doc_automator],
    tasks=[automation_task]
)

crew.kickoff()
```

----------------------------------------

TITLE: Managing Crew-Level vs Agent-Level LLM Hierarchy
DESCRIPTION: Ignoring Crew-Level vs Agent-Level LLM Hierarchy: Not understanding how CrewAI's LLM hierarchy works can lead to conflicts or poor coordination between crew LLM, manager LLM, and agent LLM settings. For instance, setting a crew to use Claude while agents are configured with GPT models creates inconsistent behavior and unnecessary model switching overhead. The CrewAI solution is to strategically plan your LLM hierarchy.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/llm-selection-guide.mdx#_snippet_9

LANGUAGE: python
CODE:
```
crew = Crew(
    agents=[agent1, agent2],
    tasks=[task1, task2],
    manager_llm=LLM(model="gpt-4o"),  # For crew coordination
    process=Process.hierarchical  # When using manager_llm
)

# Agents inherit crew LLM unless specifically overridden
agent1 = Agent(llm=LLM(model="claude-3-5-sonnet"))  # Override for specific needs
```

----------------------------------------

TITLE: Define Custom Tool by Subclassing BaseTool in CrewAI
DESCRIPTION: This snippet demonstrates how to create a custom tool by inheriting from `BaseTool`. It defines an input schema using Pydantic's `BaseModel` and implements the `_run` method for the tool's core logic. This approach provides structured input validation and clear tool definition.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/tools.mdx#_snippet_3

LANGUAGE: python
CODE:
```
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

----------------------------------------

TITLE: Define and Run a CrewAI Application with Weave Tracing
DESCRIPTION: This comprehensive Python example demonstrates how to define agents, tasks, and a CrewAI crew. It sets up an LLM, assigns roles and goals to agents, creates specific tasks, and then executes the crew, with all operations automatically traced by Weave.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/observability/weave.mdx#_snippet_2

LANGUAGE: python
CODE:
```
from crewai import Agent, Task, Crew, LLM, Process

# Create an LLM with a temperature of 0 to ensure deterministic outputs
llm = LLM(model="gpt-4o", temperature=0)

# Create agents
researcher = Agent(
    role='Research Analyst',
    goal='Find and analyze the best investment opportunities',
    backstory='Expert in financial analysis and market research',
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

writer = Agent(
    role='Report Writer',
    goal='Write clear and concise investment reports',
    backstory='Experienced in creating detailed financial reports',
    llm=llm,
    verbose=True,
    allow_delegation=False,
)

# Create tasks
research_task = Task(
    description='Deep research on the {topic}',
    expected_output='Comprehensive market data including key players, market size, and growth trends.',
    agent=researcher
)

writing_task = Task(
    description='Write a detailed report based on the research',
    expected_output='The report should be easy to read and understand. Use bullet points where applicable.',
    agent=writer
)

# Create a crew
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, writing_task],
    verbose=True,
    process=Process.sequential,
)

# Run the crew
result = crew.kickoff(inputs={"topic": "AI in material science"})
print(result)
```

----------------------------------------

TITLE: Inspect Complete System and User Prompts in CrewAI
DESCRIPTION: This Python code demonstrates how to instantiate a CrewAI Agent and Task, then utilize the `Prompts` utility to generate and print the complete system and user prompts that are sent to the LLM. This provides full transparency into the prompt structure, including automatically injected instructions and task context.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/advanced/customizing-prompts.mdx#_snippet_3

LANGUAGE: python
CODE:
```
from crewai import Agent, Crew, Task
from crewai.utilities.prompts import Prompts

# Create your agent
agent = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="You are an expert data analyst with 10 years of experience.",
    verbose=True
)

# Create a sample task
task = Task(
    description="Analyze the sales data and identify trends",
    expected_output="A detailed analysis with key insights and trends",
    agent=agent
)

# Create the prompt generator
prompt_generator = Prompts(
    agent=agent,
    has_tools=len(agent.tools) > 0,
    use_system_prompt=agent.use_system_prompt
)

# Generate and inspect the actual prompt
generated_prompt = prompt_generator.task_execution()

# Print the complete system prompt that will be sent to the LLM
if "system" in generated_prompt:
    print("=== SYSTEM PROMPT ===")
    print(generated_prompt["system"])
    print("\n=== USER PROMPT ===")
    print(generated_prompt["user"])
else:
    print("=== COMPLETE PROMPT ===")
    print(generated_prompt["prompt"])

# You can also see how the task description gets formatted
print("\n=== TASK CONTEXT ===")
print(f"Task Description: {task.description}")
print(f"Expected Output: {task.expected_output}")
```

----------------------------------------

TITLE: Holistic Agent-LLM Optimization for a Technical Documentation Specialist in CrewAI
DESCRIPTION: This snippet demonstrates the synergy of specific role definition, a deep backstory, and tailored LLM selection for an 'API Documentation Specialist' agent. It shows how to configure an agent with relevant tools and fine-tuned LLM parameters (like low temperature) to maximize accuracy and usability for technical writing tasks.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/learn/llm-selection-guide.mdx#_snippet_5

LANGUAGE: python
CODE:
```
tech_writer = Agent(
    role="API Documentation Specialist",  # Specific role for clear LLM requirements
    goal="Create comprehensive, developer-friendly API documentation",
    backstory="""
    You're a technical writer with 8+ years documenting REST APIs, GraphQL endpoints, 
    and SDK integration guides. You've worked with developer tools companies and 
    understand what developers need: clear examples, comprehensive error handling, 
    and practical use cases. You prioritize accuracy and usability over marketing fluff.
    """,
    llm=LLM(
        model="claude-3-5-sonnet",  # Excellent for technical writing
        temperature=0.1  # Low temperature for accuracy
    ),
    tools=[code_analyzer_tool, api_scanner_tool],
    verbose=True 
)
```

----------------------------------------

TITLE: Basic Example: Implementing Structured State Management in CrewAI Flows
DESCRIPTION: This Python example demonstrates how to implement structured state management in a CrewAI flow using Pydantic models. It defines `UserPreferences` and `AppState` models to structure the flow's state, then creates a `StructuredStateFlow` class that uses `AppState` as its type parameter. The example illustrates how to initialize, access, and modify state fields with type checking and autocompletion within different flow steps (`initialize_data`, `process_data`, `generate_summary`), and shows how the automatic `id` field is available. Finally, it demonstrates running the flow and printing the final state.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/guides/flows/mastering-flow-state.mdx#_snippet_1

LANGUAGE: python
CODE:
```
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

----------------------------------------

TITLE: Initializing Meta Llama LLM in CrewAI with Python
DESCRIPTION: This Python code demonstrates how to initialize a Meta Llama LLM instance in CrewAI. It specifies the model (meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8), temperature, stop sequences, and a seed. This configuration enables CrewAI to leverage Meta's Llama models for various tasks.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/concepts/llms.mdx#_snippet_7

LANGUAGE: python
CODE:
```
from crewai import LLM

# Initialize Meta Llama LLM
llm = LLM(
    model="meta_llama/Llama-4-Scout-17B-16E-Instruct-FP8",
    temperature=0.8,
    stop=["END"],
    seed=42
)
```

----------------------------------------

TITLE: Configuring RagTool with Custom Embedchain Settings in Python
DESCRIPTION: This snippet illustrates how to provide advanced configuration for the `RagTool` by passing a detailed dictionary to its `config` parameter. This allows customization of the underlying Embedchain app, including LLM provider and model, embedding model, vector database (e.g., Elasticsearch), and chunking parameters, enabling fine-grained control over the RAG process.
SOURCE: https://github.com/crewaiinc/crewai/blob/main/docs/tools/ai-ml/ragtool.mdx#_snippet_3

LANGUAGE: Python
CODE:
```
from crewai_tools import RagTool

# Create a RAG tool with custom configuration
config = {
    "app": {
        "name": "custom_app"
    },
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4"
        }
    },
    "embedding_model": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-ada-002"
        }
    },
    "vectordb": {
        "provider": "elasticsearch",
        "config": {
            "collection_name": "my-collection",
            "cloud_id": "deployment-name:xxxx",
            "api_key": "your-key",
            "verify_certs": False
        }
    },
    "chunker": {
        "chunk_size": 400,
        "chunk_overlap": 100,
        "length_function": "len",
        "min_chunk_size": 0
    }
}

rag_tool = RagTool(config=config, summarize=True)
```