#!/bin/bash

# Development startup script for Chatbot Control Panel

echo "🚀 Starting Chatbot Control Panel in Development Mode"
echo "================================================="

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

echo "📦 Starting infrastructure services (PostgreSQL + MinIO + FastAPI ML)..."

# Start infrastructure services
$DOCKER_COMPOSE_CMD -f docker-compose.dev.yml up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check PostgreSQL
echo "  - PostgreSQL: " $(docker exec chatbot-postgres-dev pg_isready -U postgres -d chatbot_control_panel 2>/dev/null && echo "✅ Ready" || echo "❌ Not Ready")

# Check MinIO
echo "  - MinIO: " $(curl -s http://localhost:9000/minio/health/live > /dev/null && echo "✅ Ready" || echo "❌ Not Ready")

# Check FastAPI ML
echo "  - FastAPI ML: " $(curl -s http://localhost:8000/health > /dev/null && echo "✅ Ready" || echo "❌ Not Ready")

echo ""
echo "🎯 Infrastructure services are starting up!"
echo ""
echo "📝 Next steps:"
echo "  1. Open a new terminal"
echo "  2. Navigate to the express-api directory: cd express-api"
echo "  3. Copy environment file: cp env.example .env"
echo "  4. Edit .env file with your configuration"
echo "  5. Install dependencies: npm install"
echo "  6. Run database migrations: npm run migration:run"
echo "  7. Start the Express API: npm run dev"
echo ""
echo "🌐 Service URLs:"
echo "  - Express API: http://localhost:3000"
echo "  - FastAPI ML: http://localhost:8000"
echo "  - MinIO Console: http://localhost:9001 (admin/minioadmin)"
echo "  - PostgreSQL: localhost:5432"
echo ""
echo "📊 View logs:"
echo "  - All services: $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml logs -f"
echo "  - FastAPI ML only: docker logs -f chatbot-fastapi-ml-dev"
echo ""
echo "🛑 To stop all services: $DOCKER_COMPOSE_CMD -f docker-compose.dev.yml down"
