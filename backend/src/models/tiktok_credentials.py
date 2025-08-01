"""Database models for TikTok OAuth credentials."""

from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from cryptography.fernet import Fernet
import os
import base64

from src.core.database import Base


class InstanceTikTokCredentials(Base):
    """TikTok OAuth credentials for an instance."""
    __tablename__ = "instance_tiktok_credentials"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)
    
    # Account identification
    account_name = Column(String(255), nullable=True)  # Optional friendly name for the account
    
    # TikTok User Info
    tiktok_open_id = Column(String(255), nullable=False, unique=True)
    tiktok_union_id = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    
    # OAuth Tokens (encrypted)
    _access_token = Column("access_token", Text, nullable=False)
    _refresh_token = Column("refresh_token", Text, nullable=False)
    
    # Token Expiration
    access_token_expires_at = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=False)
    
    # Scopes
    scopes = Column(JSON, nullable=False)  # List of granted scopes
    
    # Additional User Info
    user_info = Column(JSON, nullable=True)  # Store full user info response
    
    # Status
    is_active = Column(String(20), default="active", nullable=False)  # active, revoked, expired
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    instance = relationship("Instance", backref="tiktok_credentials")
    
    # Indexes and constraints
    __table_args__ = (
        Index('idx_tiktok_credentials_instance', 'instance_id'),
        Index('idx_tiktok_credentials_open_id', 'tiktok_open_id'),
        Index('idx_tiktok_credentials_expires', 'access_token_expires_at'),
        # Ensure same TikTok account can't be connected twice to same instance
        Index('uq_instance_tiktok_open_id', 'instance_id', 'tiktok_open_id', unique=True),
    )
    
    # Encryption key - in production, this should come from environment/secrets
    @property
    def _encryption_key(self):
        key = os.environ.get('ENCRYPTION_KEY')
        if not key:
            # Generate a key for development - DO NOT use in production
            key = Fernet.generate_key().decode()
            os.environ['ENCRYPTION_KEY'] = key
        return key.encode() if isinstance(key, str) else key
    
    @property
    def _cipher(self):
        return Fernet(self._encryption_key)
    
    @hybrid_property
    def access_token(self):
        """Decrypt access token."""
        try:
            return self._cipher.decrypt(self._access_token.encode()).decode()
        except Exception:
            return None
    
    @access_token.setter
    def access_token(self, value):
        """Encrypt access token."""
        if value:
            self._access_token = self._cipher.encrypt(value.encode()).decode()
    
    @hybrid_property
    def refresh_token(self):
        """Decrypt refresh token."""
        try:
            return self._cipher.decrypt(self._refresh_token.encode()).decode()
        except Exception:
            return None
    
    @refresh_token.setter
    def refresh_token(self, value):
        """Encrypt refresh token."""
        if value:
            self._refresh_token = self._cipher.encrypt(value.encode()).decode()
    
    @property
    def is_access_token_expired(self):
        """Check if access token is expired."""
        return datetime.utcnow() >= self.access_token_expires_at
    
    @property
    def is_refresh_token_expired(self):
        """Check if refresh token is expired."""
        return datetime.utcnow() >= self.refresh_token_expires_at
    
    def to_dict(self):
        """Convert to dictionary (without sensitive data)."""
        return {
            'id': str(self.id),
            'instance_id': str(self.instance_id),
            'account_name': self.account_name,
            'tiktok_open_id': self.tiktok_open_id,
            'display_name': self.display_name,
            'avatar_url': self.avatar_url,
            'scopes': self.scopes,
            'is_active': self.is_active,
            'access_token_expires_at': self.access_token_expires_at.isoformat() if self.access_token_expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
        }