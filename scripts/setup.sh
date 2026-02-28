#!/bin/bash
# setup.sh - MyHealth AI Development Setup Script

set -e

echo "=== MyHealth AI Setup ==="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is required. Install it from https://python.org"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is required. Install it from https://nodejs.org"
    exit 1
fi

echo "1. Setting up Python virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

echo "2. Installing Python dependencies..."
pip install -r requirements.txt

echo "3. Setting up environment variables..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "  Created .env from .env.example. Please update it with your settings."
fi

echo "4. Running database migrations..."
python manage.py migrate

echo "5. Creating superuser (optional)..."
echo "  Run: python manage.py createsuperuser"

echo "6. Setting up React frontend..."
cd ../frontend
npm install

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start development servers:"
echo "  Backend:  cd backend && source venv/bin/activate && python manage.py runserver"
echo "  Frontend: cd frontend && npm start"
echo ""
echo "To run tests:"
echo "  Backend:  cd backend && python manage.py test"
echo "  Frontend: cd frontend && npm test"
echo ""
echo "To run with Docker:"
echo "  docker-compose up --build"
