import os
import requests
from shutil import copyfile
import json
from distutils.dir_util import copy_tree


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
                mod_proc = ModulesProcessorFactory(
                    self.envvars, self.utility, self.output, os.path.join(module_dir, "module.json")).get()
                    
                # build module
                if (mod_proc.build(module_dir) == False):
                    continue

                # Get all docker files in project
                docker_files = self.utility.find_files(
                    module_dir, "Dockerfile*")

                # Filter by Docker Dirs in envvars
                docker_dirs_process = [docker_dir.strip()
                                       for docker_dir in self.envvars.ACTIVE_DOCKER_DIRS.split(",") if docker_dir]

                # Process each Dockerfile found
                for docker_file in docker_files:

                    docker_file_parent_folder = os.path.basename(
                        os.path.dirname(docker_file))

                    if len(
                            docker_dirs_process) == 0 or docker_dirs_process[0] == "*" or docker_file_parent_folder in docker_dirs_process:

                        self.output.info(
                            "PROCESSING DOCKER FILE: " + docker_file)

                        docker_file_name = os.path.basename(docker_file)

                        # assume /Docker/{runtime}/Dockerfile folder structure
                        # image name will be the same as the module folder name, filter-module
                        # tag will be {runtime}{ext}{container_tag}, i.e. linux-x64-debug-jong
                        # runtime is the Dockerfile immediate parent folder name
                        # ext is Dockerfile extension for example with Dockerfile.debug, debug is the mod
                        # CONTAINER_TAG is env var

                        # i.e. when found: filter-module/Docker/linux-x64/Dockerfile.debug and CONTAINER_TAG = jong
                        # we'll get: filtermodule:linux-x64-debug-jong

                        runtime = os.path.basename(
                            os.path.dirname(docker_file))
                        ext = "" if os.path.splitext(docker_file)[
                            1] == "" else "-" + os.path.splitext(docker_file)[1][1:]
                        container_tag = "" if self.envvars.CONTAINER_TAG == "" else "-" + \
                            self.envvars.CONTAINER_TAG

                        tag_name = runtime + ext + container_tag

                        # construct the build output path
                        build_path = os.path.join(
                            os.getcwd(), "build", "modules", module, runtime)
                        if not os.path.exists(build_path):
                            os.makedirs(build_path)

                        # publish module
                        self.output.info(
                            "PUBLISHING PROJECT: " + module_dir)
                        mod_proc.publish(module_dir, build_path)


                        # copy Dockerfile to publish dir
                        build_dockerfile = os.path.join(
                            build_path, docker_file_name)

                        copyfile(docker_file, build_dockerfile)

                        image_destination_name = "{0}/{1}:{2}".format(
                            self.envvars.CONTAINER_REGISTRY_SERVER, module, tag_name).lower()

                        self.output.info(
                            "BUILDING DOCKER IMAGE: " + image_destination_name)

                        # cd to the build output to build the docker image
                        project_dir = os.getcwd()
                        os.chdir(build_path)

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


class ModulesProcessorFactory(object):

    def __init__(self, envvars, utility, output, module_json_file):
        self.envvars = envvars
        self.utility = utility
        self.output = output
        self.module_json_file = module_json_file

    def load_module_json(self):
        if os.path.exists(self.module_json_file):
            file_json_content = json.loads(
                self.utility.get_file_contents(self.module_json_file))
            return file_json_content.get("language")

        else:
            self.output.info(
                "No module.json file found. Default to dotnet module")
            return "csharp"

    def get(self):
        module_language = self.load_module_json().lower()
        if module_language == "csharp" or module_language == "fsharp" or module_language == "vbasic":
            return DotNetModuleProcessor(self.envvars, self.utility, self.output, "")

        else:
            return OtherModuleProcessor(self.envvars, self.utility, self.output, "")


class DotNetModuleProcessor(ModulesProcessorFactory):
    def build(self, module_dir):
        project_files = [os.path.join(module_dir, f) for f in os.listdir(
            module_dir) if f.endswith("proj")]

        if len(project_files) == 0:
            self.output.error("No project file found for module.")
            return False
        else:
            self.utility.exe_proc(["dotnet", "build", project_files[0],
                                   "-v", self.envvars.DOTNET_VERBOSITY])
            return True

    def publish(self, module_dir, build_path):
        project_file = [os.path.join(module_dir, f) for f in os.listdir(
            module_dir) if f.endswith("proj")][0]
        self.utility.exe_proc(["dotnet", "publish", project_file, "-f", "netcoreapp2.0",
                               "-o", build_path, "-v", self.envvars.DOTNET_VERBOSITY])


class OtherModuleProcessor (ModulesProcessorFactory):
    def build(self, module_dir):
        return True

    def publish(self, module_dir, build_path):
        copy_tree(module_dir, os.path.join("build", module_dir))
