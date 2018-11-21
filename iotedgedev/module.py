import json
import os

from .compat import PY2
from .utility import Utility

if PY2:
    from .compat import FileNotFoundError


class Module(object):
    def __init__(self, envvars, utility, module_name):
        self.utility = utility
        self.module_dir = os.path.join(envvars.MODULES_PATH, module_name)
        self.module_json_file = os.path.join(self.module_dir, "module.json")
        self.module_language = "csharp"
        self.file_json_content = None
        self.load_module_json()

    def load_module_json(self):
        if os.path.exists(self.module_json_file):
            try:
                self.file_json_content = json.loads(Utility.get_file_contents(self.module_json_file, expandvars=True))
                self.module_language = self.file_json_content.get("language").lower()
            except KeyError as e:
                raise KeyError("Error parsing {0} from module.json file : {1}".format(str(e), self.module_json_file))
            except IOError:
                raise IOError("Error loading module.json file : {0}".format(self.module_json_file))
        else:
            raise FileNotFoundError("No module.json file found. module.json file is required in the root of your module folder")

    @property
    def language(self):
        return self.module_language

    @property
    def platforms(self):
        return self.file_json_content.get("image", {}).get("tag", {}).get("platforms", "")

    @property
    def tag_version(self):
        tag = self.file_json_content.get("image", {}).get("tag", {}).get("version", "0.0.0")

        return tag

    @property
    def repository(self):
        return self.file_json_content.get("image", {}).get("repository", "")

    @repository.setter
    def repository(self, repo):
        self.utility.nested_set(self.file_json_content, ["image", "repository"], repo)

    @property
    def build_options(self):
        return self.file_json_content.get("image", {}).get("buildOptions", [])

    @property
    def context_path(self):
        context_path = self.file_json_content.get("image", {}).get("contextPath", ".")
        return os.path.abspath(os.path.join(self.module_dir, context_path))

    def get_dockerfile_by_platform(self, platform):
        platforms = self.file_json_content.get("image", {}).get("tag", {}).get("platforms", {})
        if platform not in platforms:
            raise KeyError("Dockerfile for {0} is not defined in {1}", platform, self.module_json_file)

        return os.path.abspath(os.path.join(self.module_dir, platforms.get(platform)))

    def dump(self):
        with open(self.module_json_file, "w") as f:
            json.dump(self.file_json_content, f, indent=2)
