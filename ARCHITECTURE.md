# 🏗️ System Architecture Diagram

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER'S BROWSER                          │
│                     http://localhost:5173                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      REACT FRONTEND                             │
│                         (Vite + React)                          │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   HomePage   │  │ AddPromptPage│  │    Header    │        │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘        │
│         │                  │                                    │
│         └─────────┬────────┘                                   │
│                   │                                             │
│         ┌─────────▼──────────┐                                │
│         │  PromptCard        │                                │
│         │  PromptModal       │                                │
│         │  SearchBar         │                                │
│         └─────────┬──────────┘                                │
│                   │                                             │
│         ┌─────────▼──────────┐                                │
│         │   API Client       │                                │
│         │  (Axios/utils/api) │                                │
│         └─────────┬──────────┘                                │
│                   │                                             │
└───────────────────┼─────────────────────────────────────────────┘
                    │
                    │ REST API Calls
                    │ (HTTP/JSON)
                    │
┌───────────────────▼─────────────────────────────────────────────┐
│                    FASTAPI BACKEND                              │
│                   http://localhost:8000                         │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                  API Endpoints                          │  │
│  │                                                         │  │
│  │  GET  /api/prompts          → List all prompts        │  │
│  │  POST /api/prompts          → Create new prompt       │  │
│  │  GET  /api/prompts/{id}     → Get single prompt       │  │
│  │  GET  /api/categories       → List categories         │  │
│  │  GET  /api/stats            → Get statistics          │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼────────────────────────────────────┐  │
│  │              Pydantic Models                           │  │
│  │         (Data validation & serialization)              │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                         │
│  ┌────────────────────▼────────────────────────────────────┐  │
│  │             SQLAlchemy ORM                             │  │
│  │          (Database queries & operations)               │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                         │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        │ SQL Queries
                        │
┌───────────────────────▼─────────────────────────────────────────┐
│                   PostgreSQL DATABASE                           │
│                   localhost:5432/promptdb                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    prompts Table                         │ │
│  │                                                          │ │
│  │  • id (PRIMARY KEY)                                     │ │
│  │  • title                                                │ │
│  │  • prompt_text                                          │ │
│  │  • category                                             │ │
│  │  • tags (JSON)                                          │ │
│  │  • source                                               │ │
│  │  • views                                                │ │
│  │  • created_at                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Examples

### 1. Browsing Prompts (GET Request)

```
User Opens App
    ↓
HomePage.jsx loads
    ↓
usePrompts() hook called
    ↓
promptsAPI.getPrompts() → axios.get('/api/prompts')
    ↓
FastAPI receives GET /api/prompts
    ↓
Query database: SELECT * FROM prompts ORDER BY created_at DESC
    ↓
PostgreSQL returns results
    ↓
FastAPI formats as JSON
    ↓
React receives data
    ↓
PromptCard components render
    ↓
User sees prompts!
```

### 2. Adding a Prompt (POST Request)

```
User clicks "Add Prompt"
    ↓
AddPromptPage.jsx loads
    ↓
User fills form and clicks submit
    ↓
handleSubmit() called
    ↓
promptsAPI.createPrompt(data) → axios.post('/api/prompts', data)
    ↓
FastAPI receives POST /api/prompts
    ↓
Pydantic validates data
    ↓
SQLAlchemy creates INSERT query
    ↓
INSERT INTO prompts (title, prompt_text, ...) VALUES (...)
    ↓
PostgreSQL saves data and returns ID
    ↓
FastAPI returns created prompt
    ↓
React shows success message
    ↓
User redirected to HomePage
    ↓
New prompt appears in list!
```

### 3. Searching Prompts

```
User types in search box
    ↓
handleSearch() called
    ↓
setFilters({ search: "sentiment" })
    ↓
usePrompts() hook detects change
    ↓
promptsAPI.getPrompts({ search: "sentiment" })
    ↓
FastAPI receives GET /api/prompts?search=sentiment
    ↓
Query: SELECT * FROM prompts 
       WHERE title ILIKE '%sentiment%' 
       OR prompt_text ILIKE '%sentiment%'
    ↓
PostgreSQL returns matching prompts
    ↓
React updates displayed prompts
    ↓
User sees filtered results!
```

### 4. Copying Prompt to Clipboard

