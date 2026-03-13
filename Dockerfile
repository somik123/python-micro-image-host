# Use ubuntu 24.04
FROM ubuntu:24.04 AS base

# Set required environmental variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Singapore

# Install dependencies
RUN apt update \
    && apt install -y curl nginx nano \
    && apt install -y python3-venv python3-pip \
    && apt clean all \
    && rm -rf /var/lib/apt/lists/* /var/tmp/*

# Copy startup file
COPY start.sh /start.sh
# Copy nginx site config
COPY nginx-default.conf /etc/nginx/sites-available/default
# Copy/create html dir
ADD  html /var/www/html
# Copy/create uploader_script dir
ADD uploader_script /opt/uploader_script

WORKDIR /opt/uploader_script

RUN chmod +x /start.sh \
    && chmod +x /opt/uploader_script/run.sh \
    && chmod +x /opt/uploader_script/setup.sh \
    && /opt/uploader_script/setup.sh \
    && chown -hR www-data:uploader /var/www/html \
    && sed -i -e "s/server_tokens off\;/server_tokens off\;\\n        client_max_body_size 500M\;/g" /etc/nginx/nginx.conf

EXPOSE 80

CMD ["sh", "/start.sh"]