"""Image Evaluation Crew using CrewAI architecture."""

import logging
from typing import Any, Dict, Optional
from datetime import datetime, timezone

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

from ..core.config import get_settings
from ..models.evaluation import ImageEvaluationOutput


@CrewBase
class ImageEvaluationCrew():
    """Crew for evaluating generated product images against reference images."""
    
    # YAML config paths relative to this file
    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'
    
    def __init__(
        self,
        reference_url: str,
        generated_path: str,
        product_name: str = "Product",
        threshold: float = 0.85
    ):
        """Initialize with evaluation parameters."""
        self.settings = get_settings()
        # Process file:// URLs to absolute paths for better compatibility
        self.reference_url = self._process_file_url(reference_url)
        self.generated_path = self._process_file_url(generated_path)
        self.product_name = product_name
        self.threshold = threshold
        self.logger = logging.getLogger(f"ImageEvaluationCrew[{product_name}]")
    
    def _process_file_url(self, url: str) -> str:
        """Convert file:// URLs to absolute paths for AddImageTool compatibility."""
        if url.startswith('file://'):
            # Remove file:// prefix for better tool compatibility
            return url.replace('file://', '')
        return url
    
    @agent
    def image_evaluator(self) -> Agent:
        """Image evaluation specialist with multimodal vision."""
        # Create multimodal LLM for evaluation
        multimodal_llm = LLM(
            model="gpt-4o",  # GPT-4 with vision capabilities
            temperature=0.3,  # Lower temperature for consistent evaluation
            max_tokens=4000
        )
        
        return Agent(
            config=self.agents_config['image_evaluator'],  # type: ignore[index]
            llm=multimodal_llm,
            verbose=True,
            multimodal=True  # Enable multimodal capabilities - automatically includes AddImageTool
        )
    
    @task
    def evaluate_image_task(self) -> Task:
        """Task to evaluate generated image quality."""
        return Task(
            description=f"""Evaluate whether the generated image correctly represents the SAME product as shown in the reference image.

Reference image: {self.reference_url}
Generated image: {self.generated_path}

CRITICAL CONTEXT: You are evaluating AI-generated product images for e-commerce. The generated image was created using the reference image and a text prompt. Your job is to ensure:
1. The generated image shows the EXACT SAME PRODUCT as the reference (not just similar category)
2. The product features, shape, and identity are preserved
3. The generation prompt was followed while maintaining product accuracy

IMPORTANT SCORING RULES:
- If the generated image shows a DIFFERENT product than the reference, product_accuracy_score should be 0-20
- If products are completely different (e.g., Squirtle vs Mew, red shirt vs blue shirt), overall_score should be < 50
- High scores (80+) are ONLY for images showing the SAME product with good quality

Approval threshold: {self.threshold * 100}%

Your evaluation process:
1. Use the AddImageTool to examine both images
2. FIRST determine: Are these the SAME product or DIFFERENT products?
3. Score each category from 0-100:
   - Visual fidelity: Style and mood consistency (but ONLY if same product)
   - Product accuracy: Is this the EXACT SAME product? (0-20 if different product)
   - Technical quality: Image sharpness, lighting, composition
   - Professional appearance: Overall polish and presentation
   - E-commerce suitability: Would customers recognize this as the same product?
4. Calculate overall score (weighted average, heavily penalize different products)
5. Set approved=true ONLY if overall_score >= {self.threshold * 100} AND same product
6. Provide specific feedback on what needs to change
7. List strengths and weaknesses
8. Indicate confidence level (High/Medium/Low)

Remember: Different products should NEVER pass, regardless of image quality!""",
            expected_output="""A structured evaluation with all required fields:
- overall_score: The weighted average score (0-100) - MUST be < 50 if different products
- visual_fidelity_score: How well style/mood matches (0-100) - only high if same product
- product_accuracy_score: Is this the SAME product? (0-20 for different products, 80-100 for same)
- technical_quality_score: Image sharpness, lighting, composition (0-100)
- professional_appearance_score: Professional look (0-100)
- ecommerce_suitability_score: Customer product recognition (0-100) - low if different product
- approved: true ONLY if overall_score >= {self.threshold * 100} AND products match
- feedback: List of specific improvements (MUST mention if products don't match)
- confidence: Your confidence level (High/Medium/Low)
- strengths: List of image strengths
- weaknesses: List of image weaknesses (MUST include "different product" if applicable)""",
            agent=self.image_evaluator(),
            output_pydantic=ImageEvaluationOutput
        )
    
    @crew
    def crew(self) -> Crew:
        """Create the evaluation crew."""
        return Crew(
            agents=self.agents,  # Automatically includes all @agent methods
            tasks=self.tasks,    # Automatically includes all @task methods
            process=Process.sequential,
            verbose=True,
            memory=False,  # No memory needed for single evaluation
            planning=False  # No planning needed for single task
        )
    
    def evaluate(self) -> Dict[str, Any]:
        """Execute the evaluation synchronously."""
        self.logger.info(f"Starting image evaluation for {self.product_name}")
        
        # Debug logging for image URLs
        self.logger.debug(f"Reference URL: {self.reference_url}")
        self.logger.debug(f"Generated Path: {self.generated_path}")
        self.logger.debug(f"Threshold: {self.threshold * 100}%")
        
        # Check if comparing identical images
        if self.reference_url == self.generated_path:
            self.logger.warning("Reference and generated images are identical - expecting high scores")
        
        inputs = {
            "reference_url": self.reference_url,
            "generated_path": self.generated_path,
            "product_name": self.product_name,
            "threshold": self.threshold
        }
        
        try:
            self.logger.debug("Executing crew kickoff...")
            result = self.crew().kickoff(inputs=inputs)
            
            # Log raw result information
            self.logger.debug(f"Result type: {type(result)}")
            self.logger.debug(f"Has pydantic: {hasattr(result, 'pydantic')}")
            self.logger.debug(f"Has raw: {hasattr(result, 'raw')}")
            
            if hasattr(result, 'raw'):
                raw_output = result.raw
                self.logger.debug(f"Raw output length: {len(raw_output)}")
                self.logger.debug(f"Raw output preview (first 1000 chars): {raw_output[:1000]}...")
                
                # Check if agent mentioned seeing images
                saw_images = any(phrase in raw_output.lower() for phrase in [
                    "i can see", "i see", "looking at", "examining", "viewing",
                    "both images", "reference image", "generated image", "observ"
                ])
                self.logger.info(f"Agent appears to have seen images: {saw_images}")
                
                # Check for error indicators
                error_indicators = any(phrase in raw_output.lower() for phrase in [
                    "unable to", "cannot access", "can't see", "error", "failed",
                    "not accessible", "404", "not found"
                ])
                if error_indicators:
                    self.logger.warning(f"Potential vision issues detected in output")
                    # Log specific error phrases found
                    for phrase in ["unable to", "cannot access", "can't see", "error", "failed", "not accessible", "404", "not found"]:
                        if phrase in raw_output.lower():
                            self.logger.warning(f"Found error phrase: '{phrase}'")
            
            # Check if we have structured output
            if hasattr(result, 'pydantic') and result.pydantic:
                # Use structured output directly
                eval_output: ImageEvaluationOutput = result.pydantic
                
                self.logger.debug("Structured output available")
                self.logger.debug(f"Overall score: {eval_output.overall_score}")
                self.logger.debug(f"Approved: {eval_output.approved}")
                self.logger.debug(f"Individual scores: visual_fidelity={eval_output.visual_fidelity_score}, "
                                f"product_accuracy={eval_output.product_accuracy_score}, "
                                f"technical_quality={eval_output.technical_quality_score}")
                
                # Log warning if identical images got low scores
                if self.reference_url == self.generated_path and eval_output.overall_score < 90:
                    self.logger.warning(f"Identical images received low score: {eval_output.overall_score}")
                
                return {
                    "success": True,
                    "approved": eval_output.approved,
                    "overall_score": eval_output.overall_score,
                    "scores": {
                        "visual_fidelity": eval_output.visual_fidelity_score,
                        "product_accuracy": eval_output.product_accuracy_score,
                        "technical_quality": eval_output.technical_quality_score,
                        "professional_appearance": eval_output.professional_appearance_score,
                        "ecommerce_suitability": eval_output.ecommerce_suitability_score
                    },
                    "feedback": eval_output.feedback,
                    "confidence": eval_output.confidence,
                    "strengths": eval_output.strengths,
                    "weaknesses": eval_output.weaknesses,
                    "raw_output": result.raw if hasattr(result, 'raw') else str(result),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            else:
                # Fallback to parsing raw output if structured output not available
                self.logger.warning("No structured output available, falling back to raw parsing")
                
                raw_output = result.raw if hasattr(result, 'raw') else str(result)
                
                # Simple fallback parsing
                approved = "approved: true" in raw_output.lower() or "approved\": true" in raw_output.lower()
                
                # Try to extract overall score from raw output
                import re
                score_match = re.search(r'overall_score["\s:]+(\d+)', raw_output, re.IGNORECASE)
                overall_score = int(score_match.group(1)) if score_match else 0
                
                return {
                    "success": True,
                    "approved": approved,
                    "overall_score": overall_score,
                    "scores": {},
                    "feedback": [],
                    "raw_output": raw_output,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "warning": "Structured output not available, using fallback parsing"
                }
            
        except Exception as e:
            self.logger.error(f"Image evaluation failed: {str(e)}")
            return {
                "success": False,
                "approved": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }