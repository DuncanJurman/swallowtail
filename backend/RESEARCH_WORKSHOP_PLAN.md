# Research Workshop Implementation Plan

## Overview
The Research Workshop is a continuous discovery engine that identifies and evaluates e-commerce opportunities. It operates independently from product instances, constantly scanning for trends and opportunities to feed into the product pipeline.

## Architecture Design

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Research Workshop                         │
├───────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐        ┌──────────────────────────┐    │
│  │ ResearchWorkshop │        │   Opportunity Queue      │    │
│  │   Orchestrator   │───────▶│  (Priority-based)       │    │
│  └────────┬─────────┘        └──────────────────────────┘    │
│           │                                                   │
│  ┌────────▼─────────────────────────────────────────────┐    │
│  │                    Agent Pool                         │    │
│  ├───────────────────┬────────────────┬─────────────────┤    │
│  │ TrendScanner      │ MarketAnalyzer │ SourcingScout   │    │
│  │                   │                │                  │    │
│  ├───────────────────┴────────────────┴─────────────────┤    │
│  │              OpportunityEvaluator                     │    │
│  └───────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼────────────┐
                    │  Shared Knowledge Base │
                    │   (Vector Storage)     │
                    └───────────────────────┘
```

### Database Schema Extensions

```sql
-- Opportunities table
CREATE TABLE market_opportunities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trend_data JSONB NOT NULL,
    market_analysis JSONB,
    sourcing_options JSONB,
    score DECIMAL(3, 2),
    status VARCHAR(50) DEFAULT 'pending', -- pending, reviewed, approved, rejected, promoted
    discovery_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewer_id UUID REFERENCES users(id),
    review_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trend tracking
CREATE TABLE trend_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(100), -- google_trends, social_media, marketplace
    keywords TEXT[],
    metrics JSONB,
    geographic_data JSONB,
    captured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE
);

-- Research metrics
CREATE TABLE research_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name VARCHAR(100),
    execution_date DATE,
    opportunities_found INTEGER DEFAULT 0,
    opportunities_approved INTEGER DEFAULT 0,
    success_rate DECIMAL(3, 2),
    average_score DECIMAL(3, 2),
    metrics_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_opportunities_status ON market_opportunities(status);
CREATE INDEX idx_opportunities_score ON market_opportunities(score DESC);
CREATE INDEX idx_trends_processed ON trend_snapshots(processed);
CREATE INDEX idx_trends_captured ON trend_snapshots(captured_at DESC);
```

## Implementation Phases

### Phase 1: Core Infrastructure

#### 1.1 ResearchWorkshop Orchestrator
```python
class ResearchWorkshop:
    """Main orchestrator for continuous opportunity discovery"""
    
    def __init__(self):
        self.agents = {}
        self.opportunity_queue = PriorityQueue()
        self.discovery_interval = 3600  # 1 hour
        self.is_running = False
        
    async def initialize_agents(self):
        """Initialize all research agents"""
        self.agents['trend_scanner'] = TrendScannerAgent()
        self.agents['market_analyzer'] = MarketAnalyzerAgent()
        self.agents['sourcing_scout'] = SourcingScoutAgent()
        self.agents['opportunity_evaluator'] = OpportunityEvaluatorAgent()
        
    async def start_discovery_cycle(self):
        """Start continuous discovery loop"""
        self.is_running = True
        while self.is_running:
            await self.run_discovery_cycle()
            await asyncio.sleep(self.discovery_interval)
            
    async def run_discovery_cycle(self):
        """Single discovery cycle execution"""
        # Implementation details below
