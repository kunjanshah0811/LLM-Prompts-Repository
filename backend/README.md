# LLM Prompts Repository - Backend

FastAPI backend for the LLM Prompts Repository application.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+

### Local Development Setup

1. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up PostgreSQL database:**
```bash
# Create database
createdb promptdb

# Or using psql:
psql -U postgres
CREATE DATABASE promptdb;
```

4. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. **Run the application:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ API Endpoints

### Prompts
- `GET /api/prompts` - Get all prompts (supports filtering, search, sorting)
- `POST /api/prompts` - Create a new prompt
- `GET /api/prompts/{id}` - Get a specific prompt
- `GET /api/categories` - Get all categories
- `GET /api/stats` - Get statistics

### Query Parameters for `/api/prompts`:
- `category` - Filter by category
- `search` - Search in title, tags, and text
- `sort` - Sort by `date` or `popularity`
- `limit` - Max results (default: 100)
- `offset` - Pagination offset

## 🗄️ Database Schema

```sql
CREATE TABLE prompts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    prompt_text TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    tags JSON DEFAULT '[]',
    source VARCHAR(255),
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🌱 Seeding Data

The application automatically seeds the database with example prompts from Wolfram Prompt Repository on first startup.

## 🚀 Deployment

### Railway

1. Create a new project on Railway
2. Add PostgreSQL service
3. Add this backend as a service
4. Set environment variable: `DATABASE_URL` (auto-set by Railway)
5. Deploy!

### Render

1. Create new Web Service
2. Connect your repository
3. Add PostgreSQL database
4. Set environment variables
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🧪 Testing API

Using curl:
```bash
# Get all prompts
curl http://localhost:8000/api/prompts

# Create a prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Prompt",
    "prompt_text": "This is a test prompt",
    "category": "Testing",
    "tags": ["test", "example"]
  }'

# Search prompts
curl "http://localhost:8000/api/prompts?search=sentiment"

# Filter by category
curl "http://localhost:8000/api/prompts?category=Qualitative%20Coding"
```

## 📝 Example Request/Response

**POST /api/prompts**
```json
Request:
{
  "title": "Data Analysis Prompt",
  "prompt_text": "Analyze the following dataset...",
  "category": "Data Analysis",
  "tags": ["analysis", "statistics"],
  "source": "Custom"
}

Response:
{
  "id": 1,
  "title": "Data Analysis Prompt",
  "prompt_text": "Analyze the following dataset...",
  "category": "Data Analysis",
  "tags": ["analysis", "statistics"],
  "source": "Custom",
  "views": 0,
  "created_at": "2024-02-01T12:00:00"
}
```

## 🔧 Environment Variables

- `DATABASE_URL` - PostgreSQL connection string (required)

## 📦 Dependencies

- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Databases** - Async database support
- **SQLAlchemy** - SQL toolkit and ORM
- **Psycopg2** - PostgreSQL adapter
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variable management
