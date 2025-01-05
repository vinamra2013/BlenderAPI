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
async def render_image_preloaded(
    file_name: str = Form(...),  # Blender file name already on the server
    frame: int = Form(1),  # Frame to render
    output_name: str = Form("rendered_image.png"),  # Output file name
):
    logger.info("Starting image render process with preloaded Blender file...")

    # Define paths and validate extensions
    blend_path = Path("/data/blender") / file_name
    output_extension = Path(output_name).suffix.lstrip(".").upper()
    valid_formats = {"PNG", "JPEG", "TIFF", "BMP", "OPEN_EXR", "HDR", "MP4", "AVI"}
    if output_extension not in valid_formats:
        logger.error(f"Unsupported file format: {output_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(valid_formats)}"
        )

    # Set the output path (base path for Blender rendering)
    output_base = OUTPUT_DIR / Path(output_name).stem
    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Validate the .blend file exists
    if not blend_path.exists():
        logger.error(f"Blend file not found: {blend_path}")
        raise HTTPException(status_code=404, detail="Blend file not found")

    logger.info(f"Using preloaded blend file: {blend_path}")

    # Construct the Blender command
    python_script = f"""
import bpy
scene = bpy.context.scene
scene.frame_start = {frame}
scene.frame_end = {frame}
scene.render.image_settings.file_format = '{output_extension}'
scene.render.filepath = '{output_base}'
"""
    blender_command = [
        "blender",
        "--background",
        str(blend_path),
        "--enable-autoexec",
        "--python-expr",
        python_script,
        "--render-frame",
        str(frame),
    ]

    try:
        logger.info(f"Executing Blender command: {' '.join(blender_command)}")
        subprocess.run(blender_command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Render failed: {e}")
        raise HTTPException(status_code=500, detail="Render failed")

    # Handle potential output file patterns
    if output_extension in {"MP4", "AVI"}:
        rendered_file = list(OUTPUT_DIR.glob(f"{Path(output_name).stem}-*.{output_extension.lower()}"))
    else:
        rendered_file = list(OUTPUT_DIR.glob(f"{Path(output_name).stem}*.{output_extension.lower()}"))

    if not rendered_file:
        logger.error("Render failed: output file not found.")
        raise HTTPException(status_code=500, detail="Render failed: output file not found.")

    final_output = rendered_file[0]
    logger.info(f"Render completed successfully: {final_output}")

    # Return the rendered file
    return FileResponse(
        path=final_output,
        media_type=f"video/{output_extension.lower()}" if output_extension in {"MP4", "AVI"} else f"image/{output_extension.lower()}",
        filename=output_name,
    )

