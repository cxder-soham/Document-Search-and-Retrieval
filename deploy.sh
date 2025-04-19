#!/bin/bash
set -e

# Variables
AWS_REGION="ap-south-1"
ECR_REPOSITORY="doc-search-repo"
IMAGE_TAG="latest"
CLUSTER_NAME="doc-search-cluster"
SERVICE_NAME="doc-search-service"
TASK_FAMILY="doc-search-task"

# Build and push Docker image
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin 260874765701.dkr.ecr.$AWS_REGION.amazonaws.com
docker build -t $ECR_REPOSITORY:$IMAGE_TAG .
docker tag $ECR_REPOSITORY:$IMAGE_TAG 260874765701.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG
docker push 260874765701.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY:$IMAGE_TAG

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json --region $AWS_REGION

# Create or update ECS service
aws ecs create-service \
    --cluster $CLUSTER_NAME \
    --service-name $SERVICE_NAME \
    --task-definition $TASK_FAMILY \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[<YOUR_SUBNET_ID>],securityGroups=[<YOUR_SECURITY_GROUP_ID>],assignPublicIp=ENABLED}" \
    --region $AWS_REGION || \
aws ecs update-service \
    --cluster $CLUSTER_NAME \
    --service $SERVICE_NAME \
    --task-definition $TASK_FAMILY \
    --desired-count 1 \
    --region $AWS_REGION