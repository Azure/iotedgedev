# -*- coding: utf-8 -*-

from __future__ import absolute_import
import requests
import uuid
import docker
import os
import subprocess
import sys
import json
import click
import zipfile
import socket
import platform
from io import StringIO
from azure.cli.core import get_default_cli
from base64 import b64encode, b64decode
from hashlib import sha256
from time import time
import fnmatch
import inspect
from hmac import HMAC
from shutil import copyfile
from enum import Enum
from distutils.util import strtobool
from dotenv import load_dotenv, set_key
from .connectionstring import IoTHubConnectionString, DeviceConnectionString
if sys.version_info.major >= 3:
    from urllib.parse import quote, urlencode
else:
    from urllib import quote, urlencode

#print("Python Version: " + sys.version)

class Output:

    def info(self, text):
        click.secho(text, fg='yellow')

    def error(self, text):
        click.secho(text, fg='red')

    def header(self, text):
        click.secho("======== {0} ========".format(text).upper(), fg='white')

    def footer(self, text):
        self.info(text.upper())
        self.line()

    def procout(self, text):
        click.secho(text, dim=True)

    def line(self):
        click.secho("")


class EnvVars:
    def __init__(self, output):
        self.output = output
        self.checked = False

    def load_dotenv(self):
        dotenv_file = self.get_dotenv_file()
        dotenv_path = os.path.join(os.getcwd(), dotenv_file)

        try:
            if os.path.exists(dotenv_path):
                load_dotenv(dotenv_path)
                self.output.info(
                    "Environment Variables loaded from: {0} ({1})".format(dotenv_file, dotenv_path))
            else:
                self.output.info(
                    "{0} file not found on disk. Without a file on disk, you must specify all Environment Variables at the system level. ({1})".format(dotenv_file, dotenv_path))
        except Exception as e:
            self.output.error("ERROR: Error while trying to load .env file: {0}. {1}".format(
                dotenv_path, str(e)))

    def get_dotenv_file(self):
        default_dotenv_file = ".env"

        if not "DOTENV_FILE" in os.environ:
            return default_dotenv_file
        else:
            dotenv_file_from_environ = os.environ["DOTENV_FILE"].strip(
                "\"").strip("'")
            if dotenv_file_from_environ:
                return dotenv_file_from_environ

        return default_dotenv_file   

    def check(self):
        if not self.checked:

            try:
                try:
                    self.IOTHUB_CONNECTION_STRING = self.get_envvar(
                        "IOTHUB_CONNECTION_STRING")
                    self.IOTHUB_CONNECTION_INFO = IoTHubConnectionString(
                        self.IOTHUB_CONNECTION_STRING)
                except:
                    self.output.error("ERROR: Unable to parse IOTHUB_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set.")
                    sys.exit(-1)

                try:
                    self.DEVICE_CONNECTION_STRING = self.get_envvar(
                        "DEVICE_CONNECTION_STRING")
                    self.DEVICE_CONNECTION_INFO = DeviceConnectionString(
                        self.DEVICE_CONNECTION_STRING)
                except:
                    self.output.error("ERROR: Unable to parse DEVICE_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set.")
                    sys.exit(-1)

                
                self.RUNTIME_HOST_NAME = self.get_envvar("RUNTIME_HOST_NAME")
                if self.RUNTIME_HOST_NAME == ".":
                    self.set_envvar("RUNTIME_HOST_NAME", socket.gethostname())

                self.RUNTIME_HOME_DIR = self.get_envvar("RUNTIME_HOME_DIR")
                if self.RUNTIME_HOME_DIR == ".":
                    self.set_envvar("RUNTIME_HOME_DIR", self.get_runtime_home_dir())


                self.RUNTIME_CONFIG_DIR = self.get_envvar("RUNTIME_CONFIG_DIR")
                if self.RUNTIME_CONFIG_DIR == ".":
                    self.set_envvar("RUNTIME_CONFIG_DIR", self.get_runtime_config_dir())

                self.ACTIVE_MODULES = self.get_envvar("ACTIVE_MODULES")
                self.ACTIVE_DOCKER_DIRS = self.get_envvar("ACTIVE_DOCKER_DIRS")
                self.CONTAINER_REGISTRY_SERVER = self.get_envvar(
                    "CONTAINER_REGISTRY_SERVER")
                self.CONTAINER_REGISTRY_USERNAME = self.get_envvar(
                    "CONTAINER_REGISTRY_USERNAME")
                self.CONTAINER_REGISTRY_PASSWORD = self.get_envvar(
                    "CONTAINER_REGISTRY_PASSWORD")
                self.CONTAINER_TAG = self.get_envvar("CONTAINER_TAG")
                self.RUNTIME_TAG = self.get_envvar("RUNTIME_TAG")
                self.RUNTIME_VERBOSITY = self.get_envvar("RUNTIME_VERBOSITY")
                self.MODULES_CONFIG_FILE = self.get_envvar(
                    "MODULES_CONFIG_FILE")
                self.RUNTIME_CONFIG_FILE = self.get_envvar(
                    "RUNTIME_CONFIG_FILE")
                self.LOGS_PATH = self.get_envvar("LOGS_PATH")
                self.MODULES_PATH = self.get_envvar("MODULES_PATH")
                self.IOT_REST_API_VERSION = self.get_envvar(
                    "IOT_REST_API_VERSION")
                self.DOTNET_VERBOSITY = self.get_envvar("DOTNET_VERBOSITY")
                self.LOGS_CMD = self.get_envvar("LOGS_CMD")
                if "DOCKER_HOST" in os.environ:
                    self.DOCKER_HOST = self.get_envvar("DOCKER_HOST")
                else:
                    self.DOCKER_HOST = None
            except Exception as e:
                self.output.error(
                    "Environment variables not configured correctly. Run `iotedgedev project --create [name]` to create a new project with sample .env file. Please see README for variable configuration options. Tip: You might just need to restart your command prompt to refresh your Environment Variables.")
                self.output.error("Variable that caused exception: " + str(e))
                sys.exit(-1)

        self.checked = True

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            if name in os.environ:
                return self.get_envvar(name)
            else:
                raise e

    def save_envvar(self, key, value):
        try:
            dotenv_file = self.get_dotenv_file()
            dotenv_path = os.path.join(os.getcwd(), dotenv_file)
            set_key(dotenv_path, key, value)
        except Exception:
            self.output.error(
                f"Could not update the environment variable {key} in file {dotenv_path}")
            sys.exit(-1)

    def get_envvar(self, key):
        return os.environ[key].strip()
    
    def set_envvar(self, key, value):
        os.environ[key] = value

    def get_runtime_home_dir(self):
        plat = platform.system().lower()
        if plat == "linux" or plat == "darwin":
            return "/var/lib/azure-iot-edge"
        else:
            return os.environ["PROGRAMDATA"].replace("\\", "\\\\") + "\\\\azure-iot-edge\\\data"

    def get_runtime_config_dir(self):
        plat = platform.system().lower()

        if plat == "linux" or plat == "darwin":
            return "/etc/azure-iot-edge"
        else:
            return os.environ["PROGRAMDATA"].replace("\\", "\\\\") + "\\\\azure-iot-edge\\\\config"


