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
UPLOAD_DIR = Path("/app/uploads")
OUTPUT_DIR = Path("/app/outputs")

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.post("/render-animation", response_class=FileResponse)
async def render_animation(
    file_name: str = Form(...),  # Blender file name already on the server
    start_frame: int = Form(1),  # Animation start frame
    end_frame: int = Form(None),  # Optional; default is None (to be determined dynamically)
    output_name: str = Form("animation.mp4"),  # Output file name
):
    logger.info("Starting animation render process with preloaded Blender file...")

    # Define paths and validate extensions
    blend_path = Path("/app/blender") / file_name
    logger.debug(f"Blend file path set to: {blend_path}")

    output_extension = Path(output_name).suffix.lstrip(".").upper()
    logger.debug(f"Output extension resolved to: {output_extension}")

    valid_formats = {"PNG", "JPEG", "TIFF", "BMP", "OPEN_EXR", "HDR", "MP4", "AVI"}
    if output_extension not in valid_formats:
        logger.error(f"Unsupported file format: {output_extension}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Supported formats: {', '.join(valid_formats)}"
        )

    # Set the output path (base path for Blender rendering)
    output_base = OUTPUT_DIR / Path(output_name).stem
    logger.debug(f"Output base path set to: {output_base}")

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created output directory: {OUTPUT_DIR}")

    # Validate the .blend file exists
    if not blend_path.exists():
        logger.error(f"Blend file not found: {blend_path}")
        raise HTTPException(status_code=404, detail="Blend file not found")

    logger.info(f"Using preloaded blend file: {blend_path}")

    # Create a temporary Python script for Blender
    script_content = f"""
import bpy re

# Set up the GPU for rendering
scene = bpy.context.scene
scene.cycles.device = 'GPU'
prefs = bpy.context.preferences
prefs.addons['cycles'].preferences.get_devices()
cprefs = prefs.addons['cycles'].preferences

print(cprefs)

# Attempt to set GPU device types if available
for compute_device_type in ('CUDA', 'OPENCL', 'NONE'):
    try:
        cprefs.compute_device_type = compute_device_type
        print('Device found:', compute_device_type)
        break
    except TypeError:
        pass

# Enable all CPU and GPU devices
for device in cprefs.devices:
    if not re.match('intel', device.name, re.I):
        print('Activating:', device)
        device.use = True

# Set render frame range
print(f"Start Frame: {start_frame}, End Frame: {end_frame} or bpy.context.scene.frame_end")
bpy.context.scene.frame_start = {start_frame}
bpy.context.scene.frame_end = {end_frame} or bpy.context.scene.frame_end

# Configure render settings
bpy.context.scene.render.filepath = '{output_base}'

bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
bpy.context.scene.render.ffmpeg.format = 'MPEG4'
bpy.context.scene.render.ffmpeg.codec = 'H264'
bpy.context.scene.render.use_file_extension = False

bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Configure Cycles-specific settings
bpy.context.scene.cycles.samples = 200
bpy.context.scene.cycles.adaptive_threshold = 0.01
print("Render settings configured.")

# Render the animation
bpy.ops.render.render(animation=True)
print("Animation render completed.")
"""
    script_path = OUTPUT_DIR / "render_script.py"
    logger.debug(f"Writing temporary Blender script to: {script_path}")

    with script_path.open("w") as script_file:
        script_file.write(script_content)

    blender_command = [
        "blender",
        "--background",
        str(blend_path),
        "--enable-autoexec",
        "--python", str(script_path),
    ]

    try:
        logger.info(f"Executing Blender command: {' '.join(blender_command)}")
        subprocess.run(blender_command, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Render failed: {e}")
        raise HTTPException(status_code=500, detail="Render failed")

    # Handle potential output file patterns
    logger.debug(f"Looking for output files with base: {Path(output_name).stem}")
    if output_extension in {"MP4", "AVI"}:
        rendered_file = list(OUTPUT_DIR.glob(f"{Path(output_name).stem}-*.{output_extension.lower()}"))
    else:
        rendered_file = list(OUTPUT_DIR.glob(f"{Path(output_name).stem}*.{output_extension.lower()}"))

    logger.debug(f"Rendered files found: {rendered_file}")
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


@app.post("/render-image", response_class=FileResponse)
async def render_image_preloaded(
    file_name: str = Form(...),  # Blender file name already on the server
    frame: int = Form(1),  # Frame to render
    output_name: str = Form("rendered_image.png"),  # Output file name
):
    logger.info("Starting image render process with preloaded Blender file...")

    # Define paths and validate extensions
    blend_path = Path("/app/blender") / file_name
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

    # Create a temporary Python script for Blender
    script_content = f"""
import bpy

# Set render frame range
bpy.context.scene.frame_start = {frame}
bpy.context.scene.frame_end = {frame}

# Configure render settings
bpy.context.scene.render.image_settings.file_format = '{output_extension}'
bpy.context.scene.render.filepath = '{output_base}'
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080

# Configure Cycles-specific settings
bpy.context.scene.cycles.samples = 200
bpy.context.scene.cycles.adaptive_threshold = 0.01

# Render the frame
bpy.ops.render.render(write_still=True)
"""
    script_path = OUTPUT_DIR / "render_script.py"
    with script_path.open("w") as script_file:
        script_file.write(script_content)


    blender_command = [
        "blender",
        "--background",
        str(blend_path),
        "--enable-autoexec",
        "--python", str(script_path),
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

