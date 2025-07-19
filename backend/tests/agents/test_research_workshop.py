"""Tests for ResearchWorkshop orchestrator."""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.agents.research.workshop import ResearchWorkshop, OpportunityQueue
from src.models.research import MarketOpportunity, TrendData, TrendSource


class TestOpportunityQueue:
    """Test the opportunity priority queue."""
    
    def test_add_opportunity(self):
        """Test adding opportunities to queue."""
        queue = OpportunityQueue()
        
        opp1 = MarketOpportunity(
            id="1",
            title="High Score Opportunity",
            description="Test",
            trend_data=TrendData(
                source=TrendSource.GOOGLE_TRENDS,
                keywords=["test"],
                growth_rate=0.5,
                current_volume=1000,
                three_month_avg=800,
                yoy_change=0.3,
                confidence_score=0.9
            ),
            score=0.9
        )
        
        opp2 = MarketOpportunity(
            id="2",
            title="Low Score Opportunity",
            description="Test",
            trend_data=TrendData(
                source=TrendSource.GOOGLE_TRENDS,
                keywords=["test2"],
                growth_rate=0.2,
                current_volume=500,
                three_month_avg=400,
                yoy_change=0.1,
                confidence_score=0.6
            ),
            score=0.3
        )
        
        queue.add(opp1)
        queue.add(opp2)
        
        assert queue.size() == 2
        
        # Should get high score opportunity first
        next_opp = queue.get_next()
        assert next_opp.id == "1"
        assert next_opp.score == 0.9
        
    def test_get_all_opportunities_sorted(self):
        """Test getting all opportunities in priority order."""
        queue = OpportunityQueue()
        
        opportunities = []
        for i, score in enumerate([0.5, 0.9, 0.3, 0.7]):
            opp = MarketOpportunity(
                id=str(i),
                title=f"Opportunity {i}",
                description="Test",
                trend_data=TrendData(
                    source=TrendSource.GOOGLE_TRENDS,
                    keywords=[f"test{i}"],
                    growth_rate=score,
                    current_volume=1000,
                    three_month_avg=800,
                    yoy_change=0.3,
                    confidence_score=score
                ),
                score=score
            )
            opportunities.append(opp)
            queue.add(opp)
            
        all_opps = queue.get_all()
        
        # Should be sorted by score descending
        assert len(all_opps) == 4
        assert all_opps[0].score == 0.9
        assert all_opps[1].score == 0.7
        assert all_opps[2].score == 0.5
        assert all_opps[3].score == 0.3
        
        # Queue should still have all items
        assert queue.size() == 4


