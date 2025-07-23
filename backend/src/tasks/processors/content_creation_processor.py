"""Content creation task processor."""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timezone
from uuid import uuid4

from src.tasks.base_processor import BaseTaskProcessor
from src.models.instance_schemas import TaskExecutionStep

logger = logging.getLogger(__name__)


class ContentCreationProcessor(BaseTaskProcessor):
    """Processor for content creation tasks."""
    
    def process(self) -> Dict[str, Any]:
        """Process a content creation task."""
        logger.info(f"Processing content creation task {self.task_id}")
        
        # Step 1: Analyze content requirements
        self.update_progress(10, "Analyzing content requirements")
        
        analysis_step = TaskExecutionStep(
            step_id="analyze_requirements",
            agent="ContentAnalyzer",
            action="Analyzing content requirements from task description",
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        self.add_execution_step(analysis_step)
        
        # Simulate analysis
        time.sleep(1)
        
        # Parse platforms and content type from description
        platforms = self._extract_platforms(self.task.description)
        content_type = self._determine_content_type(self.task.description)
        
        analysis_result = {
            "platforms": platforms,
            "content_type": content_type,
            "tone": "professional",
            "length": "medium"
        }
        
        analysis_step.status = "completed"
        analysis_step.completed_at = datetime.now(timezone.utc)
        analysis_step.output = analysis_result
        self.add_execution_step(analysis_step)
        
        # Step 2: Generate content
        self.update_progress(40, f"Generating {content_type} content for {', '.join(platforms)}")
        
        generation_step = TaskExecutionStep(
            step_id="generate_content",
            agent="ContentCreator",
            action=f"Creating {content_type} content",
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        self.add_execution_step(generation_step)
        
        # Simulate content generation
        time.sleep(2)
        
        generated_content = self._generate_dummy_content(content_type, platforms)
        
        generation_step.status = "completed"
        generation_step.completed_at = datetime.now(timezone.utc)
        generation_step.output = {"content": generated_content}
        self.add_execution_step(generation_step)
        
        # Step 3: Optimize for platforms
        self.update_progress(70, "Optimizing content for each platform")
        
        optimization_step = TaskExecutionStep(
            step_id="optimize_platforms",
            agent="PlatformOptimizer",
            action="Adapting content for platform requirements",
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        self.add_execution_step(optimization_step)
        
        # Simulate optimization
        time.sleep(1)
        
        optimized_content = self._optimize_for_platforms(generated_content, platforms)
        
        optimization_step.status = "completed"
        optimization_step.completed_at = datetime.now(timezone.utc)
        optimization_step.output = {"optimized_content": optimized_content}
        self.add_execution_step(optimization_step)
        
        # Step 4: Generate media (if needed)
        media_ids = []
        if content_type in ["product_showcase", "visual_story"]:
            self.update_progress(85, "Generating visual content")
            
            media_step = TaskExecutionStep(
                step_id="generate_media",
                agent="MediaGenerator",
                action="Creating visual assets",
                status="in_progress",
                started_at=datetime.now(timezone.utc)
            )
            self.add_execution_step(media_step)
            
            # Simulate media generation
            time.sleep(1)
            
            # In real implementation, this would generate actual media
            media_ids = [str(uuid4()) for _ in range(2)]
            
            media_step.status = "completed"
            media_step.completed_at = datetime.now(timezone.utc)
            media_step.output = {"media_ids": media_ids}
            self.add_execution_step(media_step)
        
        # Step 5: Finalize output
        self.update_progress(95, "Finalizing content package")
        
        output_data = {
            "content": optimized_content,
            "platforms": platforms,
            "content_type": content_type,
            "media_ids": media_ids,
            "metadata": {
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "word_count": sum(len(c["text"].split()) for c in optimized_content.values()),
                "estimated_reach": self._estimate_reach(platforms)
            }
        }
        
        self.set_output(
            output_format="mixed" if media_ids else "json",
            output_data=output_data,
            output_media_ids=media_ids
        )
        
        self.update_progress(100, "Content creation completed")
        
        return {
            "status": "success",
            "result": output_data
        }
    
    def _extract_platforms(self, description: str) -> List[str]:
        """Extract target platforms from task description."""
        description_lower = description.lower()
        platforms = []
        
        platform_keywords = {
            "instagram": ["instagram", "ig", "insta"],
            "tiktok": ["tiktok", "tik tok"],
            "facebook": ["facebook", "fb"],
            "twitter": ["twitter", "x platform", "tweet"],
            "linkedin": ["linkedin"],
            "youtube": ["youtube"],
        }
        
        for platform, keywords in platform_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                platforms.append(platform)
        
        # Default to Instagram if no platforms specified
        if not platforms:
            platforms = ["instagram"]
        
        return platforms
    
    def _determine_content_type(self, description: str) -> str:
        """Determine content type from description."""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ["product", "showcase", "feature"]):
            return "product_showcase"
        elif any(word in description_lower for word in ["story", "narrative", "behind"]):
            return "brand_story"
        elif any(word in description_lower for word in ["announce", "launch", "new"]):
            return "announcement"
        elif any(word in description_lower for word in ["tip", "how to", "tutorial"]):
            return "educational"
        else:
            return "general_post"
    
    def _generate_dummy_content(self, content_type: str, platforms: List[str]) -> Dict[str, str]:
        """Generate dummy content based on type."""
        templates = {
            "product_showcase": {
                "title": "Introducing Our Latest Innovation",
                "body": "Experience the perfect blend of style and functionality with our newest addition. Crafted with attention to detail and designed for modern living. #NewProduct #Innovation #Quality",
                "cta": "Shop Now - Link in Bio"
            },
            "brand_story": {
                "title": "Our Journey",
                "body": "From humble beginnings to where we are today, every step has been driven by our passion for excellence and commitment to our community. #BrandStory #Community #Journey",
                "cta": "Learn More About Us"
            },
            "announcement": {
                "title": "Big News!",
                "body": "We're excited to share something special with you. Stay tuned for what's coming next! #Announcement #ComingSoon #Excited",
                "cta": "Be the First to Know"
            },
            "educational": {
                "title": "Pro Tip",
                "body": "Did you know? Here's a quick tip to make your life easier. Save this post for later! #Tips #Educational #HowTo",
                "cta": "Follow for More Tips"
            },
            "general_post": {
                "title": "Thought of the Day",
                "body": "Sometimes the best moments are the simple ones. What's bringing you joy today? #DailyThoughts #Community #Inspiration",
                "cta": "Share Your Thoughts"
            }
        }
        
        return templates.get(content_type, templates["general_post"])
    
    def _optimize_for_platforms(self, content: Dict[str, str], platforms: List[str]) -> Dict[str, Dict[str, str]]:
        """Optimize content for each platform."""
        optimized = {}
        
        for platform in platforms:
            if platform == "instagram":
                optimized["instagram"] = {
                    "text": f"{content['body']}\n\n{content['cta']}",
                    "type": "feed_post",
                    "hashtags": self._extract_hashtags(content['body']),
                    "first_comment": "Drop a ❤️ if you agree!"
                }
            elif platform == "tiktok":
                optimized["tiktok"] = {
                    "text": f"{content['title']} {content['body'][:100]}...",
                    "type": "video_caption",
                    "hashtags": self._extract_hashtags(content['body']) + ["#fyp", "#foryou"],
                    "sounds": "trending_audio_placeholder"
                }
            elif platform == "facebook":
                optimized["facebook"] = {
                    "text": f"{content['title']}\n\n{content['body']}\n\n{content['cta']}",
                    "type": "page_post",
                    "hashtags": self._extract_hashtags(content['body'])[:5]  # FB prefers fewer hashtags
                }
            elif platform == "twitter":
                # Twitter has character limits
                short_text = f"{content['title']}: {content['body'][:200]}..."
                optimized["twitter"] = {
                    "text": short_text,
                    "type": "tweet",
                    "thread": [short_text, content['cta']],
                    "hashtags": self._extract_hashtags(content['body'])[:3]
                }
            elif platform == "linkedin":
                optimized["linkedin"] = {
                    "text": f"**{content['title']}**\n\n{content['body']}\n\n{content['cta']}",
                    "type": "article",
                    "hashtags": self._extract_hashtags(content['body']),
                    "professional_tone": True
                }
            else:
                optimized[platform] = {
                    "text": f"{content['title']}\n\n{content['body']}\n\n{content['cta']}",
                    "type": "generic",
                    "hashtags": self._extract_hashtags(content['body'])
                }
        
        return optimized
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text."""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def _estimate_reach(self, platforms: List[str]) -> int:
        """Estimate potential reach based on platforms."""
        # Dummy reach estimates
        platform_reach = {
            "instagram": 5000,
            "tiktok": 10000,
            "facebook": 3000,
            "twitter": 2000,
            "linkedin": 1500,
            "youtube": 8000
        }
        
        return sum(platform_reach.get(p, 1000) for p in platforms)