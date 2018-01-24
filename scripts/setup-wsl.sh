echo "PATH=\"$PATH:$HOME/bin:$HOME/.local/bin:/mnt/c/Program\ Files/Docker/Docker/resources/bin\"" >> ~/.bashrc
echo "alias docker=docker.exe" >> ~/.bashrc
echo "alias docker-machine=docker-machine.exe" >> ~/.bashrc
echo "alias docker-compose=docker-compose.exe" >> ~/.bashrc
echo "export DOCKER_HOST='${DOCKER_HOST}'" >> ~/.bashrc
source ~/.bashrc

sudo sh -c "echo Defaults  env_keep += \"DOCKER_HOST\" >> /etc/sudoers.d/docker"