```

#### 1.2 Opportunity Model
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TrendData(BaseModel):
    keywords: List[str]
    growth_rate: float
    current_volume: int
    three_month_avg: int
    yoy_change: float
    geographic_hotspots: List[str]
    related_topics: List[str]
    confidence_score: float
    source: str
    
class MarketAnalysis(BaseModel):
    market_size_estimate: float
    competition_level: str  # low, medium, high
    average_price_range: tuple[float, float]
    top_competitors: List[dict]
    customer_pain_points: List[str]
    seasonality_factor: float
    market_maturity: str  # emerging, growing, mature, declining
    
class SupplierOption(BaseModel):
    supplier_id: str
    name: str
    location: str
    unit_price: float
    moq: int
    lead_time_days: int
    shipping_cost_per_unit: float
    rating: float
    certifications: List[str]
    payment_terms: str
    
class MarketOpportunity(BaseModel):
    id: Optional[str] = None
    trend_data: TrendData
    market_analysis: Optional[MarketAnalysis] = None
    sourcing_options: Optional[List[SupplierOption]] = None
    score: Optional[float] = None
    profit_margin_estimate: Optional[float] = None
    risk_assessment: Optional[dict] = None
    recommended_action: Optional[str] = None
    discovery_date: datetime = datetime.utcnow()
```

### Phase 2: Agent Implementation (TDD Approach)

#### 2.1 TrendScannerAgent

**Test-First Implementation:**

```python
# tests/agents/test_trend_scanner.py
import pytest
from unittest.mock import Mock, patch
from src.agents.research.trend_scanner import TrendScannerAgent

class TestTrendScannerAgent:
    """Test suite for TrendScannerAgent"""
    
    @pytest.fixture
    def agent(self):
        return TrendScannerAgent()
        
    @pytest.fixture
    def mock_google_trends_data(self):
        return {
            "eco water bottle": {
                "interest": 85,
                "growth_rate": 0.35,
                "related_queries": ["sustainable", "reusable", "BPA-free"]
            }
        }
    
    async def test_scan_google_trends(self, agent, mock_google_trends_data):
        """Test Google Trends scanning functionality"""
        with patch('pytrends.TrendReq') as mock_trends:
            mock_trends.return_value.interest_over_time.return_value = mock_google_trends_data
            
            trends = await agent.scan_google_trends(["water bottle", "eco friendly"])
            
            assert len(trends) > 0
            assert trends[0].growth_rate > 0
            assert "eco water bottle" in trends[0].keywords
            
    async def test_scan_social_media(self, agent):
        """Test social media trend detection"""
        mock_social_data = [
            {"hashtag": "#ecofriendly", "mentions": 50000, "growth": 0.25},
            {"hashtag": "#sustainableliving", "mentions": 35000, "growth": 0.30}
        ]
        
        with patch.object(agent, '_fetch_social_trends', return_value=mock_social_data):
            trends = await agent.scan_social_media()
            
            assert len(trends) == 2
            assert all(t.source == "social_media" for t in trends)
            
    async def test_filter_high_growth_trends(self, agent):
        """Test filtering of high-growth trends"""
        trends = [
            TrendData(keywords=["trend1"], growth_rate=0.15, ...),
            TrendData(keywords=["trend2"], growth_rate=0.45, ...),
            TrendData(keywords=["trend3"], growth_rate=0.08, ...)
        ]
        
        filtered = agent.filter_high_growth(trends, min_growth=0.20)
        
        assert len(filtered) == 1
        assert filtered[0].keywords == ["trend2"]
```

**Agent Implementation:**

```python
# src/agents/research/trend_scanner.py
from typing import List, Dict
import asyncio
from pytrends.request import TrendReq
from datetime import datetime, timedelta
from src.agents.base import BaseAgent
from src.models.research import TrendData

class TrendScannerAgent(BaseAgent):
    """Agent responsible for scanning multiple sources for emerging trends"""
    
    def __init__(self):
        super().__init__("TrendScannerAgent")
        self.min_growth_threshold = 0.20  # 20% growth minimum
        self.sources = ['google_trends', 'social_media', 'marketplace']
        
    async def execute(self, context: dict) -> List[TrendData]:
        """Main execution: scan all sources for trends"""
        self.logger.info("Starting trend scanning across all sources")
        
        # Parallel scanning of all sources
        tasks = [
            self.scan_google_trends(context.get('seed_keywords', [])),
            self.scan_social_media(),
            self.scan_marketplaces()
        ]
        
        all_trends = []
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"Error in trend scanning: {result}")
            else:
                all_trends.extend(result)
                
        # Filter and rank trends
        high_growth_trends = self.filter_high_growth(all_trends)
        ranked_trends = self.rank_trends(high_growth_trends)
        
        self.logger.info(f"Found {len(ranked_trends)} high-growth trends")
        return ranked_trends[:10]  # Top 10 trends
```

