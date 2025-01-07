#!/bin/bash

# Set environment variables
export PATH="/opt/blender:$PATH"

# Install necessary dependencies
echo "Updating and installing required packages..."
# apt-get update && \
#     apt-get install -y software-properties-common && \
#     add-apt-repository -y ppa:deadsnakes/ppa && \
#     apt-get update && \
#     apt-get install -y python3.11 python3.11-distutils curl tzdata libxi6 libgconf-2-4 libfontconfig1 libxrender1 libboost-all-dev libgl1-mesa-dev libglu1-mesa libsm-dev libxkbcommon-x11-dev && \
#     curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*

!apt update -y
# !apt upgrade -y
!apt-get install curl libxi6 libgconf-2-4 -y
!apt install libfontconfig1 libxrender1 -y
!apt install libboost-all-dev -y
!apt install libgl1-mesa-dev -y
!apt install libglu1-mesa libsm-dev libxkbcommon-x11-dev -y
!apt update -y
# !apt upgrade -y



# # Create symbolic links for default Python and pip
# ln -sf /usr/bin/python3.11 /usr/bin/python
# ln -sf /usr/bin/python3.11 /usr/bin/python3
# ln -sf /usr/local/bin/pip /usr/bin/pip

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

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p /app/blender /app/uploads /app/output

# Download the .blend model file
MODEL_URL="https://www.dropbox.com/scl/fi/71cm0ehliqk3qapux0fte/Copy-of-ALL-3D_INTERIOR_SCENE-COLECTION120-FNL2CLEAN7-FNL-BAKING_SCENE-CHARR6_LIPSC13FIX2.blend?rlkey=5q9xblrrlxpmpjo17f5fj5yyu&st=xu75gqh8&dl=1"
MODEL_PATH="/app/blender/1.blend"

echo "Downloading model file..."
curl -sSL $MODEL_URL -o $MODEL_PATH

if [ -f "$MODEL_PATH" ]; then
    echo "Model downloaded and saved as $MODEL_PATH"
else
    echo "Failed to download the model file."
    exit 1
fi

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install --no-cache-dir -r requirements.txt
fi

# Start the FastAPI application
echo "Starting FastAPI application..."
exec uvicorn main:app --host 0.0.0.0 --port 8003
