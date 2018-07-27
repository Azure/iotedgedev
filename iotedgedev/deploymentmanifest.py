"""
This module provides interfaces to manipulate IoT Edge deployment manifest (deployment.json)
and deployment manifest template (deployment.template.json)
"""

import json
import os
import shutil
import sys


class DeploymentManifest:
    def __init__(self, envvars, output, utility, path, is_template):
        self.utility = utility
        self.output = output
        try:
            self.path = path
            self.is_template = is_template
            self.json = json.loads(self.utility.get_file_contents(path, expandvars=True))
        except FileNotFoundError:
            self.output.error('Deployment manifest template file "{0}" not found'.format(path))
            if is_template:
                deployment_manifest_path = envvars.DEPLOYMENT_CONFIG_FILE_PATH
                if os.path.exists(deployment_manifest_path):
                    if output.confirm('Would you like to make a copy of the deployment manifest file "{0}" as the deployment template file?'.format(deployment_manifest_path), default=True):
                        shutil.copyfile(deployment_manifest_path, path)
                        self.json = json.load(open(envvars.DEPLOYMENT_CONFIG_FILE_PATH))
                        envvars.save_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", path)
            else:
                self.output.error('Deployment manifest file "{0}" not found'.format(path))
                sys.exit(1)

    def add_module_template(self, module_name):
        """Add a module template to the deployment manifest with amd64 as the default platform"""
        new_module = """{
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": \"${MODULES.""" + module_name + """.amd64}\",
              "createOptions": ""
            }
        }"""

        self.utility.nested_set(self.json, ["moduleContent", "$edgeAgent", "properties.desired", "modules", module_name], json.loads(new_module))

        self.add_default_route(module_name)

    def add_default_route(self, module_name):
        """Add a default route to send messages to IoT Hub"""
        new_route_name = "{0}ToIoTHub".format(module_name)
        new_route = "FROM /messages/modules/{0}/outputs/* INTO $upstream".format(module_name)

        self.utility.nested_set(self.json, ["moduleContent", "$edgeHub", "properties.desired", "routes", new_route_name], new_route)

    def get_modules_to_process(self):
        """Get modules to process from deployment manifest template"""
        user_modules = self.json.get("moduleContent", {}).get("$edgeAgent", {}).get("properties.desired", {}).get("modules", {})
        modules_to_process = []
        for _, module_info in user_modules.items():
            image = module_info.get("settings", {}).get("image", "")
            # If the image is placeholder, e.g., ${MODULES.NodeModule.amd64}, parse module folder and platform from the placeholder
            if image.startswith("${") and image.endswith("}") and len(image.split(".")) > 2:
                first_dot = image.index(".")
                second_dot = image.index(".", first_dot + 1)
                module_dir = image[first_dot+1:second_dot]
                module_platform = image[second_dot+1:image.index("}")]
                modules_to_process.append((module_dir, module_platform))
        return modules_to_process

    def save(self):
        """Dump the JSON to the disk"""
        with open(self.path, "w") as deployment_manifest:
            json.dump(self.json, deployment_manifest, indent=2)