class Utility:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.envvars.check()
        self.output = output
        self.config_set = False

    def exe_proc(self, params, shell=False):
        proc = subprocess.Popen(
            params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)

        stdout_data, stderr_data = proc.communicate()
        if stdout_data != "":
            self.output.procout(self.decode(stdout_data))

        if proc.returncode != 0:
            self.output.error(self.decode(stderr_data))
            sys.exit()

    def find_files(self, directory, pattern):
        # find all files in directory that match the pattern.
        for root, dirs, files in os.walk(directory):
            for basename in files:
                if fnmatch.fnmatch(basename, pattern):
                    filename = os.path.join(root, basename)
                    yield filename

    def get_iot_hub_sas_token(self, uri, key, policy_name, expiry=3600):
        ttl = time() + expiry
        sign_key = "%s\n%d" % ((quote(uri)), int(ttl))
        signature = b64encode(
            HMAC(b64decode(key), sign_key.encode("utf-8"), sha256).digest())

        rawtoken = {
            "sr": uri,
            "sig": signature,
            "se": str(int(ttl))
        }

        if policy_name is not None:
            rawtoken["skn"] = policy_name

        return "SharedAccessSignature " + urlencode(rawtoken)

    def get_file_contents(self, file):
        with open(file, "r") as file:
            return file.read()

    def decode(self, val):
        return val.decode("utf-8").strip()

    def get_config_files(self):
        # config files are in root of project

        return [os.path.join(os.getcwd(), f) for f in os.listdir(os.getcwd()) if f.endswith("template.json")]

    def get_active_modules(self):
        return [module.strip()
                for module in self.envvars.ACTIVE_MODULES.split(",") if module]

    def get_modules_in_config(self, moduleType):
        modules_config = json.load(open(self.envvars.MODULES_CONFIG_FILE))

        props = modules_config["moduleContent"]["$edgeAgent"]["properties.desired"]

        system_modules = props["systemModules"]
        user_modules = props["modules"]

        if moduleType == ModuleType.System:
            return system_modules
        elif moduleType == ModuleType.User:
            return user_modules
        else:
            return_modules = {}
            return_modules.update(system_modules)
            return_modules.update(user_modules)
            return return_modules

    def set_config(self, force=False):

        if not self.config_set or force:
            self.envvars.check()
            self.output.header("PROCESSING CONFIG FILES")

            config_output_dir = ".config"

            # Create config dir if it doesn't exist
            if not os.path.exists(config_output_dir):
                os.makedirs(config_output_dir)

            config_files = self.get_config_files()

            if len(config_files) == 0:
                self.output.info(
                    "Unable to find config files in project root directory")
                sys.exit()

            # Expand envars and rewrite to .config/
            for config_file in config_files:

                build_config_file = os.path.join(
                    config_output_dir, os.path.basename(config_file).replace(".template", ""))

                self.output.info("Expanding '{0}' to '{1}'".format(
                    os.path.basename(config_file), build_config_file))

                config_file_expanded = os.path.expandvars(
                    self.get_file_contents(config_file))

                with open(build_config_file, "w") as config_file_build:
                    config_file_build.write(config_file_expanded)

            self.output.line()

        self.config_set = True


