#!/bin/bash

# Township 311 Request Management System Deployment Script

set -e

echo "🚀 Starting Township 311 Request Management System deployment..."

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p postgres_data
mkdir -p redis_data

# Set proper permissions
chmod 755 uploads
chmod 755 logs

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your configuration before continuing."
    echo "   Especially update the SECRET_KEY and POSTGRES_PASSWORD!"
    exit 1
fi

# Validate environment variables
echo "🔍 Validating environment configuration..."
if grep -q "your_secret_key_change_this_in_production" .env; then
    echo "❌ Please change the SECRET_KEY in .env file!"
    exit 1
fi

if grep -q "your_secure_password_here" .env; then
    echo "❌ Please change the POSTGRES_PASSWORD in .env file!"
    exit 1
fi

# Pull latest images
echo "📥 Pulling latest Docker images..."
if command -v docker compose &> /dev/null; then
  docker compose pull
else
  docker-compose pull
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
if command -v docker compose &> /dev/null; then
  docker compose down --remove-orphans
else
  docker-compose down --remove-orphans
fi

# Build and start services
echo "🏗️  Building and starting services..."
ARCH=$(uname -m || echo "")
if [ "$ARCH" = "aarch64" ]; then
  echo "🧩 ARM architecture detected. Enabling multi-arch emulation..."
  sudo docker run --privileged --rm tonistiigi/binfmt --install all || true
fi

if command -v docker compose &> /dev/null; then
  set +e
  docker compose up -d --build
  STATUS=$?
  if [ $STATUS -ne 0 ] && [ "$ARCH" = "aarch64" ]; then
    echo "⚠️  Compose failed. Retrying with amd64 default platform for compatibility..."
    export DOCKER_DEFAULT_PLATFORM=linux/amd64
    docker compose up -d --build
  fi
  set -e
else
  docker-compose up -d --build
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🏥 Checking service health..."
if command -v docker compose &> /dev/null; then
  backend_healthy=$(docker compose ps backend | grep -c "healthy" || echo "0")
  frontend_healthy=$(docker compose ps frontend | grep -c "healthy" || echo "0")
  db_healthy=$(docker compose ps db | grep -c "healthy" || echo "0")
else
  backend_healthy=$(docker-compose ps backend | grep -c "healthy" || echo "0")
  frontend_healthy=$(docker-compose ps frontend | grep -c "healthy" || echo "0")
  db_healthy=$(docker-compose ps db | grep -c "healthy" || echo "0")
fi

if [ "$backend_healthy" -eq "0" ]; then
    echo "⚠️  Backend service may not be healthy. Check logs with: docker-compose logs backend"
fi

if [ "$db_healthy" -eq "0" ]; then
    echo "⚠️  Database service may not be healthy. Check logs with: docker-compose logs db"
fi

# Test API endpoint
echo "🧪 Testing API endpoint..."
max_attempts=10
attempt=1
while [ $attempt -le $max_attempts ]; do
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        echo "✅ API is responding!"
        break
    else
        echo "⏳ Attempt $attempt/$max_attempts: API not ready yet..."
        sleep 10
        attempt=$((attempt + 1))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    echo "❌ API is not responding after $max_attempts attempts."
    echo "   Check logs with: docker-compose logs backend"
    exit 1
fi

# Display service status
echo ""
echo "📊 Service Status:"
if command -v docker compose &> /dev/null; then
  docker compose ps
else
  docker-compose ps
fi

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📍 Access your application:"
echo "   Frontend: http://localhost:8080"
echo "   API Documentation: http://localhost:8080/docs"
echo "   API Health Check: http://localhost:8080/health"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker compose logs -f [service_name]"
echo "   Stop services: docker compose down"
echo "   Restart services: docker compose restart"
echo "   Update services: docker compose pull && docker compose up -d"
echo ""
echo "⚠️  Important: Make sure to configure your firewall and SSL certificates for production use!"
