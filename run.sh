#!/bin/bash

# Set environment variables
export PATH="/opt/blender:$PATH"

# Install necessary dependencies
echo "Updating and installing required packages..."
apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils curl tzdata libxi6 libgconf-2-4 libfontconfig1 libxrender1 libboost-all-dev libgl1-mesa-dev libglu1-mesa libsm-dev libxkbcommon-x11-dev && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create symbolic links for default Python and pip
ln -sf /usr/bin/python3.11 /usr/bin/python
ln -sf /usr/bin/python3.11 /usr/bin/python3
ln -sf /usr/local/bin/pip /usr/bin/pip

# Set Blender version and download URL
BLENDER_VERSION=4.2.2
BLENDER_URL=https://ftp.halifax.rwth-aachen.de/blender/release/Blender4.2/blender-${BLENDER_VERSION}-linux-x64.tar.xz

# Download and extract Blender if not already present
if [ ! -d "/opt/blender" ]; then
    echo "Downloading and extracting Blender..."
    mkdir -p /opt/blender && \
    curl -sSL $BLENDER_URL -o /tmp/blender.tar.xz && \
    tar xf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 && \
    rm /tmp/blender.tar.xz
fi

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install --no-cache-dir -r requirements.txt
fi

# Create directories for uploads and outputs
mkdir -p /data/uploads /data/outputs

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8003
