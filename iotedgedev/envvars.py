from dotenv import load_dotenv, set_key
import os
import platform
import socket
import sys
from shutil import copyfile
from fstrings import f
from .connectionstring import IoTHubConnectionString, DeviceConnectionString

class EnvVars:
    def __init__(self, output):
        self.output = output
        self.checked = False

    def backup_dotenv(self):
        dotenv_file = self.get_dotenv_file()
        dotenv_path = os.path.join(os.getcwd(), dotenv_file)
        dotenv_backup_path= dotenv_path+".backup"
        try:
            copyfile(dotenv_path, dotenv_backup_path)
            self.output.info(f("Successfully backed up {dotenv_path} to {dotenv_backup_path}"))
            return True
        except Exception as e:
            self.output.error(f("Could not backup {dotenv_path} to {dotenv_backup_path}"))
            self.output.error(str(e))
        return False
        
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
        except Exception as ex:
            self.output.error("Error while trying to load .env file: {0}. {1}".format(
                dotenv_path, str(ex)))

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
            self.load_dotenv()

            try:
                try:
                    self.IOTHUB_CONNECTION_STRING = self.get_envvar(
                        "IOTHUB_CONNECTION_STRING")
                    self.IOTHUB_CONNECTION_INFO = IoTHubConnectionString(
                        self.IOTHUB_CONNECTION_STRING)
                except Exception as ex:
                    self.output.error(
                        "Unable to parse IOTHUB_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set.")
                    self.output.error(str(ex))
                    sys.exit(-1)

                try:
                    self.DEVICE_CONNECTION_STRING = self.get_envvar(
                        "DEVICE_CONNECTION_STRING")
                    self.DEVICE_CONNECTION_INFO = DeviceConnectionString(
                        self.DEVICE_CONNECTION_STRING)
                except Exception as ex:
                    self.output.error(
                        "Unable to parse DEVICE_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set.")
                    self.output.error(str(ex))
                    sys.exit(-1)

                self.RUNTIME_HOST_NAME = self.get_envvar("RUNTIME_HOST_NAME")
                if self.RUNTIME_HOST_NAME == ".":
                    self.set_envvar("RUNTIME_HOST_NAME", socket.gethostname())

                self.RUNTIME_HOME_DIR = self.get_envvar("RUNTIME_HOME_DIR")
                if self.RUNTIME_HOME_DIR == ".":
                    self.set_envvar("RUNTIME_HOME_DIR",
                                    self.get_runtime_home_dir())

                self.RUNTIME_CONFIG_DIR = self.get_envvar("RUNTIME_CONFIG_DIR")
                if self.RUNTIME_CONFIG_DIR == ".":
                    self.set_envvar("RUNTIME_CONFIG_DIR",
                                    self.get_runtime_config_dir())

                self.ACTIVE_MODULES = self.get_envvar("ACTIVE_MODULES")             
                self.ACTIVE_DOCKER_ARCH = self.get_envvar("ACTIVE_DOCKER_ARCH")
                
                self.CONTAINER_REGISTRY_SERVER = self.get_envvar(
                    "CONTAINER_REGISTRY_SERVER", False)
                self.CONTAINER_REGISTRY_USERNAME = self.get_envvar(
                    "CONTAINER_REGISTRY_USERNAME", False)
                self.CONTAINER_REGISTRY_PASSWORD = self.get_envvar(
                    "CONTAINER_REGISTRY_PASSWORD", False)
                self.CONTAINER_TAG = self.get_envvar("CONTAINER_TAG", False)
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
                    self.DOCKER_HOST = self.get_envvar("DOCKER_HOST", False)
                else:
                    self.DOCKER_HOST = None
            except Exception as ex:
                self.output.error(
                    "Environment variables not configured correctly. Run `iotedgedev solution --create [name]` to create a new solution with sample .env file. Please see README for variable configuration options. Tip: You might just need to restart your command prompt to refresh your Environment Variables.")
                self.output.error("Variable that caused exception: " + str(ex))
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

    def get_envvar(self, key, required=True):
        val = os.environ[key].strip()
        if not val and required:
            self.output.error(
                "Environment Variable {0} not set. Either add to .env file or to your system's Environment Variables".format(key))
            sys.exit(-1)

        return val

    def set_envvar(self, key, value):
        os.environ[key] = value

    def save_envvar(self, key, value):
        try:
            dotenv_file = self.get_dotenv_file()
            dotenv_path = os.path.join(os.getcwd(), dotenv_file)
            set_key(dotenv_path, key, value)
        except Exception:
            self.output.error(
                f("Could not update the environment variable {key} in file {dotenv_path}"))
            sys.exit(-1)

    def get_runtime_home_dir(self):
        if self.is_posix():
            return "/var/lib/azure-iot-edge"
        else:
            return os.environ["PROGRAMDATA"].replace("\\", "\\\\") + "\\\\azure-iot-edge\\\data"

    def get_runtime_config_dir(self):
        if self.is_posix():
            return "/etc/azure-iot-edge"
        else:
            return os.environ["PROGRAMDATA"].replace("\\", "\\\\") + "\\\\azure-iot-edge\\\\config"

    def is_posix(self):
        plat = platform.system().lower()
        return plat == "linux" or plat == "darwin"
