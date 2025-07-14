#!/bin/bash

# AWS ECS Deployment Script for Gemini Backend Clone
# Prerequisites: AWS CLI configured, Docker installed

set -e

# Configuration
AWS_REGION="us-east-1"
ECR_REPOSITORY="gemini-backend"
ECS_CLUSTER="gemini-cluster"
ECS_SERVICE="gemini-service"
TASK_DEFINITION="gemini-task"

echo "🚀 Starting AWS ECS deployment..."

# Get AWS account ID
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo "📦 Building Docker image..."
docker build -t ${ECR_REPOSITORY}:latest .

echo "🔐 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

echo "🏷️ Tagging image..."
docker tag ${ECR_REPOSITORY}:latest ${ECR_URI}:latest

echo "⬆️ Pushing image to ECR..."
docker push ${ECR_URI}:latest

echo "📝 Creating task definition..."
cat > task-definition.json << EOF
{
  "family": "${TASK_DEFINITION}",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::${AWS_ACCOUNT_ID}:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "gemini-backend",
      "image": "${ECR_URI}:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/gemini-backend",
          "awslogs-region": "${AWS_REGION}",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {
          "name": "PORT",
          "value": "8000"
        }
      ]
    }
  ]
}
EOF

echo "📋 Registering task definition..."
aws ecs register-task-definition --cli-input-json file://task-definition.json

echo "🔄 Updating ECS service..."
aws ecs update-service \
  --cluster ${ECS_CLUSTER} \
  --service ${ECS_SERVICE} \
  --task-definition ${TASK_DEFINITION}

echo "✅ Deployment completed successfully!"
echo "🌐 Your application will be available at the ALB endpoint"

# Clean up
rm task-definition.json

