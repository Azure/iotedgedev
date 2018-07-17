
import os
import json
import sys


class Module(object):
    def __init__(self, output, utility, module_json_file):
        self.output = output
        self.utility = utility
        self.module_json_file = module_json_file

        self.module_language = "csharp"
        self.file_json_content = None
        self.load_module_json()

    def load_module_json(self):
        if os.path.exists(self.module_json_file):
            try:
                self.file_json_content = json.loads(
                    os.path.expandvars(self.utility.get_file_contents(self.module_json_file)))

                self.module_language = self.file_json_content.get(
                    "language").lower()
            except:
                self.output.error(
                    "Error while loading module.json file : {0}".format(self.module_json_file))

        else:
            self.output.error(
                "No module.json file found. module.json file is required in the root of your module folder")
            sys.exit()

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

    @property
    def build_options(self):
        return self.file_json_content.get("image", {}).get("buildOptions", [])

    def get_dockerfile_by_platform(self, platform):
        return self.file_json_content.get("image", {}).get("tag", {}).get("platforms", {}).get(platform, "")
