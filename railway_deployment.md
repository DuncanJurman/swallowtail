
# Railway Deployment Guide for Swallowtail Backend

This guide documents the complete process of deploying the Swallowtail backend to Railway, including all issues encountered and their solutions.

## Prerequisites

1. Railway account (sign up at https://railway.app)
2. GitHub repository with backend code
3. Supabase database instance
4. Redis instance (Railway provides this)
5. TikTok OAuth app credentials

## Deployment Steps

### 1. Initial Railway Setup

1. **Create New Project**: 
   - Click "New Project" in Railway dashboard
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub account
   - Select the Swallowtail repository

2. **Configure Service Settings**:
   - Set root directory to `/backend`
   - Railway will auto-detect Python/FastAPI application

### 2. Environment Variables

Configure the following environment variables in Railway's service settings:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[database]

# Redis (Railway provides this automatically)
REDIS_URL=redis://default:[password]@[host]:[port]

# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT  # Railway provides this
API_PREFIX=/api/v1
API_VERSION=1.0.0
API_ENV=production

# Security
API_KEY=your-secure-api-key
SECRET_KEY=your-secret-key

# CORS (comma-separated values)
CORS_ORIGINS=https://skipper-ecom.com,https://your-frontend.vercel.app

# Supabase
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_KEY=your-supabase-anon-key

# TikTok OAuth
TIKTOK_CLIENT_KEY=your-client-key
TIKTOK_CLIENT_SECRET=your-client-secret
TIKTOK_REDIRECT_URI=https://swallowtail-production.up.railway.app/api/v1/tiktok/callback
```

### 3. Configuration Files

#### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python run.py",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### Procfile
```
web: python run.py
```

#### requirements.txt
Generated from Poetry dependencies:
```bash
cd backend
poetry export -f requirements.txt --output requirements.txt --without-hashes
```

### 4. Code Modifications for Railway

#### Update run.py
```python
# Use Railway's PORT env var
import os
port = int(os.environ.get("PORT", settings.api_port))
host = "0.0.0.0"  # Railway requires binding to all interfaces
```

#### Update core/config.py for CORS
```python
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
```

## Issues Encountered and Solutions

### 1. Nixpacks Build Failure
**Error**: "Nixpacks was unable to generate a build plan"

**Solution**: 
- Created requirements.txt from Poetry dependencies
- Set root directory to `/backend` in Railway settings

### 2. Poetry Command Not Found
**Error**: "/bin/bash: line 1: poetry: command not found"

**Solution**:
- Changed pre-deploy command from `poetry run alembic upgrade head` to `alembic upgrade head`
- Railway installs from requirements.txt, not Poetry

### 3. CORS_ORIGINS JSON Parsing Error
**Error**: "json.decoder.JSONDecodeError: Expecting value: line 1 column 2"

**Cause**: Railway was passing environment variable as string, not JSON array

**Solution**:
- Modified config.py to handle both JSON and comma-separated formats
- Created `cors_origins_list` property to parse the value appropriately

### 4. Missing deps Module
**Error**: "ModuleNotFoundError: No module named 'src.api.deps'"

**Solution**:
- Created `src/api/deps.py` with authentication dependencies
- Implemented placeholder `get_current_user` function for MVP

### 5. Missing User Model
**Error**: Foreign key constraint violation for instances.user_id

**Solution**:
- Created simple User model in `src/models/user.py`
- Added database migration with default user
- Updated Instance model to include user relationship

### 6. Database Migration Issues
**Error**: Foreign key constraint failures during migration

**Solution**:
- Modified migration to create default user before adding foreign key constraint
- Used `ON CONFLICT DO NOTHING` to handle duplicate key errors

## Redis Configuration

Railway automatically provisions Redis when added to the project:
1. Click "New" in Railway project
2. Select "Database" > "Redis"
3. Railway automatically injects `REDIS_URL` environment variable

## Domain Configuration

After successful deployment:
1. Railway assigns a default domain: `[project-name]-production.up.railway.app`
2. Custom domain can be configured in service settings
3. Update TikTok OAuth redirect URI to match production domain

## Monitoring and Logs

Railway provides:
- Real-time logs in the dashboard
- Deployment history
- Resource usage metrics
- Automatic restart on failures (configured in railway.json)

## Database Migrations

Runs alembic upgrade head as a pre-deploy command

## Dummy Implementations

The following features have placeholder implementations for MVP:

1. **Authentication** (`src/api/deps.py`):
   - `get_current_user()` returns mock user
   - No actual JWT validation

2. **User Access Control**:
   - No verification of user access to instances
   - All endpoints marked with "TODO: Verify user has access"

3. **State Validation** (TikTok OAuth):
   - State parameter not validated against cache/database
   - Instance ID extracted from state without verification

4. **Error Handling**:
   - Basic error responses
   - No detailed logging or monitoring

5. **Rate Limiting**:
   - No rate limiting implemented
   - Relying on TikTok's API limits

## Next Steps

1. Implement proper authentication with JWT
2. Add user access control for instances
3. Implement state validation for OAuth flow
4. Set up proper logging and monitoring
5. Add rate limiting and request throttling
6. Configure automated database migrations
7. Set up staging environment

## Useful Commands

```bash
# View logs
railway logs

# Run command in production
railway run python manage.py migrate

# Open production shell
railway shell

# View environment variables
railway variables
```

## Resources

- [Railway Documentation](https://docs.railway.app)
- [Nixpacks Documentation](https://nixpacks.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)