class Project:
    def __init__(self, output):
        self.output = output

    def create(self, name):
        self.output.header("CREATING AZURE IOT EDGE PROJECT")

        try:
            template_zip = os.path.join(os.path.split(
                __file__)[0], "template", "template.zip")
        except Exception as e:
            self.output.error("Error while trying to load template.zip")
            self.output.error(str(e))

        if name == ".":
            name = ""

        zipf = zipfile.ZipFile(template_zip)
        zipf.extractall(name)

        os.rename(os.path.join(name, ".env.tmp"), os.path.join(name, ".env"))
        self.output.footer("Azure IoT Edge project created")


class Runtime:
    def __init__(self, envvars, utility, output, dock):
        self.envvars = envvars
        self.envvars.check()
        self.utility = utility
        self.utility.set_config()
        self.dock = dock
        self.output = output

    def start(self):
        self.output.header("Starting Edge Runtime")
        self.utility.exe_proc(["iotedgectl", "--verbose",
                               self.envvars.RUNTIME_VERBOSITY, "start"])

    def stop(self):
        self.output.header("Stopping Edge Runtime")
        self.utility.exe_proc(["iotedgectl", "--verbose",
                               self.envvars.RUNTIME_VERBOSITY, "stop"])

    def setup(self):
        self.output.header("Setting Up Edge Runtime")
        self.utility.exe_proc(["iotedgectl", "--verbose", self.envvars.RUNTIME_VERBOSITY,
                               "setup", "--config-file", self.envvars.RUNTIME_CONFIG_FILE])

    def status(self):
        self.output.header("Getting Edge Runtime Status")
        self.utility.exe_proc(["iotedgectl", "--verbose", self.envvars.RUNTIME_VERBOSITY,
                               "status"])

    def restart(self):
        self.stop()
        self.dock.remove_modules()
        self.setup()
        self.start()


