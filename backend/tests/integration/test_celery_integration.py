"""Integration tests for Celery task queue."""
import pytest
import time
from celery.result import AsyncResult

from src.core.celery_app import celery_app
from src.core.tasks import ping, process_market_research, check_celery_health


class TestCeleryIntegration:
    """Integration tests that require a running Celery worker."""
    
    @pytest.mark.integration
    def test_ping_task_execution(self):
        """Test the simple ping task executes successfully."""
        result = ping.delay()
        assert isinstance(result, AsyncResult)
        
        # Wait for result with timeout
        response = result.get(timeout=10)
        assert response == "pong"
        assert result.successful()
    
    @pytest.mark.integration
    def test_market_research_task_execution(self):
        """Test market research task processes correctly."""
        test_data = {"query": "trending products 2024", "market": "US"}
        
        result = process_market_research.delay(test_data)
        assert isinstance(result, AsyncResult)
        
        # Wait for result
        response = result.get(timeout=10)
        assert response["status"] == "completed"
        assert response["products_found"] == 3
        assert response["data"] == test_data
    
    @pytest.mark.integration
    def test_celery_health_with_running_worker(self):
        """Test health check detects running worker."""
        # Give worker time to register
        time.sleep(2)
        
        health = check_celery_health()
        
        # This test will only pass if worker is running
        # Otherwise it will show unhealthy status
        if health["status"] == "healthy":
            assert len(health["workers"]) > 0
            assert "celery@" in health["workers"][0]
        else:
            pytest.skip("No Celery worker running - skipping integration test")
    
    @pytest.mark.integration
    def test_task_retry_on_failure(self):
        """Test task retry mechanism on failure."""
        from src.core.tasks import agent_task
        
        call_count = 0
        
        @agent_task
        def failing_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Simulated failure")
            return "success"
        
        # This would test retry logic if we had a way to mock failures
        # For now, we'll skip this as it requires more complex setup
        pytest.skip("Retry testing requires mock setup")
    
    @pytest.mark.integration
    def test_task_timeout(self):
        """Test task timeout handling."""
        from src.core.tasks import background_task
        
        @background_task
        def long_running_task():
            time.sleep(60)  # Longer than timeout
            return "should not reach here"
        
        # This would test timeout if we could configure shorter timeouts
        # For now, we'll skip this as it requires configuration changes
        pytest.skip("Timeout testing requires configuration setup")