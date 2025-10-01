#!/bin/bash

# Production startup script for Chatbot Control Panel

echo "🚀 Starting Chatbot Control Panel in Production Mode"
echo "===================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ docker-compose or docker compose is not available. Please install Docker Compose."
    exit 1
fi

# Use docker compose if available, otherwise fall back to docker-compose
DOCKER_COMPOSE_CMD="docker compose"
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null 2>&1; then
    DOCKER_COMPOSE_CMD="docker-compose"
fi

echo "🔧 Building and starting all services..."

# Build and start all services
$DOCKER_COMPOSE_CMD up --build -d

echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
echo "  - PostgreSQL: " $(docker exec chatbot-postgres pg_isready -U postgres -d chatbot_control_panel 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready")

# Check MinIO
echo "  - MinIO: " $(curl -s http://localhost:9000/minio/health/live > /dev/null && echo "✅ Ready" || echo "❌ Not Ready")

# Check Express API
echo "  - Express API: " $(curl -s http://localhost:3000/health > /dev/null && echo "✅ Ready" || echo "❌ Not Ready")

# Check FastAPI ML
echo "  - FastAPI ML: " $(curl -s http://localhost:8000/health > /dev/null && echo "✅ Ready" || echo "❌ Not Ready")

echo ""
echo "🎉 All services are running!"
echo ""
echo "🌐 Service URLs:"
echo "  - Express API: http://localhost:3000"
echo "  - FastAPI ML: http://localhost:8000"
echo "  - MinIO Console: http://localhost:9001 (admin/minioadmin)"
echo ""
echo "📊 View logs:"
echo "  - All services: $DOCKER_COMPOSE_CMD logs -f"
echo "  - Express API: docker logs -f chatbot-express-api"
echo "  - FastAPI ML: docker logs -f chatbot-fastapi-ml"
echo ""
echo "🛑 To stop all services: $DOCKER_COMPOSE_CMD down"
echo "🗑️  To stop and remove volumes: $DOCKER_COMPOSE_CMD down -v"
