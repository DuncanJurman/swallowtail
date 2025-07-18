# Image Generation Agent Implementation with OpenAI images.edit

## Executive Summary

This document outlines the implementation strategy for the Image Generation Agent using OpenAI's `images.edit` endpoint. This approach allows direct reference image input, enabling high-quality product image generation based on existing product photos. The system integrates with the Image Evaluator Agent to create an automated quality control loop.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [API Integration](#api-integration)
3. [Implementation Details](#implementation-details)
4. [Prompt Optimization](#prompt-optimization)
5. [Workflow Integration](#workflow-integration)
6. [Storage Strategy](#storage-strategy)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Performance Considerations](#performance-considerations)

---

## Architecture Overview

### Key Advantages
1. **Direct Reference Input**: Pass product photos directly to generate variations
2. **Simplified Architecture**: No complex conversation state management
3. **Better Control**: Image-to-image generation with text prompts
4. **Cost Efficiency**: Single API call per attempt vs. multi-turn conversations
5. **Reproducibility**: Easier to reproduce results with fixed inputs

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Image Generation Agent                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌──────────────────┐                │
│  │ Reference Image │    │  Prompt Engine   │                │
│  │    Manager      │───►│                  │                │
│  └─────────────────┘    └──────────────────┘                │
│           │                      │                           │
│           ▼                      ▼                           │
│  ┌─────────────────────────────────────────┐                │
│  │      OpenAI images.edit API              │                │
│  │  • Reference image input                 │                │
│  │  • Text prompt guidance                  │                │
│  │  • Quality & size parameters             │                │
│  └─────────────────────────────────────────┘                │
│                      │                                       │
│                      ▼                                       │
│  ┌─────────────────────────────────────────┐                │
│  │         Generation Tracker               │                │
│  │  • Attempt tracking                      │                │
│  │  • Prompt history                        │                │
│  │  • Quality scores                        │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

---

## API Integration

### 1. OpenAI images.edit Client

```python
from openai import OpenAI
import base64
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import io
from PIL import Image

@dataclass
class ImageGenerationResult:
    """Result from image generation attempt."""
    attempt_id: str
    prompt_used: str
    image_data: bytes
    image_url: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime
    quality_settings: Dict[str, Any]

class ImageGenerationClient:
    """Client for OpenAI images.edit endpoint."""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-image-1"
        
    async def generate_from_reference(self,
                                    reference_images: List[bytes],
                                    prompt: str,
                                    quality_params: Optional[Dict] = None) -> ImageGenerationResult:
        """Generate new image based on reference(s) and prompt."""
        
        # Default quality parameters
        params = {
            "size": "1024x1024",
            "quality": "high",
            "format": "png",
            "background": "transparent"
        }
        
        if quality_params:
            params.update(quality_params)
            
        # Prepare reference images
        image_files = []
        for img_data in reference_images:
            image_files.append(io.BytesIO(img_data))
            
        # Call API
        try:
            result = self.client.images.edit(
                model=self.model,
                image=image_files,
                prompt=prompt,
                **params
            )
            
            # Extract result
            image_base64 = result.data[0].b64_json
            image_bytes = base64.b64decode(image_base64)
            
            return ImageGenerationResult(
                attempt_id=generate_attempt_id(),
                prompt_used=prompt,
                image_data=image_bytes,
                image_url=None,  # Will be set after storage
                metadata={
                    "model": self.model,
                    "reference_count": len(reference_images),
                    "api_response": result.model_dump()
                },
                created_at=datetime.utcnow(),
                quality_settings=params
            )
            
        finally:
            # Clean up file objects
            for f in image_files:
                f.close()
```

### 2. Reference Image Handler

```python
class ReferenceImageHandler:
    """Manages reference images for generation."""
    
    def __init__(self, storage_service: SupabaseStorageService):
        self.storage = storage_service
        
    async def prepare_reference_images(self, 
                                     product_id: str,
                                     reference_urls: List[str]) -> List[bytes]:
        """Download and prepare reference images."""
        
        images = []
        for url in reference_urls:
            # Download image
            image_data = await self.storage.download_image(url)
            
            # Validate and potentially resize
            processed = await self._process_reference_image(image_data)
            images.append(processed)
            
        return images
        
    async def _process_reference_image(self, image_data: bytes) -> bytes:
        """Process reference image for optimal API usage."""
        
        img = Image.open(io.BytesIO(image_data))
        
        # Resize if too large (to reduce API costs)
        max_size = 2048
        if img.width > max_size or img.height > max_size:
            img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
            
        # Save to bytes
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=True)
        return buffer.getvalue()
```

---

## Implementation Details

### 1. Image Generation Agent Class

```python
class ImageGenerationAgent(BaseProductAgent):
    """Agent responsible for product image generation using reference images."""
    
    def __init__(self, product_id: str, config: ImageAgentConfig):
        super().__init__(product_id, "image_generation")
        self.config = config
        self.client = ImageGenerationClient(settings.OPENAI_API_KEY)
        self.reference_handler = ReferenceImageHandler(get_storage_service())
        self.prompt_optimizer = PromptOptimizer(config)
        self.tracker = GenerationTracker()
        
    async def generate_product_images(self, 
                                    reference_images: List[str],
                                    product_data: ProductData) -> GenerationSession:
        """Generate product images based on references."""
        
        session = GenerationSession(
            session_id=generate_session_id(),
            product_id=self.product_id,
            reference_images=reference_images,
            product_data=product_data
        )
        
        # Prepare reference images
        ref_image_data = await self.reference_handler.prepare_reference_images(
            self.product_id, 
            reference_images
        )
        
        # Generate main product image
        main_result = await self._generate_main_image(
            ref_image_data,
            product_data,
            session
        )
        session.add_result(main_result)
        
        # Generate lifestyle variations if configured
        if self.config.generate_lifestyle:
            for environment in self.config.lifestyle_environments:
                lifestyle_result = await self._generate_lifestyle_image(
                    ref_image_data,
                    product_data,
                    environment,
                    session
                )
                session.add_result(lifestyle_result)
                
        return session
        
    async def _generate_main_image(self,
                                 reference_images: List[bytes],
                                 product_data: ProductData,
                                 session: GenerationSession) -> ImageGenerationResult:
        """Generate main product image."""
        
        # Build optimized prompt
        prompt = self.prompt_optimizer.build_product_prompt(
            product_data,
            style="main_product",
            additional_context={
                "background": self.config.main_image_background,
                "lighting": self.config.main_image_lighting,
                "composition": self.config.main_image_composition
            }
        )
        
        # Generate image
        result = await self.client.generate_from_reference(
            reference_images=reference_images,
            prompt=prompt,
            quality_params={
                "size": self.config.main_image_size,
                "quality": "high",
                "format": self.config.output_format
            }
        )
        
        # Track attempt
        await self.tracker.track_attempt(session.session_id, result)
        
        return result
        
    async def regenerate_with_feedback(self,
                                     session_id: str,
                                     evaluation_feedback: EvaluationFeedback) -> ImageGenerationResult:
        """Regenerate image based on evaluation feedback."""
        
        # Retrieve session
        session = await self.tracker.get_session(session_id)
        
        # Get reference images
        ref_images = await self.reference_handler.prepare_reference_images(
            session.product_id,
            session.reference_images
        )
        
        # Optimize prompt based on feedback
        improved_prompt = self.prompt_optimizer.improve_prompt(
            original_prompt=session.last_prompt,
            feedback=evaluation_feedback,
            product_data=session.product_data
        )
        
        # Generate with improved prompt
        result = await self.client.generate_from_reference(
            reference_images=ref_images,
            prompt=improved_prompt,
            quality_params=session.quality_params
        )
        
        # Track attempt
        await self.tracker.track_attempt(session_id, result)
        
        return result
```

### 2. Generation Tracking

```python
class GenerationTracker:
    """Tracks image generation attempts and sessions."""
    
    def __init__(self, db_session):
        self.db = db_session
        
    async def create_session(self, session: GenerationSession) -> str:
        """Create new generation session."""
        
        await self.db.execute("""
            INSERT INTO image_generation_sessions
            (session_id, product_id, reference_images, status, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, session.session_id, session.product_id, 
            json.dumps(session.reference_images), "active", datetime.utcnow())
        
        return session.session_id
        
    async def track_attempt(self, session_id: str, result: ImageGenerationResult):
        """Track generation attempt."""
        
        await self.db.execute("""
            INSERT INTO generation_attempts
            (attempt_id, session_id, prompt_used, quality_settings, 
             created_at, metadata)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, result.attempt_id, session_id, result.prompt_used,
            json.dumps(result.quality_settings), result.created_at,
            json.dumps(result.metadata))
            
    async def get_session_history(self, session_id: str) -> List[Dict]:
        """Get all attempts for a session."""
        
        return await self.db.fetch_all("""
            SELECT * FROM generation_attempts
            WHERE session_id = $1
            ORDER BY created_at ASC
        """, session_id)
```

---

## Prompt Optimization

### 1. Prompt Optimizer

```python
class PromptOptimizer:
    """Optimizes prompts based on product data and feedback."""
    
    def __init__(self, config: ImageAgentConfig):
        self.config = config
        self.templates = self._load_prompt_templates()
        
    def build_product_prompt(self,
                           product_data: ProductData,
                           style: str = "main_product",
                           additional_context: Dict = None) -> str:
        """Build optimized prompt for product image generation."""
        
        template = self.templates.get(style, self.templates["default"])
        
        # Core product details
        prompt_parts = [
            template["base"].format(
                product_name=product_data.name,
                product_type=product_data.category
            )
        ]
        
        # Add key features
        if product_data.features:
            features_text = f"Key features: {', '.join(product_data.features[:5])}"
            prompt_parts.append(features_text)
            
        # Add style requirements
        if style == "main_product":
            prompt_parts.extend([
                f"Style: {self.config.visual_style}",
                f"Background: {additional_context.get('background', 'pure white')}",
                f"Lighting: {additional_context.get('lighting', 'professional studio')}",
                f"Composition: {additional_context.get('composition', 'centered, full product visible')}"
            ])
            
        # Add brand guidelines
        if self.config.brand_guidelines:
            prompt_parts.append(f"Brand style: {self.config.brand_guidelines.tone}")
            
        # Add technical requirements
        prompt_parts.extend([
            "High quality, professional product photography",
            "Sharp focus, clear details",
            "Consistent with reference image style"
        ])
        
        return "\n".join(prompt_parts)
        
    def improve_prompt(self,
                      original_prompt: str,
                      feedback: EvaluationFeedback,
                      product_data: ProductData) -> str:
        """Improve prompt based on evaluation feedback."""
        
        improvements = []
        
        # Analyze feedback issues
        for issue in feedback.issues:
            if issue.type == "color_mismatch":
                improvements.append(f"Ensure {issue.element} matches the exact color from reference: {issue.target_value}")
            elif issue.type == "detail_missing":
                improvements.append(f"Include {issue.element} as shown in reference image")
            elif issue.type == "composition_error":
                improvements.append(f"Adjust composition: {issue.suggestion}")
            elif issue.type == "lighting_issue":
                improvements.append(f"Lighting should be {issue.target_value}")
                
        # Build improved prompt
        improved_parts = [original_prompt]
        
        if improvements:
            improved_parts.append("\nIMPORTANT CORRECTIONS:")
            improved_parts.extend(improvements)
            
        # Add emphasis on accuracy
        improved_parts.append("\nMatch the reference image style and details exactly.")
        
        return "\n".join(improved_parts)
```

### 2. Prompt Templates

```python
DEFAULT_PROMPT_TEMPLATES = {
    "main_product": {
        "base": "Generate a professional product photo of {product_name} ({product_type})",
        "modifiers": [
            "studio lighting",
            "clean background",
            "high resolution",
            "commercial quality"
        ]
    },
    "lifestyle": {
        "base": "Create a lifestyle photo showing {product_name} in {environment}",
        "modifiers": [
            "natural setting",
            "authentic usage",
            "appealing composition"
        ]
    },
    "detail_shot": {
        "base": "Close-up detail shot of {product_name} highlighting {feature}",
        "modifiers": [
            "macro photography style",
            "sharp focus on details",
            "blurred background"
        ]
    }
}
```

---

## Workflow Integration

### 1. Automated Generation with Evaluation

```python
class ImageGenerationWorkflow:
    """Orchestrates image generation with automatic evaluation."""
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.gen_agent = ImageGenerationAgent(product_id, load_config(product_id))
        self.eval_agent = ImageEvaluatorAgent(product_id)
        self.storage = SupabaseStorageService()
        self.max_attempts = 5
        
    async def generate_with_approval(self,
                                   reference_images: List[str],
                                   product_data: ProductData,
                                   requirements: ProductRequirements) -> ApprovedImageResult:
        """Generate images with automatic evaluation loop."""
        
        # Store reference images
        stored_refs = []
        for ref in reference_images:
            url = await self.storage.upload_reference_image(
                product_id=self.product_id,
                image_data=ref,
                metadata={"type": "reference", "product_id": self.product_id}
            )
            stored_refs.append(url)
            
        # Start generation session
        session = await self.gen_agent.generate_product_images(
            reference_images=stored_refs,
            product_data=product_data
        )
        
        # Evaluation loop
        approved = False
        attempts = 0
        
        while not approved and attempts < self.max_attempts:
            latest_result = session.latest_result
            
            # Evaluate generated image
            evaluation = await self.eval_agent.evaluate(
                reference_image=stored_refs[0],  # Primary reference
                generated_image_data=latest_result.image_data,
                requirements=requirements
            )
            
            if evaluation.approved:
                approved = True
                # Store final approved image
                final_url = await self.storage.upload_generated_image(
                    product_id=self.product_id,
                    session_id=session.session_id,
                    image_data=latest_result.image_data,
                    image_type="main_product",
                    metadata={
                        "approved": True,
                        "evaluation_score": evaluation.score.overall,
                        "attempts": attempts + 1
                    }
                )
                break
                
            # Generate new attempt with feedback
            new_result = await self.gen_agent.regenerate_with_feedback(
                session_id=session.session_id,
                evaluation_feedback=evaluation.feedback
            )
            session.add_result(new_result)
            
            attempts += 1
            
        # Handle result
        if approved:
            return ApprovedImageResult(
                success=True,
                final_image_url=final_url,
                session_id=session.session_id,
                attempts=attempts,
                final_score=evaluation.score.overall
            )
        else:
            # Create checkpoint for human review
            checkpoint = await self.create_human_checkpoint(session, evaluation)
            return ApprovedImageResult(
                success=False,
                checkpoint_id=checkpoint.id,
                reason="max_attempts_exceeded",
                best_attempt=session.best_result
            )
```

### 2. Batch Processing

```python
class BatchImageGenerator:
    """Handle batch image generation for multiple products."""
    
    async def process_batch(self, batch_requests: List[ImageGenerationRequest]) -> List[GenerationResult]:
        """Process multiple image generation requests efficiently."""
        
        results = []
        
        # Group by similar requirements for potential optimization
        grouped = self._group_similar_requests(batch_requests)
        
        for group in grouped:
            # Process group concurrently
            group_results = await asyncio.gather(*[
                self._process_single_request(req) for req in group
            ])
            results.extend(group_results)
            
        return results
```

---

## Storage Strategy

### 1. Optimized Storage

```python
class ImageStorageOptimizer:
    """Optimizes storage to minimize costs."""
    
    def __init__(self, storage_backend: SupabaseStorageService):
        self.storage = storage_backend
        
    async def store_generation_result(self,
                                    session: GenerationSession,
                                    result: ImageGenerationResult,
                                    approved: bool) -> Optional[str]:
        """Store image only if approved or for temporary evaluation."""
        
        if approved:
            # Store permanently
            return await self.storage.upload_generated_image(
                product_id=session.product_id,
                session_id=session.session_id,
                image_data=result.image_data,
                image_type="final",
                metadata={
                    "approved": True,
                    "prompt": result.prompt_used,
                    "attempt_number": session.attempt_count
                }
            )
        else:
            # Store temporarily for evaluation (auto-cleanup after 24h)
            return await self.storage.upload_temp_image(
                image_data=result.image_data,
                ttl_hours=24,
                metadata={
                    "session_id": session.session_id,
                    "attempt_id": result.attempt_id
                }
            )
```

---

## Configuration

### 1. Agent Configuration

```python
class ImageAgentConfig(BaseModel):
    """Configuration for image generation agent."""
    
    # API settings
    model: str = "gpt-image-1"
    max_attempts: int = 5
    
    # Image quality settings
    main_image_size: str = "1024x1024"
    output_format: str = "png"
    quality: str = "high"
    enable_transparency: bool = True
    
    # Generation settings
    generate_lifestyle: bool = True
    lifestyle_environments: List[str] = ["home", "office", "outdoor"]
    generate_variations: int = 0  # Number of variations per image
    
    # Style configuration
    visual_style: str = "professional product photography"
    main_image_background: str = "pure white"
    main_image_lighting: str = "studio lighting with soft shadows"
    main_image_composition: str = "centered, full product visible"
    
    # Brand guidelines
    brand_guidelines: Optional[BrandGuidelines] = None
    
    # Optimization
    compress_output: bool = True
    compression_level: int = 85  # For JPEG/WebP
    
    # Prompt templates (customizable)
    prompt_templates: Dict[str, Dict] = DEFAULT_PROMPT_TEMPLATES
```

---

## Error Handling

### 1. Retry Logic

```python
class ImageGenerationRetry:
    """Handles retries for failed generation attempts."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        
    async def generate_with_retry(self, 
                                generation_func,
                                *args, 
                                **kwargs) -> ImageGenerationResult:
        """Execute generation with retry logic."""
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return await generation_func(*args, **kwargs)
                
            except RateLimitError as e:
                # Exponential backoff for rate limits
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
                last_error = e
                
            except InvalidRequestError as e:
                # Don't retry invalid requests
                raise
                
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(1)
                    
        raise GenerationFailedError(f"Failed after {self.max_retries} attempts: {last_error}")
```

---

## Performance Considerations

### 1. Cost Optimization

```python
class CostOptimizer:
    """Optimizes API usage for cost efficiency."""
    
    def calculate_optimal_settings(self, requirements: Dict) -> Dict:
        """Calculate optimal quality settings based on requirements."""
        
        settings = {}
        
        # Size optimization
        if requirements.get("usage") == "thumbnail":
            settings["size"] = "512x512"
            settings["quality"] = "medium"
        elif requirements.get("usage") == "web":
            settings["size"] = "1024x1024"
            settings["quality"] = "high"
        else:  # Full quality
            settings["size"] = "1536x1024"
            settings["quality"] = "high"
            
        # Format optimization
        if requirements.get("needs_transparency"):
            settings["format"] = "png"
        else:
            settings["format"] = "jpeg"
            settings["compression"] = 85
            
        return settings
```

### 2. Monitoring

```python
class GenerationMetrics:
    """Track generation performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "generations_total": Counter(),
            "generations_approved": Counter(),
            "average_attempts": Histogram(),
            "generation_time": Histogram(),
            "api_cost_estimate": Counter()
        }
        
    async def record_generation(self, session: GenerationSession):
        """Record metrics for generation session."""
        
        self.metrics["generations_total"].inc()
        
        if session.approved:
            self.metrics["generations_approved"].inc()
            
        self.metrics["average_attempts"].observe(session.attempt_count)
        self.metrics["generation_time"].observe(session.duration_seconds)
        
        # Estimate cost (rough approximation)
        cost = session.attempt_count * 0.04  # ~$0.04 per image
        self.metrics["api_cost_estimate"].inc(cost)
```

---

## Conclusion

This implementation leverages OpenAI's `images.edit` endpoint to create a streamlined image generation system that:

1. **Uses reference images directly** - Better control over output quality
2. **Simplifies architecture** - No complex conversation management
3. **Optimizes costs** - Single API call per attempt
4. **Integrates seamlessly** - Works with evaluator agent for quality control
5. **Scales efficiently** - Batch processing and smart storage

The system focuses on generating high-quality product images that match reference photos while allowing for style variations through prompt engineering.