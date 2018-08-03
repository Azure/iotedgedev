import os
import platform
import socket
import sys
from shutil import copyfile

from dotenv import load_dotenv, set_key
from fstrings import f

from .args import Args
from .connectionstring import DeviceConnectionString, IoTHubConnectionString
from .containerregistry import ContainerRegistry


class EnvVars:
    def __init__(self, output):
        self.output = output
        self.loaded = False
        self.args = Args()
        self.current_command = self.args.get_current_command()
        self.terse_commands = ['', 'azure', 'solution']
        self.bypass_dotenv_load_commands = ['init', 'e2e', 'solution']

        # for some commands we don't want verbose dotenv load output
        self.verbose = self.current_command not in self.terse_commands

    def backup_dotenv(self):
        dotenv_file = self.get_dotenv_file()
        dotenv_path = os.path.join(os.getcwd(), dotenv_file)
        dotenv_backup_path = dotenv_path + ".backup"
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
                if self.verbose:
                    self.output.info("Environment Variables loaded from: {0} ({1})".format(dotenv_file, dotenv_path))
            else:
                if self.verbose:
                    self.output.info("{0} file not found on disk. Without a file on disk, you must specify all Environment Variables at the system level. ({1})".format(dotenv_file, dotenv_path))
        except Exception as ex:
            self.output.error("Error while trying to load .env file: {0}. {1}".format(dotenv_path, str(ex)))

    def get_dotenv_file(self):
        default_dotenv_file = ".env"

        if not "DOTENV_FILE" in os.environ:
            return default_dotenv_file
        else:
            dotenv_file_from_environ = os.environ["DOTENV_FILE"].strip("\"").strip("'")
            if dotenv_file_from_environ:
                return dotenv_file_from_environ

        return default_dotenv_file

    def load(self, force=False):

        # for some commands we don't want to load dotenv
        if self.current_command in self.bypass_dotenv_load_commands and not force:
            return

        if not self.loaded or force:
            if self.verbose:
                self.output.header("ENVIRONMENT VARIABLES")

            self.load_dotenv()

            try:
                try:
                    self.IOTHUB_CONNECTION_STRING = self.get_envvar("IOTHUB_CONNECTION_STRING")

                    if self.IOTHUB_CONNECTION_STRING:
                        self.IOTHUB_CONNECTION_INFO = IoTHubConnectionString(self.IOTHUB_CONNECTION_STRING)

                except Exception as ex:
                    self.output.error("Unable to parse IOTHUB_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set.")
                    self.output.error(str(ex))
                    sys.exit(-1)

                try:
                    self.DEVICE_CONNECTION_STRING = self.get_envvar("DEVICE_CONNECTION_STRING")

                    if self.DEVICE_CONNECTION_STRING:
                        self.DEVICE_CONNECTION_INFO = DeviceConnectionString(self.DEVICE_CONNECTION_STRING)

                except Exception as ex:
                    self.output.error("Unable to parse DEVICE_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set.")
                    self.output.error(str(ex))
                    sys.exit(-1)
                
                self.get_registries()

                self.RUNTIME_HOST_NAME = self.get_envvar("RUNTIME_HOST_NAME", default=".")
                if self.RUNTIME_HOST_NAME == ".":
                    self.set_envvar("RUNTIME_HOST_NAME", socket.gethostname())

                self.RUNTIME_HOME_DIR = self.get_envvar("RUNTIME_HOME_DIR", default=".")
                if self.RUNTIME_HOME_DIR == ".":
                    self.set_envvar("RUNTIME_HOME_DIR", self.get_runtime_home_dir())

                self.RUNTIME_CONFIG_DIR = self.get_envvar("RUNTIME_CONFIG_DIR", default=".")
                if self.RUNTIME_CONFIG_DIR == ".":
                    self.set_envvar("RUNTIME_CONFIG_DIR", self.get_runtime_config_dir())
                self.BYPASS_MODULES = self.get_envvar("BYPASS_MODULES")
                self.ACTIVE_DOCKER_PLATFORMS = self.get_envvar("ACTIVE_DOCKER_PLATFORMS", altkeys=["ACTIVE_DOCKER_ARCH"])
                self.CONTAINER_TAG = self.get_envvar("CONTAINER_TAG")
                self.RUNTIME_TAG = self.get_envvar("RUNTIME_TAG")
                self.RUNTIME_VERBOSITY = self.get_envvar("RUNTIME_VERBOSITY")
                self.RUNTIME_LOG_LEVEL = self.get_envvar("RUNTIME_LOG_LEVEL", default="info")
                self.CONFIG_OUTPUT_DIR = self.get_envvar("CONFIG_OUTPUT_DIR", default="config")
                self.DEPLOYMENT_CONFIG_FILE = self.get_envvar("DEPLOYMENT_CONFIG_FILE", altkeys=['MODULES_CONFIG_FILE'])
                self.DEPLOYMENT_CONFIG_FILE_PATH = os.path.join(self.CONFIG_OUTPUT_DIR, self.DEPLOYMENT_CONFIG_FILE)
                self.DEPLOYMENT_CONFIG_TEMPLATE_FILE = self.get_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", default="deployment.template.json")
                self.RUNTIME_CONFIG_FILE = self.get_envvar("RUNTIME_CONFIG_FILE")
                self.RUNTIME_CONFIG_FILE_PATH = os.path.join(self.CONFIG_OUTPUT_DIR, self.RUNTIME_CONFIG_FILE)
                self.LOGS_PATH = self.get_envvar("LOGS_PATH")
                self.MODULES_PATH = self.get_envvar("MODULES_PATH")
                self.IOT_REST_API_VERSION = self.get_envvar("IOT_REST_API_VERSION")
                self.DOTNET_VERBOSITY = self.get_envvar("DOTNET_VERBOSITY")
                self.DOTNET_EXE_DIR = self.get_envvar("DOTNET_EXE_DIR")
                self.LOGS_CMD = self.get_envvar("LOGS_CMD")
                self.SUBSCRIPTION_ID = self.get_envvar("SUBSCRIPTION_ID")
                self.RESOURCE_GROUP_NAME = self.get_envvar("RESOURCE_GROUP_NAME")
                self.RESOURCE_GROUP_LOCATION = self.get_envvar("RESOURCE_GROUP_LOCATION")
                self.IOTHUB_NAME = self.get_envvar("IOTHUB_NAME")
                self.IOTHUB_SKU = self.get_envvar("IOTHUB_SKU")
                self.EDGE_DEVICE_ID = self.get_envvar("EDGE_DEVICE_ID")
                self.CREDENTIALS = self.get_envvar("CREDENTIALS")
                self.UPDATE_DOTENV = self.get_envvar("UPDATE_DOTENV")

                if "DOCKER_HOST" in os.environ:
                    self.DOCKER_HOST = self.get_envvar("DOCKER_HOST")
                else:
                    self.DOCKER_HOST = None
            except Exception as ex:
                self.output.error(
                    "Environment variables not configured correctly. Run `iotedgedev solution --create [name]` to create a new solution with sample .env file. Please see README for variable configuration options. Tip: You might just need to restart your command prompt to refresh your Environment Variables.")
                self.output.error("Variable that caused exception: " + str(ex))
                sys.exit(-1)

        self.loaded = True

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError as e:
            if name in os.environ:
                return self.get_envvar(name)
            else:
                raise e

    def get_envvar(self, key, required=False, default=None, altkeys=None):
        val = ""
        if altkeys is None:
            altkeys = []

        # some envvars have alternate keys for legacy reasons, name changes, etc.  this processes key first and then looks in each altkey until it finds a match.
        altkeys.insert(0, key)
        for altkey in altkeys:
            if altkey in os.environ:
                val = os.environ[altkey].strip()
                if val:
                    break

        if required and not val:
            self.output.error("Environment Variable {0} not set. Either add to .env file or to your system's Environment Variables".format(key))
            sys.exit(-1)

        # if we have a val return it, if not and we have a default then return default, otherwise return None.
        if val:
            return val
        elif default:
            self.set_envvar(key, default)
            return default
        else:
            return ''

    def verify_envvar_has_val(self, key, value):
        if not value:
            self.output.error("Environment Variable {0} not set. Either add to .env file or to your system's Environment Variables".format(key))
            sys.exit(-1)

    def get_envvar_key_if_val(self, key):
        if key in os.environ and os.environ.get(key):
            return key
        else:
            return None

    def set_envvar(self, key, value):
        os.environ[key] = value

    def save_envvar(self, key, value):
        try:
            dotenv_file = self.get_dotenv_file()
            dotenv_path = os.path.join(os.getcwd(), dotenv_file)
            set_key(dotenv_path, key, value)
        except Exception:
            self.output.error(f("Could not update the environment variable {key} in file {dotenv_path}"))
            sys.exit(-1)

    def get_registries(self):
        registries = {}
        self.CONTAINER_REGISTRY_MAP = {}
        length_container_registry_server = len('container_registry_server')
        length_container_registry_username_or_password = len('container_registry_username')
        length_container_registry_ = len('container_registry_')
        for key in os.environ:
            key = key.lower()
            if key.startswith('container_registry_server'):
                token = key[length_container_registry_server:]
                if token not in registries:
                    registries[token] = {}
                registries[token]['server'] = os.environ[key]
            elif key.startswith(('container_registry_username', 'container_registry_password')):
                token = key[length_container_registry_username_or_password:]
                subkey = key[length_container_registry_:length_container_registry_username_or_password]
                if token not in registries:
                    registries[token] = {}
                registries[token][subkey] = os.environ[key]

        for key, value in registries.items():
            self.CONTAINER_REGISTRY_MAP[key] = ContainerRegistry(value['server'], value['username'], value['password'])

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
