# 📚 Quick Reference Guide

Fast lookup for common tasks and commands.

## 🚀 Quick Start Commands

### Local Development
```bash
# Backend (Terminal 1)
cd backend && source venv/bin/activate && python main.py

# Frontend (Terminal 2)
cd frontend && npm run dev

# Open: http://localhost:5173
```

### Docker (Fastest)
```bash
docker-compose up
# Open: http://localhost:5173
```

---

## 📡 API Endpoints

Base URL: `http://localhost:8000`

### Get All Prompts
```bash
GET /api/prompts?category=X&search=Y&sort=date&limit=100&offset=0
```

### Get Single Prompt
```bash
GET /api/prompts/{id}
```

### Create Prompt
```bash
POST /api/prompts
Content-Type: application/json

{
  "title": "string",
  "prompt_text": "string",
  "category": "string",
  "tags": ["tag1", "tag2"],
  "source": "string" (optional)
}
```

### Get Categories
```bash
GET /api/categories
```

### Get Stats
```bash
GET /api/stats
```

---

## 🔧 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

---

## 🗄️ Database Commands

### PostgreSQL
```bash
# Create database
createdb promptdb

# Connect
psql -U postgres -d promptdb

# List tables
\dt

# Describe table
\d prompts

# Query
SELECT * FROM prompts LIMIT 10;

# Exit
\q
```

### SQL Queries
```sql
-- Get all prompts
SELECT * FROM prompts;

-- Search by title
SELECT * FROM prompts WHERE title ILIKE '%sentiment%';

-- Count by category
SELECT category, COUNT(*) FROM prompts GROUP BY category;

-- Most viewed
SELECT * FROM prompts ORDER BY views DESC LIMIT 10;

-- Recent prompts
SELECT * FROM prompts ORDER BY created_at DESC LIMIT 10;
```

---

## 📦 Package Management

### Backend (Python)
```bash
# Install
pip install -r requirements.txt

# Add package
pip install package_name
pip freeze > requirements.txt

# Update all
pip install --upgrade -r requirements.txt
```

### Frontend (npm)
```bash
# Install
npm install

# Add package
npm install package-name

# Add dev package
npm install -D package-name

# Update all
npm update

# Audit security
npm audit fix
```

---

## 🐛 Debugging

### Backend Logs
```bash
# Backend shows logs in terminal automatically
# Look for:
# - Error tracebacks
# - SQL queries
# - Request logs
```

### Frontend Console
```bash
# Open browser DevTools (F12)
# Console tab shows:
# - JavaScript errors
# - API responses
# - React warnings
```

### API Testing
```bash
# Using curl
curl http://localhost:8000/api/prompts

# Using httpie (prettier)
http localhost:8000/api/prompts

# Swagger UI
http://localhost:8000/docs
```

---

## 🔄 Git Workflow

```bash
# Clone
git clone <url>

# Create branch
git checkout -b feature-name

# Stage changes
git add .

# Commit
git commit -m "Add feature"

# Push
git push origin feature-name

# Pull latest
git pull origin main

# Merge branch
git checkout main
git merge feature-name
```

---

## 🏗️ Build & Deploy

### Build Frontend
```bash
cd frontend
npm run build
# Output: dist/
```

### Build Backend (Docker)
```bash
cd backend
docker build -t prompts-backend .
docker run -p 8000:8000 prompts-backend
```

### Deploy to Railway
```bash
# Backend auto-deploys from GitHub
# Just push:
git push origin main
```

### Deploy to Vercel
```bash
# Frontend auto-deploys from GitHub
# Or manual:
cd frontend
vercel
```

---

## 🧪 Testing

### Test Backend Endpoints
```bash
# Health check
curl http://localhost:8000/

# Get prompts
curl http://localhost:8000/api/prompts

# Create prompt
curl -X POST http://localhost:8000/api/prompts \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","prompt_text":"Test","category":"Testing","tags":[]}'

# Search
curl "http://localhost:8000/api/prompts?search=test"

# Filter
curl "http://localhost:8000/api/prompts?category=Testing"
```

### Test Frontend
```bash
# Just open http://localhost:5173 and:
# - Browse prompts
# - Search
# - Filter
# - Add prompt
# - Copy prompt
```

---

## 📝 Common Code Snippets

### Backend: Add New Endpoint
```python
@app.get("/api/custom")
async def custom_endpoint():
    return {"message": "Hello"}
```

### Frontend: New Component
```jsx
const MyComponent = () => {
  return <div>Hello World</div>;
};

export default MyComponent;
```

### Frontend: API Call
```jsx
import { promptsAPI } from '../utils/api';

const data = await promptsAPI.getPrompts({ category: 'Testing' });
```

### Frontend: State Hook
```jsx
import { useState } from 'react';

const [value, setValue] = useState('initial');
```

---

