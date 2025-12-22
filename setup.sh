#!/bin/bash

# JeweledTech Agentic OS Setup Script
# This script helps you set up your environment for running the Agentic OS

set -e

echo "======================================"
echo "🤖 JeweledTech Agentic OS Setup"
echo "======================================"
echo

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo
    echo "🔧 Please review and update the .env file with your specific configuration."
    echo "   The default settings should work for most local development scenarios."
    echo
else
    echo "✅ .env file already exists"
    echo
fi

# Pull required Docker images
echo "🐳 Pulling required Docker images..."
echo "This may take a few minutes on first run..."
echo

docker pull ollama/ollama:latest
echo "✅ Ollama image pulled"

# Check if user wants to download a model
echo
read -p "Would you like to download the default LLM model (llama3.2:latest)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📥 Downloading LLM model..."
    echo "This will take several minutes depending on your internet connection..."
    
    # Start Ollama temporarily to download the model
    docker run -d --name ollama-setup -v ollama:/root/.ollama ollama/ollama:latest
    sleep 5
    docker exec ollama-setup ollama pull llama3.2:latest
    docker stop ollama-setup
    docker rm ollama-setup
    
    echo "✅ Model downloaded successfully"
else
    echo "⚠️  Skipping model download. You'll need to download it manually later."
fi

echo
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo
echo "To start your Agentic OS, run:"
echo "  docker-compose up -d"
echo
echo "Then open your browser to:"
echo "  http://localhost:3000"
echo
echo "For more information, visit:"
echo "  https://github.com/jeweledtech/agentic-framework"
echo "  https://jeweledtech.com"
echo