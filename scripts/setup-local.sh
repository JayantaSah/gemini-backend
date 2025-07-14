#!/bin/bash

# Local Development Setup Script for Gemini Backend Clone
set -e

echo "🚀 Setting up Gemini Backend Clone for local development..."

# Check if Python 3.11+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.11+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your actual API keys and database credentials"
fi

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "🐳 Docker found. Starting services..."
    
    # Start PostgreSQL and Redis with Docker Compose
    docker-compose up -d postgres redis
    
    # Wait for services to be ready
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Run database migrations
    echo "🗄️ Running database migrations..."
    alembic upgrade head
    
else
    echo "⚠️  Docker not found. Please install PostgreSQL and Redis manually"
    echo "   PostgreSQL: https://www.postgresql.org/download/"
    echo "   Redis: https://redis.io/download"
fi

echo "✅ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Start the development server: python -m uvicorn app.main:app --reload"
echo "3. Start Celery worker: celery -A app.services.celery_app worker --loglevel=info"
echo "4. Visit http://localhost:8000/docs for API documentation"

