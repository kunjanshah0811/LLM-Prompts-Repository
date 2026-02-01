# 🚀 Complete Setup Guide for Beginners

This guide will walk you through setting up the LLM Prompts Repository from scratch, even if you're new to web development.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installing Prerequisites](#installing-prerequisites)
3. [Getting the Code](#getting-the-code)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Running the Application](#running-the-application)
7. [Common Issues](#common-issues)

---

## Prerequisites

You'll need to install these tools:

- **Python 3.8+** - Backend programming language
- **Node.js 18+** - Frontend build tool
- **PostgreSQL 12+** - Database
- **Git** - Version control (to download the code)
- **Text Editor** - VS Code recommended

---

## Installing Prerequisites

### Windows

#### 1. Install Python
1. Visit [python.org/downloads](https://www.python.org/downloads/)
2. Download Python 3.11 (or latest)
3. **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click "Install Now"
5. Verify:
   ```cmd
   python --version
   ```

#### 2. Install Node.js
1. Visit [nodejs.org](https://nodejs.org/)
2. Download LTS version (18.x or higher)
3. Run installer with default options
4. Verify:
   ```cmd
   node --version
   npm --version
   ```

#### 3. Install PostgreSQL
1. Visit [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Download installer
3. During installation:
   - Remember your password (you'll need it!)
   - Default port: 5432
   - Install pgAdmin 4
4. Verify:
   ```cmd
   psql --version
   ```

#### 4. Install Git
1. Visit [git-scm.com](https://git-scm.com/)
2. Download and install
3. Use default options
4. Verify:
   ```cmd
   git --version
   ```

#### 5. Install VS Code (Optional but recommended)
1. Visit [code.visualstudio.com](https://code.visualstudio.com/)
2. Download and install

### macOS

#### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Python
```bash
brew install python@3.11
python3 --version
```

#### 3. Install Node.js
```bash
brew install node@18
node --version
npm --version
```

#### 4. Install PostgreSQL
```bash
brew install postgresql@15
brew services start postgresql@15
psql --version
```

#### 5. Install Git
```bash
brew install git
git --version
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python
sudo apt install python3 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Git
sudo apt install git

# Verify installations
python3 --version
node --version
psql --version
git --version
```

---

## Getting the Code

### Option 1: Download ZIP
1. Go to the GitHub repository
2. Click green "Code" button
3. Click "Download ZIP"
4. Extract to a folder (e.g., `C:\Projects\llm-prompts-repo`)

### Option 2: Clone with Git
```bash
git clone <repository-url>
cd llm-prompts-repo
```

---

## Backend Setup

### Step 1: Create Database

#### Windows
1. Open "pgAdmin 4" (installed with PostgreSQL)
2. Right-click "Databases" → "Create" → "Database"
3. Name: `promptdb`
4. Click "Save"

**OR using Command Line:**
```cmd
createdb -U postgres promptdb
```

#### macOS/Linux
```bash
createdb promptdb
```

**OR using psql:**
```bash
psql -U postgres
CREATE DATABASE promptdb;
\q
```

### Step 2: Navigate to Backend Directory

```bash
cd backend
```

### Step 3: Create Virtual Environment

#### Windows
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal.

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL drivers
- Other dependencies

### Step 5: Configure Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file:
   ```env
   DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/promptdb
   ```
   
   Replace `yourpassword` with your PostgreSQL password.

### Step 6: Test Backend

```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test it:** Open browser to `http://localhost:8000/docs`

You should see the API documentation!

**Stop the server:** Press `Ctrl+C`

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

Open a **NEW** terminal (keep backend running if you want to test):

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install:
- React
- Vite
- Tailwind CSS
- React Router
- Axios
- Other dependencies

This may take 2-5 minutes.

### Step 3: Configure Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. The default `.env` should work for local development:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

### Step 4: Test Frontend

```bash
npm run dev
```

You should see:
```
  VITE v5.0.12  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Test it:** Open browser to `http://localhost:5173`

You should see the app!

---

## Running the Application

You need **TWO** terminals running simultaneously:

### Terminal 1: Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python main.py
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

### Access the App
Open your browser to: `http://localhost:5173`

---

## Using the Application

### Browse Prompts
1. Main page shows all prompts
2. Use search bar to find specific prompts
3. Filter by category
4. Sort by date or popularity
5. Toggle grid/list view

### View Prompt Details
1. Click any prompt card
2. Modal opens with full details
3. Click "Copy Prompt" to copy to clipboard
4. Press ESC or click X to close

### Add a Prompt
1. Click "+ Add Prompt" button
2. Fill out the form:
   - Title (required)
   - Category (required)
   - Prompt Text (required)
   - Tags (optional, comma-separated)
   - Source (optional)
3. Click "Add Prompt"
4. You'll be redirected to home page

### Example: Adding a Prompt

**Title:**
```
Email Response Generator
```

**Category:**
```
Academic Writing
```

**Prompt Text:**
```
Write a professional email response to {request_type} regarding {topic}. 

The email should:
1. Be polite and professional
2. Address the main points
3. Suggest next steps if applicable

Context: {additional_context}
```

**Tags:**
```
email, communication, professional
```

**Source:**
```
Custom
```

---

## Common Issues

### Issue: "Command not found: python"

**Solution (Windows):**
- Use `python` instead of `python3`
- OR reinstall Python and check "Add to PATH"

**Solution (Mac/Linux):**
- Use `python3` instead of `python`

### Issue: "Command not found: npm"

**Solution:**
- Reinstall Node.js
- Make sure to restart terminal after installation

### Issue: Database connection error

**Error:**
```
could not connect to server: Connection refused
```

**Solution:**
1. Make sure PostgreSQL is running:
   - **Windows:** Check Services, start "postgresql" service
   - **Mac:** `brew services start postgresql@15`
   - **Linux:** `sudo systemctl start postgresql`

2. Check your `.env` DATABASE_URL:
   - Make sure username is correct (usually `postgres`)
   - Make sure password is correct
   - Make sure database name is `promptdb`

### Issue: Port already in use

**Error:**
```
Address already in use
```

**Solution:**

**Windows:**
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Mac/Linux:**
```bash
lsof -ti:8000 | xargs kill -9
```

### Issue: Frontend can't reach backend

**Solution:**
1. Make sure backend is running on port 8000
2. Check `frontend/.env` has `VITE_API_URL=http://localhost:8000`
3. Clear browser cache
4. Check browser console for errors (F12)

### Issue: "Module not found" errors

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue: Database doesn't have seed data

**Solution:**
```bash
# The app seeds automatically on first run
# If data is missing, restart the backend:
cd backend
python main.py
```

The console should show:
```
✅ Seeded database with 12 example prompts
```

---

## Next Steps

### Customize the App

1. **Change colors:**
   - Edit `frontend/tailwind.config.js`

2. **Add more categories:**
   - Edit `frontend/src/pages/AddPromptPage.jsx`
   - Look for `predefinedCategories`

3. **Modify seed data:**
   - Edit `backend/main.py`
   - Look for `example_prompts`

### Deploy to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

**Quick options:**
- **Free & Easy:** Railway (backend) + Vercel (frontend)
- **Alternative:** Render (backend) + Netlify (frontend)

### Learn More

**Backend (FastAPI):**
- Official docs: https://fastapi.tiangolo.com
- API docs (when running): http://localhost:8000/docs

**Frontend (React):**
- Official docs: https://react.dev
- Tailwind CSS: https://tailwindcss.com

**Database (PostgreSQL):**
- Official docs: https://www.postgresql.org/docs

---

## Getting Help

If you're stuck:

1. **Check the error message carefully**
   - Copy the full error
   - Search Google with the error message

2. **Check this guide's Common Issues section**

3. **Check the main README.md**

4. **Check platform documentation**
   - FastAPI docs
   - React docs
   - PostgreSQL docs

5. **Ask for help**
   - Open GitHub issue
   - Include:
     - What you were trying to do
     - What happened instead
     - Full error message
     - Your operating system

---

## Useful Commands

### Backend

```bash
# Activate virtual environment
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python main.py

# Deactivate virtual environment
deactivate
```

### Frontend

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database

```bash
# Connect to database
psql -U postgres -d promptdb

# List databases
psql -U postgres -l

# Backup database
pg_dump -U postgres promptdb > backup.sql

# Restore database
psql -U postgres promptdb < backup.sql
```

### Git

```bash
# Check status
git status

# Pull latest changes
git pull

# See changes
git diff
```

---

## Video Tutorial (Recommended)

For visual learners, search YouTube for:
- "FastAPI tutorial"
- "React tutorial"
- "PostgreSQL tutorial"

---

**Congratulations! You're now running a full-stack web application! 🎉**

Experiment, break things, and learn. That's how you improve!
