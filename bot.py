import os
import cv2
import asyncio
import tempfile
import subprocess
from PIL import Image
from pyrogram import Client, filters
from pyrogram.types import Message

API_ID = int(os.environ.get("API_ID", 23049826))
API_HASH = os.environ.get("API_HASH", "4a4216f089ce68a3ce2c8b9b9a6fa79a")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7244848756:AAFopeXeDCZ3MRKdE4LnRn8fblpd_u4wNsc")

MODEL_NAME = "2x_DBZScanLite"
REALESRGAN_DIR = "Real-ESRGAN"

app = Client("upscaler_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


async def upscale_image(input_path, output_path):
    subprocess.run([
        "python3", f"{REALESRGAN_DIR}/inference_realesrgan.py",
        "-n", MODEL_NAME,
        "-i", input_path,
        "-o", output_path
    ], check=True)


async def upscale_video(input_video_path, output_video_path, update_func):
    cap = cv2.VideoCapture(input_video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    temp_dir = tempfile.mkdtemp()
    upscaled_frames = []

    await update_func("🔁 Extracting & upscaling frames...")

    for i in range(frame_count):
        ret, frame = cap.read()
        if not ret:
            break
        frame_path = os.path.join(temp_dir, f"frame_{i}.png")
        Image.fromarray(frame).save(frame_path)

        await upscale_image(frame_path, frame_path)  # Output to same file
        upscaled_frames.append(frame_path)

        if i % 10 == 0:
            await update_func(f"🧠 Upscaled {i}/{frame_count} frames...")

    cap.release()
    await update_func("🎞️ Rebuilding video...")

    first_frame = cv2.imread(upscaled_frames[0])
    height, width, _ = first_frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

    for frame_path in upscaled_frames:
        img = cv2.imread(frame_path)
        out.write(img)
    out.release()

    await update_func("✅ Upscaling complete!")


@app.on_message(filters.command("start"))
async def start(_, msg: Message):
    await msg.reply("👋 Welcome to the Anime Upscaler Bot!\n\nSend a photo or video to upscale it.\n\nPowered by @SharkToonsIndia")


@app.on_message(filters.video | filters.photo)
async def handle_media(_, msg: Message):
    status = await msg.reply("📥 Downloading file...")
    file = await msg.download()

    if msg.photo:
        try:
            output_path = file.replace(".", "_upscaled.")
            await status.edit("🧠 Upscaling photo...")
            await upscale_image(file, output_path)
            await msg.reply_document(output_path, caption="✅ Upscaled by @SharkToonsIndia")
        except Exception as e:
            await status.edit(f"❌ Error: {e}")
        finally:
            os.remove(file)
            if os.path.exists(output_path):
                os.remove(output_path)

    elif msg.video:
        try:
            output_video = file.replace(".", "_upscaled.")
            async def update(text): await status.edit(text)
            await upscale_video(file, output_video, update)
            await msg.reply_video(output_video, caption="✅ Upscaled by @SharkToonsIndia")
        except Exception as e:
            await status.edit(f"❌ Error: {e}")
        finally:
            os.remove(file)
            if os.path.exists(output_video):
                os.remove(output_video)


app.run()
