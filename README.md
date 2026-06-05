# CABP Client Application

A comprehensive, production-ready CLI client for the Content-Aware Backup Platform (CABP). This application provides an intuitive interface for interacting with CABP backend services without requiring direct API access.

## 🚀 Features

### Core Functionality
- ✅ **Authentication & API Key Management**
- ✅ **File Ingestion** (Single, Large, Batch)
- ✅ **Semantic Search** with AI-powered responses
- ✅ **File & Document Management**
- ✅ **Topology Visualization** (Tree structure)
- ✅ **Health Monitoring** (System & Components)
- ✅ **Component Management** (CRUD operations)
- ✅ **Mapping Explorer** (File-Component relationships)

### Technical Features
- 🎨 Rich terminal UI with colors and formatting
- 🔄 Automatic retry logic with exponential backoff
- 📝 Structured logging with file rotation
- ⚡ Chunked upload for large files
- 🔍 Advanced search with filters
- 📊 Statistics and analytics
- 🌳 Hierarchical topology display
- 💾 Session management

## 📋 Prerequisites

- Python 3.9 or higher
- CABP Backend running at `http://localhost:8000`
- Valid API key

## 🛠️ Installation

### 1. Clone or Navigate to Project

```bash
cd /Users/saniya/Desktop/client_server
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
```

### 3. Activate Virtual Environment

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```env
CABP_API_KEY=your_api_key_here
CABP_BASE_URL=http://localhost:8000/api/v1
```

## 🎯 Quick Start

### Run the Application

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the application
python3 src/main.py
```

### First Time Setup

1. The application will initialize and check backend connectivity
2. You'll see the main menu with 8 options
3. Navigate using number keys (1-8)
4. Follow on-screen prompts for each operation

## 📖 Usage Guide

### Main Menu Options

```
========================================
Content-Aware Backup Platform Client
========================================

1. Authentication & Ingestion
2. Search Operations
3. Management Operations
4. Topology Explorer
5. Health Dashboard
6. Mapping Explorer
7. System Information
8. Exit
```

### 1. Authentication & Ingestion

**Ingest Single File:**
- Upload individual files with metadata
- Automatic processing and chunking
- Real-time progress feedback

**Ingest Large File:**
- Chunked upload for files > 10MB
- Progress tracking
- Automatic retry on failure

**Batch Ingest:**
- Upload multiple files at once
- Parallel processing
- Summary report

### 2. Search Operations

**Semantic Search:**
- Natural language queries
- Similarity-based ranking
- AI-generated summaries

**AI-Powered Query:**
- Ask questions about your data
- Context-aware responses
- Source attribution

**Advanced Search:**
- Filter by product, version, OS
- Date range filtering
- Backup type filtering

### 3. Management Operations

**File Management:**
- List all files with pagination
- View detailed file information
- Delete files and associated data
- File statistics and analytics

**Document Management:**
- List documents
- View document content
- Access document chunks

### 4. Topology Explorer

**View Topology:**
- Hierarchical tree visualization
- Component relationships
- Health status indicators

**Search Components:**
- Find components by ID
- View component paths
- Filter by type

### 5. Health Dashboard

**System Health:**
- Overall system status
- Service availability
- Component health

**Monitoring:**
- Database status
- Embedding service status
- Ollama service status
- Component-level metrics

### 6. Mapping Explorer

**Manage Mappings:**
- Create file-component mappings
- View relationships
- Delete mappings
- Mapping statistics

**Relationship Types:**
- `backed_up_by`
- `stored_in_pool`
- `stored_on_volume`
- `generated_by`
- `managed_by`

### 7. System Information

View comprehensive system information:
- Backend version and status
- File statistics
- Component counts
- Client configuration

## 🏗️ Architecture

```
client_server/
├── src/
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   ├── api_client.py           # HTTP client with retry logic
│   ├── logger.py               # Structured logging
│   ├── error_handler.py        # Exception handling
│   │
│   ├── services/               # Service layer
│   │   ├── auth_service.py
│   │   ├── ingestion_service.py
│   │   ├── search_service.py
│   │   ├── management_service.py
│   │   ├── topology_service.py
│   │   ├── health_service.py
│   │   ├── components_service.py
│   │   └── mappings_service.py
│   │
│   └── ui/                     # User interface
│       ├── menus.py            # Interactive menus
│       └── displays.py         # Display components
│
├── docs/                       # Documentation
│   ├── design.md
│   ├── requirements.md
│   └── implementation.md
│
├── tests/                      # Test suite
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CABP_API_KEY` | API authentication key | Required |
| `CABP_BASE_URL` | Backend API base URL | `http://localhost:8000/api/v1` |
| `CABP_TIMEOUT` | Request timeout (seconds) | `30` |
| `CABP_MAX_RETRIES` | Maximum retry attempts | `3` |
| `CABP_LOG_LEVEL` | Logging level | `INFO` |
| `CABP_LOG_FILE` | Log file path | `cabp_client.log` |
| `CABP_ENVIRONMENT` | Environment name | `development` |

