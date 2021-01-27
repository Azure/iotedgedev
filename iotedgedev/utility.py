import fnmatch
import json
import os
import subprocess
from base64 import b64decode, b64encode
from hashlib import sha256
from hmac import HMAC
from time import time

from urllib.parse import quote, urlencode

from .constants import Constants


class Utility:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output

    def exe_proc(self, params, shell=False, cwd=None, suppress_out=False):
        proc = subprocess.Popen(
            params, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell, cwd=cwd)

        stdout_data, stderr_data = proc.communicate()
        if not suppress_out and stdout_data != "":
            self.output.procout(self.decode(stdout_data))

        if proc.returncode != 0:
            raise Exception(self.decode(stderr_data))

    def call_proc(self, params, shell=False, cwd=None):
        try:
            subprocess.check_call(params, shell=shell, cwd=cwd)
            return 0
        except KeyboardInterrupt as ki:
            return 1
        except Exception as e:
            self.output.error("Error while executing command: {0}. {1}".format(' '.join(params), str(e)))
            return 1

    def check_dependency(self, params, description):
        try:
            self.exe_proc(params, shell=not self.envvars.is_posix(), suppress_out=True)
        except FileNotFoundError:
            raise FileNotFoundError("{0} is required by the Azure IoT Edge Dev Tool. For installation instructions, see https://aka.ms/iotedgedevwiki.".format(description))

    def is_dir_empty(self, name):
        if os.path.exists(name):
            return len(os.listdir(name)) == 0
        else:
            return True

    def ensure_dir(self, name):
        if not os.path.exists(name):
            os.makedirs(name)

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

    @staticmethod
    def get_file_contents(file, expandvars=False):
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

    def in_asterisk_list(self, item, asterisk_list):
        return len(asterisk_list) > 0 and (asterisk_list[0] == "*" or item in asterisk_list)

    def copy_from_template_dir(self, src_file, dest_dir, dest_file=None, replacements=None):
        if dest_file is None:
            dest_file = src_file

        template_dir = os.path.join(os.path.split(__file__)[0], "template")
        self.copy_template(os.path.join(template_dir, src_file), os.path.join(dest_dir, dest_file), replacements, expandvars=False)

    def copy_template(self, src, dest=None, replacements=None, expandvars=True):
        """Read file at src, replace the keys in replacements with their values, optionally expand environment variables, and save to dest"""
        if dest is None:
            dest = src

        content = Utility.get_file_contents(src)

        if replacements:
            for key, value in replacements.items():
                content = content.replace(key, value)

        if expandvars:
            content = os.path.expandvars(content)

        with open(dest, "w") as dest_file:
            dest_file.write(content)

    def nested_set(self, dict_, key_path, value):
        current = dict_
        for key in key_path[:-1]:
            if key not in current:
                current[key] = {}
            current = current.get(key)

        current[key_path[-1]] = value

    def del_key(self, dict_, key_path):
        if not isinstance(dict_, dict):
            return None

        current = dict_
        for key in key_path[:-1]:
            current = current.get(key, None)

            if not isinstance(current, dict):
                return None

        return current.pop(key_path[-1], None)

    @staticmethod
    def get_sha256_hash(val):
        hash_object = sha256(val.encode('utf-8'))

        return str(hash_object.hexdigest()).lower()

    @staticmethod
    def get_deployment_manifest_name(template_file, template_schema_ver, platform):
        if "DEPLOYMENT_CONFIG_FILE" in os.environ:
            return os.environ["DEPLOYMENT_CONFIG_FILE"]

        if template_schema_ver is None:
            if os.path.exists(template_file):
                json_ = json.loads(Utility.get_file_contents(template_file, expandvars=True))
                template_schema_ver = json_.get("$schema-template", "")
            else:
                template_schema_ver = Constants.deployment_template_schema_version

        platform = "." + platform if template_schema_ver > "0.0.1" else ""
        prefix = os.path.basename(template_file)
        if prefix.endswith(Constants.deployment_template_suffix):
            prefix = prefix[:-len(Constants.deployment_template_suffix)]
        elif prefix.endswith(".json"):
            prefix = prefix[:-len(".json")]
        else:
            prefix = "deployment"

        return "{0}{1}.json".format(prefix, platform)
