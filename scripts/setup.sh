#!/bin/bash

# Check if running with correct permissions
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root"
    exit 1
fi

# Source the check prerequisites script
source "$(dirname "$0")/check_prerequisites.sh"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️ Please edit .env file with your actual configuration values"
fi

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p apps/frontend/static
mkdir -p apps/backend/static
mkdir -p common/mcp/static

echo "Setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your configuration values"
echo "2. Run 'docker compose -f docker/compose/dev.yml up' to start the development environment"
echo "3. Visit http://localhost:8501 to access the frontend"