#!/bin/bash

# Set environment variables
export DEBIAN_FRONTEND=noninteractive
export TZ=Etc/UTC

# Ensure git is installed
echo "Checking if git is installed..."
if ! command -v git &>/dev/null; then
    echo "Git not found. Installing..."
    apt-get update && apt-get install -y git && apt-get clean
else
    echo "Git is already installed."
fi

# Clone or pull the repository
PROJECT_DIR="/app"
REPO_URL="https://your-git-repository-url.git"  # Replace with your Git repository URL

if [ -d "$PROJECT_DIR/.git" ]; then
    echo "Pulling latest changes from repository..."
    git -C $PROJECT_DIR pull
else
    echo "Cloning repository..."
    git clone $REPO_URL $PROJECT_DIR
fi

# Navigate to the project directory
cd $PROJECT_DIR

# Make sure the second script is executable
chmod +x run.sh

# Execute the second script
./run.sh
