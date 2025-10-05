#!/bin/bash
set -e

echo "Starting CyberPrompt..."

# Check if .env exists
if [ ! -f .env ]; then
    echo ".env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your API keys before running again"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Please start Docker first."
    exit 1
fi

# Start services (build only if needed)
echo "🚀 Starting services..."
docker compose up -d --build

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are healthy
echo "Checking service health..."
if docker compose ps | grep -q "unhealthy\|exited"; then
    echo "Some services failed to start properly"
    docker compose logs
    exit 1
fi

echo "✅ CyberPrompt is ready!"
echo "Frontend: http://localhost:3000"
echo "API: http://localhost:8000"
echo "MongoDB Admin: http://localhost:8081"
echo ""
echo "To stop: docker compose down"