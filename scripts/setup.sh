#!/bin/bash

# Default environment
ENVIRONMENT="development"

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        *)
            echo "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "development" && "$ENVIRONMENT" != "production" ]]; then
    echo "Invalid environment: $ENVIRONMENT. Must be 'development' or 'production'."
    exit 1
fi

# Check if running with correct permissions
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run as root"
    exit 1
fi

# Source the check prerequisites script
if [ "$ENVIRONMENT" == "development" ]; then
    source "$(dirname "$0")/check_prerequisites.sh"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies for $ENVIRONMENT environment..."
if [ "$ENVIRONMENT" == "production" ]; then
    pip install --no-cache-dir --no-input --quiet -r requirements.txt
else
    pip install -r requirements.txt
fi

# Check if .env file exists
if [ "$ENVIRONMENT" != "production" ] && [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env.development
    cp .env.example .env.production
    echo "⚠️ Please edit .env.development and/or .env.production file with your actual configuration values"
fi

echo "Setup complete! 🎉"
echo ""
echo "To run in development:"
echo "1. Edit the .env.development file with your configuration values (if you haven't already)"
echo "2. Run 'docker compose -f docker/compose/dev.yml up' to start the development environment"
echo "3. Visit http://localhost:8501 to access the Chainlit app"
echo ""
echo "To run in production:"
echo "1. Edit the .env.production file with your configuration values (if you haven't already)"
echo "2. Run 'docker compose -f docker/compose/prod.yml up' to start the production environment"
echo "3. Visit http://localhost:8501 to access the Chainlit app"