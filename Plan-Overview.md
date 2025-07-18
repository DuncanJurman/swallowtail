# Swallowtail: Hierarchical Multi-Agent E-Commerce System
## Architecture Design Document v2.0

### Executive Summary

Swallowtail is a two-phase autonomous e-commerce system that separates product discovery from product lifecycle management. The system uses a hierarchical multi-agent architecture where specialized AI agents handle different aspects of the business, from market research to fulfillment. Each product operates as an independent instance with customized agents, allowing for product-specific strategies while maintaining system-wide learning and efficiency.

### Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Design](#architecture-design)
3. [Phase 1: Research Workshop](#phase-1-research-workshop)
4. [Phase 2: Product Lifecycle Management](#phase-2-product-lifecycle-management)
5. [Agent Specifications](#agent-specifications)
6. [Backend Architecture](#backend-architecture)
7. [Frontend Architecture](#frontend-architecture)
8. [Data Flow and Integration](#data-flow-and-integration)
9. [Implementation Roadmap](#implementation-roadmap)
10. [Scalability and Multi-Tenancy](#scalability-and-multi-tenancy)

---

## System Overview

### Core Principles

1. **Separation of Concerns**: Product discovery (Research Workshop) is separated from product management (Product Instances)
2. **Product Autonomy**: Each product runs as an independent system with customized agents
3. **Shared Learning**: Products contribute to and benefit from a shared knowledge base
4. **Progressive Automation**: Different autonomy levels based on product lifecycle stage
5. **Human-in-the-Loop**: Strategic checkpoints for human oversight at critical decisions

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Master Orchestrator                       │
│                 (Global Strategy & Resource Manager)             │
└────────────┬──────────────────────┬─────────────────────────────┘
             │                      │
    ┌────────▼──────────┐  ┌───────▼─────────────────────────────┐
    │ Research Workshop │  │      Product Portfolio Manager       │
    │                   │  │                                      │
    │ • Trend Scanner   │  │  ┌────────────────────────────┐    │
    │ • Market Analyzer │  │  │   Product Instance Alpha    │    │
    │ • Sourcing Scout  │  │  │ ┌────────────────────────┐ │    │
    │ • Opportunity     │  │  │ │  Product Orchestrator  │ │    │
    │   Evaluator       │  │  │ └───────────┬────────────┘ │    │
    └───────────────────┘  │  │             │              │    │
                           │  │  ┌──────────▼───────────┐  │    │
                           │  │  │    Agent Pool        │  │    │
                           │  │  │ • Content Generator  │  │    │
                           │  │  │ • Marketing Manager  │  │    │
                           │  │  │ • Fulfillment Agent  │  │    │
                           │  │  │ • Analytics Engine   │  │    │
                           │  │  │ • Customer Service   │  │    │
                           │  │  └──────────────────────┘  │    │
                           │  └────────────────────────────┘    │
                           │                                      │
                           │  ┌────────────────────────────┐    │
                           │  │   Product Instance Beta    │    │
                           │  │   (Different Config)       │    │
                           │  └────────────────────────────┘    │
                           └──────────────────────────────────────┘
                                            │
                           ┌────────────────▼────────────────────┐
                           │        Shared Services Layer        │
                           │ • Knowledge Base  • Monitoring      │
                           │ • Resource Pool   • Billing         │
                           └─────────────────────────────────────┘
```

---

## Architecture Design

### 1. Master Orchestrator

The Master Orchestrator serves as the central nervous system of the entire platform, managing resources and coordinating between the Research Workshop and Product Instances.

**Responsibilities:**
- Resource allocation across all products and agents
- Cross-product learning and optimization
- System health monitoring and alerting
- User management and access control (for SaaS model)
- Billing and usage tracking

**Technical Implementation:**
```python
class MasterOrchestrator:
    def __init__(self):
        self.research_workshop = ResearchWorkshop()
        self.product_manager = ProductPortfolioManager()
        self.resource_manager = ResourceManager()
        self.knowledge_base = SharedKnowledgeBase()
        
    async def process_new_opportunity(self, opportunity):
        """When Research Workshop finds opportunity"""
        # Evaluate resource availability
        resources = await self.resource_manager.check_availability()
        
        # Score opportunity
        score = await self.knowledge_base.predict_success(opportunity)
        
        # Present to human for approval
        if await self.request_human_approval(opportunity, score):
            # Allocate resources and create product instance
            product_id = await self.product_manager.create_instance(
                opportunity, 
                resources
            )
            return product_id
            
    async def monitor_system_health(self):
        """Continuous monitoring of all components"""
        metrics = await self.collect_all_metrics()
        
        # Identify underperforming products
        for product in self.product_manager.get_all_products():
            if product.roi < threshold:
                await self.flag_for_review(product)
                
        # Reallocate resources from low to high performers
        await self.resource_manager.optimize_allocation(metrics)
```

### 2. Research Workshop

The Research Workshop operates continuously as a product-agnostic discovery engine.

**Components:**
- **Trend Scanner Agent**: Monitors multiple data sources for emerging trends
- **Market Analyzer Agent**: Deep dives into specific opportunities
- **Sourcing Scout Agent**: Identifies potential suppliers and pricing
- **Opportunity Evaluator Agent**: Scores and ranks opportunities

**Data Sources:**
- Google Trends API
- Social Media APIs (Twitter, TikTok, Reddit)
- E-commerce marketplaces (Amazon, eBay, Alibaba)
- Industry reports and news feeds
- Competitor analysis tools

### 3. Product Instance Architecture

Each product runs as a self-contained system with its own:
- Dedicated orchestrator (lightweight, configured from template)
- Customized agent configurations
- Isolated state management
- Performance tracking

**Product Lifecycle Stages:**
```yaml
lifecycle_stages:
  discovery:
    human_oversight: high
    automation_level: 20%
    checkpoints: [product_selection, supplier_approval, initial_content]
    
  launch:
    human_oversight: medium
    automation_level: 60%
    checkpoints: [final_content, marketing_budget, go_live]
    
  growth:
    human_oversight: low
    automation_level: 80%
    checkpoints: [major_strategy_changes, budget_increases]
    
  maturity:
    human_oversight: minimal
    automation_level: 95%
    checkpoints: [exception_handling]
    
  decline:
    human_oversight: minimal
    automation_level: 100%
    checkpoints: [discontinuation_decision]
```

---

## Phase 1: Research Workshop

### Architecture

```python
class ResearchWorkshop:
    def __init__(self):
        self.agents = {
            'trend_scanner': TrendScannerAgent(),
            'market_analyzer': MarketAnalyzerAgent(),
            'sourcing_scout': SourcingScoutAgent(),
            'opportunity_evaluator': OpportunityEvaluatorAgent()
        }
        self.opportunity_queue = PriorityQueue()
        
    async def run_discovery_cycle(self):
        """Main discovery loop - runs continuously"""
        # Step 1: Scan for trends
        trends = await self.agents['trend_scanner'].scan_all_sources()
        
        # Step 2: Analyze promising trends
        for trend in trends:
            if trend.growth_rate > MIN_GROWTH_THRESHOLD:
                analysis = await self.agents['market_analyzer'].deep_dive(trend)
                
                # Step 3: Find sourcing options
                if analysis.market_size > MIN_MARKET_SIZE:
                    suppliers = await self.agents['sourcing_scout'].find_suppliers(
                        analysis.product_keywords
                    )
                    
                    # Step 4: Evaluate complete opportunity
                    opportunity = await self.agents['opportunity_evaluator'].score(
                        trend, analysis, suppliers
                    )
                    
                    if opportunity.score > MIN_OPPORTUNITY_SCORE:
                        await self.opportunity_queue.add(opportunity)
```

### Agent Specifications

#### 1. Trend Scanner Agent

**Purpose**: Continuously monitor multiple data sources for emerging trends and opportunities.

**Tools & Integrations:**
- Google Trends API
- Social media monitoring (Twitter API, Reddit API, TikTok scraper)
- E-commerce bestseller trackers
- News aggregation APIs

**Output Format:**
```json
{
  "trend_id": "eco-water-bottle-2024-11",
  "keywords": ["eco water bottle", "sustainable hydration"],
  "growth_rate": 0.35,
  "volume_data": {
    "current_monthly": 45000,
    "3_month_avg": 32000,
    "yoy_change": 0.28
  },
  "geographic_hotspots": ["California", "New York", "Oregon"],
  "related_topics": ["plastic-free", "reusable", "BPA-free"],
  "confidence_score": 0.87
}
```

#### 2. Market Analyzer Agent

**Purpose**: Perform deep analysis on promising trends to validate market opportunity.

**Analysis Components:**
- Competition analysis (number of sellers, price ranges, market leaders)
- Customer sentiment analysis (reviews, complaints, desires)
- Market size estimation
- Seasonality and longevity assessment

**Tools:**
- Web scraping frameworks
- Sentiment analysis models
- Market research APIs
- Price tracking tools

#### 3. Sourcing Scout Agent

**Purpose**: Identify and evaluate potential suppliers for products.

**Capabilities:**
- Search multiple supplier databases (Alibaba, Global Sources, ThomasNet)
- Extract and compare pricing, MOQs, shipping terms
- Evaluate supplier reliability (ratings, years in business, certifications)
- Calculate landed costs and potential margins

**Output Format:**
```json
{
  "product": "eco-water-bottle",
  "suppliers": [
    {
      "supplier_id": "ALI-398472",
      "name": "GreenTech Manufacturing Ltd",
      "location": "Shenzhen, China",
      "unit_price": 3.50,
      "moq": 500,
      "lead_time_days": 21,
      "shipping_cost_per_unit": 0.75,
      "rating": 4.8,
      "certifications": ["ISO9001", "FDA", "BPA-Free"],
      "payment_terms": "30% deposit, 70% before shipping",
      "samples_available": true
    }
  ],
  "recommended_supplier": "ALI-398472",
  "estimated_margin": 0.68
}
```

#### 4. Opportunity Evaluator Agent

**Purpose**: Score and rank complete opportunities based on multiple factors.

**Scoring Factors:**
- Market demand trajectory
- Competition intensity
- Profit margin potential
- Operational complexity
- Brand fit (if applicable)
- Risk assessment

**Machine Learning Integration:**
- Uses historical data from SharedKnowledgeBase
- Predicts success probability based on similar past products
- Continuously improves scoring algorithm

---

## Phase 2: Product Lifecycle Management

### Product Instance Creation

When an opportunity is approved, the system creates a new Product Instance:

```python
class ProductInstance:
    def __init__(self, product_id, opportunity_data, template):
        self.product_id = product_id
        self.orchestrator = ProductOrchestrator(product_id)
        self.agents = self._initialize_agents(template, opportunity_data)
        self.state_manager = StateManager(f"product:{product_id}")
        self.lifecycle_stage = "discovery"
        self.config = ProductConfiguration(opportunity_data)
        
    def _initialize_agents(self, template, opportunity_data):
        """Initialize agents with product-specific configurations"""
        agents = {}
        
        # Load base template
        base_config = load_template(template)
        
        # Customize for this specific product
        for agent_type, base_agent_config in base_config.items():
            custom_config = self._customize_agent_config(
                base_agent_config, 
                opportunity_data
            )
            agents[agent_type] = create_agent(agent_type, custom_config)
            
        return agents
```

### Product Orchestrator

Each product has its own orchestrator managing the product-specific workflow:

```python
class ProductOrchestrator:
    def __init__(self, product_id):
        self.product_id = product_id
        self.workflow_engine = WorkflowEngine()
        self.checkpoint_manager = CheckpointManager()
        
    async def execute_lifecycle_stage(self, stage):
        """Execute workflows for current lifecycle stage"""
        workflow = self.get_workflow_for_stage(stage)
        
        for step in workflow.steps:
            # Check if human checkpoint needed
            if step.requires_checkpoint:
                approval = await self.checkpoint_manager.request_approval(
                    step.checkpoint_data
                )
                if not approval.approved:
                    return await self.handle_rejection(approval)
            
            # Execute step with appropriate agent
            result = await self.agents[step.agent_type].execute(step.params)
            
            # Store result and update state
            await self.state_manager.update(step.name, result)
            
            # Learn from outcome
            await self.knowledge_base.record_outcome(
                self.product_id, 
                step.name, 
                result
            )
```

### Agent Pool per Product

Each product instance has access to customized versions of these agents:

#### 1. Content Generator Agent

**Base Capabilities:**
- Product description writing
- Feature list generation
- SEO optimization
- Multi-language support

**Customization Parameters:**
```yaml
content_config:
  tone: "professional|casual|luxury|technical|friendly"
  target_audience:
    age_range: [25, 45]
    interests: ["sustainability", "fitness", "outdoor"]
    income_level: "middle-high"
  emphasis_points:
    - "eco-friendly materials"
    - "lifetime warranty"
    - "made in USA"
  seo_keywords:
    primary: ["eco water bottle", "sustainable hydration"]
    secondary: ["BPA free", "reusable", "stainless steel"]
  content_length:
    title: 60
    description: 500
    bullets: 5
```

#### 2. Visual Content Agent

**Capabilities:**
- Product image generation (via Stable Diffusion/DALL-E)
- Lifestyle photography creation
- Infographic design
- Video script and generation (via Veo 3)

**Customization:**
```yaml
visual_config:
  style: "minimalist|lifestyle|studio|outdoor"
  color_scheme: ["#2ECC71", "#FFFFFF", "#34495E"]
  backgrounds: ["nature", "gym", "office"]
  model_demographics: 
    apparent_age: [25, 35]
    ethnicity: "diverse"
  image_requirements:
    main_image: "product on white background"
    lifestyle_images: 3
    detail_shots: 2
    size_chart: true
  video_config:
    length_seconds: 15
    style: "demo|lifestyle|unboxing"
    music: "upbeat-corporate"
```

#### 3. Marketing Campaign Agent

**Capabilities:**
- Campaign strategy development
- Ad copy generation
- Platform selection and budget allocation
- A/B test setup
- Performance monitoring

**Platform Integrations:**
- Facebook/Instagram Ads API
- Google Ads API
- TikTok Ads API
- Pinterest Ads API
- Email marketing platforms

**Customization:**
```yaml
marketing_config:
  channels:
    - platform: "facebook"
      budget_percentage: 40
      targeting:
        interests: ["environmental", "fitness", "hiking"]
        behaviors: ["engaged_shoppers", "early_adopters"]
    - platform: "google"
      budget_percentage: 30
      campaign_types: ["shopping", "search"]
    - platform: "tiktok"
      budget_percentage: 30
      content_style: "ugc|branded|influencer"
  
  budget_rules:
    daily_limit: 100
    auto_scale_threshold: 2.5  # ROI threshold
    max_scale_factor: 3
    
  messaging_themes:
    - "Save the planet, one sip at a time"
    - "Your sustainable hydration companion"
    - "Eco-friendly never looked so good"
```

#### 4. Pricing Optimization Agent

**Capabilities:**
- Dynamic pricing based on demand
- Competitor price monitoring
- Margin optimization
- Promotional pricing strategies

**Algorithm:**
```python
class PricingAgent:
    def calculate_optimal_price(self, product_data):
        base_cost = product_data.landed_cost
        competitor_prices = self.get_competitor_prices()
        demand_elasticity = self.estimate_demand_elasticity()
        
        # Factor in multiple variables
        optimal_price = base_cost * (1 + target_margin)
        
        # Adjust for competition
        if competitor_prices.median < optimal_price:
            optimal_price = competitor_prices.median * 0.95
            
        # Ensure minimum margin
        if optimal_price < base_cost * 1.3:
            return PricingDecision(
                price=base_cost * 1.3,
                strategy="minimum_margin",
                warning="Below competitive pricing"
            )
            
        return PricingDecision(
            price=optimal_price,
            strategy="competitive",
            confidence=0.85
        )
```

#### 5. Fulfillment Agent

**Capabilities:**
- Order processing automation
- Supplier communication
- Inventory monitoring
- Shipping coordination
- Returns processing

**Integrations:**
- E-commerce platform APIs (Shopify, WooCommerce)
- Supplier APIs or email automation
- Shipping carrier APIs
- Inventory1 management systems

#### 6. Customer Service Agent

**Capabilities:**
- Pre-sale inquiry handling
- Order status updates
- Return/refund processing
- Product question answering
- Escalation to human support

**Knowledge Base Integration:**
```python
class CustomerServiceAgent:
    def __init__(self, product_id):
        self.product_id = product_id
        self.knowledge_base = ProductKnowledgeBase(product_id)
        self.conversation_memory = ConversationMemory()
        
    async def handle_inquiry(self, customer_message):
        # Classify intent
        intent = self.classify_intent(customer_message)
        
        # Retrieve relevant information
        if intent == "order_status":
            order_info = await self.get_order_info(customer_message)
            response = self.generate_order_status_response(order_info)
            
        elif intent == "product_question":
            context = await self.knowledge_base.search(customer_message)
            response = self.generate_answer(context, customer_message)
            
        elif intent == "return_request":
            if self.requires_human_escalation(customer_message):
                return self.escalate_to_human(customer_message)
            response = self.process_return_request(customer_message)
            
        return response
```

#### 7. Analytics & Optimization Agent

**Capabilities:**
- Performance monitoring across all channels
- ROI calculation and optimization
- Trend identification
- Automated reporting
- Optimization recommendations

**Metrics Tracked:**
```yaml
analytics_config:
  kpis:
    - metric: "conversion_rate"
      target: 0.02
      alert_threshold: 0.01
    - metric: "customer_acquisition_cost"
      target: 25
      alert_threshold: 40
    - metric: "lifetime_value"
      target: 150
      calculate_method: "cohort_analysis"
      
  reporting:
    frequency: "daily"
    recipients: ["owner", "product_manager"]
    include_recommendations: true
    
  optimization_triggers:
    - condition: "conversion_rate < 0.01 for 7 days"
      action: "recommend_landing_page_optimization"
    - condition: "ad_spend > revenue * 0.5"
      action: "pause_underperforming_campaigns"
    - condition: "stock_level < 14_day_demand"
      action: "trigger_reorder"
```

---

## Backend Architecture

### Technology Stack

```yaml
core_framework: "FastAPI"
task_orchestration: "Celery + Redis"
database: 
  primary: "PostgreSQL"
  cache: "Redis"
  vector_store: "Pinecone/Weaviate"
message_queue: "RabbitMQ/Redis"
container_orchestration: "Kubernetes"
monitoring: "Prometheus + Grafana"
logging: "ELK Stack"
```

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        API Gateway                           │
│                    (Authentication, Routing)                 │
└──────────────┬─────────────────────────┬────────────────────┘
               │                         │
   ┌───────────▼──────────┐   ┌─────────▼────────────┐
   │   Research Service   │   │  Product Management  │
   │                      │   │      Service         │
   │ • Trend Analysis     │   │ • Instance Creation  │
   │ • Market Research    │   │ • Lifecycle Mgmt     │
   │ • Opportunity Queue  │   │ • Agent Coordination │
   └──────────────────────┘   └──────────────────────┘
               │                         │
   ┌───────────▼──────────┐   ┌─────────▼────────────┐
   │    Agent Service     │   │   Analytics Service  │
   │                      │   │                      │
   │ • Agent Registry     │   │ • Metrics Collection │
   │ • Agent Execution    │   │ • Reporting          │
   │ • Tool Integration   │   │ • Optimization       │
   └──────────────────────┘   └──────────────────────┘
               │                         │
   ┌───────────▼──────────────────────────▼───────────┐
   │                 Data Layer                        │
   │  PostgreSQL | Redis | S3 | Vector DB | MQ        │
   └──────────────────────────────────────────────────┘
```

### Database Schema

```sql
-- Core Tables
CREATE TABLE products (
    id UUID PRIMARY KEY,
    name VARCHAR(255),
    status VARCHAR(50), -- discovery, launch, growth, maturity, decline
    created_at TIMESTAMP,
    opportunity_data JSONB,
    configuration JSONB,
    lifecycle_stage VARCHAR(50),
    owner_id UUID REFERENCES users(id)
);

CREATE TABLE agent_executions (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    agent_type VARCHAR(100),
    execution_time TIMESTAMP,
    input_data JSONB,
    output_data JSONB,
    success BOOLEAN,
    error_message TEXT,
    duration_ms INTEGER
);

CREATE TABLE checkpoints (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    checkpoint_type VARCHAR(100),
    created_at TIMESTAMP,
    data JSONB,
    status VARCHAR(50), -- pending, approved, rejected
    reviewer_id UUID REFERENCES users(id),
    review_notes TEXT,
    reviewed_at TIMESTAMP
);

CREATE TABLE product_metrics (
    id UUID PRIMARY KEY,
    product_id UUID REFERENCES products(id),
    metric_date DATE,
    revenue DECIMAL(10, 2),
    costs DECIMAL(10, 2),
    conversions INTEGER,
    ad_spend DECIMAL(10, 2),
    metrics_data JSONB -- flexible for various KPIs
);

-- Research Workshop Tables
CREATE TABLE opportunities (
    id UUID PRIMARY KEY,
    trend_data JSONB,
    market_analysis JSONB,
    sourcing_options JSONB,
    score DECIMAL(3, 2),
    status VARCHAR(50), -- pending, approved, rejected, promoted
    created_at TIMESTAMP
);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY,
    knowledge_type VARCHAR(100),
    context JSONB,
    outcome JSONB,
    success_metrics JSONB,
    created_at TIMESTAMP,
    product_id UUID REFERENCES products(id)
);
```

### API Endpoints

```yaml
# Research Workshop APIs
/api/v1/research/opportunities:
  GET: List current opportunities
  POST: Manually add opportunity

/api/v1/research/opportunities/{id}/approve:
  POST: Approve opportunity for product creation

/api/v1/research/trends:
  GET: Get current trend analysis
  
# Product Management APIs  
/api/v1/products:
  GET: List all products
  POST: Create new product from opportunity

/api/v1/products/{id}:
  GET: Get product details
  PUT: Update product configuration
  DELETE: Archive product

/api/v1/products/{id}/agents/{agent_type}/config:
  GET: Get agent configuration
  PUT: Update agent configuration

/api/v1/products/{id}/checkpoint:
  POST: Submit checkpoint decision

/api/v1/products/{id}/metrics:
  GET: Get product metrics

# Agent APIs
/api/v1/agents/execute:
  POST: Execute agent task

/api/v1/agents/templates:
  GET: List available agent templates
```

---

## Frontend Architecture

### Technology Stack

```yaml
framework: "Next.js 15 (App Router)"
ui_library: "React 19"
styling: "Tailwind CSS + shadcn/ui"
state_management: "Zustand + React Query"
real_time: "Socket.io"
visualization: "Recharts/D3.js"
```

### UI Structure

```
┌─────────────────────────────────────────────────────────┐
│                    Dashboard Layout                      │
├─────────────┬────────────────────────┬──────────────────┤
│             │                        │                  │
│  Sidebar    │     Main Content       │   Right Panel   │
│             │                        │                  │
│ • Dashboard │  ┌─────────────────┐  │ • Notifications │
│ • Research  │  │ Research View   │  │ • Quick Stats   │
│ • Products  │  │                 │  │ • AI Chat       │
│ • Analytics │  │ OR              │  │                 │
│ • Settings  │  │                 │  │                 │
│             │  │ Product View    │  │                 │
│             │  └─────────────────┘  │                 │
└─────────────┴────────────────────────┴──────────────────┘
```

### Key Views

#### 1. Research Workshop Dashboard

```typescript
interface ResearchDashboard {
  sections: {
    activeOpportunities: OpportunityCard[]
    trendingNow: TrendVisualization
    queuedForReview: OpportunityQueue
    historicalPerformance: SuccessRateChart
  }
  
  actions: {
    reviewOpportunity: (id: string) => void
    approveForPromotion: (id: string, config: ProductConfig) => void
    requestMoreInfo: (id: string, questions: string[]) => void
    adjustResearchParameters: (params: ResearchParams) => void
  }
}

// Opportunity Review Modal
interface OpportunityReviewModal {
  opportunity: {
    trendData: TrendAnalysis
    marketSize: MarketMetrics
    competition: CompetitionAnalysis
    suppliers: SupplierOption[]
    projectedROI: ROIProjection
  }
  
  actions: {
    approve: () => void
    reject: (reason: string) => void
    customizeConfig: () => void
  }
}
```

#### 2. Product Management View

```typescript
interface ProductDashboard {
  layout: "grid" | "list" | "kanban"
  
  productCard: {
    header: {
      name: string
      status: LifecycleStage
      health: "healthy" | "warning" | "critical"
    }
    
    metrics: {
      revenue: MoneyValue
      roi: Percentage
      conversions: Number
      trend: "up" | "down" | "stable"
    }
    
    quickActions: {
      viewDetails: () => void
      pauseProduct: () => void
      adjustBudget: () => void
      viewAnalytics: () => void
    }
  }
  
  filters: {
    lifecycle: LifecycleStage[]
    performance: "all" | "overperforming" | "underperforming"
    dateRange: DateRange
  }
}
```

#### 3. Product Detail View

```typescript
interface ProductDetailView {
  tabs: {
    overview: {
      configuration: ProductConfig
      currentAgents: AgentStatus[]
      checkpoints: CheckpointHistory
    }
    
    content: {
      descriptions: ProductContent
      images: ImageGallery
      videos: VideoPlayer
      editActions: ContentEditActions
    }
    
    marketing: {
      activeCampaigns: Campaign[]
      performance: CampaignMetrics
      budget: BudgetAllocation
      scheduling: CampaignCalendar
    }
    
    fulfillment: {
      orderQueue: Order[]
      supplierStatus: SupplierHealth
      inventory: InventoryLevels
      shipping: ShippingMetrics
    }
    
    analytics: {
      revenue: RevenueChart
      traffic: TrafficSources
      conversion: ConversionFunnel
      customers: CustomerAnalytics
    }
    
    agentConfig: {
      currentSettings: AgentConfiguration[]
      editMode: ConfigurationEditor
      templates: AgentTemplate[]
      customPrompts: PromptEditor
    }
  }
}
```

#### 4. Agent Configuration UI

```tsx
// Agent Configuration Component
const AgentConfigurator: React.FC<{productId: string}> = ({productId}) => {
  return (
    <div className="space-y-6">
      {/* Global Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Global Agent Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Select label="Autonomy Level" 
                    options={["High", "Medium", "Low"]} />
            <Switch label="Enable Auto-Scaling" />
            <NumberInput label="Daily Budget Limit" prefix="$" />
          </div>
        </CardContent>
      </Card>
      
      {/* Individual Agent Configs */}
      {AGENT_TYPES.map(agentType => (
        <Card key={agentType}>
          <CardHeader>
            <CardTitle>{agentType} Agent</CardTitle>
            <Switch label="Enabled" />
          </CardHeader>
          <CardContent>
            <Tabs>
              <TabsList>
                <Tab>Prompts</Tab>
                <Tab>Parameters</Tab>
                <Tab>Integrations</Tab>
              </TabsList>
              
              <TabsContent value="prompts">
                <PromptEditor 
                  agent={agentType}
                  prompts={getAgentPrompts(productId, agentType)}
                  onSave={updatePrompts}
                />
              </TabsContent>
              
              <TabsContent value="parameters">
                <ParameterForm
                  schema={getAgentSchema(agentType)}
                  values={getAgentParams(productId, agentType)}
                  onSave={updateParams}
                />
              </TabsContent>
              
              <TabsContent value="integrations">
                <IntegrationManager
                  agent={agentType}
                  available={getAvailableIntegrations(agentType)}
                  connected={getConnectedIntegrations(productId, agentType)}
                />
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
```

#### 5. Checkpoint Approval Interface

```tsx
const CheckpointApproval: React.FC<{checkpoint: Checkpoint}> = ({checkpoint}) => {
  return (
    <Modal size="xl">
      <ModalHeader>
        <h2>Approval Required: {checkpoint.type}</h2>
        <Badge>{checkpoint.product.name}</Badge>
      </ModalHeader>
      
      <ModalContent>
        {/* Dynamic content based on checkpoint type */}
        {checkpoint.type === 'product_selection' && (
          <ProductSelectionView 
            options={checkpoint.data.products}
            analysis={checkpoint.data.analysis}
          />
        )}
        
        {checkpoint.type === 'content_review' && (
          <ContentReviewView
            content={checkpoint.data.content}
            previews={checkpoint.data.previews}
          />
        )}
        
        {checkpoint.type === 'campaign_launch' && (
          <CampaignReviewView
            strategy={checkpoint.data.strategy}
            budget={checkpoint.data.budget}
            projections={checkpoint.data.projections}
          />
        )}
      </ModalContent>
      
      <ModalFooter>
        <Button variant="outline" onClick={requestChanges}>
          Request Changes
        </Button>
        <Button variant="destructive" onClick={reject}>
          Reject
        </Button>
        <Button variant="primary" onClick={approve}>
          Approve & Continue
        </Button>
      </ModalFooter>
    </Modal>
  )
}
```

### Real-time Updates

```typescript
// WebSocket integration for real-time updates
const useProductUpdates = (productId: string) => {
  const socket = useSocket()
  
  useEffect(() => {
    socket.on(`product:${productId}:update`, (update) => {
      // Handle different update types
      switch(update.type) {
        case 'metric_update':
          updateMetrics(update.data)
          break
        case 'agent_completion':
          showNotification(`${update.agent} completed task`)
          refreshAgentStatus()
          break
        case 'checkpoint_required':
          showCheckpointModal(update.checkpoint)
          break
      }
    })
    
    return () => socket.off(`product:${productId}:update`)
  }, [productId])
}
```

---

## Data Flow and Integration

### Agent Communication Protocol

```python
# Standard message format for inter-agent communication
class AgentMessage:
    def __init__(self, 
                 from_agent: str,
                 to_agent: str,
                 message_type: str,
                 payload: dict,
                 context: dict):
        self.id = generate_uuid()
        self.timestamp = datetime.utcnow()
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.message_type = message_type
        self.payload = payload
        self.context = context
        self.product_id = context.get('product_id')
        
    def to_json(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'from': self.from_agent,
            'to': self.to_agent,
            'type': self.message_type,
            'payload': self.payload,
            'context': self.context
        }
```

### Workflow Example: New Product Launch

```python
# Complete workflow from opportunity to launch
async def launch_new_product(opportunity_id: str, user_id: str):
    # 1. Create product instance
    product = await create_product_from_opportunity(opportunity_id)
    
    # 2. Discovery Phase
    await product.orchestrator.execute_stage('discovery', {
        'checkpoints': [
            {
                'type': 'supplier_selection',
                'data': await product.agents['sourcing'].get_supplier_options()
            },
            {
                'type': 'initial_content',
                'data': await product.agents['content'].generate_drafts()
            }
        ]
    })
    
    # 3. Launch Preparation
    await product.orchestrator.execute_stage('launch', {
        'parallel_tasks': [
            product.agents['visual'].generate_images(),
            product.agents['video'].create_promo_video(),
            product.agents['marketing'].prepare_campaigns()
        ],
        'checkpoints': [
            {
                'type': 'final_review',
                'data': await compile_launch_package(product)
            }
        ]
    })
    
    # 4. Go Live
    results = await product.orchestrator.execute_stage('go_live', {
        'tasks': [
            product.agents['listing'].create_product_listing(),
            product.agents['marketing'].launch_campaigns(),
            product.agents['analytics'].initialize_tracking()
        ]
    })
    
    # 5. Start monitoring
    await product.orchestrator.transition_to('growth')
    await product.agents['analytics'].start_monitoring()
    
    return results
```

### Shared Knowledge Base

```python
class SharedKnowledgeBase:
    def __init__(self):
        self.vector_store = VectorStore()  # Pinecone/Weaviate
        self.sql_store = PostgreSQL()
        self.cache = Redis()
        
    async def learn_from_outcome(self, product_id: str, action: str, outcome: dict):
        """Record and learn from product outcomes"""
        # Store raw outcome
        await self.sql_store.insert('outcomes', {
            'product_id': product_id,
            'action': action,
            'outcome': outcome,
            'timestamp': datetime.utcnow()
        })
        
        # Extract learnings
        learnings = await self.extract_learnings(action, outcome)
        
        # Update vector embeddings for similarity search
        await self.vector_store.upsert(
            id=f"{product_id}:{action}",
            vector=self.encode_learning(learnings),
            metadata={'product_id': product_id, 'action': action}
        )
        
        # Update cached recommendations
        await self.update_recommendations_cache()
        
    async def get_recommendations(self, context: dict) -> list:
        """Get recommendations based on similar past scenarios"""
        # Check cache first
        cache_key = self.generate_cache_key(context)
        cached = await self.cache.get(cache_key)
        if cached:
            return cached
            
        # Search for similar scenarios
        similar = await self.vector_store.search(
            vector=self.encode_context(context),
            top_k=10
        )
        
        # Analyze outcomes of similar scenarios
        recommendations = await self.analyze_similar_outcomes(similar)
        
        # Cache results
        await self.cache.set(cache_key, recommendations, ttl=3600)
        
        return recommendations
```

---

## Implementation Roadmap

### Phase 1: Foundation

**Month 1:**
- Set up core infrastructure (FastAPI, PostgreSQL, Redis)
- Implement Master Orchestrator skeleton
- Create basic Research Workshop with Trend Scanner
- Build initial UI framework

**Month 2:**
- Complete Research Workshop agents
- Implement opportunity scoring system
- Create checkpoint system
- Build opportunity review UI

**Deliverable:** Working Research Workshop that can identify and score opportunities

### Phase 2: Product Management

**Month 3:**
- Implement Product Instance architecture
- Create first set of product agents (Content, Marketing)
- Build product configuration system
- Develop product dashboard UI

**Month 4:**
- Add remaining agents (Fulfillment, Analytics, Customer Service)
- Implement agent customization framework
- Create shared knowledge base
- Complete product detail views

**Deliverable:** Full product lifecycle management with customizable agents

### Phase 3: Integration & Optimization (Months 5-6)

**Month 5:**
- Integrate with external platforms (Shopify, ad platforms)
- Implement real-time monitoring and alerts
- Add advanced analytics and reporting
- Create agent performance optimization

**Month 6:**
- Multi-tenancy support for SaaS
- Billing and usage tracking
- Advanced ML-based optimization
- Performance testing and optimization

**Deliverable:** Production-ready platform with SaaS capabilities

### Phase 4: Scale & Enhance (Months 7+)

- Add more agent capabilities
- Implement advanced AI features (voice, advanced video)
- Expand platform integrations
- Build marketplace for agent templates
- International expansion features

---

## Scalability and Multi-Tenancy

### Architecture for Scale

```yaml
deployment:
  orchestration: Kubernetes
  
  services:
    research_workshop:
      replicas: 3
      autoscaling:
        min: 2
        max: 10
        target_cpu: 70%
        
    product_orchestrators:
      strategy: "one-per-product"
      resource_limits:
        cpu: "500m"
        memory: "1Gi"
        
    agents:
      pool_size: 50
      allocation: "dynamic"
      scaling_policy: "predictive"
      
  databases:
    postgresql:
      strategy: "primary-replica"
      replicas: 3
      
    redis:
      strategy: "cluster"
      nodes: 6
      
  message_queue:
    type: "rabbitmq"
    cluster_size: 3
```

### Multi-Tenant Isolation

```python
class TenantManager:
    def __init__(self):
        self.tenants = {}
        
    async def create_tenant(self, tenant_id: str, config: dict):
        """Create isolated environment for new tenant"""
        tenant = {
            'id': tenant_id,
            'database': await self.provision_database(tenant_id),
            'redis_namespace': f"tenant:{tenant_id}",
            'resource_quota': config.get('quota', DEFAULT_QUOTA),
            'agent_limits': config.get('agent_limits', DEFAULT_LIMITS)
        }
        
        # Create isolated namespaces
        await self.create_kubernetes_namespace(tenant_id)
        await self.setup_network_policies(tenant_id)
        
        self.tenants[tenant_id] = tenant
        return tenant
        
    async def get_tenant_context(self, request):
        """Extract and validate tenant context from request"""
        tenant_id = request.headers.get('X-Tenant-ID')
        if not tenant_id or tenant_id not in self.tenants:
            raise UnauthorizedError("Invalid tenant")
            
        return self.tenants[tenant_id]
```

### Cost Management

```python
class ResourceTracker:
    def __init__(self):
        self.metrics = MetricsCollector()
        
    async def track_usage(self, tenant_id: str, resource_type: str, usage: float):
        """Track resource usage for billing"""
        await self.metrics.record({
            'tenant_id': tenant_id,
            'resource_type': resource_type,
            'usage': usage,
            'timestamp': datetime.utcnow()
        })
        
    async def get_monthly_bill(self, tenant_id: str) -> dict:
        """Calculate monthly bill for tenant"""
        usage = await self.metrics.get_monthly_usage(tenant_id)
        
        bill = {
            'compute_hours': usage.compute_hours * COMPUTE_RATE,
            'api_calls': usage.api_calls * API_RATE,
            'storage_gb': usage.storage_gb * STORAGE_RATE,
            'bandwidth_gb': usage.bandwidth_gb * BANDWIDTH_RATE,
            'ai_tokens': usage.ai_tokens * TOKEN_RATE
        }
        
        bill['total'] = sum(bill.values())
        return bill
```

---

## Security and Compliance

### Security Measures

```yaml
security:
  authentication:
    method: "JWT + OAuth2"
    providers: ["Google", "GitHub", "Email"]
    mfa: required_for_production
    
  authorization:
    model: "RBAC"
    roles:
      - owner: "full_access"
      - manager: "product_management"
      - analyst: "read_only"
      
  encryption:
    at_rest: "AES-256"
    in_transit: "TLS 1.3"
    secrets: "HashiCorp Vault"
    
  api_security:
    rate_limiting: "per_tenant"
    ddos_protection: "CloudFlare"
    input_validation: "strict"
    
  compliance:
    gdpr: true
    ccpa: true
    soc2: "in_progress"
```

### Data Privacy

```python
class PrivacyManager:
    async def anonymize_customer_data(self, data: dict) -> dict:
        """Anonymize customer data for analytics"""
        return {
            'id': hash_customer_id(data['id']),
            'location': generalize_location(data['location']),
            'age_group': generalize_age(data['age']),
            # Remove or hash other PII
        }
        
    async def handle_deletion_request(self, customer_id: str):
        """Handle GDPR deletion request"""
        # Delete from all systems
        await self.delete_from_orders(customer_id)
        await self.delete_from_analytics(customer_id)
        await self.delete_from_support(customer_id)
        
        # Log deletion for compliance
        await self.log_deletion(customer_id)
```

---

## Monitoring and Observability

### Metrics Collection

```yaml
metrics:
  system:
    - cpu_usage
    - memory_usage
    - disk_io
    - network_traffic
    
  application:
    - request_rate
    - response_time
    - error_rate
    - agent_execution_time
    
  business:
    - products_launched
    - conversion_rate
    - revenue_per_product
    - agent_success_rate
    
  ai_specific:
    - token_usage
    - model_latency
    - prompt_effectiveness
    - checkpoint_approval_rate
```

### Alerting Rules

```python
ALERT_RULES = [
    {
        'name': 'agent_failure_rate_high',
        'condition': 'rate(agent_failures[5m]) > 0.1',
        'severity': 'warning',
        'notification': ['slack', 'email']
    },
    {
        'name': 'product_roi_negative',
        'condition': 'product_roi < -0.2',
        'severity': 'critical',
        'notification': ['slack', 'sms', 'email'],
        'action': 'pause_marketing_spend'
    },
    {
        'name': 'checkpoint_pending_too_long',
        'condition': 'checkpoint_age > 24h',
        'severity': 'warning',
        'notification': ['email']
    }
]
```

---

## Conclusion

This updated architecture provides a robust, scalable foundation for the Swallowtail platform. The two-phase approach (Research Workshop → Product Instances) allows for efficient resource utilization while maintaining product-specific optimization. The hierarchical multi-agent system ensures coordinated execution while preserving flexibility.

Key advantages of this design:

1. **Scalability**: From single products to thousands
2. **Flexibility**: Per-product customization without system complexity
3. **Efficiency**: Shared resources and learning
4. **Reliability**: Isolated failures, graceful degradation
5. **Extensibility**: Easy to add new agents or capabilities

The system is designed to start simple (one user, few products) and scale to a full SaaS platform serving multiple businesses, each with their own product portfolios and customization needs.