#!/bin/bash

# Script to start the frontend development server

echo "Starting Homeless Assistant Frontend..."
echo "======================================="

# Navigate to frontend directory
cd "$(dirname "$0")/frontend" || exit

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Dependencies not found. Installing..."
    npm install
fi

# Start the development server
echo ""
echo "Starting React development server on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
