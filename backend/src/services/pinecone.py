"""Pinecone vector database service for managing product embeddings."""

import logging
from typing import Optional, List, Dict, Any

from pinecone import Pinecone, ServerlessSpec
from pydantic import BaseModel, Field

from src.core.config import get_settings


logger = logging.getLogger(__name__)


class PineconeServiceError(Exception):
    """Custom exception for Pinecone service errors."""
    pass


class VectorMetadata(BaseModel):
    """Model for vector metadata."""
    text: str
    category: Optional[str] = None
    product_id: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PineconeService:
    """Service for managing vector embeddings in Pinecone."""
    
    def __init__(self):
        """Initialize Pinecone service with configuration."""
        self.settings = get_settings()
        
        if not self.settings.pinecone_api_key:
            raise PineconeServiceError("Pinecone API key not configured")
        
        self.client = Pinecone(api_key=self.settings.pinecone_api_key)
        self.index_name = self.settings.pinecone_index_name
        self._index = None
        
        logger.info(f"Initialized Pinecone service for index: {self.index_name}")
    
    @property
    def index(self):
        """Lazy load and cache index connection."""
        if self._index is None:
            # Get the index host for better performance
            desc = self.client.describe_index(self.index_name)
            self._index = self.client.Index(host=desc.host)
        return self._index
    
    def create_index_if_not_exists(
        self,
        dimension: int = 1536,
        metric: str = "cosine",
        cloud: str = "aws",
        region: str = "us-east-1"
    ) -> bool:
        """Create index if it doesn't exist.
        
        Args:
            dimension: Vector dimension (default 1536 for OpenAI embeddings)
            metric: Distance metric (cosine, euclidean, dotproduct)
            cloud: Cloud provider (aws, gcp, azure)
            region: Cloud region
            
        Returns:
            bool: True if index was created or already exists
        """
        try:
            existing_indexes = [index.name for index in self.client.list_indexes()]
            if self.index_name not in existing_indexes:
                logger.info(f"Creating index: {self.index_name}")
                self.client.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric=metric,
                    spec=ServerlessSpec(
                        cloud=cloud,
                        region=region
                    )
                )
                logger.info(f"Successfully created index: {self.index_name}")
                # Wait for index to be ready
                import time
                time.sleep(5)
            else:
                logger.info(f"Index already exists: {self.index_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create index: {str(e)}")
            raise PineconeServiceError(f"Failed to create index: {str(e)}")
    
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = "default"
    ) -> bool:
        """Upsert vectors to Pinecone index.
        
        Args:
            vectors: List of vector dictionaries with id, values, and metadata
            namespace: Namespace to upsert vectors into
            
        Returns:
            bool: True if successful
        """
        try:
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Successfully upserted {len(vectors)} vectors to namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to upsert vectors: {str(e)}")
            raise PineconeServiceError(f"Failed to upsert vectors: {str(e)}")
    
    def query_similar_vectors(
        self,
        query_vector: List[float],
        top_k: int = 10,
        namespace: str = "default",
        filter: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """Query for similar vectors.
        
        Args:
            query_vector: Query vector
            top_k: Number of results to return
            namespace: Namespace to query
            filter: Metadata filter
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matching vectors with scores
        """
        try:
            query_params = {
                "vector": query_vector,
                "top_k": top_k,
                "include_metadata": include_metadata,
                "namespace": namespace
            }
            
            if filter:
                query_params["filter"] = filter
            
            response = self.index.query(**query_params)
            
            logger.info(f"Query returned {len(response['matches'])} results")
            return response["matches"]
            
        except Exception as e:
            logger.error(f"Failed to query vectors: {str(e)}")
            raise PineconeServiceError(f"Failed to query vectors: {str(e)}")
    
    def delete_vectors(
        self,
        ids: List[str],
        namespace: str = "default"
    ) -> bool:
        """Delete vectors by IDs.
        
        Args:
            ids: List of vector IDs to delete
            namespace: Namespace to delete from
            
        Returns:
            bool: True if successful
        """
        try:
            self.index.delete(ids=ids, namespace=namespace)
            logger.info(f"Successfully deleted {len(ids)} vectors from namespace: {namespace}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {str(e)}")
            raise PineconeServiceError(f"Failed to delete vectors: {str(e)}")
    
    def delete_all_vectors(self, namespace: str = "default") -> bool:
        """Delete all vectors in a namespace.
        
        Args:
            namespace: Namespace to clear
            
        Returns:
            bool: True if successful
        """
        try:
            self.index.delete(delete_all=True, namespace=namespace)
            logger.info(f"Successfully deleted all vectors from namespace: {namespace}")
            return True
            
        except Exception as e:
            # Namespace not found is not an error when deleting all
            if "Namespace not found" in str(e):
                logger.info(f"Namespace {namespace} not found, nothing to delete")
                return True
            logger.error(f"Failed to delete all vectors: {str(e)}")
            raise PineconeServiceError(f"Failed to delete all vectors: {str(e)}")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Returns:
            Dictionary with index statistics
        """
        try:
            stats = self.index.describe_index_stats()
            logger.info(f"Retrieved index stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get index stats: {str(e)}")
            raise PineconeServiceError(f"Failed to get index stats: {str(e)}")