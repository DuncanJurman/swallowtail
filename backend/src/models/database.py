"""SQLAlchemy database models for Swallowtail."""

from datetime import datetime
from typing import Optional, Dict, Any
import uuid

from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, JSON, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from src.core.database import Base


class ProductStatus(str, enum.Enum):
    """Product lifecycle status."""
    DISCOVERED = "discovered"
    EVALUATING = "evaluating"
    APPROVED = "approved"
    REJECTED = "rejected"
    SOURCING = "sourcing"
    LISTING = "listing"
    ACTIVE = "active"
    PAUSED = "paused"
    DISCONTINUED = "discontinued"


class AgentType(str, enum.Enum):
    """Types of agents in the system."""
    TREND_SCANNER = "trend_scanner"
    MARKET_ANALYZER = "market_analyzer"
    SOURCING_SCOUT = "sourcing_scout"
    OPPORTUNITY_EVALUATOR = "opportunity_evaluator"
    CONTENT_GENERATOR = "content_generator"
    MARKETING_MANAGER = "marketing_manager"
    FULFILLMENT_AGENT = "fulfillment_agent"
    ANALYTICS_ENGINE = "analytics_engine"
    CUSTOMER_SERVICE = "customer_service"


class TaskStatus(str, enum.Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Product(Base):
    """Product entity representing an e-commerce product."""
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.DISCOVERED, nullable=False)
    
    # Market data
    category = Column(String(100))
    tags = Column(JSON, default=list)
    target_market = Column(JSON)
    competition_analysis = Column(JSON)
    
    # Pricing
    cost_price = Column(Float)
    selling_price = Column(Float)
    profit_margin = Column(Float)
    
    # Metrics
    opportunity_score = Column(Float)
    market_demand_score = Column(Float)
    competition_score = Column(Float)
    sourcing_difficulty_score = Column(Float)
    
    # Supplier information
    supplier_info = Column(JSON)
    sourcing_data = Column(JSON)
    
    # Platform data
    shopify_product_id = Column(String(100))
    listing_data = Column(JSON)
    
    # Discovery metadata
    discovered_by_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    discovered_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime)
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    discovered_by = relationship("Agent", back_populates="discovered_products")
    tasks = relationship("AgentTask", back_populates="product", cascade="all, delete-orphan")
    decisions = relationship("AgentDecision", back_populates="product", cascade="all, delete-orphan")


class Agent(Base):
    """Agent entity representing an AI agent in the system."""
    __tablename__ = "agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(SQLEnum(AgentType), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Configuration
    configuration = Column(JSON, default=dict)
    capabilities = Column(JSON, default=list)
    
    # Performance metrics
    total_tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    average_task_duration = Column(Float)  # in seconds
    performance_metrics = Column(JSON, default=dict)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_active_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    discovered_products = relationship("Product", back_populates="discovered_by")
    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    decisions = relationship("AgentDecision", back_populates="agent", cascade="all, delete-orphan")


class AgentTask(Base):
    """Task executed by an agent."""
    __tablename__ = "agent_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    
    # Task details
    task_type = Column(String(50), nullable=False)
    description = Column(Text)
    parameters = Column(JSON, default=dict)
    
    # Execution
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    result = Column(JSON)
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # Celery integration
    celery_task_id = Column(String(100))
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Relationships
    agent = relationship("Agent", back_populates="tasks")
    product = relationship("Product", back_populates="tasks")


class MarketOpportunity(Base):
    """Discovered market opportunity awaiting evaluation."""
    __tablename__ = "market_opportunities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    discovered_by_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    
    # Opportunity details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    source = Column(String(100))  # e.g., "google_trends", "social_media", "competitor_analysis"
    
    # Scoring
    initial_score = Column(Float)
    final_score = Column(Float)
    scoring_breakdown = Column(JSON)
    
    # Market data
    market_data = Column(JSON)
    trend_data = Column(JSON)
    competition_data = Column(JSON)
    
    # Status
    is_processed = Column(Boolean, default=False)
    is_approved = Column(Boolean)
    processed_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class AgentDecision(Base):
    """Audit log of agent decisions for transparency."""
    __tablename__ = "agent_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    
    # Decision details
    decision_type = Column(String(50), nullable=False)  # e.g., "approve_product", "set_price", "pause_listing"
    decision = Column(JSON, nullable=False)
    reasoning = Column(Text)
    confidence_score = Column(Float)
    
    # Context
    context = Column(JSON)  # Input data that led to the decision
    alternatives_considered = Column(JSON)  # Other options the agent evaluated
    
    # Human oversight
    requires_approval = Column(Boolean, default=False)
    is_approved = Column(Boolean)
    approved_by = Column(String(100))  # User ID/email
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Outcome tracking
    outcome = Column(JSON)  # Result of the decision after execution
    outcome_timestamp = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    agent = relationship("Agent", back_populates="decisions")
    product = relationship("Product", back_populates="decisions")


class SharedKnowledge(Base):
    """Shared knowledge base entries for cross-product learning."""
    __tablename__ = "shared_knowledge"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Knowledge details
    knowledge_type = Column(String(50), nullable=False)  # e.g., "supplier_quality", "market_trend", "pricing_strategy"
    category = Column(String(100))
    tags = Column(JSON, default=list)
    
    # Content
    title = Column(String(255), nullable=False)
    content = Column(Text)
    data = Column(JSON)
    
    # Source
    source_agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"))
    source_product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    
    # Embeddings (for vector search)
    embedding_id = Column(String(100))  # Pinecone vector ID
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)