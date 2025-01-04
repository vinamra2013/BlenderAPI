from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import bpy
from pathlib import Path
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

    # Save uploaded .blend file
    blend_path = UPLOAD_DIR / file.filename
    async with open(blend_path, "wb") as f:
        content = await file.read()
        f.write(content)

    logger.info(f"Blend file saved to: {blend_path}")

    # Load the .blend file in Blender
    try:
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))
        logger.info(f"Successfully loaded blend file: {blend_path}")
    except Exception as e:
        logger.error(f"Failed to load blend file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load .blend file: {str(e)}")

    # Set render output settings for animation
    output_path = OUTPUT_DIR / output_name
    bpy.context.scene.render.filepath = str(output_path)
    bpy.context.scene.render.image_settings.file_format = "FFMPEG"
    bpy.context.scene.render.ffmpeg.format = "MPEG4"
    bpy.context.scene.render.ffmpeg.codec = "H264"
    bpy.context.scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
    bpy.context.scene.render.ffmpeg.ffmpeg_preset = "GOOD"

    # Set frame range
    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame

    # Set the render engine and device (GPU)
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'

    # Render the animation
    try:
        logger.info(f"Rendering animation from frame {start_frame} to {end_frame}...")
        bpy.ops.render.render(animation=True)

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
    except Exception as e:
        logger.error(f"Render failed: {e}")
        raise HTTPException(status_code=500, detail=f"Render failed: {str(e)}")

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

    # Load the .blend file in Blender
    try:
        bpy.ops.wm.open_mainfile(filepath=str(blend_path))
        logger.info(f"Successfully loaded blend file: {blend_path}")
    except Exception as e:
        logger.error(f"Failed to load blend file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load .blend file: {str(e)}")

    # Set render output settings
    output_path = OUTPUT_DIR / output_name
    bpy.context.scene.render.filepath = str(output_path)
    bpy.context.scene.render.image_settings.file_format = "PNG"

    # Set the frame to render
    bpy.context.scene.frame_set(frame)

    # Render the image
    try:
        logger.info(f"Rendering image for frame {frame}...")
        bpy.ops.render.render(write_still=True)

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
    except Exception as e:
        logger.error(f"Render failed: {e}")
        raise HTTPException(status_code=500, detail=f"Render failed: {str(e)}")