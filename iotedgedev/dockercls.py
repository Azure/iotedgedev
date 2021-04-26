import os
import zipfile

import docker

from .deploymentmanifest import DeploymentManifest
from .utility import Utility


class Docker:

    def __init__(self, envvars, utility, output):
        self.envvars = envvars
        self.utility = utility
        self.output = output

        try:
            self.docker_client = docker.from_env(version="auto")
            self.docker_api = self.docker_client.api
        except Exception as ex:
            msg = "Could not connect to Docker daemon. Please make sure Docker daemon is running and accessible"
            raise ValueError(msg, ex)

    def get_os_type(self):
        return self.docker_client.info()["OSType"].lower()

    def init_registry(self):

        for registry in self.envvars.CONTAINER_REGISTRY_MAP.values():
            self.output.header("INITIALIZING CONTAINER REGISTRY")
            self.output.info("REGISTRY: " + registry.server)

            if "localhost" in registry.server:
                self.init_local_registry(registry.server)

        self.output.line()

    def init_local_registry(self, local_server):

        parts = local_server.split(":")

        if len(parts) < 2:
            raise ValueError("You must specific a port for your local registry server. Expected: 'localhost:5000'. Found: " + local_server)

        port = parts[1]
        ports = {'5000/tcp': int(port)}

        try:
            self.output.info("Looking for local 'registry' container")
            self.docker_client.containers.get("registry")
            self.output.info("Found local 'registry' container")
        except docker.errors.NotFound:
            self.output.info("Local 'registry' container not found")

            try:
                self.output.info("Looking for local 'registry' image")
                self.docker_client.images.get("registry:2")
                self.output.info("Local 'registry' image found")
            except docker.errors.ImageNotFound:
                self.output.info("Local 'registry' image not found")
                self.output.info("Pulling 'registry' image")
                self.docker_client.images.pull("registry", tag="2")

            self.output.info("Running registry container")
            self.docker_client.containers.run("registry:2", detach=True, name="registry", ports=ports, restart_policy={"Name": "always"})

    def setup_registry(self):
        self.output.header("SETTING UP CONTAINER REGISTRY")
        self.init_registry()
        self.output.info("PUSHING EDGE IMAGES TO CONTAINER REGISTRY")
        image_names = ["azureiotedge-agent", "azureiotedge-hub", "azureiotedge-simulated-temperature-sensor"]
        default_cr = self.envvars.CONTAINER_REGISTRY_MAP['']

        for image_name in image_names:

            microsoft_image_name = "mcr.microsoft.com/{0}:{1}".format(
                image_name, self.envvars.EDGE_RUNTIME_VERSION)

            container_registry_image_name = "{0}/{1}:{2}".format(
                default_cr.server, image_name, self.envvars.EDGE_RUNTIME_VERSION)

            # Pull image from MCR
            try:
                self.output.info(
                    "PULLING IMAGE: '{0}'".format(microsoft_image_name))
                image_pull = self.docker_client.images.pull(
                    microsoft_image_name)
                self.output.info(
                    "SUCCESSFULLY PULLED IMAGE: '{0}'".format(microsoft_image_name))
                self.output.info(str(image_pull))
            except docker.errors.APIError as e:
                self.output.error(
                    "ERROR WHILE PULLING IMAGE: '{0}'".format(microsoft_image_name))
                self.output.error(str(e))

            # Tagging Image with Container Registry Name
            try:
                self.docker_api.tag(
                    image=microsoft_image_name, repository=container_registry_image_name)
            except docker.errors.APIError as e:
                self.output.error(
                    "ERROR WHILE TAGGING IMAGE: '{0}'".format(microsoft_image_name))
                self.output.error(str(e))

            # Push Image to Container Registry
            try:
                self.output.info("PUSHING IMAGE: '{0}'".format(
                    container_registry_image_name))

                response = self.docker_client.images.push(repository=container_registry_image_name, tag=self.envvars.EDGE_RUNTIME_VERSION, stream=True, auth_config={
                                                          "username": default_cr.username, "password": default_cr.password})
                self.process_api_response(response)
                self.output.info("SUCCESSFULLY PUSHED IMAGE: '{0}'".format(
                    container_registry_image_name))
            except docker.errors.APIError as e:
                self.output.error("ERROR WHILE PUSHING IMAGE: '{0}'".format(
                    container_registry_image_name))
                self.output.error(str(e))

        self.setup_registry_in_config(image_names)

        self.output.footer("Container Registry Setup Complete")

    def setup_registry_in_config(self, image_names):
        self.output.info(
            "Replacing 'mcr.microsoft.com/' with '{CONTAINER_REGISTRY_SERVER}/' in config files.")

        # Replace mcr.microsoft.com/ with ${CONTAINER_REGISTRY_SERVER}
        for config_file in self.utility.get_config_files():
            config_file_contents = Utility.get_file_contents(config_file)
            for image_name in image_names:
                config_file_contents = config_file_contents.replace(
                    "mcr.microsoft.com/" + image_name, "${CONTAINER_REGISTRY_SERVER}/" + image_name)

            with open(config_file, "w") as config_file_build:
                config_file_build.write(config_file_contents)

    def remove_modules(self):
        self.output.info(
            "Removing Edge Modules Containers and Images from Docker")

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.utility, self.envvars.DEPLOYMENT_CONFIG_FILE_PATH, False)
        modules_in_config = list(deployment_manifest.get_user_modules().keys())

        for module in modules_in_config:
            self.output.info("Searching for {0} Containers".format(module))
            containers = self.docker_client.containers.list(
                filters={"name": module})
            for container in containers:
                self.output.info("Removing Container: " + str(container))
                container.remove(force=True)

            self.output.info("Searching for {0} Images".format(module))
            for image in self.docker_client.images.list():
                if module in str(image):
                    self.output.info(
                        "Removing Module Image: " + str(image))
                    self.docker_client.images.remove(
                        image=image.id, force=True)

    def remove_containers(self):
        self.output.info("Removing Containers....")
        containers = self.docker_client.containers.list(all=True)
        self.output.info("Found {0} Containers".format(len(containers)))
        for container in containers:
            self.output.info("Removing Container: {0}:{1}".format(
                container.id, container.name))
            container.remove(force=True)
        self.output.info("Containers Removed")

    def remove_images(self):
        self.output.info("Removing Dangling Images....")
        images = self.docker_client.images.list(
            all=True, filters={"dangling": True})
        self.output.info("Found {0} Images".format(len(images)))

        for image in images:
            self.output.info("Removing Image: {0}".format(str(image.id)))
            self.docker_client.images.remove(image=image.id, force=True)
        self.output.info("Images Removed")

        self.output.info("Removing Images....")
        images = self.docker_client.images.list()
        self.output.info("Found {0} Images".format(len(images)))

        for image in images:
            self.output.info("Removing Image: {0}".format(str(image.id)))
            self.docker_client.images.remove(image=image.id, force=True)
        self.output.info("Images Removed")

    def handle_logs_cmd(self, show, save):

        # Create LOGS_PATH dir if it doesn't exist
        if save:
            self.utility.ensure_dir(self.envvars.LOGS_PATH)

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.utility, self.envvars.DEPLOYMENT_CONFIG_FILE_PATH, False)
        modules_in_config = list(deployment_manifest.get_all_modules().keys())

        for module in modules_in_config:
            if show:
                try:
                    command = self.envvars.LOGS_CMD.format(module)
                    os.system(command)
                except Exception as ex:
                    self.output.error(
                        "Error while trying to open module log '{0}' with command '{1}'. Try `iotedgedev docker log --save` instead.".format(module, command))
                    self.output.error(str(ex))
            if save:
                try:
                    self.utility.exe_proc(["docker", "logs", module, ">",
                                           os.path.join(self.envvars.LOGS_PATH, module + ".log")], True)
                except Exception as ex:
                    self.output.error("Error while trying to save module log file '{0}'".format(module))
                    self.output.error(str(ex))

        if save:
            self.zip_logs()

    def zip_logs(self):
        log_files = [os.path.join(self.envvars.LOGS_PATH, f)
                     for f in os.listdir(self.envvars.LOGS_PATH) if f.endswith(".log")]
        zip_path = os.path.join(self.envvars.LOGS_PATH, 'edge-logs.zip')

        self.output.info("Creating {0} file".format(zip_path))

        zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)

        for log_file in log_files:
            self.output.info("Adding {0} to zip". format(log_file))
            zipf.write(log_file)

        zipf.close()

        self.output.info("Log files successfully saved to: " + zip_path)

    def process_api_response(self, response):
        for json_ in docker.utils.json_stream.json_stream(response):
            for key in json_:
                if key == "stream" and isinstance(json_[key], str):
                    self.output.procout(json_[key], nl=False)
                if key == "status" and isinstance(json_[key], str):
                    message = ""
                    if ("id" in json_):
                        message += json_["id"] + " "
                    message += json_[key] + " "
                    if ("progress" in json_):
                        message += json_["progress"]
                    self.output.procout(message)

            # Docker SDK won't throw exceptions for some failures.
            # We have to check the response ourselves.
            # Related issue: https://github.com/docker/docker-py/issues/1772
            if "error" in json_:
                raise ValueError(json_["error"])