#### 2.2 MarketAnalyzerAgent

**Test-First Implementation:**

```python
# tests/agents/test_market_analyzer.py
class TestMarketAnalyzerAgent:
    """Test suite for MarketAnalyzerAgent"""
    
    @pytest.fixture
    def agent(self):
        return MarketAnalyzerAgent()
        
    async def test_analyze_competition(self, agent):
        """Test competition analysis functionality"""
        trend = TrendData(
            keywords=["eco water bottle"],
            growth_rate=0.35,
            current_volume=45000
        )
        
        with patch.object(agent, '_search_competitors') as mock_search:
            mock_search.return_value = [
                {"name": "EcoBottle Co", "market_share": 0.15, "price": 25.99},
                {"name": "GreenHydrate", "market_share": 0.12, "price": 22.99}
            ]
            
            analysis = await agent.analyze_competition(trend)
            
            assert analysis.competition_level in ["low", "medium", "high"]
            assert len(analysis.top_competitors) == 2
            assert analysis.average_price_range[0] > 0
            
    async def test_estimate_market_size(self, agent):
        """Test market size estimation"""
        trend = TrendData(current_volume=50000, growth_rate=0.30)
        
        market_size = await agent.estimate_market_size(trend)
        
        assert market_size > 0
        assert isinstance(market_size, float)
```

#### 2.3 SourcingScoutAgent

**Test-First Implementation:**

```python
# tests/agents/test_sourcing_scout.py
class TestSourcingScoutAgent:
    """Test suite for SourcingScoutAgent"""
    
    async def test_find_suppliers(self, agent):
        """Test supplier discovery functionality"""
        product_keywords = ["eco water bottle", "stainless steel bottle"]
        
        with patch.object(agent, '_search_alibaba') as mock_alibaba:
            mock_alibaba.return_value = [
                {
                    "supplier_id": "ALI123",
                    "name": "EcoTech Manufacturing",
                    "unit_price": 3.50,
                    "moq": 500,
                    "rating": 4.8
                }
            ]
            
            suppliers = await agent.find_suppliers(product_keywords)
            
            assert len(suppliers) > 0
            assert suppliers[0].unit_price == 3.50
            assert suppliers[0].moq == 500
            
    async def test_calculate_landed_cost(self, agent):
        """Test landed cost calculation"""
        supplier = SupplierOption(
            unit_price=3.50,
            shipping_cost_per_unit=0.75,
            moq=500
        )
        
        landed_cost = agent.calculate_landed_cost(supplier)
        
        assert landed_cost == 4.25  # unit_price + shipping
```

#### 2.4 OpportunityEvaluatorAgent

**Test-First Implementation:**

```python
# tests/agents/test_opportunity_evaluator.py
class TestOpportunityEvaluatorAgent:
    """Test suite for OpportunityEvaluatorAgent"""
    
    async def test_score_opportunity(self, agent):
        """Test opportunity scoring algorithm"""
        opportunity = MarketOpportunity(
            trend_data=TrendData(growth_rate=0.35, current_volume=50000),
            market_analysis=MarketAnalysis(
                market_size_estimate=1000000,
                competition_level="medium"
            ),
            sourcing_options=[
                SupplierOption(unit_price=3.50, moq=500, rating=4.8)
            ]
        )
        
        score = await agent.score_opportunity(opportunity)
        
        assert 0 <= score <= 1.0
        assert opportunity.score == score
        
    async def test_ml_prediction(self, agent):
        """Test ML-based success prediction"""
        opportunity = MarketOpportunity(...)
        
        with patch.object(agent.ml_model, 'predict') as mock_predict:
            mock_predict.return_value = 0.75
            
            prediction = await agent.predict_success(opportunity)
            
            assert prediction == 0.75
```

