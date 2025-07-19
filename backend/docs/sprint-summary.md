# Sprint Summary: Image Generation Crew with CrewAI

## Overview
This sprint focused on implementing a proper CrewAI-based image generation and evaluation system that uses multimodal LLMs and tools, moving away from direct API calls to leverage CrewAI's agent orchestration capabilities.

## Work Completed

### 1. Created CrewAI Tools
- **ImageGenerationTool** (`src/tools/image_generation_tool.py`)
  - Wraps OpenAI's image generation API
  - Handles reference image loading from file paths or URLs
  - Returns generated images with metadata
  - Implements both async (`_arun`) and sync (`_run`) methods for CrewAI compatibility

- **ImageStorageTool** (`src/tools/image_storage_tool.py`)
  - Stores images in Supabase storage
  - Handles base64 encoded image data
  - Returns storage URLs for downstream use

- **ImageRetrievalTool** (`src/tools/image_storage_tool.py`)
  - Retrieves images from storage or file paths
  - Modified to return file paths instead of base64 data to avoid token limits

- **ImageAnalysisTool** (`src/tools/image_analysis_tool.py`)
  - Uses GPT-4 Vision to analyze images
  - Provides detailed descriptions of visual elements
  - Helps agents understand reference images without passing raw data

### 2. Revised Agent Architecture
- **ImageGenerationAgent** (`src/agents/image_generation.py`)
  - Redesigned to use tools instead of direct API calls
  - Now acts as a proper CrewAI agent that coordinates tools
  - Removed direct OpenAI API integration

- **ImageEvaluatorAgent** (`src/agents/image_evaluator.py`)
  - Updated to leverage multimodal LLM capabilities
  - Uses agent's vision capabilities instead of API calls
  - Properly configured with `multimodal: true`

### 3. Updated YAML Configuration
- Modified `src/config/agents.yaml` to reflect new architecture
- Configured agents with proper multimodal settings
- Updated agent descriptions to match new tool-based approach

### 4. Created Multiple Crew Implementations
- **ImageGenerationCrew** (original) - Had YAML loading issues
- **ImageGenerationCrewV2** - Fixed YAML loading, follows CrewAI patterns
- **ImageGenerationCrewV3** - Attempted token-safe approach

### 5. Fixed Technical Issues
- **YAML Configuration Loading**: Fixed path resolution in crew base class
- **Synchronous Tool Execution**: Added `_run` methods to tools for sync execution
- **Token Limit Management**: Modified tools to avoid passing large base64 data

## Current Issue: Crew Execution Stalls

### The Problem
When executing the crew, the agent successfully:
1. Retrieves the reference image path
2. Gets stuck trying to analyze the image

The execution stalls after the `retrieve_image` tool returns a file path. The agent needs to visually analyze the reference image but can't proceed.

### Root Cause
The multimodal agent expects to "see" images but the `retrieve_image` tool only returns a file path. The agent is stuck because:
- It receives: `{"image_path": "/path/to/image.jpg"}`
- It needs: Actual visual access to the image content
- The multimodal LLM can't analyze an image it can't see

### Approaches Tried

#### 1. Base64 Data in Tool Response (Failed)
- Initially returned base64 image data from tools
- Caused token limit errors (47,610 tokens requested vs 30,000 limit)
- The entire image data was being included in the conversation context

#### 2. Token-Safe Tools (Partial Success)
- Modified tools to return file paths instead of data
- Created SafeImageGenerationTool that stores data separately
- Reduced token usage but created the visibility problem

#### 3. Image Analysis Tool (Current Approach)
- Created `ImageAnalysisTool` that uses GPT-4 Vision
- Agent workflow: retrieve → analyze → generate
- Tool analyzes images and returns text descriptions
- This should allow agents to understand images without token overload

### Current Status
The crew structure is correct, tools are working individually, but the execution flow stalls when the agent tries to understand the reference image. The analyze_image tool has been added but testing shows the crew still times out during execution.

## Test Results
- Direct image generation (without crew) works perfectly
- Crew assembly and configuration works
- Execution starts but doesn't complete the full workflow

## Next Steps
1. Debug why the crew execution stalls after image retrieval
2. Verify the analyze_image tool is being called correctly
3. Consider adding more explicit instructions in task descriptions
4. Potentially add logging to track exact tool call sequences
5. Test with simpler task chains to isolate the issue

