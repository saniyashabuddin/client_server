# CABP Client - CABS Backend Connection Guide

## Overview

This client application is designed to connect to the **CABS (Content-Aware Backup System)** backend located at `/Users/saniya/Desktop/cabs/`. The connection is already configured and ready to use.

## Backend Information

### CABS Backend Location
```
/Users/saniya/Desktop/cabs/
```

### API Endpoints

The CABS backend exposes the following API endpoints:

| Endpoint Base | Description |
|---------------|-------------|
| `http://localhost:8000` | Backend server root |
| `http://localhost:8000/api/v1` | API version 1 base path |
| `http://localhost:8000/docs` | Swagger UI documentation |
| `http://localhost:8000/redoc` | ReDoc documentation |

### Available API Routes

Based on the CABS backend (`/Users/saniya/Desktop/cabs/api/main.py`):

```
/api/v1/auth          - Authentication endpoints
/api/v1/ingest        - Ingestion endpoints
/api/v1/search        - Search endpoints
/api/v1/management    - Management endpoints
/api/v1/topology      - Topology endpoints
/api/v1/components    - Components endpoints
/api/v1/health        - Health endpoints
/api/v1/mappings      - Mappings endpoints
```

## Connection Setup

### 1. Start CABS Backend

First, ensure the CABS backend is running:

```bash
# Navigate to CABS directory
cd /Users/saniya/Desktop/cabs

# Activate virtual environment (if using one)
source venv/bin/activate

# Start the backend
python -m api.main
# OR
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The backend should start on `http://localhost:8000`

### 2. Verify Backend is Running

Open your browser and check:
- http://localhost:8000 - Should show API information
- http://localhost:8000/health - Should return `{"status": "healthy"}`
- http://localhost:8000/docs - Should show Swagger UI

### 3. Configure Client

The client is pre-configured to connect to the CABS backend:

```bash
# In the client_server directory
cd /Users/saniya/Desktop/client_server

# Copy environment template
cp .env.example .env

# Edit .env file
nano .env
```

Update the `.env` file:
```env
CABP_BASE_URL=http://localhost:8000/api/v1
CABP_API_KEY=your_api_key_here
```

### 4. Get API Key

You need to create an API key from the CABS backend:

**Option A: Using Swagger UI**
1. Open http://localhost:8000/docs
2. Find the `/api/v1/auth/keys` POST endpoint
3. Click "Try it out"
4. Enter request body:
   ```json
   {
     "name": "my-client-key",
     "permissions": ["ingest", "search", "admin"],
     "expires_in_days": 30
   }
   ```
5. Click "Execute"
6. Copy the returned API key

**Option B: Using curl**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/keys" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-client-key",
    "permissions": ["ingest", "search", "admin"],
    "expires_in_days": 30
  }'
```

**Option C: Using Python**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/auth/keys",
    json={
        "name": "my-client-key",
        "permissions": ["ingest", "search", "admin"],
        "expires_in_days": 30
    }
)
api_key = response.json()["api_key"]
print(f"API Key: {api_key}")
```

### 5. Update Client Configuration

Add the API key to your `.env` file:
```env
CABP_API_KEY=<your_api_key_from_step_4>
```

### 6. Test Connection

```bash
# Activate client virtual environment
source venv/bin/activate

# Test connection with Python
python -c "
from src.api_client import APIClient
client = APIClient()
if client.health_check():
    print('✓ Successfully connected to CABS backend!')
else:
    print('✗ Connection failed')
"
```

## Endpoint Mapping

The client services map to CABS backend endpoints as follows:

### Authentication Service
```
Client: auth_service.authenticate()
→ Backend: POST /api/v1/auth/keys
```

### Ingestion Service
```
Client: ingestion_service.ingest_document()
→ Backend: POST /api/v1/ingest/upload

Client: ingestion_service.ingest_metadata()
→ Backend: POST /api/v1/ingest/metadata
```

### Search Service
```
Client: search_service.semantic_search()
→ Backend: POST /api/v1/search/semantic

Client: search_service.keyword_search()
→ Backend: POST /api/v1/search/keyword
```

### Management Service
```
Client: management_service.list_files()
→ Backend: GET /api/v1/management/files

Client: management_service.view_file()
→ Backend: GET /api/v1/management/files/{id}
```

### Topology Service
```
Client: topology_service.get_topology()
→ Backend: GET /api/v1/topology

Client: topology_service.export_topology()
→ Backend: GET /api/v1/topology/export
```

### Health Service
```
Client: health_service.get_health_status()
→ Backend: GET /api/v1/health

Client: health_service.get_component_health()
→ Backend: GET /api/v1/health/components
```

### Mappings Service
```
Client: mappings_service.get_mappings()
→ Backend: GET /api/v1/mappings

Client: mappings_service.create_mapping()
→ Backend: POST /api/v1/mappings
```

## Troubleshooting

### Connection Refused
**Problem**: Cannot connect to backend
**Solution**:
1. Verify CABS backend is running: `curl http://localhost:8000/health`
2. Check if port 8000 is in use: `lsof -i :8000`
3. Verify CABP_BASE_URL in .env file

### Authentication Failed
**Problem**: 401 Unauthorized error
**Solution**:
1. Verify API key is correct in .env file
2. Check if API key has expired
3. Create a new API key if needed

### Invalid Endpoint
**Problem**: 404 Not Found error
**Solution**:
1. Verify endpoint path in client code
2. Check CABS backend API documentation at http://localhost:8000/docs
3. Ensure CABP_BASE_URL includes `/api/v1`

### Timeout Errors
**Problem**: Request timeout
**Solution**:
1. Increase REQUEST_TIMEOUT in .env file
2. Check backend logs for slow operations
3. Verify network connectivity

## Development Workflow

### Running Both Projects

**Terminal 1 - CABS Backend:**
```bash
cd /Users/saniya/Desktop/cabs
source venv/bin/activate
python -m api.main
```

**Terminal 2 - Client Application:**
```bash
cd /Users/saniya/Desktop/client_server
source venv/bin/activate
python -m src.main
```

### Viewing Backend Logs

CABS backend logs will appear in Terminal 1, showing:
- Incoming requests
- Processing status
- Errors and warnings

### Viewing Client Logs

Client logs are written to `cabp_client.log` in the client directory:
```bash
tail -f cabp_client.log
```

## API Documentation

For complete API documentation, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Spec**: `/Users/saniya/Desktop/cabs/docs/implement/openapi.yaml`

## Summary

✅ **Client Location**: `/Users/saniya/Desktop/client_server/`  
✅ **Backend Location**: `/Users/saniya/Desktop/cabs/`  
✅ **Backend URL**: `http://localhost:8000/api/v1`  
✅ **Connection**: Pre-configured and ready to use  
✅ **Authentication**: API key-based (create via backend)  

The client is fully configured to communicate with the CABS backend. Just ensure the backend is running and you have a valid API key!