```
User clicks "Copy" button on PromptCard
    ↓
handleCopy() called
    ↓
navigator.clipboard.writeText(prompt.prompt_text)
    ↓
Browser copies text to clipboard
    ↓
setCopied(true)
    ↓
Button changes to "✓ Copied!"
    ↓
setTimeout 2 seconds
    ↓
setCopied(false)
    ↓
Button returns to "📋 Copy"
```

---

## Component Hierarchy

```
App.jsx
│
├── Header.jsx
│   ├── Logo/Title
│   ├── Navigation Links
│   └── Add Prompt Button
│
└── Routes
    │
    ├── HomePage.jsx
    │   │
    │   ├── SearchBar.jsx
    │   │   ├── Search Input
    │   │   ├── Category Dropdown
    │   │   ├── Sort Dropdown
    │   │   └── View Toggle (Grid/List)
    │   │
    │   ├── PromptCard.jsx (multiple)
    │   │   ├── Title
    │   │   ├── Category Badge
    │   │   ├── Prompt Preview
    │   │   ├── Tags
    │   │   ├── Copy Button
    │   │   └── Metadata (views, date)
    │   │
    │   └── PromptModal.jsx (conditional)
    │       ├── Full Prompt Text
    │       ├── Copy Button
    │       ├── Tags Display
    │       └── Metadata
    │
    └── AddPromptPage.jsx
        ├── Form
        │   ├── Title Input
        │   ├── Category Select
        │   ├── Prompt Text Area
        │   ├── Tags Input
        │   └── Source Input
        │
        ├── Submit Button
        └── Guidelines Section
```

---

## State Management Flow

```
Frontend State:
┌─────────────────────────────────────────────┐
│ HomePage.jsx                                │
│                                             │
│ States:                                     │
│ • prompts (from usePrompts hook)           │
│ • filters { search, category, sort }       │
│ • selectedPrompt (for modal)               │
│ • viewMode (grid/list)                     │
│                                             │
│ Functions:                                  │
│ • handleSearch()                            │
│ • handleCategoryChange()                    │
│ • handleSortChange()                        │
│ • openPromptModal()                         │
│ • closePromptModal()                        │
└─────────────────────────────────────────────┘
        │
        ├─→ SearchBar receives:
        │   • onSearch callback
        │   • onCategoryChange callback
        │   • onSortChange callback
        │
        ├─→ PromptCard receives:
        │   • prompt data
        │   • onClick callback
        │
        └─→ PromptModal receives:
            • prompt data
            • onClose callback

Backend State:
┌─────────────────────────────────────────────┐
│ PostgreSQL Database                         │
│                                             │
│ Single source of truth for:                │
│ • All prompts                               │
│ • Categories (derived from prompts)        │
│ • View counts                               │
│ • Creation dates                            │
│                                             │
│ No session state (stateless API)           │
└─────────────────────────────────────────────┘
```

---

## Request/Response Cycle

```
Frontend                  Backend                    Database
   │                         │                           │
   │   GET /api/prompts     │                           │
   ├───────────────────────→│                           │
   │                         │   SELECT * FROM prompts   │
   │                         ├──────────────────────────→│
   │                         │                           │
   │                         │   [rows of data]          │
   │                         │←──────────────────────────┤
   │                         │                           │
   │   [JSON array]          │                           │
   │←────────────────────────┤                           │
   │                         │                           │
   │  Update UI with data    │                           │
   └─                        │                           │
                             │                           │

   │   POST /api/prompts     │                           │
   │   {prompt data}         │                           │
   ├───────────────────────→│                           │
   │                         │  Validate with Pydantic   │
   │                         ├─                          │
   │                         │                           │
   │                         │   INSERT INTO prompts     │
   │                         ├──────────────────────────→│
   │                         │                           │
   │                         │   new_id                  │
   │                         │←──────────────────────────┤
   │                         │                           │
   │   {created prompt}      │                           │
   │←────────────────────────┤                           │
   │                         │                           │
   │  Show success, redirect │                           │
   └─                        │                           │
```

---

## Technology Stack Layers

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                   │
│                                                         │
│  React Components (JSX)                                │
│  • Functional components                               │
│  • React Hooks (useState, useEffect, custom)          │
│  • Props & state management                            │
│                                                         │
│  Tailwind CSS                                          │
│  • Utility-first styling                               │
│  • Responsive design                                    │
│  • Custom components                                    │
└─────────────────────────────────────────────────────────┘
                           │
                           │