## Key Learnings
1. CrewAI tools must be designed carefully to avoid token limits
2. Multimodal agents need proper access to visual content
3. The `@CrewBase` decorator pattern is the correct way to create crews
4. Tool outputs should be minimal to avoid overwhelming the LLM context
5. Synchronous execution requires implementing `_run` methods in tools


## New Plan

Update Todos
  ⎿ ☐ Fix OpenAI API usage in services -       
      Remove unsupported parameters (quality,
      background) for gpt-image-1
    ☐ Simplify ImageGenerationTool - Remove
      base64 returns, only return file paths
    ☐ Update both agents to be multimodal in
      image_generation_crew_v2.py
    ☐ Remove unnecessary tools from crew
      (ImageRetrievalTool, ImageAnalysisTool
      from agents)
    ☐ Implement feedback loop with conditional
      task execution based on evaluation
    ☐ Update task descriptions to pass image
      paths in context for multimodal
      processing
    ☐ Create comprehensive integration test
      for end-to-end workflow
    ☐ Add proper error handling and logging
      throughout the workflow
    ☐ Test with multiple iterations to verify
      feedback loop works correctly
    ☐ Update backend.md documentation with new
      workflow details

⏺ Now let me create a detailed implementation
  plan based on these todos:

╭──────────────────────────────────────────────────╮
│ Ready to code?                                   │
│                                                  │
│ Here is Claude's plan:                           │
│ ╭──────────────────────────────────────────────╮ │
│ │ Simplified Multimodal Image Generation Crew  │ │
│ │ Implementation Plan                          │ │
│ │                                              │ │
│ │ Overview                                     │ │
│ │                                              │ │
│ │ Implement a clean, efficient image           │ │
│ │ generation workflow using CrewAI's built-in  │ │
│ │ multimodal capabilities, minimizing custom   │ │
│ │ tools and following best practices.          │ │
│ │                                              │ │
│ │ Detailed Implementation Steps                │ │
│ │                                              │ │
│ │ 1. Fix OpenAI API Usage (Priority: HIGH)     │ │
│ │                                              │ │
│ │ File:                                        │ │
│ │ backend/src/services/openai_image_service.py │ │
│ │ - Remove quality parameter from              │ │
│ │ generate_image method (line 54)              │ │
│ │ - Update images.edit call to only use        │ │
│ │ supported parameters                         │ │
│ │ - Ensure we're using                         │ │
│ │ response_format="b64_json" for consistency   │ │
│ │                                              │ │
│ │ File: backend/src/services/openai_client.py  │ │
│ │ - Remove quality and background parameters   │ │
│ │ from all methods                             │ │
│ │ - Update generate_from_reference to match    │ │
│ │ actual API                                   │ │
│ │                                              │ │
│ │ 2. Simplify ImageGenerationTool (Priority:   │ │
│ │ HIGH)                                        │ │
│ │                                              │ │
│ │ File:                                        │ │
│ │ backend/src/tools/image_generation_tool.py   │ │
│ │ - Remove the image_b64 return field (line    │ │
│ │ 104)                                         │ │
│ │ - Only return temp_image_path and metadata   │ │
│ │ - Ensure proper cleanup of temp files after  │ │
│ │ workflow                                     │ │
│ │                                              │ │
│ │ 3. Update Agents to Multimodal (Priority:    │ │
│ │ HIGH)                                        │ │
│ │                                              │ │
│ │ File: backend/src/crews/image_generation_cre │ │
│ │ w_v2.py                                      │ │
│ │ - Add multimodal=True to image_generator     │ │
│ │ agent (line 73)                              │ │
│ │ - Remove ImageAnalysisTool and               │ │
│ │ ImageRetrievalTool from generator's tools    │ │
│ │ - Keep only ImageGenerationTool and          │ │
│ │ ImageStorageTool for generator               │ │
│ │ - Remove all tools from evaluator agent (it  │ │
│ │ only needs multimodal vision)                │ │
│ │                                              │ │
│ │ 4. Implement Feedback Loop (Priority: HIGH)  │ │
│ │                                              │ │
│ │ File: backend/src/crews/image_generation_cre │ │
│ │ w_v2.py                                      │ │
│ │ - Create new task:                           │ │
│ │ regenerate_with_feedback_task                │ │
│ │ - Add conditional logic to check evaluation  │ │
│ │ results                                      │ │
│ │ - Implement attempt counter (max 3 attempts) │ │
│ │ - Use Process.hierarchical or custom         │ │
│ │ workflow for conditional execution           │ │
│ │                                              │ │
│ │ 5. Update Task Descriptions (Priority: HIGH) │ │
│ │                                              │ │
│ │ File: backend/src/crews/image_generation_cre │ │
│ │ w_v2.py                                      │ │
│ │ - Update generate_image_task to include      │ │
│ │ reference image path in context              │ │
│ │ - Modify evaluate_image_task to receive both │ │
│ │  image paths                                 │ │
│ │ - Add clear instructions for multimodal      │ │
│ │ image processing                             │ │
│ │                                              │ │
│ │ Example task description:                    │ │
│ │ description=f"""Generate a high-quality      │ │
│ │ product image for {self.product_name}.       │ │
│ │                                              │ │
│ │ Reference image is available at:             │ │
│ │ {self.reference_image_url}                   │ │
│ │ You can see and analyze this image directly  │ │
│ │ with your multimodal capabilities.           │ │
│ │                                              │ │
│ │ Steps:                                       │ │
│ │ 1. Examine the reference image to understand │ │
│ │  its style and composition                   │ │
│ │ 2. Create a detailed prompt that captures    │ │
│ │ the reference style while highlighting:      │ │
│ │ {features_str}                               │ │
│ │ 3. Use the generate_image tool with your     │ │
│ │ crafted prompt                               │ │
│ │ 4. Return the path to the generated image    │ │
│ │ """                                          │ │
│ │                                              │ │
│ │ 6. Create Integration Test (Priority:        │ │
│ │ MEDIUM)                                      │ │
│ │                                              │ │
│ │ File: backend/tests/crews/test_image_generat │ │
│ │ ion_crew_v2.py (NEW)                         │ │
│ │ - Test successful generation on first        │ │
│ │ attempt                                      │ │
│ │ - Test rejection and regeneration flow       │ │
│ │ - Test max attempts reached scenario         │ │
│ │ - Verify multimodal agents can see images    │ │
│ │ - Check proper cleanup of temporary files    │ │
│ │                                              │ │
│ │ 7. Error Handling & Logging (Priority:       │ │
│ │ MEDIUM)                                      │ │
│ │                                              │ │
│ │ - Add try-catch blocks in crew execution     │ │
│ │ - Log each step of the workflow              │ │
│ │ - Capture and log evaluation scores          │ │
│ │ - Save intermediate results for debugging    │ │
│ │                                              │ │
│ │ 8. Testing Multiple Iterations (Priority:    │ │
│ │ MEDIUM)                                      │ │
│ │                                              │ │
│ │ - Create test cases with varying approval    │ │
│ │ thresholds                                   │ │
│ │ - Test with different types of reference     │ │
│ │ images                                       │ │
│ │ - Verify feedback is properly incorporated   │ │
│ │ - Ensure token limits are respected          │ │
│ │                                              │ │
│ │ Key Changes from Original Plan               │ │
│ │                                              │ │
│ │ 1. No ImageAnalysisTool needed - Multimodal  │ │
│ │ agents see images directly                   │ │
│ │ 2. No ImageEvaluationTool needed - Evaluator │ │
│ │  uses built-in vision                        │ │
│ │ 3. Minimal tool usage - Only                 │ │
│ │ ImageGenerationTool and ImageStorageTool     │ │
│ │ 4. Simplified workflow - Let CrewAI handle   │ │
│ │ the complexity                               │ │
│ │                                              │ │
│ │ Expected Benefits                            │ │
│ │                                              │ │
│ │ 1. Simpler code - Fewer tools, less          │ │
│ │ complexity                                   │ │
│ │ 2. Better performance - No redundant API     │ │
│ │ calls                                        │ │
│ │ 3. Token efficient - Images handled by       │ │
│ │ multimodal system                            │ │
│ │ 4. Follows best practices - Uses CrewAI as   │ │
│ │ designed                                     │ │
│ │                                              │ │
│ │ Success Criteria                             │ │
│ │                                              │ │
│ │ - Crew executes end-to-end without stalling  │ │
│ │ - Images are generated based on reference    │ │
│ │ style                                        │ │
│ │ - Feedback loop improves image quality       │ │
│ │ - All tests pass consistently                │ │
│ │ - Token usage stays within limits    