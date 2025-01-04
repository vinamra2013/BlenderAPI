# Use the BlenderGrid Blender image as the base
FROM blendergrid/blender:latest

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Create directories for uploads and outputs
RUN mkdir -p /data/uploads /data/outputs

# Copy the FastAPI application
COPY app /app

# Expose the API port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
