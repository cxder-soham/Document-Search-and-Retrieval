# Document Search and Retrieval

A simple document search system using Flask, Elasticsearch, and AWS S3, deployed on AWS ECS Fargate.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables in `.env`:

3. Run locally: `docker-compose up`

## Deployment

1. Configure AWS CLI: `aws configure`
2. Update `deploy.sh` and `ecs-task-definition.json` with your AWS Account ID, subnet, and security group.
3. Run: `bash deploy.sh`

## Usage

- Upload: `POST /upload` with a file in the `file` field.
- Search: `GET /search?q=<query>`