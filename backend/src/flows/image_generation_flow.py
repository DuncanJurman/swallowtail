"""Image Generation Flow with quality control using CrewAI."""

import logging
import os
import tempfile
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone

from crewai.flow.flow import Flow, listen, router, start

from .models import ImageGenerationState
from ..crews.image_generation_crew import ImageGenerationCrew
from ..crews.image_evaluation_crew import ImageEvaluationCrew
from ..tools.image_storage_tool import ImageStorageTool


class ImageGenerationFlow(Flow[ImageGenerationState]):
    """Modular image generation flow with automatic quality control."""
    
    def __init__(self):
        """Initialize the flow."""
        super().__init__()
        self.logger = logging.getLogger("ImageGenerationFlow")
        self.storage_tool = ImageStorageTool()
    
    @start()
    def generate_initial_image(self):
        """Start the generation process."""
        self.logger.info(f"Starting image generation for {self.state.product_name}")
        self.state.attempts += 1
        
        # Use generation crew
        gen_crew = ImageGenerationCrew(
            product_id=self.state.product_id,
            reference_image_url=self.state.reference_image_url,
            product_name=self.state.product_name,
            product_features=self.state.product_features,
            style_requirements=self.state.style_requirements,
            previous_feedback=self.state.feedback_history
        )
        
        try:
            # Execute crew asynchronously
            import asyncio
            if asyncio.get_event_loop().is_running():
                # If already in async context
                result = asyncio.create_task(gen_crew.execute_async()).result()
            else:
                # If in sync context
                result = asyncio.run(gen_crew.execute_async())
            
            if result["success"]:
                # Store result in state
                self.state.generated_images.append({
                    "attempt": self.state.attempts,
                    "image_path": result.get("temp_image_path", ""),
                    "storage_url": result.get("storage_url", ""),
                    "prompt": result.get("prompt_used", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                self.logger.info(f"Image generated successfully on attempt {self.state.attempts}")
                return "evaluate"
            else:
                # Generation failed
                self.state.errors.append({
                    "attempt": self.state.attempts,
                    "error": result.get("error", "Unknown generation error"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                return "failed"
                
        except Exception as e:
            self.logger.error(f"Generation failed: {str(e)}")
            self.state.errors.append({
                "attempt": self.state.attempts,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return "failed"
    
    @router(generate_initial_image)
    def evaluate_generated_image(self):
        """Evaluate the generated image."""
        if not self.state.generated_images:
            self.logger.error("No generated images to evaluate")
            return "failed"
            
        latest_image = self.state.generated_images[-1]
        image_path = latest_image.get("image_path")
        
        if not image_path or not os.path.exists(image_path):
            # If we have a storage URL but no local path, skip evaluation and approve
            if latest_image.get("storage_url"):
                self.logger.info("Image already stored, skipping evaluation")
                return "approved"
            else:
                self.logger.error(f"Generated image not found at {image_path}")
                return "failed"
        
        # Use evaluation crew
        eval_crew = ImageEvaluationCrew(
            reference_url=self.state.reference_image_url,
            generated_path=image_path,
            product_name=self.state.product_name,
            threshold=self.state.approval_threshold
        )
        
        try:
            eval_result = eval_crew.evaluate()
            
            if eval_result["success"]:
                # Store evaluation results
                overall_score = eval_result.get("overall_score", 0)
                approved = eval_result.get("approved", False)
                
                self.logger.info(f"Evaluation complete: Score={overall_score}, Approved={approved}")
                
                if approved:
                    return "approved"
                elif self.state.attempts < self.state.max_attempts:
                    # Store feedback for next attempt
                    self.state.feedback_history.append({
                        "attempt": self.state.attempts,
                        "feedback": eval_result.get("feedback", []),
                        "scores": eval_result.get("scores", {}),
                        "overall_score": overall_score
                    })
                    return "retry"
                else:
                    return "max_attempts_reached"
            else:
                # Evaluation failed
                self.logger.error(f"Evaluation failed: {eval_result.get('error', 'Unknown error')}")
                return "failed"
                
        except Exception as e:
            self.logger.error(f"Evaluation error: {str(e)}")
            self.state.errors.append({
                "attempt": self.state.attempts,
                "error": f"Evaluation error: {str(e)}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return "failed"
    
    @listen("retry")
    def regenerate_with_feedback(self):
        """Generate new image incorporating feedback."""
        self.logger.info(f"Retrying generation with feedback (attempt {self.state.attempts + 1})")
        self.state.attempts += 1
        
        # Get latest feedback
        latest_feedback = self.state.feedback_history[-1] if self.state.feedback_history else {}
        feedback_list = latest_feedback.get("feedback", [])
        
        # Format feedback for the crew
        formatted_feedback = []
        for i, fb_entry in enumerate(self.state.feedback_history):
            formatted_feedback.append({
                "attempt": fb_entry.get("attempt", i + 1),
                "feedback": " ".join(fb_entry.get("feedback", []))
            })
        
        # Pass feedback to generation crew
        gen_crew = ImageGenerationCrew(
            product_id=self.state.product_id,
            reference_image_url=self.state.reference_image_url,
            product_name=self.state.product_name,
            product_features=self.state.product_features,
            style_requirements=self.state.style_requirements,
            previous_feedback=formatted_feedback
        )
        
        try:
            # Execute crew
            import asyncio
            if asyncio.get_event_loop().is_running():
                result = asyncio.create_task(gen_crew.execute_async()).result()
            else:
                result = asyncio.run(gen_crew.execute_async())
            
            if result["success"]:
                # Store result and evaluate again
                self.state.generated_images.append({
                    "attempt": self.state.attempts,
                    "image_path": result.get("temp_image_path", ""),
                    "storage_url": result.get("storage_url", ""),
                    "prompt": result.get("prompt_used", ""),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
                return self.evaluate_generated_image()
            else:
                self.state.errors.append({
                    "attempt": self.state.attempts,
                    "error": result.get("error", "Regeneration failed"),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                return "failed"
                
        except Exception as e:
            self.logger.error(f"Regeneration error: {str(e)}")
            self.state.errors.append({
                "attempt": self.state.attempts,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            return "failed"
    
    @listen("approved")
    def finalize_image(self):
        """Store approved image and cleanup."""
        self.logger.info("Finalizing approved image")
        
        if not self.state.generated_images:
            self.logger.error("No images to finalize")
            return None
            
        latest_image = self.state.generated_images[-1]
        
        # Check if already stored
        if latest_image.get("storage_url"):
            self.state.final_image_url = latest_image["storage_url"]
            self.state.final_image_path = latest_image.get("image_path")
            self.state.approved = True
            self.state.completed_at = datetime.now(timezone.utc)
            self._cleanup_temp_files()
            return self.state.final_image_url
        
        # Store in Supabase if not already stored
        image_path = latest_image.get("image_path")
        if image_path and os.path.exists(image_path):
            try:
                storage_result = self.storage_tool._run(
                    image_path=image_path,
                    product_id=str(self.state.product_id),
                    image_type="generated"
                )
                
                if storage_result["success"]:
                    self.state.final_image_url = storage_result["url"]
                    self.state.final_image_path = image_path
                    self.state.approved = True
                    self.state.completed_at = datetime.now(timezone.utc)
                    
                    self.logger.info(f"Image stored successfully: {self.state.final_image_url}")
                    
                    # Cleanup temp files
                    self._cleanup_temp_files()
                    
                    return self.state.final_image_url
                else:
                    self.logger.error(f"Storage failed: {storage_result.get('error', 'Unknown error')}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Storage error: {str(e)}")
                self.state.errors.append({
                    "error": f"Storage error: {str(e)}",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                return None
        else:
            self.logger.error("No image file to store")
            return None
    
    @listen("failed")
    def handle_failure(self):
        """Handle failure case."""
        self.logger.error(f"Flow failed after {self.state.attempts} attempts")
        self.state.errors.append({
            "error": "Flow failed",
            "attempts": self.state.attempts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self._cleanup_temp_files()
        return None
    
    @listen("max_attempts_reached")
    def handle_max_attempts(self):
        """Handle max attempts reached."""
        self.logger.warning(f"Max attempts ({self.state.max_attempts}) reached without approval")
        self.state.errors.append({
            "error": f"Max attempts ({self.state.max_attempts}) reached without approval",
            "attempts": self.state.attempts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        self._cleanup_temp_files()
        return None
    
    def _cleanup_temp_files(self):
        """Clean up temporary image files."""
        for img_data in self.state.generated_images:
            temp_path = img_data.get("image_path")
            if temp_path and os.path.exists(temp_path) and temp_path.startswith("/tmp"):
                try:
                    os.remove(temp_path)
                    self.logger.debug(f"Cleaned up temp file: {temp_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to cleanup {temp_path}: {e}")
    
    # Public API methods for integration
    async def generate_image_for_product(
        self,
        product_id: UUID,
        reference_url: str,
        product_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Public method for external callers to generate a product image.
        
        Args:
            product_id: UUID of the product
            reference_url: URL or path to reference image
            product_info: Dictionary containing:
                - name: Product name
                - features: List of product features
                - style: Style requirements dictionary
                - threshold: Approval threshold (0-1)
                
        Returns:
            Dictionary with results:
                - success: Whether generation succeeded
                - image_url: Final image URL if successful
                - attempts: Number of attempts made
                - metadata: Additional information
        """
        try:
            # Prepare inputs
            inputs = {
                "product_id": product_id,
                "reference_image_url": reference_url,
                "product_name": product_info.get("name", "Product"),
                "product_features": product_info.get("features", []),
                "style_requirements": product_info.get("style", {}),
                "approval_threshold": product_info.get("threshold", 0.85)
            }
            
            # Execute flow
            result = await self.kickoff_async(inputs=inputs)
            
            return {
                "success": self.state.approved,
                "image_url": self.state.final_image_url,
                "attempts": self.state.attempts,
                "metadata": {
                    "product_id": str(product_id),
                    "completed_at": self.state.completed_at.isoformat() if self.state.completed_at else None,
                    "feedback_history": self.state.feedback_history,
                    "errors": self.state.errors
                }
            }
            
        except Exception as e:
            self.logger.error(f"Flow execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "attempts": self.state.attempts if hasattr(self, 'state') else 0,
                "metadata": {
                    "product_id": str(product_id),
                    "errors": getattr(self.state, 'errors', [])
                }
            }
    
    def get_generation_status(self) -> Dict[str, Any]:
        """Get current status of generation process."""
        if not hasattr(self, 'state') or not self.state:
            return {
                "status": "not_started",
                "message": "Flow has not been started"
            }
        
        # Determine status
        if self.state.approved:
            status = "completed"
        elif len(self.state.errors) > 0 and not self.state.approved:
            status = "failed"
        elif self.state.attempts > 0:
            status = "in_progress"
        else:
            status = "not_started"
            
        return {
            "status": status,
            "product_id": str(self.state.product_id) if self.state.product_id else None,
            "product_name": self.state.product_name,
            "attempts": self.state.attempts,
            "max_attempts": self.state.max_attempts,
            "approved": self.state.approved,
            "in_progress": status == "in_progress",
            "failed": status == "failed",
            "final_url": self.state.final_image_url,
            "generated_count": len(self.state.generated_images),
            "last_feedback": self.state.feedback_history[-1] if self.state.feedback_history else None
        }