class Modules:
    def __init__(self, envvars, utility, output, dock):
        self.envvars = envvars
        self.envvars.check()
        self.utility = utility
        self.utility.set_config()
        self.output = output
        self.dock = dock
        self.dock.init_registry()

    def build(self):
        self.output.header("BUILDING MODULES")

        # Get all the modules to build as specified in config.
        modules_to_process = self.utility.get_active_modules()

        for module in os.listdir(self.envvars.MODULES_PATH):

            if len(
                    modules_to_process) == 0 or modules_to_process[0] == "*" or module in modules_to_process:

                module_dir = os.path.join(self.envvars.MODULES_PATH, module)

                self.output.info("BUILDING MODULE: {0}".format(module_dir))

                # Find first proj file in module dir and use it.
                project_files = [os.path.join(module_dir, f) for f in os.listdir(
                    module_dir) if f.endswith("proj")]

                if len(project_files) == 0:
                    self.output.error("No project file found for module.")
                    continue

                self.utility.exe_proc(["dotnet", "build", project_files[0],
                                       "-v", self.envvars.DOTNET_VERBOSITY])

                # Get all docker files in project
                docker_files = self.utility.find_files(
                    module_dir, "Dockerfile*")

                # Filter by Docker Dirs in envvars
                docker_dirs_process = [docker_dir.strip()
                                       for docker_dir in self.envvars.ACTIVE_DOCKER_DIRS.split(",") if docker_dir]

                # Process each Dockerfile found
                for docker_file in docker_files:

                    docker_file_parent_folder = os.path.basename(
                        os.path.dirname(docker_file))

                    if len(
                            docker_dirs_process) == 0 or docker_dirs_process[0] == "*" or docker_file_parent_folder in docker_dirs_process:

                        self.output.info(
                            "PROCESSING DOCKER FILE: " + docker_file)

                        docker_file_name = os.path.basename(docker_file)

                        # assume /Docker/{runtime}/Dockerfile folder structure
                        # image name will be the same as the module folder name, filter-module
                        # tag will be {runtime}{ext}{container_tag}, i.e. linux-x64-debug-jong
                        # runtime is the Dockerfile immediate parent folder name
                        # ext is Dockerfile extension for example with Dockerfile.debug, debug is the mod
                        # CONTAINER_TAG is env var

                        # i.e. when found: filter-module/Docker/linux-x64/Dockerfile.debug and CONTAINER_TAG = jong
                        # we'll get: filtermodule:linux-x64-debug-jong

                        runtime = os.path.basename(
                            os.path.dirname(docker_file))
                        ext = "" if os.path.splitext(docker_file)[
                            1] == "" else "-" + os.path.splitext(docker_file)[1][1:]
                        container_tag = "" if self.envvars.CONTAINER_TAG == "" else "-" + \
                            self.envvars.CONTAINER_TAG

                        tag_name = runtime + ext + container_tag

                        # construct the build output path
                        build_path = os.path.join(
                            os.getcwd(), "build", "modules", module, runtime)
                        if not os.path.exists(build_path):
                            os.makedirs(build_path)

                        # dotnet publish
                        self.output.info(
                            "PUBLISHING PROJECT: " + project_files[0])

                        self.utility.exe_proc(["dotnet", "publish", project_files[0], "-f", "netcoreapp2.0",
                                               "-o", build_path, "-v", self.envvars.DOTNET_VERBOSITY])

                        # copy Dockerfile to publish dir
                        build_dockerfile = os.path.join(
                            build_path, docker_file_name)

                        copyfile(docker_file, build_dockerfile)

                        image_destination_name = "{0}/{1}:{2}".format(
                            self.envvars.CONTAINER_REGISTRY_SERVER, module, tag_name).lower()

                        self.output.info(
                            "BUILDING DOCKER IMAGE: " + image_destination_name)

                        # cd to the build output to build the docker image
                        project_dir = os.getcwd()
                        os.chdir(build_path)

                        # BUILD DOCKER IMAGE
                        build_result = self.dock.docker_client.images.build(
                            tag=image_destination_name, path=".", dockerfile=docker_file_name)
                        self.output.info(
                            "DOCKER IMAGE DETAILS: {0}".format(build_result))

                        # CD BACK UP
                        os.chdir(project_dir)

                        # PUSH TO CONTAINER REGISTRY
                        self.output.info(
                            "PUSHING DOCKER IMAGE TO: " + image_destination_name)

                        for line in self.dock.docker_client.images.push(repository=image_destination_name, tag=tag_name, stream=True, auth_config={
                                                                        "username": self.envvars.CONTAINER_REGISTRY_USERNAME, "password": self.envvars.CONTAINER_REGISTRY_PASSWORD}):
                            self.output.procout(self.utility.decode(line))

                self.output.footer("BUILD COMPLETE")

    def deploy(self):
        self.output.header("DEPLOYING MODULES")
        self.deploy_device_configuration(
            self.envvars.IOTHUB_CONNECTION_INFO.HostName, self.envvars.IOTHUB_CONNECTION_INFO.SharedAccessKey,
            self.envvars.DEVICE_CONNECTION_INFO.DeviceId, self.envvars.MODULES_CONFIG_FILE,
            self.envvars.IOTHUB_CONNECTION_INFO.SharedAccessKeyName, self.envvars.IOT_REST_API_VERSION)
        self.output.footer("DEPLOY COMPLETE")

    def deploy_device_configuration(
            self, host_name, iothub_key, device_id, config_file, iothub_policy_name, api_version):
        resource_uri = host_name
        token_expiration_period = 60
        deploy_uri = "https://{0}/devices/{1}/applyConfigurationContent?api-version={2}".format(
            resource_uri, device_id, api_version)
        iot_hub_sas_token = self.utility.get_iot_hub_sas_token(
            resource_uri, iothub_key, iothub_policy_name, token_expiration_period)

        deploy_response = requests.post(deploy_uri,
                                        headers={
                                            "Authorization": iot_hub_sas_token,
                                            "Content-Type": "application/json"
                                        },
                                        data=self.utility.get_file_contents(
                                            config_file)
                                        )

        if deploy_response.status_code == 204:
            self.output.info(
                "Edge Device configuration successfully deployed to '{0}'.".format(device_id))
        else:
            self.output.info(deploy_uri)
            self.output.info(deploy_response.status_code)
            self.output.info(deploy_response.text)
            self.output.error(
                "There was an error deploying the configuration. Please make sure your IOTHUB_CONNECTION_STRING and DEVICE_CONNECTION_STRING Environment Variables are correct.")


