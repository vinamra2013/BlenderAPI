#!/bin/bash

# Variables
IMAGE_NAME="blender_fastapi"
CONTAINER_NAME="blender_renderer"
DOCKERFILE_PATH="./Dockerfile"

# Check if a container with the specified name is running
if docker ps -q -f name=$CONTAINER_NAME; then
  echo "Stopping and removing existing container: $CONTAINER_NAME..."
  docker stop $CONTAINER_NAME  # Stop the container by name
  docker rm $CONTAINER_NAME    # Remove the container by name
fi

# Build the new Docker image
echo "Building Docker image: $IMAGE_NAME..."
docker build -t $IMAGE_NAME -f $DOCKERFILE_PATH .

# Run the container
echo "Starting new container: $CONTAINER_NAME..."
docker run -d --name $CONTAINER_NAME \
  -v "$(pwd)/data/uploads:/data/uploads" \
  -v "$(pwd)/data/outputs:/data/outputs" \
  -p 8000:8000 \
  $IMAGE_NAME

echo "Container started. API is accessible at http://localhost:8000"