### Phase 3: Frontend Design

#### 3.1 Research Dashboard UI

```tsx
// components/research/ResearchDashboard.tsx
interface ResearchDashboardProps {
  opportunities: MarketOpportunity[]
  onReview: (id: string) => void
  onApprove: (id: string) => void
  onReject: (id: string) => void
}

const ResearchDashboard: React.FC<ResearchDashboardProps> = ({
  opportunities,
  onReview,
  onApprove,
  onReject
}) => {
  return (
    <div className="p-6 space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard title="Active Opportunities" value={opportunities.length} />
        <StatCard title="Avg Score" value={avgScore} />
        <StatCard title="This Week" value={weeklyCount} />
        <StatCard title="Pending Review" value={pendingCount} />
      </div>
      
      {/* Opportunity Queue */}
      <Card>
        <CardHeader>
          <CardTitle>Opportunity Queue</CardTitle>
          <div className="flex gap-2">
            <Button size="sm" variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              Filter
            </Button>
            <Button size="sm" variant="outline">
              <Sort className="w-4 h-4 mr-2" />
              Sort by Score
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {opportunities.map(opp => (
              <OpportunityCard
                key={opp.id}
                opportunity={opp}
                onReview={() => onReview(opp.id)}
                onQuickApprove={() => onApprove(opp.id)}
                onQuickReject={() => onReject(opp.id)}
              />
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
```

#### 3.2 Opportunity Review Modal

```tsx
// components/research/OpportunityReviewModal.tsx
const OpportunityReviewModal: React.FC<{opportunity: MarketOpportunity}> = ({
  opportunity
}) => {
  return (
    <Modal size="xl">
      <ModalHeader>
        <h2>Opportunity Review</h2>
        <Badge variant={getScoreBadgeVariant(opportunity.score)}>
          Score: {(opportunity.score * 100).toFixed(0)}%
        </Badge>
      </ModalHeader>
      
      <ModalContent>
        <Tabs defaultValue="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="market">Market Analysis</TabsTrigger>
            <TabsTrigger value="sourcing">Sourcing</TabsTrigger>
            <TabsTrigger value="projections">Projections</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            {/* Trend visualization */}
            <TrendChart data={opportunity.trend_data} />
            
            {/* Key metrics */}
            <div className="grid grid-cols-3 gap-4">
              <MetricCard 
                label="Growth Rate" 
                value={`${(opportunity.trend_data.growth_rate * 100).toFixed(0)}%`}
                trend="up"
              />
              <MetricCard 
                label="Search Volume" 
                value={opportunity.trend_data.current_volume.toLocaleString()}
              />
              <MetricCard 
                label="Competition" 
                value={opportunity.market_analysis.competition_level}
                variant={getCompetitionVariant(opportunity.market_analysis.competition_level)}
              />
            </div>
          </TabsContent>
          
          <TabsContent value="market">
            <MarketAnalysisView analysis={opportunity.market_analysis} />
          </TabsContent>
          
          <TabsContent value="sourcing">
            <SourcingOptionsTable options={opportunity.sourcing_options} />
          </TabsContent>
          
          <TabsContent value="projections">
            <ProfitProjectionChart opportunity={opportunity} />
          </TabsContent>
        </Tabs>
      </ModalContent>
      
      <ModalFooter>
        <Button variant="outline" onClick={onRequestMoreInfo}>
          Request More Info
        </Button>
        <Button variant="destructive" onClick={onReject}>
          Reject
        </Button>
        <Button variant="primary" onClick={onApprove}>
          Approve & Create Product
        </Button>
      </ModalFooter>
    </Modal>
  )
}
```

