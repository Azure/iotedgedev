import fnmatch
import os
import subprocess
import sys
from base64 import b64decode, b64encode
from hashlib import sha256
from hmac import HMAC
from time import time

from .deploymentmanifest import DeploymentManifest
from .moduletype import ModuleType

if sys.version_info.major >= 3:
    from urllib.parse import quote, urlencode
else:
    from urllib import quote, urlencode


class Utility:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.config_set = False

    def exe_proc(self, params, shell=False, cwd=None, suppress_out=False):
        proc = subprocess.Popen(
            params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, cwd=cwd)

        stdout_data, stderr_data = proc.communicate()
        if not suppress_out and stdout_data != "":
            self.output.procout(self.decode(stdout_data))

        if proc.returncode != 0:
            self.output.error(self.decode(stderr_data))
            sys.exit()

    def call_proc(self, params, shell=False, cwd=None):
        try:
            subprocess.check_call(params, shell=shell, cwd=cwd)
        except KeyboardInterrupt as ki:
            return
        except Exception as e:
            self.output.error("Error while executing command: {0}. {1}".format(' '.join(params), str(e)))

    def check_dependency(self, params, description, shell=False):
        try:
            self.exe_proc(params, shell=shell, suppress_out=True)
        except:
            self.output.error("{0} is required by the Azure IoT Edge Dev Tool. For installation instructions, see https://aka.ms/iotedgedevwiki.".format(description))
            sys.exit(-1)

    def is_dir_empty(self, name):
        if os.path.exists(name):
            return len(os.listdir(name)) == 0
        else:
            return True

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

    def get_file_contents(self, file, expandvars=False):
        with open(file, "r") as file:
            content = file.read()
            if expandvars:
                return os.path.expandvars(content)
            else:
                return content

    def decode(self, val):
        return val.decode("utf-8").strip()

    def get_config_files(self):
        # config files are in root of solution

        return [os.path.join(os.getcwd(), f) for f in os.listdir(os.getcwd()) if f.endswith("template.json")]

    def get_bypass_modules(self):
        return [module.strip()
                for module in self.envvars.BYPASS_MODULES.split(",") if module]

    def get_active_docker_platform(self):
        return [platform.strip() for platform in self.envvars.ACTIVE_DOCKER_PLATFORMS.split(",") if platform]

    def in_asterisk_list(self, item, asterisk_list):
        return len(asterisk_list) > 0 and (asterisk_list[0] == "*" or item in asterisk_list)

    def get_modules_in_config(self, moduleType):
        deployment_manifest = DeploymentManifest(self.envvars, self.output, self, self.envvars.DEPLOYMENT_CONFIG_FILE_PATH, False)

        system_modules = deployment_manifest.get_system_modules()
        user_modules = deployment_manifest.get_user_modules()

        if moduleType == ModuleType.System:
            return system_modules
        elif moduleType == ModuleType.User:
            return user_modules
        else:
            return_modules = {}
            return_modules.update(system_modules)
            return_modules.update(user_modules)
            return return_modules

    def set_config(self, force=False, replacements=None):

        if not self.config_set or force:
            self.output.header("PROCESSING CONFIG FILES")

            # Create config dir if it doesn't exist
            if not os.path.exists(self.envvars.CONFIG_OUTPUT_DIR):
                os.makedirs(self.envvars.CONFIG_OUTPUT_DIR)

            config_files = self.get_config_files()

            if len(config_files) == 0:
                self.output.info(
                    "Unable to find config files in solution root directory")
                sys.exit()

            # Expand envars and rewrite to config/
            for config_file in config_files:

                build_config_file = os.path.join(
                    self.envvars.CONFIG_OUTPUT_DIR, os.path.basename(config_file).replace(".template", ""))

                self.output.info("Expanding '{0}' to '{1}'".format(
                    os.path.basename(config_file), build_config_file))

                self.copy_template(config_file, build_config_file, replacements, True)

            self.output.line()

        self.config_set = True

    def copy_template(self, src, dest=None, replacements=None, expandvars=True):
        """Read file at src, replace the keys in replacements with their values, optionally expand environment variables, and save to dest"""
        if dest is None:
            dest = src

        content = self.get_file_contents(src)

        if replacements:
            for key, value in replacements.items():
                content = content.replace(key, value)

        if expandvars:
            content = os.path.expandvars(content)

        with open(dest, "w") as dest_file:
            dest_file.write(content)

    def nested_set(self, dic, keys, value):
        current = dic
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current.get(key)

        current[keys[-1]] = value
