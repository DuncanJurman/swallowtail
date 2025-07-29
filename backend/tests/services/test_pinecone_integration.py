"""Integration tests for Pinecone service.

These tests require a valid Pinecone API key and will interact with the actual service.
They are marked with pytest.mark.integration and can be skipped in CI.
"""

import pytest
import numpy as np
from typing import List
import os
import time

from src.services.pinecone import PineconeService


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="Pinecone API key not available"
)
class TestPineconeServiceIntegration:
    """Integration tests for PineconeService."""
    
    @pytest.fixture(scope="class")
    def pinecone_service(self):
        """Create PineconeService instance for integration testing."""
        service = PineconeService()
        # Ensure index exists for testing
        service.create_index_if_not_exists(dimension=384)  # Using smaller dimension for testing
        yield service
        # Cleanup after tests
        service.delete_all_vectors(namespace="test-namespace")
    
    @pytest.fixture
    def sample_vectors(self) -> List[dict]:
        """Generate sample vectors for testing."""
        return [
            {
                "id": "test-vec-1",
                "values": np.random.rand(384).tolist(),
                "metadata": {
                    "text": "This is a test product description for electronics",
                    "category": "electronics",
                    "product_id": "prod-123"
                }
            },
            {
                "id": "test-vec-2",
                "values": np.random.rand(384).tolist(),
                "metadata": {
                    "text": "Another test product for home appliances",
                    "category": "home",
                    "product_id": "prod-456"
                }
            },
            {
                "id": "test-vec-3",
                "values": np.random.rand(384).tolist(),
                "metadata": {
                    "text": "Test product for electronics accessories",
                    "category": "electronics",
                    "product_id": "prod-789"
                }
            }
        ]
    
    def test_full_workflow(self, pinecone_service, sample_vectors):
        """Test complete workflow: upsert, query, delete."""
        namespace = "test-namespace"
        
        # 1. Upsert vectors
        result = pinecone_service.upsert_vectors(sample_vectors, namespace=namespace)
        assert result is True
        
        # Wait for vectors to be indexed
        time.sleep(10)
        
        # 2. Get index stats to verify
        stats = pinecone_service.get_index_stats()
        assert namespace in stats.get("namespaces", {})
        assert stats["namespaces"][namespace]["vector_count"] == 3
        
        # 3. Query for similar vectors
        query_vector = np.random.rand(384).tolist()
        results = pinecone_service.query_similar_vectors(
            query_vector,
            top_k=2,
            namespace=namespace
        )
        assert len(results) == 2
        assert all("id" in r and "score" in r for r in results)
        
        # 4. Query with metadata filter
        filtered_results = pinecone_service.query_similar_vectors(
            query_vector,
            top_k=10,
            namespace=namespace,
            filter={"category": {"$eq": "electronics"}}
        )
        # Should only return electronics category items
        assert all(
            r.get("metadata", {}).get("category") == "electronics"
            for r in filtered_results
        )
        
        # 5. Delete specific vectors
        pinecone_service.delete_vectors(["test-vec-1"], namespace=namespace)
        
        # 6. Verify deletion
        stats_after = pinecone_service.get_index_stats()
        assert stats_after["namespaces"][namespace]["vector_count"] == 2
        
        # 7. Delete all remaining vectors
        pinecone_service.delete_all_vectors(namespace=namespace)
        
        # 8. Verify all deleted
        final_stats = pinecone_service.get_index_stats()
        assert namespace not in final_stats.get("namespaces", {}) or \
               final_stats["namespaces"][namespace]["vector_count"] == 0
    
    def test_batch_upsert_performance(self, pinecone_service):
        """Test upserting larger batches of vectors."""
        namespace = "perf-test"
        batch_size = 100
        
        # Generate batch of vectors
        vectors = [
            {
                "id": f"perf-vec-{i}",
                "values": np.random.rand(384).tolist(),
                "metadata": {
                    "text": f"Performance test vector {i}",
                    "batch_id": "perf-test-1"
                }
            }
            for i in range(batch_size)
        ]
        
        # Upsert batch
        result = pinecone_service.upsert_vectors(vectors, namespace=namespace)
        assert result is True
        
        # Wait for indexing
        time.sleep(10)
        
        # Verify count
        stats = pinecone_service.get_index_stats()
        assert stats["namespaces"][namespace]["vector_count"] == batch_size
        
        # Cleanup
        pinecone_service.delete_all_vectors(namespace=namespace)
    
    def test_namespace_isolation(self, pinecone_service, sample_vectors):
        """Test that namespaces are properly isolated."""
        namespace1 = "namespace-1"
        namespace2 = "namespace-2"
        
        # Upsert to different namespaces
        pinecone_service.upsert_vectors(sample_vectors[:2], namespace=namespace1)
        pinecone_service.upsert_vectors(sample_vectors[2:], namespace=namespace2)
        
        # Wait for indexing
        time.sleep(10)
        
        # Query each namespace
        query_vector = np.random.rand(384).tolist()
        
        results1 = pinecone_service.query_similar_vectors(
            query_vector,
            top_k=10,
            namespace=namespace1
        )
        results2 = pinecone_service.query_similar_vectors(
            query_vector,
            top_k=10,
            namespace=namespace2
        )
        
        # Verify isolation
        assert len(results1) == 2
        assert len(results2) == 1
        
        ids1 = {r["id"] for r in results1}
        ids2 = {r["id"] for r in results2}
        assert ids1.isdisjoint(ids2)  # No overlap
        
        # Cleanup
        pinecone_service.delete_all_vectors(namespace=namespace1)
        pinecone_service.delete_all_vectors(namespace=namespace2)