@pytest.mark.asyncio
class TestResearchWorkshop:
    """Test the ResearchWorkshop orchestrator."""
    
    async def test_initialize_agents(self):
        """Test agent initialization."""
        workshop = ResearchWorkshop()
        
        # Since agents aren't implemented yet, just check the placeholder
        await workshop.initialize_agents()
        
        assert len(workshop.agents) == 4
        assert 'trend_scanner' in workshop.agents
        assert 'market_analyzer' in workshop.agents
        assert 'sourcing_scout' in workshop.agents
        assert 'opportunity_evaluator' in workshop.agents
                        
    async def test_run_discovery_cycle_no_trends(self):
        """Test discovery cycle when no trends are found."""
        workshop = ResearchWorkshop()
        
        # Mock agents
        mock_trend_scanner = AsyncMock()
        mock_trend_scanner.execute.return_value = []  # No trends
        
        workshop.agents = {
            'trend_scanner': mock_trend_scanner
        }
        
        # Mock database operations
        with patch('src.agents.research.workshop.get_db'):
            opportunities = await workshop.run_discovery_cycle()
            
        assert len(opportunities) == 0
        mock_trend_scanner.execute.assert_called_once()
        
    async def test_run_discovery_cycle_with_opportunities(self):
        """Test discovery cycle that finds opportunities."""
        workshop = ResearchWorkshop()
        
        # Create test data
        trend = TrendData(
            source=TrendSource.GOOGLE_TRENDS,
            keywords=["eco", "water", "bottle"],
            growth_rate=0.35,
            current_volume=50000,
            three_month_avg=40000,
            yoy_change=0.4,
            confidence_score=0.85
        )
        
        market_analysis = Mock(competition_level="medium", top_competitors=[{"category": "bottles"}])
        suppliers = [Mock() for _ in range(3)]
        
        scored_opportunity = MarketOpportunity(
            id="test-1",
            title="Eco Water Bottle Opportunity",
            description="Test opportunity",
            trend_data=trend,
            market_analysis=market_analysis,
            sourcing_options=suppliers,
            score=0.75
        )
        
        # Mock agents
        mock_trend_scanner = AsyncMock()
        mock_trend_scanner.execute.return_value = [trend]
        
        mock_market_analyzer = AsyncMock()
        mock_market_analyzer.execute.return_value = market_analysis
        
        mock_sourcing_scout = AsyncMock()
        mock_sourcing_scout.execute.return_value = suppliers
        
        mock_evaluator = AsyncMock()
        mock_evaluator.execute.return_value = scored_opportunity
        
        workshop.agents = {
            'trend_scanner': mock_trend_scanner,
            'market_analyzer': mock_market_analyzer,
            'sourcing_scout': mock_sourcing_scout,
            'opportunity_evaluator': mock_evaluator
        }
        
        # Mock database operations
        with patch('src.agents.research.workshop.get_db'):
            opportunities = await workshop.run_discovery_cycle()
            
        assert len(opportunities) == 1
        assert opportunities[0].score == 0.75
        assert opportunities[0].title == "Eco Water Bottle Opportunity"
        
        # Verify agent calls
        mock_trend_scanner.execute.assert_called_once()
        mock_market_analyzer.execute.assert_called_once()
        mock_sourcing_scout.execute.assert_called_once()
        mock_evaluator.execute.assert_called_once()
        
        # Verify opportunity was queued
        assert workshop.opportunity_queue.size() == 1
        
    async def test_discovery_cycle_filters_low_scores(self):
        """Test that low-scoring opportunities are filtered out."""
        workshop = ResearchWorkshop()
        workshop.min_opportunity_score = 0.6
        
        # Create low-scoring opportunity
        trend = TrendData(
            source=TrendSource.GOOGLE_TRENDS,
            keywords=["test"],
            growth_rate=0.25,
            current_volume=1000,
            three_month_avg=900,
            yoy_change=0.1,
            confidence_score=0.5
        )
        
        low_score_opportunity = MarketOpportunity(
            id="test-1",
            title="Low Score Opportunity",
            description="Test",
            trend_data=trend,
            score=0.4  # Below threshold
        )
        
        # Mock agents
        mock_trend_scanner = AsyncMock()
        mock_trend_scanner.execute.return_value = [trend]
        
        mock_market_analyzer = AsyncMock()
        mock_market_analyzer.execute.return_value = Mock(competition_level="low", top_competitors=[])
        
        mock_sourcing_scout = AsyncMock()
        mock_sourcing_scout.execute.return_value = [Mock(), Mock(), Mock()]
        
        mock_evaluator = AsyncMock()
        mock_evaluator.execute.return_value = low_score_opportunity
        
        workshop.agents = {
            'trend_scanner': mock_trend_scanner,
            'market_analyzer': mock_market_analyzer,
            'sourcing_scout': mock_sourcing_scout,
            'opportunity_evaluator': mock_evaluator
        }
        
        # Mock database operations
        with patch('src.agents.research.workshop.get_db'):
            opportunities = await workshop.run_discovery_cycle()
            
        assert len(opportunities) == 0  # Filtered out
        assert workshop.opportunity_queue.size() == 0
        
    async def test_start_stop_discovery_cycle(self):
        """Test starting and stopping the discovery cycle."""
        workshop = ResearchWorkshop()
        workshop.discovery_interval = 0.1  # Short interval for testing
        
        # Mock run_discovery_cycle
        with patch.object(workshop, 'run_discovery_cycle', new_callable=AsyncMock) as mock_run:
            with patch.object(workshop, 'initialize_agents', new_callable=AsyncMock):
                # Start in background
                task = asyncio.create_task(workshop.start_discovery_cycle(continuous=True))
                
                # Let it run for a bit
                await asyncio.sleep(0.3)
                
                # Stop it
                await workshop.stop_discovery_cycle()
                
                # Wait for task to complete
                await task
                
                # Should have been called at least twice
                assert mock_run.call_count >= 2
                assert not workshop.is_running