### Configuration File

Edit `src/config.py` to modify default settings or add new configuration options.

## 📊 Logging

Logs are written to `cabp_client.log` with automatic rotation:

```bash
# View logs in real-time
tail -f cabp_client.log

# View last 50 lines
tail -n 50 cabp_client.log

# Search logs
grep "ERROR" cabp_client.log
```

## 🧪 Testing

### Run Connection Test

```bash
source venv/bin/activate
python3 test_connection.py
```

### Expected Output

```
✓ Backend Health: Pass
✓ Configuration: Pass
✓ API Client: Pass
✓ Authentication: Pass

All tests passed! ✓
```

## 🐛 Troubleshooting

### Backend Connection Issues

**Problem:** Cannot connect to backend

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `CABP_BASE_URL` in `.env`
3. Verify network connectivity

### Authentication Errors

**Problem:** 401 Unauthorized

**Solution:**
1. Verify API key in `.env`
2. Check API key hasn't expired
3. Ensure API key has correct permissions

### Import Errors

**Problem:** ModuleNotFoundError

**Solution:**
1. Activate virtual environment: `source venv/bin/activate`
2. Reinstall dependencies: `pip install -r requirements.txt`

### File Upload Failures

**Problem:** Large file upload fails

**Solution:**
1. Use "Ingest Large File" option for files > 10MB
2. Check available disk space
3. Verify file permissions

## 📚 API Documentation

The client interacts with the following CABP API endpoints:

### Authentication
- `POST /api/v1/auth/keys` - Create API key

### Ingestion
- `POST /api/v1/ingest/file` - Ingest single file
- `POST /api/v1/ingest/chunked/init` - Initialize chunked upload
- `POST /api/v1/ingest/chunked/upload` - Upload chunk
- `POST /api/v1/ingest/chunked/finalize` - Finalize upload

### Search
- `POST /api/v1/search/` - Semantic search
- `POST /api/v1/search/query` - AI-powered query

### Management
- `GET /api/v1/management/files` - List files
- `GET /api/v1/management/files/{id}` - Get file details
- `DELETE /api/v1/management/files/{id}` - Delete file
- `GET /api/v1/management/documents` - List documents
- `GET /api/v1/management/documents/{id}` - Get document
- `GET /api/v1/management/documents/{id}/chunks` - Get chunks

### Topology
- `GET /api/v1/topology/` - Get topology
- `POST /api/v1/topology/refresh` - Refresh topology

### Components
- `POST /api/v1/components/` - Create component
- `GET /api/v1/components/` - List components
- `GET /api/v1/components/{id}` - Get component
- `PUT /api/v1/components/{id}` - Update component
- `DELETE /api/v1/components/{id}` - Delete component
- `GET /api/v1/components/types` - Get component types
- `GET /api/v1/components/{id}/children` - Get children
- `GET /api/v1/components/{id}/files` - Get files

### Health
- `GET /api/v1/health/` - System health check
- `GET /api/v1/health/components/{id}` - Component health

### Mappings
- `POST /api/v1/mappings/` - Create mapping
- `GET /api/v1/mappings/` - List mappings
- `DELETE /api/v1/mappings/{id}` - Delete mapping

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Add docstrings to all functions
- Keep functions focused and small

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_api_client.py
```

## 📝 License

This project is part of the Content-Aware Backup Platform.

## 🆘 Support

For issues, questions, or contributions:

1. Check the troubleshooting section
2. Review the documentation in `docs/`
3. Check the logs in `cabp_client.log`
4. Contact the development team

## 🎉 Acknowledgments

Built with:
- [Rich](https://github.com/Textualize/rich) - Terminal formatting
- [Requests](https://requests.readthedocs.io/) - HTTP client
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [Python-dotenv](https://github.com/theskumar/python-dotenv) - Environment management

---

**Version:** 1.0.0  
**Last Updated:** 2026-06-04  
**Status:** Production Ready ✅