from base64 import b64encode, b64decode
import fnmatch
from hashlib import sha256
from hmac import HMAC
import json
import os
import subprocess
import sys
from time import time
if sys.version_info.major >= 3:
    from urllib.parse import quote, urlencode
else:
    from urllib import quote, urlencode
from .moduletype import ModuleType


class Utility:
    def __init__(self, envvars, output):
        self.envvars = envvars
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

    def call_proc(self, params, shell=False, cwd=None):
        try:
            subprocess.check_call(params, shell=shell, cwd=cwd)
        except KeyboardInterrupt as ki:
            return
        except Exception as e:
            self.output.error("Error while executing command: {0}. {1}".format(' '.join(params), str(e)))

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

    def get_file_contents(self, file):
        with open(file, "r") as file:
            return file.read()

    def decode(self, val):
        return val.decode("utf-8").strip()

    def get_config_files(self):
        # config files are in root of solution

        return [os.path.join(os.getcwd(), f) for f in os.listdir(os.getcwd()) if f.endswith("template.json")]

    def get_active_modules(self):
        return [module.strip()
                for module in self.envvars.ACTIVE_MODULES.split(",") if module]

    def get_modules_in_config(self, moduleType):
        modules_config = json.load(open(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH))

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

                config_file_expanded = os.path.expandvars(
                    self.get_file_contents(config_file))

                with open(build_config_file, "w") as config_file_build:
                    config_file_build.write(config_file_expanded)

            self.output.line()

        self.config_set = True
