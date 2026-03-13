import os

# Directory where uploaded images will be saved
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/var/www/html')

# Allowed MIME types for uploaded images
ALLOWED_MIME_TYPES = os.getenv('ALLOWED_MIME_TYPES', 'image/jpeg,image/png,image/gif,image/webp,image/avif').split(',')

# Secret API key required for uploads
API_KEY = os.getenv('API_KEY', 'API_KEY_HERE')

# CDN URL prefix for returning the image URL after upload
CDN_URL_PREFIX = os.getenv('CDN_URL_PREFIX', 'http://127.0.0.1/')

# Maximum allowed upload size (16 MB)
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16 MB

# Maximum dimension (largest side in pixels) to resize images to.
# JPEGs and converted images will be resized so the largest side is at most this value.
RESIZE_MAX_DIMENSION = int(os.getenv('RESIZE_MAX_DIMENSION', 800))

# Length of the generated random filename (excluding extension)
FILENAME_LENGTH = int(os.getenv('FILENAME_LENGTH', 10))

# JPEG quality for saved JPG files (1-100). Lower = smaller file size, more compression.
JPEG_QUALITY = int(os.getenv('JPEG_QUALITY', 80))
