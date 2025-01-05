# Use the BlenderGrid Blender image as the base
# FROM blendergrid/blender:latest
FROM nvidia/cudagl:11.3.0-devel-ubuntu20.04

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Set environment variables to make apt-get non-interactive
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Install necessary dependencies, tools, and Python 3.11
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.11 python3.11-distutils curl tzdata libxi6 libgconf-2-4 libfontconfig1 libxrender1 libboost-all-dev libgl1-mesa-dev libglu1-mesa libsm-dev libxkbcommon-x11-dev && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create symbolic links for default Python and pip
RUN ln -sf /usr/bin/python3.11 /usr/bin/python && \
    ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/local/bin/pip /usr/bin/pip


# Set Blender version and download URL
ENV BLENDER_VERSION=4.2.2
ENV BLENDER_URL=https://ftp.halifax.rwth-aachen.de/blender/release/Blender4.3/blender-${BLENDER_VERSION}-linux-x64.tar.xz

# Download and extract Blender
RUN mkdir /opt/blender && \
    curl -sSL $BLENDER_URL -o /tmp/blender.tar.xz && \
    tar xf /tmp/blender.tar.xz -C /opt/blender --strip-components=1 && \
    rm /tmp/blender.tar.xz

# Add Blender to PATH
ENV PATH="/opt/blender:$PATH"

# RUN apt-get update && apt-get install -y \
#     python3.11 python3-pip blender tzdata \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*


# Install Python dependencies inside the virtual environment --break-system-packages
RUN pip3 install --no-cache-dir -r requirements.txt 
# RUN pip3 install fastapi uvicorn 

# Create directories for uploads and outputs
RUN mkdir -p /data/uploads /data/outputs

# Copy the FastAPI application
COPY . .

# Expose the API port
EXPOSE 8003

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
# CMD ["/usr/bin/python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
# CMD ["/bin/bash"]
