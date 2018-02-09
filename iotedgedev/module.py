
import os
import json

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
            self.file_json_content = json.loads(
                self.utility.get_file_contents(self.module_json_file))

            self.module_language = self.file_json_content.get("language").lower()
            
        else:
            self.output.info(
                "No module.json file found. Default to dotnet module")
            

    @property
    def language(self):
        return self.module_language

    @property
    def platforms(self):
        return self.file_json_content.get("image").get("tag").get("platforms")
    
    @property
    def tag_version(self):
        return self.file_json_content.get("image").get("tag").get("version")

    def get_Platform_file(self,platform):
        return self.file_json_content.get("image").get("tag").get("platforms").get(platform)
