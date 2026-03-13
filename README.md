# python-micro-image-host



## Installation
1. Copy the content of `docker-compose.yml` into a folder of your choice
1. Edit the content of `docker-compose.yml` file. Modify the ENV variables.
1. Start the docker container: `docker compose up -d`
1. Access the website by going to `yourServerIp:port` (default port `8192`)

> **Note:** You can edit `docker-compose.yml` file and replace `img_data:/var/www/html` with `./html:/var/www/html` or with the full path to your image upload directory. You can also change the default port from `8192` to your prefered port.
