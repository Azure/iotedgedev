"""
This module provides interfaces to manipulate IoT Edge deployment manifest (deployment.json)
and deployment manifest template (deployment.template.json)
"""

import json
import os
import shutil
import sys


class DeploymentManifest:
    def __init__(self, envvars, output, path, is_template):
        self.output = output
        try:
            self.path = path
            self.is_template = is_template
            self.json = json.load(open(path))
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
                sys.exit()

    def add_module_template(self, module_name):
        """Add a module template to the deployment manifest with amd64 as the default platform"""
        new_module = """{
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": \"{MODULES.""" + module_name + """.amd64}\",
              "createOptions": ""
            }
        }"""

        self.json["moduleContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name] = json.loads(new_module)

        self.add_default_route(module_name)

    def add_default_route(self, module_name):
        """Add a default route to send messages to IoT Hub"""
        new_route_name = "{0}ToIoTHub".format(module_name)
        new_route = "FROM /messages/modules/{0}/outputs/* INTO $upstream".format(module_name)

        self.json["moduleContent"]["$edgeHub"]["properties.desired"]["routes"][new_route_name] = new_route

    def save(self):
        """Dump the JSON to the disk"""
        with open(self.path, "w") as deployment_manifest:
            json.dump(self.json, deployment_manifest, indent=2)
