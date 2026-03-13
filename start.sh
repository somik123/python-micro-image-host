#!/bin/sh
echo "Starting services..."
nginx -g "daemon off;" &

echo "Setting permissions..."
chown -R www-data:uploader /var/www/html

PROJECT_DIR="/opt/uploader_script"

cd "$PROJECT_DIR"
"$PROJECT_DIR"/venv/bin/gunicorn --bind 127.0.0.1:5000 upload_api:app

