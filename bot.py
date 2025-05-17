import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pathlib import Path
import uuid
import subprocess

# Environment configs
API_ID = int(os.environ.get("API_ID", 23049826))
API_HASH = os.environ.get("API_HASH", "4a4216f089ce68a3ce2c8b9b9a6fa79a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7244848756:AAFopeXeDCZ3MRKdE4LnRn8fblpd_u4wNsc")

# Real-ESRGAN model
MODEL_NAME = "2x_DBZScanLite"
REALESRGAN_DIR = "Real-ESRGAN"

bot = Client("upscale_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


# Upscale logic using Real-ESRGAN
async def upscale_with_realesrgan(input_path: str, output_path: str, is_video: bool, progress_cb):
    await progress_cb("🔁 Converting to image frames..." if is_video else "🔁 Starting upscaling...")

    temp_dir = f"temp/{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)

    if is_video:
        await progress_cb("🎞 Extracting frames from video...")
        subprocess.run([
            "ffmpeg", "-i", input_path,
            f"{temp_dir}/frame_%04d.png"
        ], check=True)

        await progress_cb("🖼 Upscaling frames...")
        for frame in sorted(Path(temp_dir).glob("frame_*.png")):
            subprocess.run([
                "python3", f"{REALESRGAN_DIR}/inference_realesrgan.py",
                "-n", MODEL_NAME,
                "-i", str(frame),
                "-o", str(frame)
            ], check=True)

        await progress_cb("📽 Re-encoding video...")
        subprocess.run([
            "ffmpeg", "-framerate", "24", "-i", f"{temp_dir}/frame_%04d.png",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            output_path
        ], check=True)
    else:
        subprocess.run([
            "python3", f"{REALESRGAN_DIR}/inference_realesrgan.py",
            "-n", MODEL_NAME,
            "-i", input_path,
            "-o", output_path
        ], check=True)

    await progress_cb("✅ Upscaling complete!")

    # Clean temp
    if os.path.exists(temp_dir):
        subprocess.run(["rm", "-rf", temp_dir])


# /start command
@bot.on_message(filters.command("start"))
async def start_cmd(_, message: Message):
    await message.reply_text(
        f"👋 Hello {message.from_user.first_name}!\n"
        "Send me any **photo or video**, and I’ll upscale it using **2x_DBZScanLite** model.\n\n"
        "**Powered by @SharkToonsIndia**",
        quote=True
    )


# Photo or Video handler
@bot.on_message(filters.photo | filters.video)
async def media_handler(_, message: Message):
    media = message.photo or message.video
    msg = await message.reply_text("📥 Downloading your media...", quote=True)

    unique_id = str(uuid.uuid4())
    media_type = "video" if message.video else "photo"
    input_path = f"downloads/input_{unique_id}.{'mp4' if media_type == 'video' else 'jpg'}"
    output_path = f"downloads/upscaled_{unique_id}.{'mp4' if media_type == 'video' else 'png'}"

    Path("downloads").mkdir(exist_ok=True)

    try:
        await bot.download_media(media, file_name=input_path)

        async def update_progress(status):
            await msg.edit(status)

        await upscale_with_realesrgan(input_path, output_path, media_type == "video", update_progress)

        await msg.edit("📤 Uploading result...")
        await message.reply_document(output_path, caption="✨ Upscaled by @SharkToonsIndia")

    except Exception as e:
        await msg.edit(f"❌ Error: {str(e)}")

    finally:
        try:
            os.remove(input_path)
            os.remove(output_path)
        except:
            pass


if __name__ == "__main__":
    Path("downloads").mkdir(exist_ok=True)
    Path("temp").mkdir(exist_ok=True)
    print("✅ Bot is running...")
    bot.run()
