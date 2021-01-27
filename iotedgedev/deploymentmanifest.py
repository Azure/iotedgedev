"""
This module provides interfaces to manipulate IoT Edge deployment manifest (deployment.json)
and deployment manifest template (deployment.template.json)
"""

import json
import os
import re
import shutil

import jsonschema
from urllib.request import urlopen

from .utility import Utility
from .constants import Constants


TWIN_VALUE_MAX_SIZE = 512
TWIN_VALUE_MAX_CHUNKS = 8


class DeploymentManifest:
    def __init__(self, envvars, output, utility, path, is_template, expand_vars=True):
        self.envvars = envvars
        self.utility = utility
        self.output = output
        try:
            self.path = path
            self.is_template = is_template
            self.json = json.loads(Utility.get_file_contents(path, expandvars=expand_vars))
        except FileNotFoundError:
            if is_template:
                deployment_manifest_path = self.envvars.DEPLOYMENT_CONFIG_FILE_PATH
                if os.path.exists(deployment_manifest_path):
                    self.output.error('Deployment manifest template file "{0}" not found'.format(path))
                    if output.confirm('Would you like to make a copy of the deployment manifest file "{0}" as the deployment template file?'.format(deployment_manifest_path), default=True):
                        shutil.copyfile(deployment_manifest_path, path)
                        self.json = json.load(open(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH))
                        self.envvars.save_envvar("DEPLOYMENT_CONFIG_TEMPLATE_FILE", path)
                else:
                    raise FileNotFoundError('Deployment manifest file "{0}" not found'.format(path))
            else:
                raise FileNotFoundError('Deployment manifest file "{0}" not found'.format(path))

    def add_module_template(self, module_name, create_options={}, is_debug=False):
        """Add a module template to the deployment manifest"""
        new_module = {
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
                "image": DeploymentManifest.get_image_placeholder(module_name, is_debug),
                "createOptions": create_options
            }
        }

        try:
            self.utility.nested_set(self._get_module_content(), ["$edgeAgent", "properties.desired", "modules", module_name], new_module)
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

    def get_desired_property(self, module, prop):
        return self._get_module_content()[module]["properties.desired"][prop]

    def get_template_schema_ver(self):
        return self.json.get("$schema-template", "")

    def convert_create_options(self):
        modules = self.get_all_modules()
        for module_name, module_info in modules.items():
            if "settings" in module_info and "createOptions" in module_info["settings"]:
                create_options = module_info["settings"]["createOptions"]
                if not isinstance(create_options, str):
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

    def expand_environment_variables(self):
        self.json = json.loads(os.path.expandvars(json.dumps(self.json)))

    def del_key(self, keys):
        self.utility.del_key(self.json, keys)

    def dump(self, path=None):
        """Dump the JSON to the disk"""
        if path is None:
            path = self.path

        with open(path, "w") as deployment_manifest:
            json.dump(self.json, deployment_manifest, indent=2)

    def validate_deployment_template(self):
        validation_success = True
        try:
            template_schema = json.loads(urlopen(Constants.deployment_template_schema_url).read().decode("utf-8"))
            validation_success = self._validate_json_schema(template_schema, self.json, "Deployment template")
        except Exception as ex:  # Ignore other non shcema validation errors
            self.output.info("Unexpected error during deployment template schema validation, skip schema validation. Error:%s" % ex)

        return validation_success

    def validate_deployment_manifest(self):
        validation_success = True
        try:
            validation_success = self._validate_deployment_manifest_schema()
            validation_success &= self._validate_create_options()
        except Exception as err:
            self.output.info("Unexpected error during deployment manifest validation, skip the validation. Error:%s" % err)

        return validation_success

    @staticmethod
    def get_image_placeholder(module_name, is_debug=False):
        return "${{MODULES.{0}}}".format(module_name + ".debug" if is_debug else module_name)

    def _get_module_content(self):
        if "modulesContent" in self.json:
            return self.json["modulesContent"]
        elif "moduleContent" in self.json:
            return self.json["moduleContent"]
        else:
            raise KeyError("modulesContent")

    # Carefully check upper/lower case of the output when using this function
    def _validate_json_schema(self, schema_object, json_object, schema_type):
        validation_success = True
        try:
            self.output.info("Validating schema of %s." % schema_type.lower())
            validator_class = jsonschema.validators.validator_for(schema_object)
            validator = validator_class(schema_object)
            validation_errors = validator.iter_errors(self.json)
            for error in validation_errors:
                validation_success = False
                self.output.warning("%s schema error: %s. Property path:%s" % (schema_type, error.message, "->".join(error.path)))
            if validation_success:
                self.output.info("%s schema validation passed." % schema_type)
            else:
                self.output.warning("%s schema validation failed. Please see previous logs for more details" % schema_type)

        except jsonschema.exceptions.SchemaError as schemaErr:
            self.output.info("Errors found in %s schema, skip schema validation. Error:%s" % (schema_type, schemaErr.message))
        except Exception as ex:  # Ignore other non schema validation errors
            self.output.info("Unexpected error during %s schema validation, skip schema validation. Error:%s" % (schema_type, ex))

        return validation_success

    def _validate_deployment_manifest_schema(self):
        validation_success = True
        try:
            deployment_schema = json.loads(urlopen(Constants.deployment_manifest_schema_url).read())
            validation_success = self._validate_json_schema(deployment_schema, self.json, "Deployment manifest")
        except Exception as ex:  # Ignore other non schema validation errors
            self.output.info("Unexpected error during deployment manifest schema validation, skip schema validation. Error:%s" % ex)

        return validation_success

    # Call _validate_deployment_manifest_schema first. This function assumes createOptions are strings.
    def _validate_create_options(self):
        self.output.info("Start validating createOptions for all modules.")
        modules = self.get_all_modules()
        validation_success = True
        for module_name, module_info in modules.items():
            current_module_validation_success = True
            try:
                self.output.info("Validating createOptions for module %s" % module_name)
                if "settings" in module_info and "createOptions" in module_info["settings"]:
                    current_module_validation_success = self._validate_create_options_for_module(module_name, module_info)
                    if current_module_validation_success:
                        self.output.info("createOptions of module %s validation passed" % module_name)
                else:
                    self.output.info("No settings or createOptions property found in module %s. Skip createOptions validation." % module_name)
            except Exception as ex:
                self.output.info("Unexpected error occurs when validating createOptions for module %s: %s" % (module_name, ex))
            finally:
                validation_success &= current_module_validation_success
        if (validation_success):
            self.output.info("Validation for all createOptions passed.")
        else:
            self.output.warning("Errors found during createOptions validation. Please check the logs for details.")
        return validation_success

    def _validate_create_options_for_module(self, module_name, module_info):
        validation_success = True
        validation_success &= self._validate_create_options_lengh(module_name, module_info)
        validation_success &= self._validate_create_options_format(module_name, module_info)
        return validation_success

    def _validate_create_options_lengh(self, module_name, module_info):
        validation_success = True
        create_options_value = module_info["settings"]["createOptions"]
        if len(str(create_options_value)) > TWIN_VALUE_MAX_SIZE:
            validation_success = False
            self.output.warning("Length of createOptions in module %s exceeds %d" % (module_name, TWIN_VALUE_MAX_SIZE))
        # Merge additional create options
        for i in range(1, TWIN_VALUE_MAX_CHUNKS):
            property_name = "createOptions0%d" % i
            if property_name in module_info["settings"]:
                create_options_value = module_info["settings"][property_name]
                if len(str(create_options_value)) > TWIN_VALUE_MAX_SIZE:
                    validation_success = False
                    self.output.warning("Length of %s in module %s exceeds %d" % (property_name, module_name, TWIN_VALUE_MAX_SIZE))
            else:
                break
        return validation_success

    def _validate_create_options_format(self, module_name, module_info):
        validation_success = True
        create_options_string = self._merge_create_options(module_name, module_info)
        if not create_options_string.startswith('{'):
            validation_success = False
            self.output.warning("createOptions of module %s should be an object" % module_name)
        else:
            try:
                json.loads(create_options_string)
            except ValueError as err:
                validation_success = False
                self.output.warning("createOptions of module %s is not a valid JSON string. Error: %s" % (module_name, err))
        return validation_success

    def _merge_create_options(self, module_name, module_info):
        create_options = []
        create_options.append(str(module_info["settings"]["createOptions"]))
        # Merge additional create options
        for i in range(1, TWIN_VALUE_MAX_CHUNKS):
            property_name = "createOptions0%d" % i
            if property_name in module_info["settings"]:
                create_options.append(str(module_info["settings"][property_name]))
            else:
                break
        return "".join(create_options).strip()
