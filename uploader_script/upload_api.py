from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import secrets
import string
import logging
import io
from PIL import Image
import config

# Basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins and headers

# Load configuration
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

# Ensure upload directory exists
if not os.path.exists(config.UPLOAD_FOLDER):
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

def allowed_mime_type(mimetype):
    """Check if the MIME type is allowed for upload (client-supplied)."""
    return mimetype in config.ALLOWED_MIME_TYPES

def generate_random_name(length=None):
    """Generate a random string of letters and digits (cryptographically secure).
    Uses config.FILENAME_LENGTH when length is not provided.
    """
    if length is None:
        length = getattr(config, "FILENAME_LENGTH", 10)
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def resize_image(img, max_size=None):
    """
    Resize the image while maintaining aspect ratio so the largest
    dimension is at most max_size. Uses config.RESIZE_MAX_DIMENSION by default.
    """
    if max_size is None:
        max_size = getattr(config, "RESIZE_MAX_DIMENSION", 2048)
    ratio = min(max_size / img.width, max_size / img.height, 1.0)
    if ratio >= 1.0:
        return img
    new_size = (int(img.width * ratio), int(img.height * ratio))
    return img.resize(new_size, Image.LANCZOS)

def convert_to_jpeg(img):
    """
    Convert a PIL Image to JPEG-compatible (RGB) and return (img, ext, save_format).
    """
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    return img, 'jpg', 'JPEG'

def save_raw_bytes(data, path):
    """Save raw bytes to disk (used for preserving PNG/GIF unchanged)."""
    with open(path, 'wb') as f:
        f.write(data)

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload via POST request:
      - Check API key
      - Basic MIME filter
      - Verify image using Pillow
      - For PNG/GIF: save raw bytes (no resize, preserve animation)
      - For JPEG: resize and save as JPEG using config.JPEG_QUALITY
      - For WebP/AVIF: convert -> JPEG, resize, save as JPEG using config.JPEG_QUALITY
    """
    # API key check
    client_api_key = request.form.get('api_key')
    if client_api_key != config.API_KEY:
        return jsonify({"success": False, "error": "Invalid or missing API key"}), 401

    # File presence
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "No file part"}), 400

    file = request.files['file']

    # Filename presence
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    # Quick client-side MIME filter (not sufficient on its own)
    if not allowed_mime_type(file.mimetype):
        return jsonify({"success": False, "error": "Invalid file type (client MIME)"}), 400

    # Read raw bytes from the uploaded file (so we can save raw bytes if needed)
    try:
        data = file.read()
    except Exception:
        return jsonify({"success": False, "error": "Failed to read uploaded file"}), 400

    # Basic size check (redundant with Flask's MAX_CONTENT_LENGTH but safe)
    if len(data) == 0:
        return jsonify({"success": False, "error": "Empty file"}), 400

    # Verify with Pillow using an in-memory buffer
    buf = io.BytesIO(data)
    try:
        img_verify = Image.open(buf)
        img_verify.verify()  # verify integrity
    except Exception:
        logger.exception("Uploaded file failed Pillow verification")
        return jsonify({"success": False, "error": "File is not a valid image"}), 400

    # Reopen buffer to get a working Image object and inspect format
    buf.seek(0)
    try:
        img = Image.open(buf)
        orig_format = (img.format or "").lower()
    except Exception:
        logger.exception("Failed to open image after verification")
        return jsonify({"success": False, "error": "File is not a valid image"}), 400

    # Normalize common alias
    if orig_format == 'jpg':
        orig_format = 'jpeg'

    # Ensure Pillow-detected format is allowed (safer than trusting client MIME)
    if orig_format not in {'jpeg', 'png', 'gif', 'webp', 'avif'}:
        return jsonify({"success": False, "error": f"Unsupported image format: {orig_format}"}), 400

    # Decide how to handle each format:
    # - png, gif: save raw bytes unchanged
    # - jpeg: resize then save as jpeg
    # - webp, avif: convert -> jpeg, resize, save as jpeg
    try:
        if orig_format in {'png', 'gif'}:
            # Save raw bytes without modification to preserve animation/metadata.
            ext = 'png' if orig_format == 'png' else 'gif'
            filename = f"{generate_random_name()}.{ext}"
            file_path = os.path.join(config.UPLOAD_FOLDER, filename)
            save_raw_bytes(data, file_path)
            try:
                os.chmod(file_path, 0o644)
            except Exception:
                logger.exception("Failed to chmod saved file")
        elif orig_format in {'webp', 'avif'}:
            # Convert to JPEG, resize, and save as JPG using configured JPEG quality
            buf.seek(0)
            img = Image.open(buf)
            img = resize_image(img)
            img, ext, save_format = convert_to_jpeg(img)
            filename = f"{generate_random_name()}.{ext}"
            file_path = os.path.join(config.UPLOAD_FOLDER, filename)
            # Save with JPEG options using configured quality
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            img.save(file_path, 'JPEG', quality=getattr(config, "JPEG_QUALITY", 80), optimize=True)
            try:
                os.chmod(file_path, 0o644)
            except Exception:
                logger.exception("Failed to chmod saved file")
        else:  # 'jpeg'
            # Resize JPEG and save as JPEG using configured JPEG quality
            buf.seek(0)
            img = Image.open(buf)
            img = resize_image(img)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            ext = 'jpg'
            filename = f"{generate_random_name()}.{ext}"
            file_path = os.path.join(config.UPLOAD_FOLDER, filename)
            img.save(file_path, 'JPEG', quality=getattr(config, "JPEG_QUALITY", 80), optimize=True)
            try:
                os.chmod(file_path, 0o644)
            except Exception:
                logger.exception("Failed to chmod saved file")
    except Exception:
        logger.exception("Failed processing/saving image")
        return jsonify({"success": False, "error": "Failed to process or save image"}), 500

    file_url = config.CDN_URL_PREFIX + filename
    return jsonify({"success": True, "url": file_url}), 200

if __name__ == '__main__':
    # For production, run with Gunicorn / systemd; this is for local/dev testing only.
    app.run(host='127.0.0.1', port=5000)




