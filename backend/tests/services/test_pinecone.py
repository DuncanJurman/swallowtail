"""Tests for Pinecone vector database service."""

import pytest
from unittest.mock import Mock, patch

from src.services.pinecone import PineconeService, PineconeServiceError


class TestPineconeService:
    """Test suite for PineconeService."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.pinecone_api_key = "test-api-key"
        settings.pinecone_index_name = "test-index"
        settings.pinecone_environment = "test-env"
        return settings
    
    @pytest.fixture
    def pinecone_service(self, mock_settings):
        """Create PineconeService instance with mocked settings."""
        with patch("src.services.pinecone.get_settings", return_value=mock_settings):
            return PineconeService()
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        mock_settings = Mock()
        mock_settings.pinecone_api_key = None
        
        with patch("src.services.pinecone.get_settings", return_value=mock_settings):
            with pytest.raises(PineconeServiceError, match="Pinecone API key not configured"):
                PineconeService()
    
    def test_client_initialization(self, pinecone_service):
        """Test that Pinecone client is properly initialized."""
        assert pinecone_service.client is not None
        assert pinecone_service.index_name == "test-index"
    
    @patch("src.services.pinecone.Pinecone")
    def test_create_index_if_not_exists(self, mock_pinecone_class, mock_settings):
        """Test index creation when it doesn't exist."""
        mock_client = Mock()
        mock_pinecone_class.return_value = mock_client
        mock_client.list_indexes.return_value = []
        
        with patch("src.services.pinecone.get_settings", return_value=mock_settings):
            service = PineconeService()
            service.create_index_if_not_exists(dimension=1536)
        
        mock_client.create_index.assert_called_once()
        assert mock_client.create_index.call_args[1]["name"] == "test-index"
        assert mock_client.create_index.call_args[1]["dimension"] == 1536
    
    @patch("src.services.pinecone.Pinecone")
    def test_create_index_already_exists(self, mock_pinecone_class, mock_settings):
        """Test that index creation is skipped when index exists."""
        mock_client = Mock()
        mock_pinecone_class.return_value = mock_client
        mock_index = Mock()
        mock_index.name = "test-index"
        mock_client.list_indexes.return_value = [mock_index]
        
        with patch("src.services.pinecone.get_settings", return_value=mock_settings):
            service = PineconeService()
            service.create_index_if_not_exists(dimension=1536)
        
        mock_client.create_index.assert_not_called()
    
    def test_upsert_vectors(self, pinecone_service):
        """Test upserting vectors to index."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        vectors = [
            {"id": "vec1", "values": [0.1] * 1536, "metadata": {"text": "test1"}},
            {"id": "vec2", "values": [0.2] * 1536, "metadata": {"text": "test2"}}
        ]
        
        result = pinecone_service.upsert_vectors(vectors)
        
        mock_index.upsert.assert_called_once_with(vectors=vectors, namespace="default")
        assert result is True
    
    def test_upsert_vectors_with_namespace(self, pinecone_service):
        """Test upserting vectors with custom namespace."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        vectors = [{"id": "vec1", "values": [0.1] * 1536}]
        namespace = "custom-namespace"
        
        pinecone_service.upsert_vectors(vectors, namespace=namespace)
        
        mock_index.upsert.assert_called_once_with(vectors=vectors, namespace=namespace)
    
    def test_query_similar_vectors(self, pinecone_service):
        """Test querying similar vectors."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        query_vector = [0.1] * 1536
        mock_response = {
            "matches": [
                {"id": "vec1", "score": 0.95, "metadata": {"text": "similar1"}},
                {"id": "vec2", "score": 0.85, "metadata": {"text": "similar2"}}
            ]
        }
        mock_index.query.return_value = mock_response
        
        results = pinecone_service.query_similar_vectors(query_vector, top_k=5)
        
        mock_index.query.assert_called_once_with(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            namespace="default"
        )
        assert results == mock_response["matches"]
    
    def test_query_similar_vectors_with_filter(self, pinecone_service):
        """Test querying with metadata filter."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        query_vector = [0.1] * 1536
        metadata_filter = {"category": "electronics"}
        mock_index.query.return_value = {"matches": []}
        
        pinecone_service.query_similar_vectors(
            query_vector, 
            top_k=5, 
            filter=metadata_filter
        )
        
        mock_index.query.assert_called_once_with(
            vector=query_vector,
            top_k=5,
            include_metadata=True,
            namespace="default",
            filter=metadata_filter
        )
    
    def test_delete_vectors(self, pinecone_service):
        """Test deleting vectors by IDs."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        ids_to_delete = ["vec1", "vec2", "vec3"]
        
        result = pinecone_service.delete_vectors(ids_to_delete)
        
        mock_index.delete.assert_called_once_with(
            ids=ids_to_delete,
            namespace="default"
        )
        assert result is True
    
    def test_delete_all_vectors(self, pinecone_service):
        """Test deleting all vectors in namespace."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        result = pinecone_service.delete_all_vectors()
        
        mock_index.delete.assert_called_once_with(
            delete_all=True,
            namespace="default"
        )
        assert result is True
    
    def test_get_index_stats(self, pinecone_service):
        """Test getting index statistics."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        
        mock_stats = {
            "dimension": 1536,
            "index_fullness": 0.1,
            "namespaces": {
                "default": {"vector_count": 1000}
            }
        }
        mock_index.describe_index_stats.return_value = mock_stats
        
        stats = pinecone_service.get_index_stats()
        
        mock_index.describe_index_stats.assert_called_once()
        assert stats == mock_stats
    
    def test_error_handling_on_upsert(self, pinecone_service):
        """Test error handling during upsert operation."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        mock_index.upsert.side_effect = Exception("API Error")
        
        with pytest.raises(PineconeServiceError, match="Failed to upsert vectors"):
            pinecone_service.upsert_vectors([{"id": "vec1", "values": [0.1] * 1536}])
    
    def test_error_handling_on_query(self, pinecone_service):
        """Test error handling during query operation."""
        mock_index = Mock()
        pinecone_service._index = mock_index
        mock_index.query.side_effect = Exception("Query failed")
        
        with pytest.raises(PineconeServiceError, match="Failed to query vectors"):
            pinecone_service.query_similar_vectors([0.1] * 1536)