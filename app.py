import os
import json
import zipfile
import qrcode
import re
from PIL import Image
from flask import Flask, request, render_template, redirect, url_for, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "1c03c11d932ee4a0bfefa0eca6617210"

# File storage setup
UPLOAD_FOLDER = "uploads"
THUMBNAIL_FOLDER = "static/thumbnails"
QR_FOLDER = "static/qrcodes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
os.makedirs(QR_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Data storage files
USERS_FILE = "users.json"
FILES_FILE = "files.json"

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):  
        return self.username


# Password Validation Function
def is_valid_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character (!@#$%^&* etc.)."
    return None  # No errors, password is valid

@login_manager.user_loader
def load_user(username):
    users = load_users()
    if username in users:
        return User(username)
    return None

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def load_files():
    if not os.path.exists(FILES_FILE):
        return {}
    with open(FILES_FILE, "r") as f:
        return json.load(f)

def save_files(files):
    with open(FILES_FILE, "w") as f:
        json.dump(files, f)

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/delete/<filename>", methods=["POST"])
@login_required
def delete_file(filename):
    """Delete a file and its associated QR code and thumbnail."""
    files = load_files()
    user_files = files.get(current_user.username, [])

    # Find the file in user's list
    file_to_delete = next((file for file in user_files if file["filename"] == filename), None)

    if file_to_delete:
        filepath = file_to_delete["filepath"]

        # Delete the main file
        if os.path.exists(filepath):
            os.remove(filepath)

        # Delete the QR code (if exists)
        qr_path = os.path.join("static", f"qr_{filename}.png")
        if os.path.exists(qr_path):
            os.remove(qr_path)

        # Delete the thumbnail if it's an image
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            thumb_path = os.path.join("static", filename)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)

        # Remove the file entry from user's file list
        user_files = [file for file in user_files if file["filename"] != filename]
        files[current_user.username] = user_files
        save_files(files)

        flash("File deleted successfully!", "success")
    else:
        flash("File not found!", "danger")

    return redirect(url_for("dashboard"))


def is_valid_password(password):
    """Checks if a password meets security requirements."""
    return (
        len(password) >= 8
        and re.search(r"[A-Z]", password)  # At least one uppercase letter
        and re.search(r"[a-z]", password)  # At least one lowercase letter
        and re.search(r"\d", password)     # At least one digit
        and re.search(r"[!@#$%^&*]", password)  # At least one special character
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Checks if password is valid
        error = is_valid_password(password)
        if error:
            flash(error, "danger")  # Flashs any error message to the user
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)  # Hashs password before storing it
        # Saves user data to database (modify as per your DB)
        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()

        if username in users and check_password_hash(users[username], password):
            login_user(User(username))  
            return redirect(url_for("dashboard"))

        flash("Invalid credentials. Try again.", "danger")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    clean_file_list()  # Removes deleted files from the system
    files = load_files()
    user_files = files.get(current_user.username, [])  # Ensures it's always a list

    return render_template("dashboard.html", files=user_files)


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if "files" not in request.files:
        flash("No file part", "danger")
        return redirect(url_for("dashboard"))

    files = request.files.getlist("files")  # Allow multiple files
    uploaded_files = []

    for file in files:
        if file.filename == "":
            continue

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Generate a thumbnail if the file is an image
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
            thumb_path = os.path.join(THUMBNAIL_FOLDER, f"thumb_{filename}")
            try:
                img = Image.open(filepath)
                img.thumbnail((100, 100))
                img.save(thumb_path)
            except Exception as e:
                print(f"Thumbnail generation failed for {filename}: {e}")

        # Save file details
        uploaded_files.append({"filename": filename, "filepath": filepath})

    all_files = load_files()
    if current_user.username not in all_files:
        all_files[current_user.username] = []
    
    all_files[current_user.username].extend(uploaded_files)
    save_files(all_files)

    flash("Files uploaded successfully!", "success")
    return redirect(url_for("dashboard"))

@app.route("/download/<filename>")
@login_required
def download_file(filename):
    files = load_files().get(current_user.username, [])
    for file in files:
        if file["filename"] == filename:
            return send_file(file["filepath"], as_attachment=True)
    
    flash("File not found!", "danger")
    return redirect(url_for("dashboard"))

@app.route("/batch_download")
@login_required
def batch_download():
    """Download all user files as a ZIP."""
    files = load_files().get(current_user.username, [])
    if not files:
        flash("No files to download!", "danger")
        return redirect(url_for("dashboard"))

    zip_filename = f"{current_user.username}_files.zip"
    zip_path = os.path.join(app.config["UPLOAD_FOLDER"], zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in files:
            zipf.write(file["filepath"], arcname=file["filename"])

    return send_file(zip_path, as_attachment=True)

@app.route("/qr/<filename>")
@login_required
def get_qr(filename):
    """Return a thumbnail for images and a QR code for other files."""
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
        # Serve thumbnail
        thumb_path = os.path.join(THUMBNAIL_FOLDER, f"thumb_{filename}")
        if os.path.exists(thumb_path):
            return send_file(thumb_path, mimetype="image/png")

    # Generate a QR code for non-image files
    file_url = url_for("download_file", filename=filename, _external=True)
    qr_path = os.path.join(QR_FOLDER, f"qr_{filename}.png")

    if not os.path.exists(qr_path):
        qr = qrcode.make(file_url)
        qr.save(qr_path)

    return send_file(qr_path, mimetype="image/png")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

def clean_file_list():
    """Remove deleted files from the JSON database."""
    all_files = load_files()
    updated_files = {}

    for user, files in all_files.items():
        updated_files[user] = [file for file in files if os.path.exists(file["filepath"])]

    save_files(updated_files)

if __name__ == "__main__":
    app.run(debug=True)
