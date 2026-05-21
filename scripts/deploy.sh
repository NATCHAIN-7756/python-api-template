#!/bin/bash
# Deploy Script - Production
# SCALE OS v10.0

set -e

echo "=========================================="
echo "Python API Template - Production Deploy"
echo "SCALE OS v10.0"
echo "=========================================="

# Check environment variables
if [ -z "$SECRET_KEY" ]; then
    echo "Error: SECRET_KEY environment variable is required"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "Error: DB_PASSWORD environment variable is required"
    exit 1
fi

# Create .env file if not exists
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
SECRET_KEY=${SECRET_KEY}
DB_PASSWORD=${DB_PASSWORD}
EOF
fi

# Pull latest code
echo "Pulling latest code..."
git pull origin main

# Build images
echo "Building Docker images..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Stop old containers
echo "Stopping old containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down

# Start new containers
echo "Starting new containers..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for health check
echo "Waiting for containers to be healthy..."
sleep 10

# Check container status
docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps

# Run database migrations
echo "Running database migrations..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec api-1 alembic upgrade head

echo "=========================================="
echo "Deployment complete!"
echo "=========================================="

# Show logs
echo "Showing logs (Ctrl+C to exit)..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f --tail=100
