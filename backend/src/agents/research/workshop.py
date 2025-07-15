"""Research Workshop orchestrator for continuous opportunity discovery."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from queue import PriorityQueue
import json

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.state import SharedState, StateKey
from src.core.database import get_db
from src.models.database import MarketOpportunity, TrendSnapshot, ResearchMetric
from src.models.research import MarketOpportunity as MarketOpportunityModel, TrendData
from src.core.config import get_settings

logger = logging.getLogger(__name__)


class OpportunityQueue:
    """Priority queue for market opportunities."""
    
    def __init__(self):
        self._queue = PriorityQueue()
        self._opportunities = {}
        
    def add(self, opportunity: MarketOpportunityModel):
        """Add opportunity to queue with priority based on score."""
        priority = 1.0 - (opportunity.score or 0.5)  # Higher score = lower priority number
        self._queue.put((priority, opportunity.id, opportunity))
        self._opportunities[opportunity.id] = opportunity
        
    def get_next(self) -> Optional[MarketOpportunityModel]:
        """Get highest priority opportunity."""
        if self._queue.empty():
            return None
        _, opp_id, opportunity = self._queue.get()
        del self._opportunities[opp_id]
        return opportunity
        
    def get_all(self) -> List[MarketOpportunityModel]:
        """Get all opportunities sorted by priority."""
        opportunities = []
        temp_items = []
        
        while not self._queue.empty():
            item = self._queue.get()
            temp_items.append(item)
            opportunities.append(item[2])
            
        # Put items back
        for item in temp_items:
            self._queue.put(item)
            
        return opportunities
        
    def size(self) -> int:
        """Get queue size."""
        return self._queue.qsize()


class ResearchWorkshop:
    """Main orchestrator for continuous opportunity discovery."""
    
    def __init__(self):
        self.settings = get_settings()
        self.state = SharedState()
        self.opportunity_queue = OpportunityQueue()
        self.agents = {}
        self.is_running = False
        self.discovery_interval = 3600  # 1 hour default
        self.min_opportunity_score = 0.6  # Minimum score to queue
        self.logger = logger
        
    async def initialize_agents(self):
        """Initialize all research agents."""
        # Import agents to avoid circular imports
        # TODO: Uncomment as agents are implemented
        # from src.agents.research.trend_scanner import TrendScannerAgent
        # from src.agents.research.market_analyzer import MarketAnalyzerAgent
        # from src.agents.research.sourcing_scout import SourcingScoutAgent
        # from src.agents.research.opportunity_evaluator import OpportunityEvaluatorAgent
        
        # self.agents['trend_scanner'] = TrendScannerAgent()
        # self.agents['market_analyzer'] = MarketAnalyzerAgent()
        # self.agents['sourcing_scout'] = SourcingScoutAgent()
        # self.agents['opportunity_evaluator'] = OpportunityEvaluatorAgent()
        
        self.logger.info("Initialized all research agents")
        
        # Placeholder for testing
        self.agents = {
            'trend_scanner': None,
            'market_analyzer': None,
            'sourcing_scout': None,
            'opportunity_evaluator': None
        }
        
    async def start_discovery_cycle(self, continuous: bool = True):
        """Start the discovery cycle."""
        self.is_running = True
        self.logger.info("Starting Research Workshop discovery cycle")
        
        # Initialize agents if not already done
        if not self.agents:
            await self.initialize_agents()
            
        # Update state
        await self.state.set(StateKey.WORKFLOW_STATUS, "research_active")
        
        try:
            if continuous:
                while self.is_running:
                    await self.run_discovery_cycle()
                    self.logger.info(f"Discovery cycle complete. Waiting {self.discovery_interval}s for next cycle.")
                    await asyncio.sleep(self.discovery_interval)
            else:
                # Run single cycle
                await self.run_discovery_cycle()
        except Exception as e:
            self.logger.error(f"Error in discovery cycle: {e}")
            raise
        finally:
            await self.state.set(StateKey.WORKFLOW_STATUS, "research_stopped")
            
    async def stop_discovery_cycle(self):
        """Stop the discovery cycle."""
        self.logger.info("Stopping Research Workshop discovery cycle")
        self.is_running = False
        
    async def run_discovery_cycle(self) -> List[MarketOpportunityModel]:
        """Execute a single discovery cycle."""
        cycle_start = datetime.utcnow()
        self.logger.info(f"Starting discovery cycle at {cycle_start}")
        
        discovered_opportunities = []
        
        try:
            # Step 1: Scan for trends
            self.logger.info("Step 1: Scanning for trends...")
            trends = await self.agents['trend_scanner'].execute({
                'seed_keywords': await self._get_seed_keywords()
            })
            
            if not trends:
                self.logger.warning("No trends found in this cycle")
                return discovered_opportunities
                
            self.logger.info(f"Found {len(trends)} trends")
            
            # Save trend snapshots
            await self._save_trend_snapshots(trends)
            
            # Step 2: Analyze promising trends
            for trend in trends[:10]:  # Limit to top 10 trends
                if trend.growth_rate < 0.2:  # Skip low-growth trends
                    continue
                    
                self.logger.info(f"Step 2: Analyzing trend: {trend.keywords}")
                
                # Market analysis
                market_analysis = await self.agents['market_analyzer'].execute({
                    'trend': trend
                })
                
                if not market_analysis or market_analysis.competition_level == "saturated":
                    self.logger.info(f"Skipping saturated market: {trend.keywords}")
                    continue
                    
                # Step 3: Find sourcing options
                self.logger.info(f"Step 3: Finding suppliers for: {trend.keywords}")
                suppliers = await self.agents['sourcing_scout'].execute({
                    'keywords': trend.keywords,
                    'category': market_analysis.top_competitors[0].get('category') if market_analysis.top_competitors else None
                })
                
                if not suppliers or len(suppliers) < 2:
                    self.logger.info(f"Insufficient suppliers found for: {trend.keywords}")
                    continue
                    
                # Step 4: Evaluate complete opportunity
                self.logger.info(f"Step 4: Evaluating opportunity: {trend.keywords}")
                opportunity = MarketOpportunityModel(
                    title=f"{' '.join(trend.keywords[:3])} Opportunity",
                    description=f"Market opportunity based on {trend.source} trend data",
                    trend_data=trend,
                    market_analysis=market_analysis,
                    sourcing_options=suppliers[:5]  # Top 5 suppliers
                )
                
                # Score the opportunity
                scored_opportunity = await self.agents['opportunity_evaluator'].execute({
                    'opportunity': opportunity
                })
                
                if scored_opportunity.score >= self.min_opportunity_score:
                    self.logger.info(f"High-score opportunity found: {scored_opportunity.title} (score: {scored_opportunity.score})")
                    discovered_opportunities.append(scored_opportunity)
                    await self._save_opportunity(scored_opportunity)
                    self.opportunity_queue.add(scored_opportunity)
                    
        except Exception as e:
            self.logger.error(f"Error in discovery cycle: {e}")
            raise
        finally:
            # Record metrics
            await self._record_cycle_metrics(cycle_start, discovered_opportunities)
            
        self.logger.info(f"Discovery cycle complete. Found {len(discovered_opportunities)} opportunities")
        return discovered_opportunities
        
    async def _get_seed_keywords(self) -> List[str]:
        """Get seed keywords for trend scanning."""
        # Could be enhanced to use:
        # - Previous successful products
        # - User-defined interests
        # - Seasonal trends
        # - Geographic preferences
        return [
            "eco friendly", "sustainable", "smart home", "fitness",
            "pet accessories", "home organization", "outdoor gear",
            "wellness", "tech gadgets", "kitchen tools"
        ]
        
    async def _save_trend_snapshots(self, trends: List[TrendData]):
        """Save trend data to database."""
        async with get_db() as db:
            for trend in trends:
                snapshot = TrendSnapshot(
                    source=trend.source,
                    keywords=trend.keywords,
                    metrics={
                        'growth_rate': trend.growth_rate,
                        'current_volume': trend.current_volume,
                        'three_month_avg': trend.three_month_avg,
                        'yoy_change': trend.yoy_change,
                        'confidence_score': trend.confidence_score
                    },
                    geographic_data={'hotspots': trend.geographic_hotspots},
                    captured_at=trend.captured_at
                )
                db.add(snapshot)
            await db.commit()
            
    async def _save_opportunity(self, opportunity: MarketOpportunityModel):
        """Save opportunity to database."""
        async with get_db() as db:
            db_opportunity = MarketOpportunity(
                title=opportunity.title,
                description=opportunity.description,
                source=opportunity.trend_data.source,
                trend_data=opportunity.trend_data.dict(),
                market_analysis=opportunity.market_analysis.dict() if opportunity.market_analysis else None,
                sourcing_options=[s.dict() for s in opportunity.sourcing_options] if opportunity.sourcing_options else None,
                score=opportunity.score,
                discovery_date=opportunity.discovery_date
            )
            db.add(db_opportunity)
            await db.commit()
            opportunity.id = str(db_opportunity.id)
            
    async def _record_cycle_metrics(self, cycle_start: datetime, opportunities: List[MarketOpportunityModel]):
        """Record metrics for the discovery cycle."""
        async with get_db() as db:
            metric = ResearchMetric(
                agent_name="ResearchWorkshop",
                execution_date=cycle_start.date(),
                opportunities_found=len(opportunities),
                opportunities_approved=0,  # Will be updated as opportunities are reviewed
                average_score=sum(o.score for o in opportunities) / len(opportunities) if opportunities else 0.0,
                metrics_data={
                    'cycle_duration_seconds': (datetime.utcnow() - cycle_start).total_seconds(),
                    'trends_analyzed': len(self.agents.get('trend_scanner', {}).get('last_trends', [])),
                    'queue_size': self.opportunity_queue.size()
                }
            )
            db.add(metric)
            await db.commit()
            
    async def get_queued_opportunities(self) -> List[MarketOpportunityModel]:
        """Get all queued opportunities sorted by priority."""
        return self.opportunity_queue.get_all()
        
    async def get_opportunity_stats(self) -> Dict[str, Any]:
        """Get statistics about discovered opportunities."""
        async with get_db() as db:
            # Get counts by status
            result = await db.execute(
                select(MarketOpportunity.status, func.count(MarketOpportunity.id))
                .group_by(MarketOpportunity.status)
            )
            status_counts = dict(result.fetchall())
            
            # Get average scores
            result = await db.execute(
                select(func.avg(MarketOpportunity.score))
                .where(MarketOpportunity.score.isnot(None))
            )
            avg_score = result.scalar() or 0.0
            
            return {
                'total_discovered': sum(status_counts.values()),
                'status_breakdown': status_counts,
                'average_score': float(avg_score),
                'queue_size': self.opportunity_queue.size(),
                'is_running': self.is_running
            }