class Docker:

    def __init__(self, envvars, utility, output):
        self.envvars = envvars
        self.envvars.check()
        self.utility = utility
        self.utility.set_config()
        self.output = output

        if self.envvars.DOCKER_HOST:
            self.docker_client = docker.DockerClient(
                base_url=self.envvars.DOCKER_HOST)
            self.docker_api = docker.APIClient(
                base_url=self.envvars.DOCKER_HOST)
        else:
            self.docker_client = docker.from_env()
            self.docker_api = docker.APIClient()

    def init_registry(self):

        self.output.header("INITIALIZING CONTAINER REGISTRY")
        self.output.info("REGISTRY: " + self.envvars.CONTAINER_REGISTRY_SERVER)

        if "localhost" in self.envvars.CONTAINER_REGISTRY_SERVER:
            self.init_local_registry()

        self.login_registry()
        self.output.line()

    def init_local_registry(self):

        parts = self.envvars.CONTAINER_REGISTRY_SERVER.split(":")

        if len(parts) < 2:
            self.output.error("You must specific a port for your local registry server. Expected: 'localhost:5000'. Found: " +
                              self.envvars.CONTAINER_REGISTRY_SERVER)
            sys.exit()

        port = parts[1]
        ports = {'{0}/tcp'.format(port): int(port)}

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
            self.docker_client.containers.run(
                "registry:2", detach=True, name="registry", ports=ports, restart_policy={"Name": "always"})

    def login_registry(self):
        try:

            if "localhost" in self.envvars.CONTAINER_REGISTRY_SERVER:
                client_login_status = self.docker_client.login(
                    self.envvars.CONTAINER_REGISTRY_SERVER)

                api_login_status = self.docker_api.login(
                    self.envvars.CONTAINER_REGISTRY_SERVER)
            else:

                client_login_status = self.docker_client.login(registry=self.envvars.CONTAINER_REGISTRY_SERVER,
                                                               username=self.envvars.CONTAINER_REGISTRY_USERNAME,
                                                               password=self.envvars.CONTAINER_REGISTRY_PASSWORD)

                api_login_status = self.docker_api.login(registry=self.envvars.CONTAINER_REGISTRY_SERVER,
                                                         username=self.envvars.CONTAINER_REGISTRY_USERNAME,
                                                         password=self.envvars.CONTAINER_REGISTRY_PASSWORD)

            self.output.info("Successfully logged into container registry: " +
                             self.envvars.CONTAINER_REGISTRY_SERVER)

        except Exception as ex:
            self.output.error(
                "ERROR: Could not login to Container Registry. 1. Make sure Docker is running locally. 2. Verify your credentials in CONTAINER_REGISTRY_ environment variables. 2. If you are using WSL, then please set DOCKER_HOST Environment Variable. See the projects readme for full instructions.")
            self.output.error(str(ex))
            sys.exit(-1)

    def setup_registry(self):
        self.output.header("SETTING UP CONTAINER REGISTRY")
        self.init_registry()
        self.output.info("PUSHING EDGE IMAGES TO CONTAINER REGISTRY")
        image_names = ["azureiotedge-agent", "azureiotedge-hub",
                       "azureiotedge-simulated-temperature-sensor"]

        for image_name in image_names:

            microsoft_image_name = "microsoft/{0}:{1}".format(
                image_name, self.envvars.RUNTIME_TAG)

            container_registry_image_name = "{0}/{1}:{2}".format(
                self.envvars.CONTAINER_REGISTRY_SERVER, image_name, self.envvars.RUNTIME_TAG)

            # Pull image from Microsoft Docker Hub
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
                tag_result = self.docker_api.tag(
                    image=microsoft_image_name, repository=container_registry_image_name)
            except docker.errors.APIError as e:
                self.output.error(
                    "ERROR WHILE TAGGING IMAGE: '{0}'".format(microsoft_image_name))
                self.output.error(str(e))

            # Push Image to Container Registry
            try:
                self.output.info("PUSHING IMAGE: '{0}'".format(
                    container_registry_image_name))

                for line in self.docker_client.images.push(repository=container_registry_image_name, tag=self.envvars.RUNTIME_TAG, stream=True, auth_config={"username": self.envvars.CONTAINER_REGISTRY_USERNAME, "password": self.envvars.CONTAINER_REGISTRY_PASSWORD}):
                    self.output.procout(self.utility.decode(line))

                self.output.info("SUCCESSFULLY PUSHED IMAGE: '{0}'".format(
                    container_registry_image_name))
            except docker.errors.APIError as e:
                self.output.error("ERROR WHILE PUSHING IMAGE: '{0}'".format(
                    container_registry_image_name))
                self.output.error(str(e))

        self.setup_registry_in_config(image_names)

        self.utility.set_config(force=True)

        self.output.footer("Container Registry Setup Complete")

    def setup_registry_in_config(self, image_names):
        self.output.info(
            "Replacing 'microsoft/' with '{CONTAINER_REGISTRY_SERVER}/' in config files.")

        # Replace microsoft/ with ${CONTAINER_REGISTRY_SERVER}
        for config_file in self.utility.get_config_files():
            config_file_contents = self.utility.get_file_contents(config_file)
            for image_name in image_names:
                config_file_contents = config_file_contents.replace(
                    "microsoft/" + image_name, "${CONTAINER_REGISTRY_SERVER}/" + image_name)

            with open(config_file, "w") as config_file_build:
                config_file_build.write(config_file_contents)

    def remove_modules(self):
        self.output.info(
            "Removing Edge Modules Containers and Images from Docker")

        modules_in_config = self.utility.get_modules_in_config(ModuleType.User)

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
        if save and not os.path.exists(self.envvars.LOGS_PATH):
            os.makedirs(self.envvars.LOGS_PATH)

        modules_in_config = self.utility.get_modules_in_config(ModuleType.Both)

        for module in modules_in_config:
            if show:
                try:
                    command = self.envvars.LOGS_CMD.format(module)
                    os.system(command)
                except Exception as e:
                    self.output.error(
                        "Error while trying to open module log '{0}' with command '{1}'. Try iotedgedev docker --save-logs instead.".format(module, command))
                    self.output.error(str(e))
            if save:
                try:
                    self.utility.exe_proc(["docker", "logs", module, ">",
                                           os.path.join(self.envvars.LOGS_PATH, module + ".log")], True)
                except Exception as e:
                    self.output.error(
                        "Error while trying to save module log file '{0}'".format(module))
                    self.output.error(str(e))

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


class ModuleType(Enum):
    System = 1
    User = 2
    Both = 3



