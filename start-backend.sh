#!/bin/bash

# Script to start the backend server

echo "Starting Homeless Assistant Backend..."
echo "======================================"

# Navigate to backend directory
cd "$(dirname "$0")/backend" || exit

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv

    echo "Installing dependencies..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo ""
    echo "WARNING: .env file not found!"
    echo "Copying .env.example to .env"
    cp .env.example .env
    echo ""
    echo "IMPORTANT: Please edit backend/.env and configure:"
    echo "  1. DATABASE_URL (PostgreSQL connection string)"
    echo "  2. GOOGLE_CLOUD_PROJECT (your GCP project ID)"
    echo "  3. VERTEX_AI_PRIVATE_KEY_ID, VERTEX_AI_PRIVATE_KEY, VERTEX_AI_CLIENT_EMAIL"
    echo ""
    read -p "Press Enter to continue after you've configured the .env file..."
fi

# Check Google Cloud authentication
source .env 2>/dev/null

if [ -n "$VERTEX_AI_PRIVATE_KEY" ] && [ -n "$VERTEX_AI_CLIENT_EMAIL" ]; then
    echo "✓ Using Vertex AI credentials from .env file"
elif [ -n "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    # Using service account file authentication
    if [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
        echo "✓ Using service account: $GOOGLE_APPLICATION_CREDENTIALS"
    else
        echo ""
        echo "WARNING: Service account file not found!"
        echo "Expected: $GOOGLE_APPLICATION_CREDENTIALS"
        echo ""
        echo "Please ensure the service account JSON file exists or configure credentials in .env"
        read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
    fi
else
    echo ""
    echo "WARNING: No Vertex AI authentication configured!"
    echo "Please configure in .env file:"
    echo "  - VERTEX_AI_PRIVATE_KEY_ID"
    echo "  - VERTEX_AI_PRIVATE_KEY"
    echo "  - VERTEX_AI_CLIENT_EMAIL"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Start the server
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python main.py
