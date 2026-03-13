#!/bin/sh

PROJECT_DIR="/opt/uploader_script"

cd "$PROJECT_DIR"

useradd -r -s /usr/sbin/nologin -M uploader

# Set up the virtual environment if not already present
python3 -m venv venv

# Upgrade pip in the virtual environment
$PROJECT_DIR/venv/bin/pip install --upgrade pip

# Install required Python packages in the virtual environment
$PROJECT_DIR/venv/bin/pip install flask flask-cors gunicorn pillow pillow-avif-plugin

echo "Setup completed."