### Phase 4: API Integration

#### 4.1 Research Workshop API Endpoints

```python
# src/api/routes/research.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.models.research import MarketOpportunity
from src.agents.research.workshop import ResearchWorkshop

router = APIRouter(prefix="/api/v1/research", tags=["research"])

@router.get("/opportunities", response_model=List[MarketOpportunity])
async def get_opportunities(
    status: Optional[str] = None,
    min_score: Optional[float] = None,
    limit: int = 20
):
    """Get list of discovered opportunities"""
    query = select(MarketOpportunity)
    
    if status:
        query = query.where(MarketOpportunity.status == status)
    if min_score:
        query = query.where(MarketOpportunity.score >= min_score)
        
    query = query.order_by(MarketOpportunity.score.desc()).limit(limit)
    
    async with get_db() as db:
        result = await db.execute(query)
        return result.scalars().all()

@router.post("/opportunities/{id}/review")
async def review_opportunity(
    id: str,
    decision: str,  # approve, reject, more_info
    notes: Optional[str] = None,
    config: Optional[dict] = None
):
    """Review and decide on an opportunity"""
    if decision == "approve":
        # Create product instance from opportunity
        product_id = await create_product_from_opportunity(id, config)
        return {"product_id": product_id, "status": "product_created"}
    elif decision == "reject":
        await update_opportunity_status(id, "rejected", notes)
        return {"status": "rejected"}
    else:
        # Request more information
        await trigger_deep_analysis(id)
        return {"status": "analyzing"}

@router.get("/trends/current")
async def get_current_trends():
    """Get current trending topics being monitored"""
    # Implementation

@router.post("/workshop/control")
async def control_workshop(action: str):
    """Start/stop/pause the research workshop"""
    # Implementation
```

### Phase 5: Celery Tasks

```python
# src/core/tasks.py
from src.core.celery_app import celery_app
from src.agents.research.workshop import ResearchWorkshop

@celery_app.task(bind=True, queue='agents')
def run_discovery_cycle(self):
    """Run a single discovery cycle"""
    workshop = ResearchWorkshop()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        opportunities = loop.run_until_complete(workshop.run_discovery_cycle())
        return {
            "status": "success",
            "opportunities_found": len(opportunities),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        self.retry(exc=e, countdown=300)  # Retry in 5 minutes

@celery_app.task(queue='background')
def schedule_discovery_cycles():
    """Schedule periodic discovery cycles"""
    from celery.schedules import crontab
    
    # Run every hour
    run_discovery_cycle.apply_async(eta=datetime.utcnow() + timedelta(hours=1))
```

## Testing Strategy

### Unit Tests
- Each agent tested in isolation with mocked dependencies
- Focus on core logic and algorithms
- Mock external API calls

### Integration Tests
- Test agent interactions within Research Workshop
- Test database operations
- Test API endpoints with real database

### End-to-End Tests
- Complete discovery cycle from trend detection to opportunity creation
- Human checkpoint flow testing
- Product creation from approved opportunities

## Performance Considerations

1. **Parallel Processing**: All agents run concurrently during discovery
2. **Caching**: Cache trend data for 1 hour to avoid API rate limits
3. **Batch Processing**: Process multiple trends in batches
4. **Priority Queue**: High-score opportunities processed first
5. **Resource Limits**: Rate limiting on external API calls

## UI/UX Best Practices

1. **Real-time Updates**: WebSocket for live opportunity notifications
2. **Progressive Disclosure**: Show summary first, details on demand
3. **Visual Hierarchy**: Score-based color coding and sorting
4. **Quick Actions**: One-click approve/reject for efficiency
5. **Bulk Operations**: Select multiple opportunities for batch processing
6. **Mobile Responsive**: Dashboard accessible on tablets/phones