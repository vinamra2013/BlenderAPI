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

RUN apt-get update && apt-get install -y \
    python3.11 python3-pip blender tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


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
