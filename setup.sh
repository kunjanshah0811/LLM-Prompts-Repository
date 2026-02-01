#!/bin/bash

echo "🚀 Setting up LLM Prompts Repository..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL not found. You'll need to install it manually."
    echo "   Visit: https://www.postgresql.org/download/"
else
    echo "✅ PostgreSQL found: $(psql --version)"
fi

echo ""
echo "📦 Installing dependencies..."
echo ""

# Backend setup
echo "🔧 Setting up backend..."
cd backend || exit

# Create virtual environment
python3 -m venv venv
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created backend .env file (please configure your database)"
fi

cd ..

# Frontend setup
echo ""
echo "🎨 Setting up frontend..."
cd frontend || exit

# Install dependencies
npm install

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created frontend .env file"
fi

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Create PostgreSQL database:"
echo "   createdb promptdb"
echo ""
echo "2. Configure backend/.env with your database credentials"
echo ""
echo "3. Start the backend (in one terminal):"
echo "   cd backend"
echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
echo "   python main.py"
echo ""
echo "4. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "5. Open http://localhost:5173 in your browser"
echo ""
echo "🐳 Alternatively, use Docker:"
echo "   docker-compose up"
echo ""
echo "Happy prompting! 🎉"
