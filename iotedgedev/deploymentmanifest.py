"""
This module provides interfaces to manipulate IoT Edge deployment manifest (deployment.json)
and deployment manifest template (deployment.template.json)
"""

import json
import os
import re
import shutil

import six

from .compat import PY2

if PY2:
    from .compat import FileNotFoundError

TWIN_VALUE_MAX_SIZE = 512
TWIN_VALUE_MAX_CHUNKS = 8


class DeploymentManifest:
    def __init__(self, envvars, output, utility, path, is_template):
        self.utility = utility
        self.output = output
        try:
            self.path = path
            self.is_template = is_template
            self.json = json.loads(self.utility.get_file_contents(path, expandvars=True))
        except FileNotFoundError:
            if is_template:
                deployment_manifest_path = envvars.DEPLOYMENT_CONFIG_FILE_PATH
                if os.path.exists(deployment_manifest_path):
                    self.output.error('Deployment manifest template file "{0}" not found'.format(path))
                    if output.confirm('Would you like to make a copy of the deployment manifest file "{0}" as the deployment template file?'.format(deployment_manifest_path), default=True):
                        shutil.copyfile(deployment_manifest_path, path)
                        self.json = json.load(open(envvars.DEPLOYMENT_CONFIG_FILE_PATH))
                        envvars.save_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", path)
                else:
                    raise FileNotFoundError('Deployment manifest file "{0}" not found'.format(path))
            else:
                raise FileNotFoundError('Deployment manifest file "{0}" not found'.format(path))

    def add_module_template(self, module_name):
        """Add a module template to the deployment manifest with amd64 as the default platform"""
        new_module = """{
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": \"${MODULES.""" + module_name + """.amd64}\",
              "createOptions": {}
            }
        }"""

        try:
            self.utility.nested_set(self._get_module_content(), ["$edgeAgent", "properties.desired", "modules", module_name], json.loads(new_module))
        except KeyError as err:
            raise KeyError("Missing key {0} in file {1}".format(err, self.path))

        self.add_default_route(module_name)

    def add_default_route(self, module_name):
        """Add a default route to send messages to IoT Hub"""
        new_route_name = "{0}ToIoTHub".format(module_name)
        new_route = "FROM /messages/modules/{0}/outputs/* INTO $upstream".format(module_name)

        try:
            self.utility.nested_set(self._get_module_content(), ["$edgeHub", "properties.desired", "routes", new_route_name], new_route)
        except KeyError as err:
            raise KeyError("Missing key {0} in file {1}".format(err, self.path))

    def get_user_modules(self):
        """Get user modules from deployment manifest"""
        try:
            return self.get_desired_property("$edgeAgent", "modules")
        except KeyError as err:
            raise KeyError("Missing key {0} in file {1}".format(err, self.path))

    def get_system_modules(self):
        """Get system modules from deployment manifest"""
        try:
            return self.get_desired_property("$edgeAgent", "systemModules")
        except KeyError as err:
            raise KeyError("Missing key {0} in file {1}".format(err, self.path))

    def get_all_modules(self):
        all_modules = {}
        all_modules.update(self.get_user_modules())
        all_modules.update(self.get_system_modules())

        return all_modules

    def get_modules_to_process(self):
        """Get modules to process from deployment manifest template"""
        try:
            user_modules = self.get_desired_property("$edgeAgent", "modules")
            modules_to_process = []
            for _, module_info in user_modules.items():
                image = module_info["settings"]["image"]
                # If the image is placeholder, e.g., ${MODULES.NodeModule.amd64}, parse module folder and platform from the placeholder
                if image.startswith("${") and image.endswith("}") and len(image.split(".")) > 2:
                    first_dot = image.index(".")
                    second_dot = image.index(".", first_dot + 1)
                    module_dir = image[first_dot+1:second_dot]
                    module_platform = image[second_dot+1:image.index("}")]
                    modules_to_process.append((module_dir, module_platform))
            return modules_to_process
        except KeyError as err:
            raise KeyError("Missing key {0} in file {1}".format(err, self.path))

    def get_desired_property(self, module, prop):
        return self._get_module_content()[module]["properties.desired"][prop]

    def convert_create_options(self):
        modules = self.get_all_modules()
        for module_name, module_info in modules.items():
            if "settings" in module_info and "createOptions" in module_info["settings"]:
                create_options = module_info["settings"]["createOptions"]
                if not isinstance(create_options, six.string_types):
                    # Stringify and minify the createOptions from dict format
                    create_options = json.dumps(create_options, separators=(',', ':'))

                options = [m for m in re.finditer("(.|[\r\n]){{1,{0}}}".format(TWIN_VALUE_MAX_SIZE), create_options)]
                if len(options) > TWIN_VALUE_MAX_CHUNKS:
                    raise ValueError("Size of createOptions of {0} is too big. The maximum size of createOptions is 4K".format(module_name))

                for i, option in enumerate(options):
                    if i == 0:
                        module_info["settings"]["createOptions"] = option.group()
                    else:
                        module_info["settings"]["createOptions{0:0=2d}".format(i)] = option.group()

    def expand_image_placeholders(self, replacements):
        modules = self.get_all_modules()
        for module_name, module_info in modules.items():
            if module_name in replacements:
                self.utility.nested_set(module_info, ["settings", "image"], replacements[module_name])

    def dump(self, path=None):
        """Dump the JSON to the disk"""
        if path is None:
            path = self.path

        with open(path, "w") as deployment_manifest:
            json.dump(self.json, deployment_manifest, indent=2)

    def _get_module_content(self):
        if "modulesContent" in self.json:
            return self.json["modulesContent"]
        elif "moduleContent" in self.json:
            return self.json["moduleContent"]
        else:
            raise KeyError("modulesContent")
