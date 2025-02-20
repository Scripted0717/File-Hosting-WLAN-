# File-Hosting-WLAN-
A simple Flask-based file hosting website where users can upload, download, and share files using QR codes. Supports multiple file uploads, batch downloads (ZIP), and auto-removal of deleted files.


🗂️ Flask File Hosting Server
A simple Flask-based file hosting website where users can upload, download, and share files using QR codes. Supports multiple file uploads, batch downloads (ZIP), and auto-removal of deleted files.

🚀 Features
✅ User Authentication (Register/Login)
✅ Upload & Download Multiple Files
✅ QR Code File Sharing
✅ Thumbnails for Images & File Icons
✅ Batch Download (ZIP files)
✅ Auto Cleanup (Removes deleted files from UI)
✅ Bootstrap UI for Better Design


📌 Installation & Setup
1️⃣ Clone or Download the Project
If using Git, run:
git clone https://github.com/your-username/File-hosting.git
cd flask-file-hosting
Or download the ZIP from GitHub and extract it.

2️⃣ Install Dependencies
Make sure you have Python 3+ installed. Then, install dependencies:
pip install -r requirements.txt

3️⃣ Run the Server
python app.py

The server will start at http://127.0.0.1:5000 🚀


🔧 Configuration
Uploaded files are stored in the uploads/ folder.
User data is stored in users.json (no SQL required).
Files are tracked in files.json


📤 Deployment (Host 24/7 for Free)
Option 1: Deploy on Render
1. Go to Render and create a new Web Service.
2. Connect your GitHub repository.
3. Set the Start Command:
    python app.py
4. Click Deploy.


📜 License
This project is free to use. You can modify and distribute it as needed.


