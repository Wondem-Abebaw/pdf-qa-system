#!/bin/bash

# PDF Q&A System - Quick Setup Script
# This script sets up the project and runs it locally

set -e

echo "🚀 PDF Q&A System - Quick Setup"
echo "================================"

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
if (( $(echo "$python_version < 3.10" | bc -l) )); then
    echo "❌ Error: Python 3.10+ required. Current version: $python_version"
    exit 1
fi
echo "✓ Python $python_version detected"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Setup environment file
echo ""
if [ ! -f ".env" ]; then
    echo "Setting up environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENAI_API_KEY"
    echo ""
    read -p "Press Enter to open .env in editor..."
    ${EDITOR:-nano} .env
else
    echo "✓ .env file already exists"
fi

# Create data directory
echo ""
echo "Creating data directories..."
mkdir -p data/chroma_db
echo "✓ Data directories created"

# Run the application
echo ""
echo "================================"
echo "Setup complete! Starting application..."
echo "================================"
echo ""
streamlit run src/app.py