┌─────────────────────────▼───────────────────────────────┐
│                    APPLICATION LAYER                    │
│                                                         │
│  React Router                                          │
│  • Client-side routing                                 │
│  • Route definitions                                    │
│                                                         │
│  Custom Hooks                                          │
│  • usePrompts - data fetching                          │
│  • useCategories - category data                       │
│                                                         │
│  API Client (Axios)                                    │
│  • HTTP request handling                               │
│  • Response parsing                                     │
│  • Error handling                                       │
└─────────────────────────────────────────────────────────┘
                           │
                     HTTP/JSON
                           │
┌─────────────────────────▼───────────────────────────────┐
│                      API LAYER                          │
│                                                         │
│  FastAPI Framework                                     │
│  • Route handlers (@app.get, @app.post)               │
│  • Request validation                                  │
│  • Response serialization                              │
│  • OpenAPI/Swagger docs                                │
│                                                         │
│  CORS Middleware                                       │
│  • Cross-origin request handling                       │
│                                                         │
│  Pydantic Models                                       │
│  • Request validation                                   │
│  • Response schemas                                     │
│  • Type safety                                          │
└─────────────────────────────────────────────────────────┘
                           │
                           │
┌─────────────────────────▼───────────────────────────────┐
│                   DATA ACCESS LAYER                     │
│                                                         │
│  SQLAlchemy                                            │
│  • Table definitions                                    │
│  • Query building                                       │
│  • ORM operations                                       │
│                                                         │
│  Databases (async library)                             │
│  • Async database operations                           │
│  • Connection pooling                                   │
│  • Query execution                                      │
└─────────────────────────────────────────────────────────┘
                           │
                      SQL Queries
                           │
┌─────────────────────────▼───────────────────────────────┐
│                   DATABASE LAYER                        │
│                                                         │
│  PostgreSQL                                            │
│  • Data storage                                        │
│  • ACID transactions                                    │
│  • Full-text search                                     │
│  • JSON support                                         │
│  • Indexes                                              │
└─────────────────────────────────────────────────────────┘
```

---

## Development vs Production

```
DEVELOPMENT ENVIRONMENT
─────────────────────────────────────────────────
Frontend:  http://localhost:5173  (Vite dev server)
Backend:   http://localhost:8000  (Uvicorn)
Database:  localhost:5432          (Local PostgreSQL)

Features:
• Hot Module Replacement (HMR)
• Source maps
• Detailed error messages
• No minification
• CORS allows all origins


PRODUCTION ENVIRONMENT
─────────────────────────────────────────────────
Frontend:  https://your-app.vercel.app  (Static files on CDN)
Backend:   https://your-api.railway.app (Containerized service)
Database:  Remote PostgreSQL            (Managed database)

Features:
• Minified & optimized code
• Gzip compression
• HTTPS/SSL encryption
• CORS restricted to frontend domain
• Production error handling
• Monitoring & logging
```

---

## Security & Performance

```
SECURITY MEASURES
───────────────────
┌─ Frontend ─────────────────────┐
│ • Input validation             │
│ • XSS prevention (React)       │
│ • HTTPS in production          │
│ • No sensitive data in code    │
└────────────────────────────────┘
         │
         ├─ Backend ────────────────────┐
         │ • SQL injection protection   │
         │   (ORM prevents)             │
         │ • Input validation           │
         │   (Pydantic models)          │
         │ • CORS configuration         │
         │ • Environment variables      │
         │ • No hardcoded secrets       │
         └──────────────────────────────┘
                  │
                  ├─ Database ───────────────┐
                  │ • Strong passwords       │
                  │ • Network isolation      │
                  │ • Regular backups        │
                  │ • Connection encryption  │
                  └──────────────────────────┘

PERFORMANCE OPTIMIZATIONS
────────────────────────────
┌─ Frontend ─────────────────────┐
│ • Code splitting (Vite)        │
│ • Lazy loading                 │
│ • Asset optimization           │
│ • CDN distribution             │
│ • Browser caching              │
└────────────────────────────────┘
         │
         ├─ Backend ────────────────────┐
         │ • Async operations           │
         │ • Connection pooling         │
         │ • Query optimization         │
         │ • Pagination (limit/offset)  │
         └──────────────────────────────┘
                  │
                  ├─ Database ───────────────┐
                  │ • Indexes on columns     │
                  │ • Optimized queries      │
                  │ • VACUUM (maintenance)   │
                  └──────────────────────────┘
```

---

This architecture is:
- ✅ **Scalable** - Can handle growth
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Secure** - Multiple security layers
- ✅ **Fast** - Optimized at every layer
- ✅ **Modern** - Uses current best practices
