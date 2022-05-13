# Install [Docker CE](https://docs.docker.com/install/)

- Windows
  - Be sure to check whether you are running in Linux container mode or Windows container mode.
- Linux
  - We've seen some issues with docker.io. If Edge doesn't run for you, then try installing Docker CE directly instead of via docker.io. Use the [CE install steps](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce), or use the [convenience script](https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-using-the-convenience-script).
  - By default, you need `sudo` to run `docker` commands. If you want to avoid this, please follow the [post-installation steps for Linux](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).

Note: If the device is behind the proxy server, you can set the [proxy manually](https://docs.docker.com/network/proxy/#configure-the-docker-client).
