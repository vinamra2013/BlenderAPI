from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
import subprocess
import logging

# Initialize FastAPI
app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("BlenderRenderer")

# Define paths
UPLOAD_DIR = Path("/data/uploads")
OUTPUT_DIR = Path("/data/outputs")

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/render-animation", response_class=FileResponse)
async def render_animation(
    file: UploadFile,
    start_frame: int = Form(1),  # Animation start frame
    end_frame: int = Form(None),  # Optional; default is None (to be determined dynamically)
    output_name: str = Form("animation.mp4"),  # Output file name
):
    logger.info("Starting animation render process...")

    # Save the uploaded .blend file
    blend_path = UPLOAD_DIR / file.filename
    async with open(blend_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Blend file saved to: {blend_path}")

    # Define the output path
    output_path = OUTPUT_DIR / output_name

    # Build the Blender CLI command
    cmd = [
        "blender",
        "-b",  # Run Blender in background mode
        str(blend_path),
        "-o", str(output_path.with_suffix("")),  # Output path without extension
        "-s", str(start_frame),  # Start frame
        "-e", str(end_frame),  # End frame
        "-a",  # Render animation
    ]

    # Run the Blender CLI command
    try:
        logger.info(f"Running Blender CLI command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Check if the output file exists
        if not output_path.exists():
            logger.error("Render failed: output file not found.")
            raise HTTPException(status_code=500, detail="Render failed: output file not found.")

        logger.info(f"Animation rendered successfully: {output_path}")

        # Return the rendered animation file
        return FileResponse(
            path=output_path,
            media_type="video/mp4",
            filename=output_name,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Blender command failed: {e}")
        raise HTTPException(status_code=500, detail=f"Blender command failed: {str(e)}")

@app.post("/render-image", response_class=FileResponse)
async def render_image(
    file: UploadFile,
    frame: int = Form(1),  # Frame to render
    output_name: str = Form("rendered_image.png"),
):
    logger.info("Starting image render process...")

    # Save the uploaded .blend file
    blend_path = UPLOAD_DIR / file.filename
    async with open(blend_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Blend file saved to: {blend_path}")

    # Define the output path
    output_path = OUTPUT_DIR / output_name

    # Build the Blender CLI command
    cmd = [
        "blender",
        "-b",  # Run Blender in background mode
        str(blend_path),
        "-o", str(output_path.with_suffix("")),  # Output path without extension
        "-f", str(frame),  # Specific frame to render
    ]

    # Run the Blender CLI command
    try:
        logger.info(f"Running Blender CLI command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
        # Check if the output file exists
        if not output_path.exists():
            logger.error("Render failed: output file not found.")
            raise HTTPException(status_code=500, detail="Render failed: output file not found.")

        logger.info(f"Image rendered successfully: {output_path}")

        # Return the rendered image file
        return FileResponse(
            path=output_path,
            media_type="image/png",
            filename=output_name,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Blender command failed: {e}")
        raise HTTPException(status_code=500, detail=f"Blender command failed: {str(e)}")
