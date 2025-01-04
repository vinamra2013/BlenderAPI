# Use the BlenderGrid Blender image as the base
FROM blendergrid/blender:latest

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

RUN apt-get update && apt-get install -y python3-pip


# Install Python dependencies inside the virtual environment
RUN ./venv/bin/pip install --no-cache-dir -r requirements.txt --break-system-packages

# Ensure venv is used for subsequent commands
ENV PATH="/app/venv/bin:$PATH"

# Create directories for uploads and outputs
RUN mkdir -p /data/uploads /data/outputs

# Copy the FastAPI application
COPY . .

# Expose the API port
EXPOSE 8003

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
