"""Configuration management for the Swallowtail backend."""

from functools import lru_cache
from typing import Optional, Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4.1"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Environment
    environment: str = "development"
    debug: bool = False
    
    # External API Keys
    serper_api_key: Optional[str] = None
    shopify_api_key: Optional[str] = None
    shopify_api_secret: Optional[str] = None
    shopify_store_url: Optional[str] = None
    
    # Pinecone Configuration
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "swallowtail-products"
    pinecone_environment: str = "gcp-starter"
    
    # Database Configuration
    database_url: Optional[str] = None
    database_direct_url: Optional[str] = None
    database_session_pooler_url: Optional[str] = None  # Session pooler for migrations
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None
    
    # TikTok Configuration
    tiktok_client_key: Optional[str] = None
    tiktok_client_secret: Optional[str] = None
    tiktok_redirect_uri: str = "https://skipper-ecom.com/tiktok/callback"
    tiktok_sandbox_mode: bool = True
    
    # Encryption key for token storage
    encryption_key: Optional[str] = None
    
    # Agent Configuration
    max_agent_iterations: int = 10
    agent_timeout_seconds: int = 300
    
    # Logging
    log_level: str = "INFO"
    
    # CORS - Use Optional[str] to prevent automatic JSON parsing
    cors_origins: Optional[str] = None
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list."""
        if not self.cors_origins:
            return ["http://localhost:3000", "http://localhost:3001", "https://skipper-ecom.com"]
        
        # Try to parse as JSON first
        if self.cors_origins.strip().startswith('['):
            try:
                import json
                return json.loads(self.cors_origins)
            except:
                pass
        
        # Otherwise, split by comma
        return [origin.strip() for origin in self.cors_origins.split(',')]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()