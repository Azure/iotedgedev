import os
import platform
from shutil import copyfile

from dotenv import load_dotenv, set_key
from fstrings import f

from .args import Args
from .connectionstring import DeviceConnectionString, IoTHubConnectionString
from .constants import Constants
from .containerregistry import ContainerRegistry
from .utility import Utility


class EnvVars:
    def __init__(self, output):
        self.output = output
        self.loaded = False

        current_command = Args().get_current_command()

        # for some commands we don't want verbose dotenv load output
        self.terse_commands = ['', 'iothub setup', 'solution init', 'init', 'solution e2e', 'solution new', 'new', 'simulator stop', 'simulator modulecred']
        self.verbose = not self.is_terse_command(current_command)

    def backup_dotenv(self):
        dotenv_path = self.get_dotenv_file_path()
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
        dotenv_path = self.get_dotenv_path(dotenv_file)

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

        if "DOTENV_FILE" not in os.environ:
            return default_dotenv_file
        else:
            dotenv_file_from_environ = os.environ["DOTENV_FILE"].strip("\"").strip("'")
            if dotenv_file_from_environ:
                return dotenv_file_from_environ

        return default_dotenv_file

    def get_dotenv_path(self, dotenv_file):
        return os.path.join(os.getcwd(), dotenv_file)

    def get_dotenv_file_path(self):
        return self.get_dotenv_path(self.get_dotenv_file())

    def load(self, force=False):
        if not self.loaded or force:
            if self.verbose:
                self.output.header("ENVIRONMENT VARIABLES")

            self.load_dotenv()

            try:
                try:
                    self.IOTHUB_CONNECTION_STRING = self.get_envvar("IOTHUB_CONNECTION_STRING")
                    self.IOTHUB_CONNECTION_INFO = None
                    if self.IOTHUB_CONNECTION_STRING:
                        self.IOTHUB_CONNECTION_INFO = IoTHubConnectionString(self.IOTHUB_CONNECTION_STRING)

                except Exception as ex:
                    raise ValueError("Unable to parse IOTHUB_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set. {0}".format(str(ex)))

                try:
                    self.DEVICE_CONNECTION_STRING = self.get_envvar("DEVICE_CONNECTION_STRING")
                    self.DEVICE_CONNECTION_INFO = None
                    if self.DEVICE_CONNECTION_STRING:
                        self.DEVICE_CONNECTION_INFO = DeviceConnectionString(self.DEVICE_CONNECTION_STRING)

                except Exception as ex:
                    raise ValueError("Unable to parse DEVICE_CONNECTION_STRING Environment Variable. Please ensure that you have the right connection string set. {0}".format(str(ex)))

                self.get_registries()

                self.BYPASS_MODULES = self.get_envvar("BYPASS_MODULES", default="")
                self.CONTAINER_TAG = self.get_envvar("CONTAINER_TAG", default="")
                self.EDGE_RUNTIME_VERSION = self.get_envvar("EDGE_RUNTIME_VERSION", default="")
                self.EDGEAGENT_SCHEMA_VERSION = self.get_envvar("EDGEAGENT_SCHEMA_VERSION", default="")
                self.EDGEHUB_SCHEMA_VERSION = self.get_envvar("EDGEHUB_SCHEMA_VERSION", default="")
                self.CONFIG_OUTPUT_DIR = self.get_envvar("CONFIG_OUTPUT_DIR", default=Constants.default_config_folder)
                self.DEPLOYMENT_CONFIG_TEMPLATE_FILE = self.get_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", default=Constants.default_deployment_template_file)
                self.DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE = self.get_envvar("DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE", default=Constants.default_deployment_debug_template_file)
                self.DEFAULT_PLATFORM = self.get_envvar("DEFAULT_PLATFORM", default=Constants.default_platform)
                self.DEPLOYMENT_CONFIG_FILE = Utility.get_deployment_manifest_name(self.DEPLOYMENT_CONFIG_TEMPLATE_FILE, None, self.DEFAULT_PLATFORM)
                self.MODULES_PATH = self.get_envvar("MODULES_PATH", default=Constants.default_modules_folder)
                self.LOGS_PATH = self.get_envvar("LOGS_PATH", default="logs")
                self.LOGS_CMD = self.get_envvar("LOGS_CMD", default="start /B start cmd.exe @cmd /k docker logs {0} -f")
                self.SUBSCRIPTION_ID = self.get_envvar("SUBSCRIPTION_ID")
                self.RESOURCE_GROUP_NAME = self.get_envvar("RESOURCE_GROUP_NAME")
                self.RESOURCE_GROUP_LOCATION = self.get_envvar("RESOURCE_GROUP_LOCATION")
                self.IOTHUB_NAME = self.get_envvar("IOTHUB_NAME")
                self.IOTHUB_SKU = self.get_envvar("IOTHUB_SKU")
                self.EDGE_DEVICE_ID = self.get_envvar("EDGE_DEVICE_ID")
                self.CREDENTIALS = self.get_envvar("CREDENTIALS")
                self.UPDATE_DOTENV = self.get_envvar("UPDATE_DOTENV")

            except Exception as ex:
                msg = "Environment variables not configured correctly. Run `iotedgedev new` to create a new solution with sample .env file. "
                "Please see README for variable configuration options. Tip: You might just need to restart your command prompt to refresh your Environment Variables. "
                "Variable that caused exception: {0}".format(str(ex))
                raise ValueError(msg)

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
            raise ValueError("Environment Variable {0} not set. Either add to .env file or to your system's Environment Variables".format(key))

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
            raise ValueError("Environment Variable {0} not set. Either add to .env file or to your system's Environment Variables".format(key))

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
            raise IOError(f("Could not update the environment variable {key} in file {dotenv_path}"))

    def get_registries(self):
        self.CONTAINER_REGISTRY_MAP = {}
        subkeys = ['server', 'username', 'password']
        # loops through os.environ for key matching container_registry_server, container_registry_username, container_registry_password
        for key in os.environ:
            for subkey in subkeys:
                self._set_registry_map(key, subkey)

    def is_posix(self):
        plat = platform.system().lower()
        return plat == "linux" or plat == "darwin"

    def is_terse_command(self, command):
        return self.in_command_list(command, self.terse_commands)

    def in_command_list(self, command, command_list):
        for cmd in command_list:
            if cmd == '':
                if command == '':
                    return True
                else:
                    continue

            if command.startswith(cmd):
                if len(command) == len(cmd) or command[len(cmd)] == ' ':
                    return True
                else:
                    continue
        return False

    @property
    def DEPLOYMENT_CONFIG_FILE_PATH(self):
        return os.path.join(self.CONFIG_OUTPUT_DIR, self.DEPLOYMENT_CONFIG_FILE)

    def _set_registry_map(self, env_key, subkey):
        registry_key_prefix = 'CONTAINER_REGISTRY_'
        default_key_prefix = registry_key_prefix + subkey.upper()

        # The prefix for additional registries has an additional underscore
        add_key_prefix = default_key_prefix + '_'
        add_key_prefix_length = len(add_key_prefix)

        if env_key.startswith(default_key_prefix):
            if env_key == default_key_prefix:
                token = ''
            elif env_key.startswith(add_key_prefix):
                token = env_key[add_key_prefix_length:]
            else:
                return

            if token not in self.CONTAINER_REGISTRY_MAP:
                self.CONTAINER_REGISTRY_MAP[token] = ContainerRegistry('', '', '')
            setattr(self.CONTAINER_REGISTRY_MAP[token], subkey.lower(), self.get_envvar(env_key))
