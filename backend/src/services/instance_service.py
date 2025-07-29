"""Service layer for instance management operations."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models.instance import Instance, InstanceAgent, InstanceTask, InstanceMedia, InstanceType, InstanceTaskStatus
from src.models.instance_schemas import InstanceCreate, TaskSubmission


class InstanceService:
    """Handles business logic for instance management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_instance(self, user_id: UUID, instance_data: InstanceCreate) -> Instance:
        """Create a new instance with default agent configuration."""
        instance = Instance(
            user_id=user_id,
            name=instance_data.name,
            type=instance_data.type,
            business_profile=instance_data.business_profile,
            configuration=self._get_default_configuration(instance_data.type)
        )
        
        self.db.add(instance)
        self.db.flush()
        
        # Create default agents for the instance
        self._create_default_agents(instance)
        
        self.db.commit()
        self.db.refresh(instance)
        
        return instance
    
    def get_instance(self, instance_id: UUID, user_id: UUID) -> Optional[Instance]:
        """Get an instance by ID, ensuring user owns it."""
        return self.db.query(Instance).filter(
            Instance.id == instance_id,
            Instance.user_id == user_id
        ).first()
    
    def list_instances(self, user_id: UUID) -> List[Instance]:
        """List all instances for a user."""
        return self.db.query(Instance).filter(
            Instance.user_id == user_id
        ).order_by(Instance.created_at.desc()).all()
    
    def update_instance(self, instance_id: UUID, user_id: UUID, 
                       updates: Dict[str, Any]) -> Optional[Instance]:
        """Update instance properties."""
        instance = self.get_instance(instance_id, user_id)
        if not instance:
            return None
            
        # Update allowed fields
        allowed_fields = ["name", "business_profile", "configuration"]
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(instance, field, value)
        
        self.db.commit()
        self.db.refresh(instance)
        
        return instance
    
    def submit_task(self, instance_id: UUID, user_id: UUID, 
                    task_data: TaskSubmission) -> Optional[InstanceTask]:
        """Submit a new task for processing."""
        # Verify instance ownership
        instance = self.get_instance(instance_id, user_id)
        if not instance:
            return None
        
        task = InstanceTask(
            instance_id=instance_id,
            description=task_data.description,
            status=InstanceTaskStatus.QUEUED,
            attached_media_ids=task_data.attached_media_ids
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def get_instance_tasks(self, instance_id: UUID, user_id: UUID, 
                          status: Optional[InstanceTaskStatus] = None) -> List[InstanceTask]:
        """Get tasks for an instance."""
        # Verify instance ownership
        instance = self.get_instance(instance_id, user_id)
        if not instance:
            return []
        
        query = self.db.query(InstanceTask).filter(
            InstanceTask.instance_id == instance_id
        )
        
        if status:
            query = query.filter(InstanceTask.status == status)
            
        return query.order_by(InstanceTask.created_at.desc()).all()
    
    def _get_default_configuration(self, instance_type: InstanceType) -> Dict[str, Any]:
        """Get default configuration based on instance type."""
        base_config = {
            "max_concurrent_tasks": 3,
            "task_timeout_minutes": 30,
            "enable_auto_retry": True
        }
        
        if instance_type == InstanceType.ECOMMERCE:
            base_config.update({
                "enable_product_generation": True,
                "enable_listing_optimization": True,
                "platforms": ["shopify", "etsy"]
            })
        elif instance_type == InstanceType.SOCIAL_MEDIA:
            base_config.update({
                "enable_content_scheduling": True,
                "platforms": ["instagram", "tiktok", "facebook"]
            })
            
        return base_config
    
    def _create_default_agents(self, instance: Instance) -> None:
        """Create default agent configuration for an instance."""
        # Manager agent - always created
        manager_agent = InstanceAgent(
            instance_id=instance.id,
            agent_type="manager",
            base_config={
                "role": "Task Manager",
                "goal": f"Analyze and delegate tasks for {instance.name}",
                "backstory": f"Expert coordinator for {instance.business_profile.get('industry', 'business')} operations"
            },
            is_enabled=True
        )
        self.db.add(manager_agent)
        
        # Type-specific agents
        if instance.type == InstanceType.ECOMMERCE:
            # Product creator agent
            self.db.add(InstanceAgent(
                instance_id=instance.id,
                agent_type="product_creator",
                base_config={
                    "role": "Product Content Creator",
                    "goal": "Create compelling product listings and descriptions",
                    "backstory": "Expert in e-commerce copywriting and product positioning"
                },
                is_enabled=True
            ))
            
            # Market analyst agent
            self.db.add(InstanceAgent(
                instance_id=instance.id,
                agent_type="market_analyst",
                base_config={
                    "role": "Market Research Analyst",
                    "goal": "Analyze market trends and competition",
                    "backstory": "Data-driven analyst specializing in e-commerce trends"
                },
                is_enabled=True
            ))
            
        elif instance.type == InstanceType.SOCIAL_MEDIA:
            # Content creator agent
            self.db.add(InstanceAgent(
                instance_id=instance.id,
                agent_type="content_creator",
                base_config={
                    "role": "Social Media Content Creator",
                    "goal": "Create engaging social media content",
                    "backstory": f"Creative expert in {instance.business_profile.get('industry', 'business')} content"
                },
                is_enabled=True
            ))
            
            # Social media manager agent
            self.db.add(InstanceAgent(
                instance_id=instance.id,
                agent_type="social_manager",
                base_config={
                    "role": "Social Media Strategy Manager",
                    "goal": "Plan and optimize social media presence",
                    "backstory": "Strategic thinker focused on audience growth and engagement"
                },
                is_enabled=True
            ))