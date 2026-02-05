# 🧠 LLM Prompts Repository

A full-stack web application for social scientists to share and discover LLM prompts for research purposes. Built with FastAPI (Python), React, and PostgreSQL.

![Tech Stack](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

## ✨ Features

### For Users
- 📝 **Browse Prompts** - Explore a curated collection of LLM prompts for social science research
- 🔍 **Smart Search** - Search by title, category, or tags
- 🏷️ **Filter & Sort** - Filter by category, sort by date or popularity
- 📋 **One-Click Copy** - Copy prompts to clipboard instantly
- ➕ **Add Prompts** - Contribute your own prompts to the community
- 🎭 **Anonymous** - No login required, completely anonymous
- 📱 **Responsive** - Works perfectly on desktop, tablet, and mobile
- 🎨 **Grid/List View** - Choose your preferred viewing mode

### Technical Features
- ⚡ **Fast API** - Asynchronous Python backend
- 🎯 **RESTful API** - Clean, well-documented API endpoints
- 🗄️ **PostgreSQL** - Robust database with full-text search
- 🎨 **Modern UI** - Beautiful, responsive design with Tailwind CSS
- 🔄 **Auto-Seeding** - Pre-loaded with example prompts from Wolfram
- 📊 **Statistics** - View counts and category breakdowns
- 🔐 **CORS Ready** - Configured for production deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL 12+

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd llm-prompts-repo
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create PostgreSQL database
createdb promptdb

# Configure environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run the backend
python main.py
```

Backend will run on `http://localhost:8000`

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Configure environment variables
cp .env.example .env
# Default points to localhost:8000, no changes needed for local dev

# Run the frontend
npm run dev
```

Frontend will run on `http://localhost:5173`

### 4. Open the Application

Visit `http://localhost:5173` in your browser!

## 📁 Project Structure

```
llm-prompts-repo/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application file
│   ├── requirements.txt    # Python dependencies
│   ├── .env.example        # Environment variables template
│   └── README.md           # Backend documentation
│
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom hooks
│   │   ├── utils/         # Utilities (API client)
│   │   ├── App.jsx        # Main app component
│   │   └── main.jsx       # Entry point
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── README.md          # Frontend documentation
│
└── README.md              # This file
```

## 🎯 API Endpoints

### Prompts
- `GET /api/prompts` - Get all prompts (with filters)
  - Query params: `category`, `search`, `sort`, `limit`, `offset`
- `POST /api/prompts` - Create a new prompt
- `GET /api/prompts/{id}` - Get a specific prompt (increments views)

### Metadata
- `GET /api/categories` - Get all unique categories
- `GET /api/stats` - Get statistics (total prompts, category counts)

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

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

## 🌱 Seed Data

The application automatically seeds the database with 12 example prompts from the Wolfram Prompt Repository on first startup. These include:

- Sentiment Analysis for Survey Responses
- Qualitative Data Coding Assistant
- Academic Literature Summarizer
- Survey Question Generator
- Text Classification for Social Media
- Focus Group Discussion Analyzer
- Research Hypothesis Generator
- Interview Transcript Thematic Coder
- Policy Document Summarizer
- Mixed Methods Data Integration
- Grant Proposal Abstract Writer
- Ethnographic Field Notes Analyzer

## 🚀 Deployment

### Option 1: Free Hosting (Recommended for Beginners)

#### Backend: Railway

1. Create account at [Railway.app](https://railway.app)
2. Create new project → Add PostgreSQL database
3. Add new service → Connect to your GitHub repo → Select `backend` folder
4. Environment variables are auto-set by Railway
5. Deploy! 🎉

#### Frontend: Vercel

1. Create account at [Vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Configure:
   - Framework: Vite
   - Root Directory: `frontend`
   - Environment Variable: `VITE_API_URL` → Your Railway backend URL
4. Deploy! 🎉

### Option 2: Alternative Free Hosting

#### Backend: Render

1. Create account at [Render.com](https://render.com)
2. New → Web Service → Connect repo
3. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add PostgreSQL database
5. Set `DATABASE_URL` environment variable
6. Deploy!

#### Frontend: Netlify

1. Create account at [Netlify.com](https://netlify.com)
2. Import from GitHub
3. Settings:
   - Base directory: `frontend`
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Environment: `VITE_API_URL` → Your Render backend URL
4. Deploy!

### Database Options (Free Tier)

1. **Supabase** (500MB free)
   - https://supabase.com
   - Includes PostgreSQL + dashboard

2. **Railway** (500 hours/month free)
   - PostgreSQL included with backend

3. **ElephantSQL** (20MB free)
   - https://www.elephantsql.com
   - Dedicated PostgreSQL

## 🧪 Testing

### Backend API Testing

Using curl:
```bash
# Get all prompts
curl http://localhost:8000/api/prompts

# Search prompts
curl "http://localhost:8000/api/prompts?search=sentiment"

# Filter by category
curl "http://localhost:8000/api/prompts?category=Qualitative%20Coding"

# Create a prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Prompt",
    "prompt_text": "This is a test",
    "category": "Testing",
    "tags": ["test"]
  }'
```

Or use the Swagger UI at `http://localhost:8000/docs`

### Frontend Testing

1. Start both backend and frontend
2. Navigate to `http://localhost:5173`
3. Test features:
   - Browse prompts
   - Search and filter
   - Click a prompt to view details
   - Copy a prompt
   - Add a new prompt
   - Switch between grid/list view

### Add New Categories

Edit the `predefinedCategories` array in `frontend/src/pages/AddPromptPage.jsx`

### Modify Seed Data

Edit the `example_prompts` array in `backend/main.py`

## 📊 Tech Stack Details

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Databases** - Async database support
- **SQLAlchemy** - SQL toolkit and ORM
- **Pydantic** - Data validation
- **Uvicorn** - Lightning-fast ASGI server

### Frontend
- **React 18** - UI library with hooks
- **Vite** - Next-generation build tool (10x faster than CRA)
- **Tailwind CSS** - Utility-first CSS framework
- **React Router** - Client-side routing
- **Axios** - HTTP client

### Database
- **PostgreSQL** - Advanced open-source relational database
- JSON support for tags
- Full-text search capabilities
- ACID compliant

## 📈 Scaling Considerations

For high traffic, consider:

1. **Caching**: Add Redis for frequently accessed prompts
2. **CDN**: Use Cloudflare for static assets
3. **Database**: Upgrade PostgreSQL plan or add read replicas
4. **Search**: Implement Elasticsearch for advanced search
5. **Rate Limiting**: Add API rate limiting
6. **Analytics**: Add Plausible or Google Analytics

**Happy prompting! 🚀**

Built with ❤️ for the social science research community
