#!/bin/bash
# Deploy script for production environment
# Usage: ./deploy.sh [target]

set -e

TARGET=${1:-local}

echo "🚀 Deployment Script"
echo "==================="
echo "Target: $TARGET"
echo ""

case $TARGET in
    local)
        echo "📦 Building Docker image..."
        docker build -t matform-ppo:latest --target production .
        echo "✓ Image built successfully"
        
        echo ""
        echo "🚀 Starting services..."
        docker-compose up -d
        echo "✓ Services started"
        
        echo ""
        echo "📊 Service status:"
        docker-compose ps
        ;;
        
    docker-hub)
        echo "🔐 Logging into Docker Hub..."
        docker login
        
        echo "📦 Building and pushing image..."
        docker build -t hermantqin/matform-ppo:latest --target production .
        docker push hermantqin/matform-ppo:latest
        echo "✓ Image pushed to Docker Hub"
        ;;
        
    aws)
        echo "☁️  AWS deployment not yet implemented"
        echo "Next steps:"
        echo "  1. Set up ECR repository"
        echo "  2. Configure ECS/EKS cluster"
        echo "  3. Push Docker image to ECR"
        echo "  4. Deploy to ECS/EKS"
        ;;
        
    *)
        echo "❌ Unknown target: $TARGET"
        echo "Valid targets: local, docker-hub, aws"
        exit 1
        ;;
esac

echo ""
echo "✅ Deployment to $TARGET completed!"