## 🎨 Styling Reference

### Tailwind Common Classes
```jsx
// Layout
className="container mx-auto px-4 py-8"

// Flexbox
className="flex items-center justify-between"

// Grid
className="grid grid-cols-3 gap-4"

// Button
className="bg-blue-500 text-white px-4 py-2 rounded"

// Input
className="w-full px-4 py-2 border rounded focus:ring-2"

// Card
className="bg-white rounded-lg shadow-md p-6"

// Responsive
className="md:grid-cols-3 lg:grid-cols-4"
```

---

## 🔍 Search & Filter Examples

### Backend Query Parameters
```python
# Search
/api/prompts?search=sentiment

# Filter
/api/prompts?category=Classification

# Sort
/api/prompts?sort=popularity

# Combine
/api/prompts?category=Analysis&search=survey&sort=date&limit=50
```

### Frontend State Management
```jsx
const [filters, setFilters] = useState({
  search: '',
  category: '',
  sort: 'date'
});

const handleSearch = (term) => {
  setFilters(prev => ({ ...prev, search: term }));
};
```

---

## 🔧 Troubleshooting Commands

### Kill Port
```bash
# Port 8000 (backend)
lsof -ti:8000 | xargs kill -9  # Mac/Linux
netstat -ano | findstr :8000   # Windows

# Port 5173 (frontend)
lsof -ti:5173 | xargs kill -9  # Mac/Linux
```

### Clear Caches
```bash
# Backend
rm -rf __pycache__

# Frontend
rm -rf node_modules package-lock.json
npm install
```

### Reset Database
```bash
# Drop and recreate
dropdb promptdb
createdb promptdb

# Restart backend (auto-seeds)
cd backend && python main.py
```

---

## 📊 Database Queries for Analytics

```sql
-- Total prompts
SELECT COUNT(*) FROM prompts;

-- Prompts by category
SELECT category, COUNT(*) as count 
FROM prompts 
GROUP BY category 
ORDER BY count DESC;

-- Most popular prompts
SELECT title, views 
FROM prompts 
ORDER BY views DESC 
LIMIT 10;

-- Recent additions
SELECT title, created_at 
FROM prompts 
ORDER BY created_at DESC 
LIMIT 10;

-- Search tags
SELECT title, tags 
FROM prompts 
WHERE tags::text ILIKE '%survey%';
```

---

## 🚀 Performance Tips

### Backend
```python
# Use async/await
async def get_data():
    return await database.fetch_all(query)

# Limit results
query = query.limit(100)

# Use indexes
# Add to database: CREATE INDEX idx_category ON prompts(category);
```

### Frontend
```jsx
// Lazy loading
const Component = lazy(() => import('./Component'));

// Memoization
const memoizedValue = useMemo(() => expensiveFunction(), [deps]);

// Debounce search
const debouncedSearch = debounce(handleSearch, 300);
```

---

## 🔐 Security Checklist

- [ ] Environment variables in .env (not committed)
- [ ] CORS configured properly
- [ ] SQL injection protected (using ORM)
- [ ] Input validation (Pydantic models)
- [ ] HTTPS in production
- [ ] Regular dependency updates
- [ ] Strong database passwords

---

## 📱 Responsive Breakpoints

```jsx
// Tailwind breakpoints
sm:  640px   // Mobile landscape
md:  768px   // Tablet
lg:  1024px  // Desktop
xl:  1280px  // Large desktop
2xl: 1536px  // Extra large
```

---

## 💾 Backup & Restore

```bash
# Backup database
pg_dump -U postgres promptdb > backup_$(date +%Y%m%d).sql

# Restore database
psql -U postgres promptdb < backup_20240201.sql

# Backup code
git push origin main  # GitHub is your backup!
```

---

## 🎯 Feature Flags

Want to add a feature flag?

```python
# Backend
FEATURE_ENABLED = os.getenv("FEATURE_ENABLED", "false") == "true"

if FEATURE_ENABLED:
    # New feature code
```

```jsx
// Frontend
const FEATURE_ENABLED = import.meta.env.VITE_FEATURE_ENABLED === 'true';

{FEATURE_ENABLED && <NewFeature />}
```

---

## 📚 Helpful Resources

- **FastAPI:** https://fastapi.tiangolo.com
- **React:** https://react.dev
- **Tailwind:** https://tailwindcss.com
- **PostgreSQL:** https://www.postgresql.org/docs
- **Vite:** https://vitejs.dev

---

## 🆘 Emergency Commands

```bash
# Everything broken? Nuclear option:

# Backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend  
rm -rf node_modules package-lock.json
npm install

# Database
dropdb promptdb
createdb promptdb

# Restart everything
cd backend && python main.py  # Terminal 1
cd frontend && npm run dev    # Terminal 2
```

---

**Keep this guide bookmarked for quick reference! 📖**
