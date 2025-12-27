#!/bin/bash

# LogGuard Setup and Run Script

echo "=========================================="
echo "  LogGuard - Intelligent IT Audit System"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p data models logs

# Check if model exists
if [ ! -f "models/anomaly_detector.pkl" ]; then
    echo ""
    echo "Training anomaly detection model..."
    python3 train_model.py
    
    if [ $? -ne 0 ]; then
        echo "Error: Failed to train model"
        exit 1
    fi
    
    echo "✓ Model trained successfully"
else
    echo "✓ Model already exists"
fi

# Start the application
echo ""
echo "=========================================="
echo "Starting LogGuard Web Application..."
echo "=========================================="
echo ""
echo "Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 web_app/app.py
