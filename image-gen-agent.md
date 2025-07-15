# Image Generation Agent Implementation with GPT-Image-1

## Executive Summary

This document outlines the implementation strategy for the Image Generation Agent using OpenAI's gpt-image-1 model via the Responses API. This approach enables multi-turn conversations for iterative image refinement, providing superior control over the image generation process compared to traditional single-shot APIs.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [API Integration Strategy](#api-integration-strategy)
3. [Conversation State Management](#conversation-state-management)
4. [Implementation Details](#implementation-details)
5. [Workflow Examples](#workflow-examples)
6. [Configuration and Customization](#configuration-and-customization)
7. [Best Practices](#best-practices)
8. [Error Handling and Recovery](#error-handling-and-recovery)

---

## Architecture Overview

### Key Advantages of GPT-Image-1 with Responses API

1. **Multi-turn Conversations**: Iterate on images through natural language instructions
2. **Context Preservation**: Maintain conversation history for coherent refinements
3. **Superior Instruction Following**: Better understanding of complex requirements
4. **Real-world Knowledge**: Leverages broader knowledge base for accurate representations
5. **Text Rendering**: Improved ability to include text in images
6. **Detailed Editing**: Make specific changes without regenerating entire image

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Image Generation Agent                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌──────────────────┐                │
│  │   Conversation   │    │    Response      │                │
│  │     Manager      │◄───┤    Handler       │                │
│  └────────┬─────────┘    └──────────────────┘                │
│           │                                                   │
│           ▼                                                   │
│  ┌─────────────────┐    ┌──────────────────┐                │
│  │  GPT-Image-1    │    │   Asset          │                │
│  │  API Client     │───►│   Storage        │                │
│  └─────────────────┘    └──────────────────┘                │
│                                                               │
│  ┌─────────────────────────────────────────┐                │
│  │         Conversation State Store         │                │
│  │  • Session tracking                      │                │
│  │  • Previous response IDs                 │                │
│  │  • Image history                         │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## API Integration Strategy

### 1. Primary API: Responses API with Image Generation Tool

```python
from openai import OpenAI
import base64
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ImageGenerationSession:
    """Tracks a multi-turn image generation conversation."""
    session_id: str
    product_id: str
    conversation_history: List[Dict[str, Any]]
    current_response_id: Optional[str] = None
    generated_images: List[Dict[str, Any]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        self.generated_images = self.generated_images or []
        self.created_at = self.created_at or datetime.utcnow()
        self.updated_at = self.updated_at or datetime.utcnow()

class GPTImageClient:
    """Client for GPT-Image-1 using Responses API."""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4.1-mini"  # or latest model supporting image generation
        
    async def generate_initial_image(self, 
                                   prompt: str,
                                   session: ImageGenerationSession) -> Dict[str, Any]:
        """Generate the first image in a conversation."""
        
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            tools=[{"type": "image_generation"}],
        )
        
        # Process the response
        result = await self._process_response(response, session)
        
        # Update session
        session.current_response_id = response.id
        session.conversation_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.utcnow()
        })
        session.conversation_history.append({
            "role": "assistant",
            "response_id": response.id,
            "images": result["images"],
            "timestamp": datetime.utcnow()
        })
        
        return result
        
    async def refine_image(self,
                          instruction: str,
                          session: ImageGenerationSession) -> Dict[str, Any]:
        """Refine an existing image through conversation."""
        
        if not session.current_response_id:
            raise ValueError("No previous response to refine")
            
        response = self.client.responses.create(
            model=self.model,
            input=instruction,
            tools=[{"type": "image_generation"}],
            previous_response_id=session.current_response_id  # Key for multi-turn
        )
        
        # Process and update session
        result = await self._process_response(response, session)
        session.current_response_id = response.id
        session.conversation_history.extend([
            {"role": "user", "content": instruction, "timestamp": datetime.utcnow()},
            {"role": "assistant", "response_id": response.id, "images": result["images"], "timestamp": datetime.utcnow()}
        ])
        
        return result
        
    async def _process_response(self, response, session: ImageGenerationSession) -> Dict[str, Any]:
        """Process API response and extract images."""
        
        images = []
        for output in response.output:
            if output.type == "image_generation_call":
                # Extract image data
                image_data = output.result
                
                # Handle base64 encoded images
                if isinstance(image_data, list) and image_data:
                    for img in image_data:
                        image_info = {
                            "id": generate_image_id(),
                            "base64": img if isinstance(img, str) else None,
                            "url": None,  # Set if using URL format
                            "created_at": datetime.utcnow(),
                            "session_id": session.session_id,
                            "response_id": response.id
                        }
                        
                        # Store the image
                        stored_url = await self._store_image(image_info, session.product_id)
                        image_info["stored_url"] = stored_url
                        
                        images.append(image_info)
                        session.generated_images.append(image_info)
                        
        return {
            "response_id": response.id,
            "images": images,
            "raw_response": response
        }
        
    async def _store_image(self, image_info: Dict, product_id: str) -> str:
        """Store image and return URL."""
        # Implementation depends on storage backend (S3, local, etc.)
        pass
```

### 2. Session Management

```python
class ImageConversationManager:
    """Manages multi-turn image generation conversations."""
    
    def __init__(self, redis_client, db_session):
        self.redis = redis_client
        self.db = db_session
        self.gpt_client = GPTImageClient(settings.OPENAI_API_KEY)
        
    async def start_session(self, product_id: str, initial_prompt: str) -> ImageGenerationSession:
        """Start a new image generation session."""
        
        session = ImageGenerationSession(
            session_id=generate_session_id(),
            product_id=product_id,
            conversation_history=[]
        )
        
        # Generate initial image
        result = await self.gpt_client.generate_initial_image(initial_prompt, session)
        
        # Store session in Redis for quick access
        await self._store_session(session)
        
        # Also persist to database
        await self._persist_session(session)
        
        return session
        
    async def continue_session(self, session_id: str, instruction: str) -> Dict[str, Any]:
        """Continue an existing session with new instructions."""
        
        # Retrieve session
        session = await self._get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        # Apply refinement
        result = await self.gpt_client.refine_image(instruction, session)
        
        # Update stored session
        await self._store_session(session)
        await self._persist_session(session)
        
        return result
        
    async def _store_session(self, session: ImageGenerationSession):
        """Store session in Redis for quick access."""
        key = f"image_session:{session.session_id}"
        value = session_to_json(session)
        await self.redis.set(key, value, ex=3600 * 24)  # 24 hour TTL
        
    async def _get_session(self, session_id: str) -> Optional[ImageGenerationSession]:
        """Retrieve session from storage."""
        # Try Redis first
        key = f"image_session:{session_id}"
        value = await self.redis.get(key)
        
        if value:
            return json_to_session(value)
            
        # Fall back to database
        db_session = await self.db.query(
            "SELECT * FROM image_sessions WHERE session_id = ?",
            [session_id]
        )
        
        if db_session:
            return ImageGenerationSession(**db_session)
            
        return None
```

---

## Conversation State Management

### State Schema

```python
class ImageSessionState(BaseModel):
    """Complete state of an image generation session."""
    
    # Session metadata
    session_id: str
    product_id: str
    agent_id: str
    user_id: Optional[str]
    
    # Conversation tracking
    current_response_id: Optional[str]
    conversation_turns: int = 0
    
    # Generated assets
    images: List[GeneratedImage]
    selected_image_id: Optional[str]  # Current "active" image
    
    # Context and configuration
    product_context: Dict[str, Any]  # Product details for context
    style_config: ImageStyleConfig
    brand_guidelines: Optional[Dict[str, Any]]
    
    # Workflow state
    workflow_stage: str  # "initial", "refining", "finalizing"
    approval_status: str  # "pending", "approved", "rejected"
    
    # Timestamps
    created_at: datetime
    last_updated: datetime
    expires_at: Optional[datetime]

class GeneratedImage(BaseModel):
    """Individual generated image metadata."""
    
    image_id: str
    response_id: str  # Links to API response
    turn_number: int  # Which conversation turn created this
    
    # Image data
    url: Optional[str]
    base64: Optional[str]
    stored_path: str
    
    # Generation metadata
    prompt_used: str
    instruction_used: Optional[str]  # For refinements
    generation_params: Dict[str, Any]
    
    # Quality and status
    quality_score: Optional[float]  # From automated quality check
    status: str  # "generated", "selected", "rejected", "final"
    
    # Usage tracking
    used_in_campaigns: List[str]
    performance_metrics: Optional[Dict[str, Any]]
```

### State Persistence Strategy

```sql
-- PostgreSQL schema for session persistence
CREATE TABLE image_generation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    product_id UUID REFERENCES products(id),
    agent_id VARCHAR(100),
    user_id UUID REFERENCES users(id),
    
    -- Conversation state
    current_response_id VARCHAR(255),
    conversation_history JSONB NOT NULL DEFAULT '[]',
    conversation_turns INTEGER DEFAULT 0,
    
    -- Configuration
    style_config JSONB,
    brand_guidelines JSONB,
    product_context JSONB,
    
    -- Workflow
    workflow_stage VARCHAR(50) DEFAULT 'initial',
    approval_status VARCHAR(50) DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    
    -- Indexes
    INDEX idx_sessions_product (product_id),
    INDEX idx_sessions_created (created_at),
    INDEX idx_sessions_status (approval_status)
);

CREATE TABLE generated_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES image_generation_sessions(session_id),
    image_id VARCHAR(255) UNIQUE NOT NULL,
    response_id VARCHAR(255) NOT NULL,
    turn_number INTEGER NOT NULL,
    
    -- Image data
    storage_url TEXT NOT NULL,
    thumbnail_url TEXT,
    metadata JSONB,
    
    -- Generation details
    prompt_used TEXT NOT NULL,
    instruction_used TEXT,
    generation_params JSONB,
    
    -- Status and quality
    status VARCHAR(50) DEFAULT 'generated',
    quality_score NUMERIC(3,2),
    selected BOOLEAN DEFAULT FALSE,
    
    -- Usage tracking
    usage_data JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    INDEX idx_images_session (session_id),
    INDEX idx_images_status (status),
    INDEX idx_images_selected (selected)
);
```

---

## Implementation Details

### 1. Image Generation Agent Class

```python
class ImageGenerationAgent(BaseProductAgent):
    """Agent responsible for all image generation using GPT-Image-1."""
    
    def __init__(self, product_id: str, config: ImageAgentConfig):
        super().__init__(product_id, "image_generation")
        self.config = config
        self.conversation_manager = ImageConversationManager(
            redis_client=get_redis_client(),
            db_session=get_db_session()
        )
        self.quality_checker = ImageQualityChecker()
        
    async def generate_product_images(self, product_data: ProductData) -> ImageGenerationResult:
        """Generate complete set of product images through conversation."""
        
        results = ImageGenerationResult()
        
        # 1. Generate main product image
        main_session = await self._generate_main_image(product_data)
        results.main_image = main_session.selected_image
        
        # 2. Generate lifestyle images
        for environment in self.config.lifestyle_settings["environments"]:
            lifestyle_session = await self._generate_lifestyle_image(
                product_data, environment
            )
            results.lifestyle_images.append(lifestyle_session.selected_image)
            
        # 3. Generate variations if needed
        if self.config.generate_variations:
            variations = await self._generate_variations(main_session)
            results.variations.extend(variations)
            
        return results
        
    async def _generate_main_image(self, product_data: ProductData) -> ImageGenerationSession:
        """Generate main product image with refinements."""
        
        # Build initial prompt with product context
        initial_prompt = self._build_product_prompt(product_data)
        
        # Start session
        session = await self.conversation_manager.start_session(
            product_id=self.product_id,
            initial_prompt=initial_prompt
        )
        
        # Check initial quality
        quality = await self.quality_checker.check(session.generated_images[0])
        
        # Refine if needed
        if quality.score < self.config.quality_threshold:
            refinements = self._determine_refinements(quality.issues)
            
            for refinement in refinements:
                result = await self.conversation_manager.continue_session(
                    session.session_id,
                    refinement
                )
                
                # Check quality after each refinement
                new_quality = await self.quality_checker.check(result["images"][0])
                if new_quality.score >= self.config.quality_threshold:
                    break
                    
        # Select best image from session
        session.selected_image = await self._select_best_image(session)
        
        return session
        
    async def _generate_lifestyle_image(self, 
                                      product_data: ProductData,
                                      environment: str) -> ImageGenerationSession:
        """Generate lifestyle image for specific environment."""
        
        # Build environment-specific prompt
        prompt = self._build_lifestyle_prompt(product_data, environment)
        
        # Start session
        session = await self.conversation_manager.start_session(
            product_id=self.product_id,
            initial_prompt=prompt
        )
        
        # Apply style refinements based on brand
        if self.config.brand_style_enforcement:
            style_instruction = self._build_style_instruction()
            await self.conversation_manager.continue_session(
                session.session_id,
                style_instruction
            )
            
        session.selected_image = await self._select_best_image(session)
        return session
        
    def _build_product_prompt(self, product_data: ProductData) -> str:
        """Build detailed initial prompt for product image."""
        
        template = self.config.prompts.get("main_product", DEFAULT_PRODUCT_PROMPT)
        
        # Inject product details
        prompt = template.format(
            product_name=product_data.name,
            product_description=product_data.description,
            key_features=", ".join(product_data.features[:3]),
            style=self.config.visual_style,
            background=self.config.product_shots["main_image"]["background"],
            lighting=self.config.product_shots["main_image"]["lighting"]
        )
        
        # Add technical specifications if available
        if product_data.specifications:
            prompt += f"\n\nTechnical details to showcase: {product_data.specifications}"
            
        return prompt
        
    def _determine_refinements(self, quality_issues: List[str]) -> List[str]:
        """Determine refinement instructions based on quality issues."""
        
        refinements = []
        
        issue_refinement_map = {
            "low_detail": "Increase the detail and sharpness, especially on the product surface and edges",
            "poor_lighting": "Improve the lighting to be more professional and evenly distributed",
            "wrong_angle": "Adjust the angle to show the product from a more flattering perspective",
            "background_issues": "Clean up the background to be pure white with no distractions",
            "color_accuracy": "Adjust colors to be more accurate and vibrant",
            "composition": "Improve the composition with better centering and appropriate zoom level"
        }
        
        for issue in quality_issues:
            if issue in issue_refinement_map:
                refinements.append(issue_refinement_map[issue])
                
        return refinements
```

### 2. Quality Checking System

```python
class ImageQualityChecker:
    """Automated quality checking for generated images."""
    
    def __init__(self):
        self.checks = [
            self._check_resolution,
            self._check_composition,
            self._check_lighting,
            self._check_background,
            self._check_product_visibility
        ]
        
    async def check(self, image: GeneratedImage) -> QualityResult:
        """Run quality checks on generated image."""
        
        issues = []
        scores = []
        
        # Download image for analysis
        image_data = await self._download_image(image.stored_url)
        
        # Run each check
        for check_func in self.checks:
            result = await check_func(image_data)
            scores.append(result.score)
            if result.issues:
                issues.extend(result.issues)
                
        # Calculate overall score
        overall_score = sum(scores) / len(scores)
        
        return QualityResult(
            score=overall_score,
            issues=issues,
            passed=overall_score >= 0.8
        )
```

### 3. Workflow Integration

```python
class ImageGenerationWorkflow:
    """Orchestrates image generation within product lifecycle."""
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.image_agent = ImageGenerationAgent(product_id, load_config(product_id))
        
    async def execute_discovery_phase(self) -> WorkflowResult:
        """Generate initial images for product discovery."""
        
        # Load product data
        product_data = await load_product_data(self.product_id)
        
        # Generate base images
        results = await self.image_agent.generate_product_images(product_data)
        
        # Create checkpoint for approval
        checkpoint = await create_checkpoint(
            type="image_approval",
            data={
                "images": results.to_dict(),
                "product_id": self.product_id
            }
        )
        
        return WorkflowResult(
            status="pending_approval",
            checkpoint_id=checkpoint.id,
            results=results
        )
        
    async def execute_refinement_phase(self, 
                                     checkpoint_feedback: CheckpointFeedback) -> WorkflowResult:
        """Refine images based on feedback."""
        
        refinement_sessions = []
        
        for image_feedback in checkpoint_feedback.image_feedback:
            if image_feedback.needs_refinement:
                # Retrieve original session
                session = await self.image_agent.conversation_manager.get_session(
                    image_feedback.session_id
                )
                
                # Apply refinements
                for instruction in image_feedback.refinement_instructions:
                    result = await self.image_agent.conversation_manager.continue_session(
                        session.session_id,
                        instruction
                    )
                    
                refinement_sessions.append(session)
                
        return WorkflowResult(
            status="refined",
            sessions=refinement_sessions
        )
```

---

## Workflow Examples

### Example 1: Complete Product Image Generation Flow

```python
# 1. Initial generation
session = await conversation_manager.start_session(
    product_id="prod_123",
    initial_prompt="""
    Professional product photography of an eco-friendly stainless steel water bottle.
    Features: 32oz capacity, vacuum insulated, powder-coated matte black finish, 
    bamboo cap with silicone seal. 
    Style: Minimalist, premium, sustainable aesthetic.
    Background: Pure white, studio lighting, slight reflection on surface.
    """
)

# 2. First refinement - improve angle
result1 = await conversation_manager.continue_session(
    session.session_id,
    "Rotate the bottle 15 degrees to the right to better show the bamboo cap detail"
)

# 3. Second refinement - adjust lighting
result2 = await conversation_manager.continue_session(
    session.session_id,
    "Add subtle rim lighting to emphasize the bottle's silhouette and matte texture"
)

# 4. Final refinement - add context
result3 = await conversation_manager.continue_session(
    session.session_id,
    "Add a few water droplets on the surface to suggest coldness and freshness"
)

# 5. Generate variations
variation1 = await conversation_manager.continue_session(
    session.session_id,
    "Create a version with the cap removed and placed beside the bottle"
)

variation2 = await conversation_manager.continue_session(
    session.session_id,
    "Show the bottle at a different angle highlighting the logo"
)
```

### Example 2: Lifestyle Image Generation

```python
# 1. Generate base lifestyle image
lifestyle_session = await conversation_manager.start_session(
    product_id="prod_123",
    initial_prompt="""
    Lifestyle photography of someone using the eco-friendly water bottle during a hike.
    Setting: Mountain trail with scenic background
    Person: 30-something professional, athletic wear, natural pose
    Lighting: Golden hour, natural sunlight
    Mood: Active, healthy, environmentally conscious
    Focus: Product in use but integrated naturally into the scene
    """
)

# 2. Adjust demographics
await conversation_manager.continue_session(
    lifestyle_session.session_id,
    "Make the person more diverse and inclusive in appearance"
)

# 3. Enhance product visibility
await conversation_manager.continue_session(
    lifestyle_session.session_id,
    "Ensure the water bottle is more prominently visible while maintaining natural integration"
)

# 4. Create seasonal variation
await conversation_manager.continue_session(
    lifestyle_session.session_id,
    "Transform this into a winter scene with appropriate clothing and snowy mountain background"
)
```

---

## Integration with Image Evaluator Agent

### Automated Quality Control Loop

The Image Generation Agent seamlessly integrates with the Image Evaluator Agent to create an automated quality control system that ensures generated images meet requirements without manual intervention.

### 1. Integration Architecture

```python
class ImageGenerationWithAutomatedEvaluation:
    """Orchestrates image generation with automatic evaluation and refinement."""
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.generation_agent = ImageGenerationAgent(product_id)
        self.evaluator_agent = ImageEvaluatorAgent(product_id)
        self.storage_manager = SupabaseStorageManager()
        self.max_refinement_cycles = 5
        
    async def generate_and_approve(self,
                                 reference_image_url: str,
                                 initial_prompt: str,
                                 requirements: ProductRequirements) -> ApprovedImageResult:
        """Generate image with automatic evaluation until approved."""
        
        # Start generation session
        session = await self.generation_agent.conversation_manager.start_session(
            product_id=self.product_id,
            initial_prompt=initial_prompt
        )
        
        approved = False
        cycle = 0
        
        while not approved and cycle < self.max_refinement_cycles:
            # Get latest generated image
            latest_image = session.generated_images[-1]
            
            # Evaluate against reference
            evaluation = await self.evaluator_agent.evaluate(
                reference_image=reference_image_url,
                generated_image=latest_image.stored_url,
                requirements=requirements
            )
            
            # Check if approved
            if evaluation.approved:
                approved = True
                # Store only the final approved image
                final_url = await self.storage_manager.upload_generated_image(
                    product_id=self.product_id,
                    session_id=session.session_id,
                    image_data=latest_image.base64,
                    image_type="main_product"
                )
                break
                
            # Generate refinement instructions
            refinements = await self.evaluator_agent.generate_refinements(evaluation)
            
            # Apply each refinement
            for instruction in refinements[:3]:  # Limit instructions per cycle
                result = await self.generation_agent.conversation_manager.continue_session(
                    session_id=session.session_id,
                    instruction=instruction.text
                )
                
            cycle += 1
            
        # Handle final result
        if approved:
            return ApprovedImageResult(
                success=True,
                final_image_url=final_url,
                generation_session_id=session.session_id,
                evaluation_score=evaluation.score.overall,
                refinement_cycles=cycle,
                total_images_generated=len(session.generated_images)
            )
        else:
            # Escalate to human review
            checkpoint = await self.create_human_checkpoint(session, evaluation)
            return ApprovedImageResult(
                success=False,
                checkpoint_id=checkpoint.id,
                reason="max_refinement_cycles_exceeded",
                best_attempt_url=session.generated_images[-1].stored_url
            )
```

### 2. Evaluation Feedback Integration

```python
class EvaluationFeedbackHandler:
    """Handles evaluation feedback and generates appropriate refinements."""
    
    def __init__(self):
        self.refinement_strategies = self._load_refinement_strategies()
        
    async def process_evaluation_feedback(self,
                                        evaluation: EvaluationResult,
                                        session: ImageGenerationSession) -> List[str]:
        """Convert evaluation results into actionable refinement instructions."""
        
        instructions = []
        
        # Analyze low-scoring areas
        for metric, score in evaluation.score.breakdown.items():
            if score < 0.7:  # Below threshold
                strategy = self.refinement_strategies.get(metric)
                if strategy:
                    instruction = await strategy.generate_instruction(
                        evaluation_data=evaluation,
                        current_image=session.generated_images[-1]
                    )
                    instructions.append(instruction)
                    
        # Add specific issue-based refinements
        for issue in evaluation.comparison.differences:
            if issue.severity in ["high", "medium"]:
                instruction = self._create_issue_instruction(issue)
                instructions.append(instruction)
                
        # Prioritize and consolidate instructions
        return self._prioritize_instructions(instructions, max_count=3)
        
    def _create_issue_instruction(self, issue: ImageIssue) -> str:
        """Create specific instruction for an identified issue."""
        
        templates = {
            "color_mismatch": "Adjust the {element} color to match the reference: {target_color}",
            "composition_error": "Reframe the image to {correction}",
            "detail_missing": "Add the missing {detail} to the {location}",
            "lighting_issue": "Modify the lighting to be {lighting_correction}",
            "texture_incorrect": "Change the {element} texture to appear more {target_texture}"
        }
        
        template = templates.get(issue.type, "Fix the {element}: {correction}")
        return template.format(**issue.details)
```

### 3. Storage Integration for Final Images Only

```python
class OptimizedImageStorage:
    """Handles storage of only final approved images."""
    
    def __init__(self, storage_backend: SupabaseStorageManager):
        self.storage = storage_backend
        self.temp_storage = TempImageCache()
        
    async def handle_generation_cycle(self,
                                    session: ImageGenerationSession,
                                    evaluation: EvaluationResult) -> StorageResult:
        """Handle storage for generation cycle."""
        
        latest_image = session.generated_images[-1]
        
        if evaluation.approved:
            # Store permanently only if approved
            permanent_url = await self.storage.upload_generated_image(
                product_id=session.product_id,
                session_id=session.session_id,
                image_data=latest_image.base64,
                image_type=self._determine_image_type(session)
            )
            
            # Clean up all temporary images from this session
            await self.temp_storage.cleanup_session(session.session_id)
            
            return StorageResult(
                stored=True,
                permanent_url=permanent_url,
                storage_cost_saved=self._calculate_savings(session)
            )
        else:
            # Keep in temporary cache for evaluation
            temp_url = await self.temp_storage.store_temporary(
                image_data=latest_image.base64,
                session_id=session.session_id,
                ttl_hours=24  # Auto-delete after 24 hours
            )
            
            return StorageResult(
                stored=False,
                temp_url=temp_url
            )
```

### 4. Workflow Example with Evaluator

```python
# Complete automated workflow
async def automated_product_image_workflow(product_id: str):
    """End-to-end automated image generation with evaluation."""
    
    # Initialize integrated system
    integrated_system = ImageGenerationWithAutomatedEvaluation(product_id)
    
    # Load product data and reference
    product_data = await load_product_data(product_id)
    reference_image = await load_reference_image(product_id)
    
    # Define requirements
    requirements = ProductRequirements(
        product_name=product_data.name,
        key_features=product_data.features,
        brand_guidelines=product_data.brand_guidelines,
        quality_threshold=0.85
    )
    
    # Generate with automatic approval
    result = await integrated_system.generate_and_approve(
        reference_image_url=reference_image.url,
        initial_prompt=f"""Professional product photography of {product_data.name}.
        Features: {', '.join(product_data.features[:3])}.
        Style: {product_data.brand_guidelines.style}.
        Background: pure white, professional studio lighting.""",
        requirements=requirements
    )
    
    if result.success:
        print(f"Image approved after {result.refinement_cycles} cycles")
        print(f"Final image URL: {result.final_image_url}")
        print(f"Storage savings: Generated {result.total_images_generated} images, stored only 1")
    else:
        print(f"Escalated to human review: {result.reason}")
        print(f"Checkpoint ID: {result.checkpoint_id}")
```

### 5. Metrics and Monitoring

```python
class IntegratedSystemMetrics:
    """Track metrics for the integrated generation-evaluation system."""
    
    def __init__(self):
        self.metrics = {
            "auto_approval_rate": Gauge(),
            "avg_cycles_to_approval": Histogram(),
            "storage_savings_gb": Counter(),
            "human_escalation_rate": Gauge(),
            "total_generation_time": Histogram()
        }
        
    async def record_workflow_complete(self, workflow_result: WorkflowResult):
        """Record metrics for completed workflow."""
        
        # Calculate auto-approval rate
        if workflow_result.auto_approved:
            self.metrics["auto_approval_rate"].inc()
            
        # Track cycles to approval
        self.metrics["avg_cycles_to_approval"].observe(workflow_result.cycles)
        
        # Calculate storage savings
        images_not_stored = workflow_result.total_generated - 1  # Only stored final
        storage_saved_mb = images_not_stored * 2  # Assume 2MB average
        self.metrics["storage_savings_gb"].inc(storage_saved_mb / 1024)
        
        # Track timing
        self.metrics["total_generation_time"].observe(
            workflow_result.duration_seconds
        )
```

---

## Configuration and Customization

### 1. Agent Configuration Schema

```python
class GPTImageAgentConfig(BaseModel):
    """Configuration for GPT-Image-1 based image generation."""
    
    # Model settings
    model_name: str = "gpt-4.1-mini"
    temperature: float = 0.7
    
    # Generation settings
    quality_threshold: float = 0.85
    max_refinement_turns: int = 5
    auto_refine: bool = True
    
    # Session management
    session_timeout_hours: int = 24
    max_images_per_session: int = 20
    preserve_session_history: bool = True
    
    # Style configuration
    visual_style: ImageStyle
    brand_guidelines: BrandGuidelines
    
    # Prompt templates (customizable via frontend)
    prompt_templates: Dict[str, PromptTemplate] = {
        "main_product": PromptTemplate(
            template="""Professional product photography of {product_name}.
            Description: {product_description}
            Key features to highlight: {key_features}
            Visual style: {style}
            Background: {background}
            Lighting: {lighting}
            Additional requirements: {additional_requirements}""",
            variables=["product_name", "product_description", "key_features", 
                      "style", "background", "lighting", "additional_requirements"],
            editable=True
        ),
        "lifestyle": PromptTemplate(
            template="""Lifestyle photography showing {product_name} in use.
            Environment: {environment}
            Target demographic: {demographic}
            Mood: {mood}
            Activity: {activity}
            Time of day: {time_of_day}
            Product integration: {integration_style}""",
            variables=["product_name", "environment", "demographic", 
                      "mood", "activity", "time_of_day", "integration_style"],
            editable=True
        ),
        "refinement_instruction": PromptTemplate(
            template="{instruction}",
            variables=["instruction"],
            editable=True
        )
    }
    
    # Refinement strategies
    refinement_strategies: List[RefinementStrategy] = [
        RefinementStrategy(
            trigger="low_quality_score",
            instructions=[
                "Increase overall image quality and sharpness",
                "Improve lighting and color accuracy",
                "Enhance detail in key product areas"
            ]
        ),
        RefinementStrategy(
            trigger="brand_mismatch",
            instructions=[
                "Adjust visual style to match brand guidelines: {brand_style}",
                "Ensure color palette aligns with brand colors: {brand_colors}",
                "Apply brand-specific aesthetic requirements"
            ]
        )
    ]
    
    # Output settings
    output_format: str = "url"  # or "b64_json"
    storage_backend: str = "s3"  # or "local", "gcs"
    organize_by_session: bool = True
    
    # Quality checks
    enable_auto_quality_check: bool = True
    quality_check_criteria: List[str] = [
        "resolution", "composition", "lighting", 
        "background", "product_visibility", "brand_alignment"
    ]

class ImageStyle(BaseModel):
    """Visual style configuration."""
    
    name: str = "modern_minimalist"
    characteristics: List[str] = [
        "clean lines", "ample white space", 
        "professional lighting", "subtle shadows"
    ]
    color_temperature: str = "neutral"  # warm, neutral, cool
    contrast_level: str = "medium"  # low, medium, high
    saturation: str = "natural"  # muted, natural, vibrant

class BrandGuidelines(BaseModel):
    """Brand-specific guidelines for image generation."""
    
    primary_colors: List[str]  # Hex codes
    secondary_colors: List[str]
    avoid_colors: List[str]
    
    tone: str  # "premium", "approachable", "technical", etc.
    mandatory_elements: List[str]  # e.g., ["logo visible", "tagline included"]
    prohibited_elements: List[str]  # e.g., ["competitors", "off-brand imagery"]
    
    composition_rules: List[str] = [
        "Product should occupy 60-70% of frame",
        "Maintain consistent angle across product line",
        "Include subtle brand watermark in corner"
    ]
```

### 2. Frontend Integration API

```python
@router.post("/products/{product_id}/images/generate")
async def start_image_generation(
    product_id: str,
    request: ImageGenerationRequest,
    user: User = Depends(get_current_user)
):
    """Start a new image generation session."""
    
    agent = get_image_agent(product_id)
    session = await agent.conversation_manager.start_session(
        product_id=product_id,
        initial_prompt=request.prompt
    )
    
    return {
        "session_id": session.session_id,
        "images": session.generated_images,
        "status": "success"
    }

@router.post("/products/{product_id}/images/sessions/{session_id}/refine")
async def refine_image(
    product_id: str,
    session_id: str,
    request: RefinementRequest,
    user: User = Depends(get_current_user)
):
    """Apply refinement to existing session."""
    
    agent = get_image_agent(product_id)
    result = await agent.conversation_manager.continue_session(
        session_id=session_id,
        instruction=request.instruction
    )
    
    return {
        "session_id": session_id,
        "new_images": result["images"],
        "turn_number": len(result["conversation_history"]) // 2
    }

@router.get("/products/{product_id}/images/sessions/{session_id}")
async def get_session_details(
    product_id: str,
    session_id: str,
    user: User = Depends(get_current_user)
):
    """Get full session history and images."""
    
    agent = get_image_agent(product_id)
    session = await agent.conversation_manager.get_session(session_id)
    
    return {
        "session": session.dict(),
        "conversation_history": session.conversation_history,
        "all_images": session.generated_images,
        "selected_image": session.selected_image
    }

@router.put("/products/{product_id}/images/config/prompts")
async def update_prompt_templates(
    product_id: str,
    updates: PromptTemplateUpdate,
    user: User = Depends(get_current_user)
):
    """Update customizable prompt templates."""
    
    config_manager = ImageConfigManager()
    await config_manager.update_prompt_templates(
        product_id=product_id,
        template_name=updates.template_name,
        new_template=updates.template,
        user_id=user.id
    )
    
    return {"status": "updated"}
```

---

## Best Practices

### 1. Prompt Engineering

```python
class PromptEngineeringGuide:
    """Best practices for GPT-Image-1 prompts."""
    
    @staticmethod
    def product_prompt_structure():
        return """
        1. Start with image type: "Professional product photography of..."
        2. Provide detailed product description
        3. List specific features to highlight
        4. Define visual style and mood
        5. Specify technical requirements (lighting, angle, background)
        6. Add brand-specific requirements
        7. Include any text or labels needed
        
        Example:
        'Professional product photography of [product].
         Features: [specific details about size, color, material, unique features].
         Style: [minimalist/luxury/technical/lifestyle].
         Lighting: [studio/natural/dramatic] with [specific lighting notes].
         Background: [pure white/gradient/environmental].
         Composition: [angle, framing, focus points].
         Additional: [any logos, text, or special requirements].'
        """
    
    @staticmethod
    def refinement_instruction_patterns():
        return {
            "adjust_element": "Adjust the {element} to be more {quality}",
            "add_detail": "Add {specific detail} to {location}",
            "change_style": "Transform the style to be more {new_style} while maintaining {preserve}",
            "fix_issue": "Correct the {issue} by {solution}",
            "enhance_quality": "Enhance the {aspect} to achieve {goal}",
            "iterate_variation": "Create a variation where {change} but keep {constant}"
        }
```

### 2. Session Management Best Practices

1. **Session Lifecycle**:
   - Always set expiration times on sessions
   - Clean up abandoned sessions regularly
   - Implement session recovery for interrupted workflows

2. **Performance Optimization**:
   - Cache frequently used prompts and configurations
   - Batch similar requests when possible
   - Use Redis for active session storage, PostgreSQL for archives

3. **Quality Control**:
   - Implement automated quality checks before human review
   - Track quality scores across sessions for optimization
   - Build feedback loops to improve prompt templates

### 3. Error Handling Strategies

```python
class ImageGenerationErrorHandler:
    """Comprehensive error handling for image generation."""
    
    @staticmethod
    async def handle_api_error(error: Exception, session: ImageGenerationSession):
        """Handle API-level errors."""
        
        if isinstance(error, RateLimitError):
            # Implement exponential backoff
            await implement_backoff_retry(session)
            
        elif isinstance(error, InvalidRequestError):
            # Log and notify for prompt adjustment
            await log_prompt_error(session, error)
            await notify_prompt_issue(session)
            
        elif isinstance(error, APIConnectionError):
            # Queue for retry
            await queue_for_retry(session)
            
    @staticmethod
    async def handle_quality_failure(session: ImageGenerationSession, max_attempts: int = 5):
        """Handle cases where quality threshold cannot be met."""
        
        if session.conversation_turns >= max_attempts:
            # Escalate to human review
            await create_quality_checkpoint(session)
            
        else:
            # Try alternative approach
            await apply_alternative_strategy(session)
```

---

## Error Handling and Recovery

### 1. Retry Logic

```python
class RetryableImageGeneration:
    """Implements retry logic for image generation."""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
    async def generate_with_retry(self, func, *args, **kwargs):
        """Execute image generation with retry logic."""
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await func(*args, **kwargs)
                
            except RateLimitError as e:
                wait_time = self.backoff_factor ** attempt
                await asyncio.sleep(wait_time)
                last_error = e
                
            except Exception as e:
                # Log error and determine if retryable
                if self._is_retryable(e):
                    last_error = e
                    continue
                else:
                    raise
                    
        raise MaxRetriesExceeded(f"Failed after {self.max_retries} attempts: {last_error}")
```

### 2. Session Recovery

```python
class SessionRecovery:
    """Handles recovery of interrupted sessions."""
    
    async def recover_session(self, session_id: str) -> Optional[ImageGenerationSession]:
        """Attempt to recover an interrupted session."""
        
        # Load session from persistent storage
        session = await load_session_from_db(session_id)
        
        if not session:
            return None
            
        # Validate session state
        if await self._is_session_recoverable(session):
            # Restore to Redis
            await store_session_in_redis(session)
            
            # Verify API state
            if session.current_response_id:
                # Verify we can continue from this response
                if await self._verify_response_continuity(session.current_response_id):
                    return session
                    
        # If not recoverable, create checkpoint for manual review
        await create_recovery_checkpoint(session)
        return None
```

---

## Performance Considerations

### 1. Caching Strategy

```python
class ImageGenerationCache:
    """Caching layer for image generation."""
    
    def __init__(self):
        self.prompt_cache = LRUCache(maxsize=1000)
        self.session_cache = TTLCache(maxsize=100, ttl=3600)
        
    async def get_or_generate(self, prompt_hash: str, generate_func):
        """Check cache before generating new image."""
        
        # Check if we have recent similar generation
        cached = self.prompt_cache.get(prompt_hash)
        
        if cached and self._is_cache_valid(cached):
            return cached
            
        # Generate new
        result = await generate_func()
        
        # Cache result
        self.prompt_cache[prompt_hash] = result
        
        return result
```

### 2. Batch Processing

```python
class BatchImageProcessor:
    """Handle batch image generation efficiently."""
    
    async def process_batch(self, requests: List[ImageRequest]) -> List[ImageResult]:
        """Process multiple image requests efficiently."""
        
        # Group similar requests
        grouped = self._group_similar_requests(requests)
        
        results = []
        
        for group in grouped:
            # Start sessions in parallel
            sessions = await asyncio.gather(*[
                self.start_session(req) for req in group
            ])
            
            # Process refinements in optimized order
            refined = await self._process_refinements_optimized(sessions)
            
            results.extend(refined)
            
        return results
```

---

## Monitoring and Analytics

### 1. Metrics Collection

```python
class ImageGenerationMetrics:
    """Track metrics for image generation."""
    
    def __init__(self):
        self.metrics = {
            "sessions_started": Counter(),
            "images_generated": Counter(), 
            "refinements_applied": Counter(),
            "quality_scores": Histogram(),
            "session_duration": Histogram(),
            "api_errors": Counter(),
            "cache_hits": Counter()
        }
        
    async def record_session_complete(self, session: ImageGenerationSession):
        """Record metrics for completed session."""
        
        self.metrics["sessions_started"].inc()
        self.metrics["images_generated"].inc(len(session.generated_images))
        self.metrics["refinements_applied"].inc(session.conversation_turns - 1)
        self.metrics["session_duration"].observe(
            (session.updated_at - session.created_at).total_seconds()
        )
        
        # Calculate average quality
        if session.generated_images:
            avg_quality = sum(img.quality_score for img in session.generated_images) / len(session.generated_images)
            self.metrics["quality_scores"].observe(avg_quality)
```

### 2. Performance Dashboard

```python
class ImageGenerationDashboard:
    """Dashboard data for image generation performance."""
    
    async def get_dashboard_data(self, product_id: str, timeframe: str = "7d"):
        """Get dashboard metrics for image generation."""
        
        return {
            "summary": {
                "total_sessions": await self.count_sessions(product_id, timeframe),
                "total_images": await self.count_images(product_id, timeframe),
                "avg_quality_score": await self.avg_quality(product_id, timeframe),
                "avg_refinements_per_session": await self.avg_refinements(product_id, timeframe)
            },
            "quality_distribution": await self.quality_distribution(product_id, timeframe),
            "popular_refinements": await self.top_refinements(product_id, timeframe),
            "session_outcomes": await self.session_outcomes(product_id, timeframe),
            "cost_analysis": {
                "total_api_cost": await self.calculate_api_cost(product_id, timeframe),
                "cost_per_final_image": await self.cost_per_image(product_id, timeframe)
            }
        }
```

---

## Conclusion

This implementation leverages GPT-Image-1's Responses API to create a sophisticated image generation system that supports iterative refinement through natural language conversations. The multi-turn capability enables precise control over image generation, leading to higher quality outputs and better alignment with brand requirements.

Key advantages:
1. **Iterative Refinement**: Natural language instructions for precise adjustments
2. **Context Preservation**: Maintains conversation history for coherent modifications  
3. **Quality Control**: Automated checks with human-in-the-loop approval
4. **Flexibility**: Customizable prompts and workflows per product
5. **Scalability**: Efficient session management and caching strategies

The system integrates seamlessly with the broader product lifecycle management platform while maintaining the flexibility to evolve with new capabilities as they become available.