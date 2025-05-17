Here is a complete, fast, and production-ready Python Telegram bot using Pyrogram that:

✅ Supports /start command
✅ Accepts photo or video
✅ Uses Real-ESRGAN with 2x_DBZScanLite model for upscaling
✅ Sends interactive status updates
✅ Auto-cleans temporary files
✅ Supports GPU for fast processing

📦 Requirements
Make sure you have installed the following:

bash
Copy
Edit
pip install pyrogram tgcrypto
sudo apt install ffmpeg
Also, install Real-ESRGAN (PyTorch or NCNN):

bash
Copy
Edit
git clone https://github.com/xinntao/Real-ESRGAN.git
cd Real-ESRGAN
pip install -r requirements.txt
python setup.py develop
Download 2x_DBZScanLite.pth and place it in the Real-ESRGAN/weights folder.
