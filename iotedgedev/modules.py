import os
import requests
from shutil import copyfile

from .module import Module
from .modulesprocessorfactory import ModulesProcessorFactory


class Modules:
    def __init__(self, envvars, utility, output, dock):
        self.envvars = envvars
        self.envvars.check()
        self.utility = utility
        self.utility.set_config()
        self.output = output
        self.dock = dock
        self.dock.init_registry()

    def build(self):
        self.output.header("BUILDING MODULES")

        # Get all the modules to build as specified in config.
        modules_to_process = self.utility.get_active_modules()

        for module in os.listdir(self.envvars.MODULES_PATH):

            if len(
                    modules_to_process) == 0 or modules_to_process[0] == "*" or module in modules_to_process:

                module_dir = os.path.join(self.envvars.MODULES_PATH, module)

                self.output.info("BUILDING MODULE: {0}".format(module_dir))

                module_json = Module(
                    self.output, self.utility, os.path.join(module_dir, "module.json"))
                mod_proc = ModulesProcessorFactory(
                    self.envvars, self.utility, self.output).get(module_json.language)

                # build module
                if (mod_proc.build(module_dir) == False):
                    continue

                docker_arch_process = [docker_arch.strip()
                                       for docker_arch in self.envvars.ACTIVE_DOCKER_ARCH.split(",")if docker_arch]

                for arch in module_json.platforms:
                    if len(
                            docker_arch_process) == 0 or docker_arch_process[0] == "*" or arch in docker_arch_process:

                        # get the docker file from module.json
                        docker_file = module_json.get_platform_by_key(arch)

                        self.output.info(
                            "PROCESSING DOCKER FILE: " + docker_file)

                        docker_file_name = os.path.basename(docker_file)
                        container_tag = "" if self.envvars.CONTAINER_TAG == "" else "-" + \
                            self.envvars.CONTAINER_TAG

                        tag_name = module_json.tag_version + container_tag

                        # publish module
                        self.output.info(
                            "PUBLISHING PROJECT: " + module_dir)

                        mod_proc.publish(module_dir)
                        image_destination_name = "{0}/{1}:{2}-{3}".format(
                            self.envvars.CONTAINER_REGISTRY_SERVER, module, tag_name, docker_file_name).lower()

                        self.output.info(
                            "BUILDING DOCKER IMAGE: " + image_destination_name)

                        # cd to the module folder to build the docker image
                        project_dir = os.getcwd()
                        os.chdir(os.path.join(project_dir, module_dir))

                        # BUILD DOCKER IMAGE
                        build_result = self.dock.docker_client.images.build(
                            tag=image_destination_name, path=".", dockerfile=docker_file_name)
                        self.output.info(
                            "DOCKER IMAGE DETAILS: {0}".format(build_result))

                        # CD BACK UP
                        os.chdir(project_dir)

                        # PUSH TO CONTAINER REGISTRY
                        self.output.info(
                            "PUSHING DOCKER IMAGE TO: " + image_destination_name)

                        for line in self.dock.docker_client.images.push(repository=image_destination_name, tag=tag_name, stream=True, auth_config={
                                                                        "username": self.envvars.CONTAINER_REGISTRY_USERNAME, "password": self.envvars.CONTAINER_REGISTRY_PASSWORD}):
                            self.output.procout(self.utility.decode(line))

                self.output.footer("BUILD COMPLETE")

    def deploy(self):
        self.output.header("DEPLOYING MODULES")
        self.deploy_device_configuration(
            self.envvars.IOTHUB_CONNECTION_INFO.HostName, self.envvars.IOTHUB_CONNECTION_INFO.SharedAccessKey,
            self.envvars.DEVICE_CONNECTION_INFO.DeviceId, self.envvars.MODULES_CONFIG_FILE,
            self.envvars.IOTHUB_CONNECTION_INFO.SharedAccessKeyName, self.envvars.IOT_REST_API_VERSION)
        self.output.footer("DEPLOY COMPLETE")

    def deploy_device_configuration(
            self, host_name, iothub_key, device_id, config_file, iothub_policy_name, api_version):
        resource_uri = host_name
        token_expiration_period = 60
        deploy_uri = "https://{0}/devices/{1}/applyConfigurationContent?api-version={2}".format(
            resource_uri, device_id, api_version)
        iot_hub_sas_token = self.utility.get_iot_hub_sas_token(
            resource_uri, iothub_key, iothub_policy_name, token_expiration_period)

        deploy_response = requests.post(deploy_uri,
                                        headers={
                                            "Authorization": iot_hub_sas_token,
                                            "Content-Type": "application/json"
                                        },
                                        data=self.utility.get_file_contents(
                                            config_file)
                                        )

        if deploy_response.status_code == 204:
            self.output.info(
                "Edge Device configuration successfully deployed to '{0}'.".format(device_id))
        else:
            self.output.info(deploy_uri)
            self.output.info(deploy_response.status_code)
            self.output.info(deploy_response.text)
            self.output.error(
                "There was an error deploying the configuration. Please make sure your IOTHUB_CONNECTION_STRING and DEVICE_CONNECTION_STRING Environment Variables are correct.")
