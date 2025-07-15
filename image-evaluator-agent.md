# Image Evaluator Agent Implementation

## Executive Summary

The Image Evaluator Agent automates the quality control process by comparing generated images against reference photos and either approving them or generating specific refinement instructions. This creates a closed-loop system with the Image Generation Agent, significantly reducing human intervention while ensuring high-quality outputs that match brand and product requirements.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Core Capabilities](#core-capabilities)
3. [Integration with Image Generation Agent](#integration-with-image-generation-agent)
4. [Implementation Details](#implementation-details)
5. [Evaluation Criteria](#evaluation-criteria)
6. [Workflow Examples](#workflow-examples)
7. [Configuration](#configuration)
8. [Performance and Cost Optimization](#performance-and-cost-optimization)

---

## Architecture Overview

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                   Image Evaluator Agent                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐    ┌──────────────────┐                │
│  │   Vision Model   │    │   Comparison     │                │
│  │   (GPT-4V/       │───▶│     Engine       │                │
│  │   Claude Vision) │    └──────────────────┘                │
│  └─────────────────┘             │                           │
│           │                      ▼                           │
│           │              ┌──────────────────┐                │
│           │              │   Evaluation     │                │
│           └─────────────▶│    Scorer        │                │
│                          └──────────────────┘                │
│                                  │                           │
│                                  ▼                           │
│  ┌─────────────────────────────────────────┐                │
│  │         Decision Engine                  │                │
│  │  • Approve (confidence > threshold)      │                │
│  │  • Refine (generate edit instructions)  │                │
│  │  • Escalate (human review needed)       │                │
│  └─────────────────────────────────────────┘                │
│                                  │                           │
│                                  ▼                           │
│  ┌─────────────────────────────────────────┐                │
│  │    Refinement Instruction Generator      │                │
│  │  • Specific, actionable instructions    │                │
│  │  • Prioritized by importance            │                │
│  │  • Context-aware suggestions            │                │
│  └─────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────┘
```

### Integration Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Reference  │     │   Generated  │     │  Evaluator   │
│    Image     │────▶│    Image     │────▶│    Agent     │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                  │
                           ┌──────────────────────┴───────────┐
                           │                                  │
                           ▼                                  ▼
                    ┌─────────────┐                   ┌──────────────┐
                    │  Approved   │                   │  Refinement  │
                    │   (Save)    │                   │ Instructions │
                    └─────────────┘                   └──────┬───────┘
                                                            │
                                                            ▼
                                                    ┌──────────────┐
                                                    │  Image Gen   │
                                                    │    Agent     │
                                                    │ (Continue    │
                                                    │ Conversation)│
                                                    └──────────────┘
```

---

## Core Capabilities

### 1. Visual Comparison

```python
class VisualComparisonEngine:
    """Compares reference and generated images using vision models."""
    
    def __init__(self):
        self.vision_model = self._init_vision_model()
        self.comparison_metrics = [
            self.compare_composition,
            self.compare_colors,
            self.compare_product_details,
            self.compare_brand_elements,
            self.compare_technical_quality
        ]
        
    async def compare_images(self, 
                           reference_image: str,
                           generated_image: str,
                           comparison_context: Dict) -> ComparisonResult:
        """Perform comprehensive comparison between images."""
        
        # Use vision model for detailed analysis
        analysis_prompt = self._build_comparison_prompt(comparison_context)
        
        vision_response = await self.vision_model.analyze(
            images=[reference_image, generated_image],
            prompt=analysis_prompt
        )
        
        # Extract structured comparison data
        comparison_data = self._parse_vision_response(vision_response)
        
        # Run specific metric comparisons
        metric_results = {}
        for metric_func in self.comparison_metrics:
            metric_results[metric_func.__name__] = await metric_func(
                reference_image, 
                generated_image,
                vision_response
            )
            
        return ComparisonResult(
            overall_similarity=comparison_data.similarity_score,
            differences=comparison_data.differences,
            metrics=metric_results,
            vision_analysis=vision_response
        )
```

### 2. Evaluation Scoring

```python
class EvaluationScorer:
    """Scores generated images based on multiple criteria."""
    
    def __init__(self, config: EvaluatorConfig):
        self.config = config
        self.scoring_weights = config.scoring_weights
        
    async def score_image(self, 
                         comparison_result: ComparisonResult,
                         product_requirements: ProductRequirements) -> EvaluationScore:
        """Calculate comprehensive evaluation score."""
        
        scores = {
            "visual_similarity": self._score_visual_similarity(comparison_result),
            "product_accuracy": self._score_product_accuracy(comparison_result, product_requirements),
            "brand_compliance": self._score_brand_compliance(comparison_result),
            "technical_quality": self._score_technical_quality(comparison_result),
            "composition_match": self._score_composition(comparison_result)
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[criterion] * self.scoring_weights[criterion]
            for criterion in scores
        )
        
        return EvaluationScore(
            overall=overall_score,
            breakdown=scores,
            passed=overall_score >= self.config.approval_threshold,
            confidence=self._calculate_confidence(scores)
        )
```

### 3. Refinement Instruction Generation

```python
class RefinementInstructionGenerator:
    """Generates specific instructions for image refinement."""
    
    def __init__(self):
        self.instruction_templates = self._load_instruction_templates()
        
    async def generate_instructions(self,
                                  comparison_result: ComparisonResult,
                                  evaluation_score: EvaluationScore) -> List[RefinementInstruction]:
        """Generate prioritized refinement instructions."""
        
        instructions = []
        
        # Analyze differences and low-scoring areas
        issues = self._identify_issues(comparison_result, evaluation_score)
        
        for issue in issues:
            instruction = self._create_instruction(issue)
            instructions.append(instruction)
            
        # Prioritize instructions
        prioritized = self._prioritize_instructions(instructions)
        
        # Limit to top N most important
        return prioritized[:self.config.max_instructions_per_round]
        
    def _create_instruction(self, issue: Issue) -> RefinementInstruction:
        """Create specific instruction for an issue."""
        
        template = self.instruction_templates.get(issue.type, self.default_template)
        
        instruction_text = template.format(
            element=issue.element,
            current_state=issue.current_state,
            desired_state=issue.desired_state,
            specific_action=issue.suggested_action
        )
        
        return RefinementInstruction(
            text=instruction_text,
            priority=issue.priority,
            issue_type=issue.type,
            expected_impact=issue.impact_score
        )
```

---

## Integration with Image Generation Agent

### 1. Automated Feedback Loop

```python
class ImageGenerationWithEvaluation:
    """Orchestrates image generation with automatic evaluation."""
    
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.image_agent = ImageGenerationAgent(product_id)
        self.evaluator_agent = ImageEvaluatorAgent(product_id)
        self.max_refinement_rounds = 5
        
    async def generate_with_auto_approval(self,
                                        reference_image: str,
                                        initial_prompt: str,
                                        requirements: ProductRequirements) -> ApprovedImage:
        """Generate image with automatic evaluation and refinement."""
        
        # Start image generation session
        session = await self.image_agent.conversation_manager.start_session(
            product_id=self.product_id,
            initial_prompt=initial_prompt
        )
        
        refinement_round = 0
        approved = False
        
        while not approved and refinement_round < self.max_refinement_rounds:
            # Get latest generated image
            latest_image = session.generated_images[-1]
            
            # Evaluate against reference
            evaluation = await self.evaluator_agent.evaluate(
                reference_image=reference_image,
                generated_image=latest_image.stored_url,
                requirements=requirements
            )
            
            if evaluation.approved:
                approved = True
                break
                
            # Generate refinement instructions
            instructions = await self.evaluator_agent.generate_refinements(evaluation)
            
            # Apply refinements
            for instruction in instructions:
                result = await self.image_agent.conversation_manager.continue_session(
                    session_id=session.session_id,
                    instruction=instruction.text
                )
                
            refinement_round += 1
            
        # Handle approval or escalation
        if approved:
            return await self._finalize_approved_image(session, evaluation)
        else:
            return await self._escalate_for_human_review(session, evaluation)
```

### 2. Session Integration

```python
class EvaluatorSessionExtension:
    """Extends image generation sessions with evaluation data."""
    
    @dataclass
    class EvaluationSession:
        session_id: str
        reference_image_id: str
        evaluations: List[EvaluationResult]
        refinement_history: List[RefinementRound]
        final_score: Optional[float]
        approval_status: str
        
    async def track_evaluation_progress(self,
                                      generation_session: ImageGenerationSession,
                                      evaluation_session: EvaluationSession):
        """Track evaluation progress alongside generation."""
        
        # Link sessions
        generation_session.evaluation_session_id = evaluation_session.session_id
        
        # Store evaluation data
        await self.store_evaluation_session(evaluation_session)
        
        # Update metrics
        await self.update_evaluation_metrics(evaluation_session)
```

---

## Implementation Details

### 1. Image Evaluator Agent Class

```python
class ImageEvaluatorAgent(BaseProductAgent):
    """Agent responsible for evaluating generated images against references."""
    
    def __init__(self, product_id: str, config: EvaluatorConfig):
        super().__init__(product_id, "image_evaluator")
        self.config = config
        self.comparison_engine = VisualComparisonEngine()
        self.scorer = EvaluationScorer(config)
        self.instruction_generator = RefinementInstructionGenerator()
        
        # Initialize vision model based on config
        self.vision_model = self._init_vision_model()
        
    async def evaluate(self,
                      reference_image: str,
                      generated_image: str,
                      requirements: ProductRequirements) -> EvaluationResult:
        """Evaluate generated image against reference."""
        
        # Perform visual comparison
        comparison = await self.comparison_engine.compare_images(
            reference_image=reference_image,
            generated_image=generated_image,
            comparison_context={
                "product_id": self.product_id,
                "requirements": requirements.dict(),
                "brand_guidelines": self.config.brand_guidelines
            }
        )
        
        # Score the comparison
        score = await self.scorer.score_image(comparison, requirements)
        
        # Make decision
        decision = self._make_decision(score)
        
        return EvaluationResult(
            comparison=comparison,
            score=score,
            decision=decision,
            approved=decision == "approve",
            confidence=score.confidence,
            timestamp=datetime.utcnow()
        )
        
    async def generate_refinements(self, 
                                 evaluation: EvaluationResult) -> List[RefinementInstruction]:
        """Generate specific refinement instructions based on evaluation."""
        
        if evaluation.approved:
            return []
            
        instructions = await self.instruction_generator.generate_instructions(
            comparison_result=evaluation.comparison,
            evaluation_score=evaluation.score
        )
        
        # Add context for better refinement
        contextualized = []
        for instruction in instructions:
            contextualized.append(self._add_context(instruction, evaluation))
            
        return contextualized
        
    def _init_vision_model(self):
        """Initialize vision model based on configuration."""
        
        if self.config.vision_model == "gpt-4-vision":
            return GPT4VisionModel(api_key=settings.OPENAI_API_KEY)
        elif self.config.vision_model == "claude-3-vision":
            return Claude3VisionModel(api_key=settings.ANTHROPIC_API_KEY)
        else:
            raise ValueError(f"Unsupported vision model: {self.config.vision_model}")
            
    def _make_decision(self, score: EvaluationScore) -> str:
        """Make approval decision based on score."""
        
        if score.overall >= self.config.approval_threshold:
            if score.confidence >= self.config.confidence_threshold:
                return "approve"
            else:
                return "approve_with_review"  # Approve but flag for human verification
                
        elif score.overall >= self.config.refinement_threshold:
            return "refine"
            
        else:
            return "escalate"  # Too far off, needs human intervention
```

### 2. Vision Model Integration

```python
class GPT4VisionModel:
    """GPT-4 Vision integration for image analysis."""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    async def analyze(self, images: List[str], prompt: str) -> VisionAnalysis:
        """Analyze images using GPT-4 Vision."""
        
        # Prepare messages with images
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    *[{"type": "image_url", "image_url": {"url": img}} for img in images]
                ]
            }
        ]
        
        response = await self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=1000
        )
        
        # Parse structured response
        analysis = self._parse_response(response.choices[0].message.content)
        
        return VisionAnalysis(
            raw_response=response,
            structured_data=analysis,
            model="gpt-4-vision"
        )
        
    def _parse_response(self, response_text: str) -> Dict:
        """Parse vision model response into structured data."""
        
        # Use structured parsing or JSON mode if available
        try:
            # Attempt to extract JSON if response is formatted
            import json
            return json.loads(response_text)
        except:
            # Fall back to text parsing
            return self._parse_text_response(response_text)
```

---

## Evaluation Criteria

### 1. Core Evaluation Metrics

```python
class EvaluationCriteria:
    """Defines evaluation criteria for image comparison."""
    
    VISUAL_SIMILARITY = {
        "composition": {
            "weight": 0.2,
            "aspects": ["framing", "angle", "zoom_level", "object_placement"]
        },
        "color_accuracy": {
            "weight": 0.15,
            "aspects": ["color_palette", "saturation", "brightness", "contrast"]
        },
        "lighting": {
            "weight": 0.15,
            "aspects": ["direction", "intensity", "shadows", "highlights"]
        }
    }
    
    PRODUCT_ACCURACY = {
        "product_details": {
            "weight": 0.25,
            "aspects": ["shape", "texture", "material", "features"]
        },
        "brand_elements": {
            "weight": 0.15,
            "aspects": ["logo", "colors", "style", "positioning"]
        }
    }
    
    TECHNICAL_QUALITY = {
        "resolution": {
            "weight": 0.05,
            "minimum": 1024,
            "preferred": 2048
        },
        "sharpness": {
            "weight": 0.05,
            "threshold": 0.8
        }
    }
```

### 2. Scoring Configuration

```python
class EvaluatorConfig(BaseModel):
    """Configuration for image evaluator agent."""
    
    # Model selection
    vision_model: str = "gpt-4-vision"  # or "claude-3-vision"
    
    # Scoring thresholds
    approval_threshold: float = 0.85
    refinement_threshold: float = 0.60
    confidence_threshold: float = 0.80
    
    # Scoring weights
    scoring_weights: Dict[str, float] = {
        "visual_similarity": 0.30,
        "product_accuracy": 0.40,
        "brand_compliance": 0.20,
        "technical_quality": 0.10
    }
    
    # Refinement settings
    max_refinement_rounds: int = 5
    max_instructions_per_round: int = 3
    
    # Brand guidelines
    brand_guidelines: Dict[str, Any] = {}
    
    # Evaluation prompts (customizable)
    evaluation_prompts: Dict[str, str] = {
        "comparison": """
        Compare these two images:
        1. Reference image (first image)
        2. Generated image (second image)
        
        Analyze the following aspects:
        - Overall visual similarity (0-100%)
        - Product accuracy and details
        - Composition and framing
        - Color accuracy
        - Lighting and shadows
        - Brand compliance
        
        Identify specific differences and suggest improvements.
        Format response as JSON with similarity_score, differences[], and suggestions[].
        """,
        
        "detailed_analysis": """
        Perform detailed analysis of the generated image compared to the reference.
        Focus on: {focus_areas}
        Requirements: {requirements}
        """
    }
```

---

## Workflow Examples

### Example 1: Automated Product Image Approval

```python
# Complete automated workflow
async def automated_product_image_workflow(product_id: str, reference_image: str):
    """End-to-end automated image generation with evaluation."""
    
    # Initialize agents
    gen_agent = ImageGenerationAgent(product_id)
    eval_agent = ImageEvaluatorAgent(product_id)
    
    # Load product requirements
    requirements = await load_product_requirements(product_id)
    
    # Generate initial image
    session = await gen_agent.start_session(
        initial_prompt=f"Product photography of {requirements.product_name}..."
    )
    
    # Evaluation loop
    for round in range(5):
        latest_image = session.generated_images[-1]
        
        # Evaluate
        evaluation = await eval_agent.evaluate(
            reference_image=reference_image,
            generated_image=latest_image.url,
            requirements=requirements
        )
        
        if evaluation.approved:
            # Save approved image
            await save_approved_image(latest_image, evaluation)
            return {"status": "approved", "image": latest_image, "rounds": round + 1}
            
        # Get refinement instructions
        refinements = await eval_agent.generate_refinements(evaluation)
        
        # Apply refinements
        for instruction in refinements:
            await gen_agent.refine_image(session.session_id, instruction.text)
            
    # Max rounds reached - escalate
    return {"status": "escalated", "reason": "max_rounds_exceeded"}
```

### Example 2: Specific Issue Detection and Refinement

```python
# Example evaluation result with specific issues
evaluation_result = {
    "score": {
        "overall": 0.72,
        "breakdown": {
            "visual_similarity": 0.85,
            "product_accuracy": 0.65,  # Low score
            "brand_compliance": 0.70,
            "technical_quality": 0.90
        }
    },
    "issues": [
        {
            "type": "product_detail",
            "element": "bottle_cap",
            "description": "Cap material appears metallic instead of bamboo",
            "severity": "high"
        },
        {
            "type": "color_mismatch",
            "element": "product_body",
            "description": "Body color is too dark compared to reference",
            "severity": "medium"
        }
    ]
}

# Generated refinement instructions
refinement_instructions = [
    "Change the bottle cap material to natural bamboo wood with visible grain texture",
    "Lighten the bottle body color to match the reference matte black finish",
    "Ensure the bamboo cap has the characteristic light brown color with natural variations"
]
```

---

## Performance and Cost Optimization

### 1. Efficient Vision Model Usage

```python
class OptimizedVisionAnalysis:
    """Optimized vision model usage for cost efficiency."""
    
    def __init__(self):
        self.cache = TTLCache(maxsize=100, ttl=3600)
        self.batch_size = 5
        
    async def analyze_with_caching(self, 
                                  reference_image: str,
                                  generated_image: str) -> VisionAnalysis:
        """Analyze with caching to reduce API calls."""
        
        # Generate cache key
        cache_key = self._generate_cache_key(reference_image, generated_image)
        
        # Check cache
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Perform analysis
        result = await self._perform_analysis(reference_image, generated_image)
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
        
    async def batch_analyze(self, image_pairs: List[Tuple[str, str]]) -> List[VisionAnalysis]:
        """Batch multiple comparisons for efficiency."""
        
        results = []
        
        for i in range(0, len(image_pairs), self.batch_size):
            batch = image_pairs[i:i + self.batch_size]
            batch_results = await self._analyze_batch(batch)
            results.extend(batch_results)
            
        return results
```

### 2. Selective Evaluation Strategy

```python
class SelectiveEvaluator:
    """Implements selective evaluation to reduce costs."""
    
    def __init__(self, config: SelectiveEvaluationConfig):
        self.config = config
        self.quick_check_threshold = config.quick_check_threshold
        
    async def should_deep_evaluate(self, 
                                 generated_image: str,
                                 quick_metrics: Dict) -> bool:
        """Determine if deep evaluation is needed."""
        
        # Quick checks using basic computer vision
        if quick_metrics["technical_quality"] < self.quick_check_threshold:
            return True  # Definitely needs evaluation
            
        # Check if image matches basic requirements
        if not self._passes_basic_requirements(quick_metrics):
            return True
            
        # Random sampling for quality assurance
        if random.random() < self.config.sampling_rate:
            return True
            
        return False
        
    def _passes_basic_requirements(self, metrics: Dict) -> bool:
        """Check basic requirements without vision model."""
        
        return all([
            metrics["resolution"] >= self.config.min_resolution,
            metrics["aspect_ratio"] == self.config.required_aspect_ratio,
            metrics["file_size"] < self.config.max_file_size
        ])
```

### 3. Progressive Evaluation

```python
class ProgressiveEvaluator:
    """Implements progressive evaluation for efficiency."""
    
    async def evaluate_progressive(self,
                                 reference_image: str,
                                 generated_image: str) -> EvaluationResult:
        """Progressively evaluate from cheap to expensive checks."""
        
        # Level 1: Basic technical checks (fast, cheap)
        technical_check = await self.check_technical_quality(generated_image)
        if not technical_check.passed:
            return self._quick_reject(technical_check)
            
        # Level 2: Basic visual similarity (medium cost)
        basic_similarity = await self.check_basic_similarity(reference_image, generated_image)
        if basic_similarity.score < 0.5:
            return self._early_refinement(basic_similarity)
            
        # Level 3: Full vision model evaluation (expensive)
        full_evaluation = await self.full_vision_evaluation(reference_image, generated_image)
        
        return full_evaluation
```

---

## Storage Architecture Integration

### Image Storage Strategy

```python
class EvaluatorStorageStrategy:
    """Storage strategy optimized for evaluation workflow."""
    
    def __init__(self, storage_backend: StorageBackend):
        self.storage = storage_backend
        
    async def store_evaluation_images(self, evaluation_session: EvaluationSession):
        """Store only necessary images from evaluation."""
        
        # Store reference image (if not already stored)
        reference_url = await self.storage.store_reference(
            image=evaluation_session.reference_image,
            product_id=evaluation_session.product_id,
            metadata={
                "type": "reference",
                "uploaded_by": evaluation_session.user_id,
                "uploaded_at": datetime.utcnow()
            }
        )
        
        # Store ONLY the final approved image
        if evaluation_session.approved_image:
            final_url = await self.storage.store_final(
                image=evaluation_session.approved_image,
                product_id=evaluation_session.product_id,
                metadata={
                    "type": "generated_final",
                    "reference_image": reference_url,
                    "generation_session": evaluation_session.generation_session_id,
                    "evaluation_score": evaluation_session.final_score,
                    "approved_at": datetime.utcnow()
                }
            )
            
        # Clean up intermediate images
        await self._cleanup_intermediate_images(evaluation_session)
        
    async def _cleanup_intermediate_images(self, session: EvaluationSession):
        """Remove intermediate images to save storage costs."""
        
        # Delete all non-approved generated images
        for image in session.intermediate_images:
            await self.storage.delete_temporary(image.temp_url)
```

---

## Configuration Examples

### 1. Strict Quality Configuration

```python
strict_config = EvaluatorConfig(
    vision_model="gpt-4-vision",
    approval_threshold=0.90,
    refinement_threshold=0.70,
    confidence_threshold=0.85,
    scoring_weights={
        "visual_similarity": 0.25,
        "product_accuracy": 0.45,  # Higher weight on accuracy
        "brand_compliance": 0.25,
        "technical_quality": 0.05
    },
    max_refinement_rounds=7,
    max_instructions_per_round=2
)
```

### 2. Fast Iteration Configuration

```python
fast_config = EvaluatorConfig(
    vision_model="gpt-4-vision",
    approval_threshold=0.80,
    refinement_threshold=0.60,
    confidence_threshold=0.75,
    scoring_weights={
        "visual_similarity": 0.40,  # Focus on overall look
        "product_accuracy": 0.30,
        "brand_compliance": 0.20,
        "technical_quality": 0.10
    },
    max_refinement_rounds=3,
    max_instructions_per_round=3
)
```

---

## Metrics and Monitoring

```python
class EvaluatorMetrics:
    """Track evaluator performance metrics."""
    
    def __init__(self):
        self.metrics = {
            "evaluations_total": Counter(),
            "approvals": Counter(),
            "refinements": Counter(),
            "escalations": Counter(),
            "avg_rounds_to_approval": Histogram(),
            "evaluation_time": Histogram(),
            "vision_api_calls": Counter(),
            "vision_api_cost": Counter()
        }
        
    async def record_evaluation_complete(self, session: EvaluationSession):
        """Record metrics for completed evaluation."""
        
        self.metrics["evaluations_total"].inc()
        
        if session.approved:
            self.metrics["approvals"].inc()
            self.metrics["avg_rounds_to_approval"].observe(session.refinement_rounds)
        elif session.escalated:
            self.metrics["escalations"].inc()
            
        self.metrics["evaluation_time"].observe(session.duration_seconds)
        self.metrics["vision_api_calls"].inc(session.api_calls_made)
        self.metrics["vision_api_cost"].inc(session.estimated_cost)
```

---

## Conclusion

The Image Evaluator Agent creates an intelligent quality control system that dramatically reduces the need for human intervention in the image generation process. By comparing generated images against references and providing specific refinement instructions, it enables a closed-loop system that consistently produces high-quality, brand-compliant images.

Key benefits:
1. **Automation**: Reduces manual review from 100% to <10% of images
2. **Consistency**: Ensures all images meet quality standards
3. **Speed**: Automated refinement cycles complete in minutes vs hours
4. **Cost Efficiency**: Optimized vision model usage and storage
5. **Scalability**: Handles multiple products and images concurrently

The integration with the Image Generation Agent creates a powerful system for autonomous product image creation that maintains high quality while minimizing costs.