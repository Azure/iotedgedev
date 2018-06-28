import os
import re

from .deploymentmanifest import DeploymentManifest
from .dotnet import DotNet
from .module import Module
from .modulesprocessorfactory import ModulesProcessorFactory


class Modules:
    def __init__(self, envvars, utility, output, dock):
        self.envvars = envvars
        self.utility = utility
        self.output = output
        self.dock = dock
        self.dock.init_registry()

    def add(self, name, template):
        self.output.header("ADDING MODULE")

        cwd = self.envvars.MODULES_PATH
        if name.startswith("_") or name.endswith("_"):
            self.output.error("Module name cannot start or end with the symbol _")
            return
        elif not re.match("^[a-zA-Z0-9_]+$", name):
            self.output.error("Module name can only contain alphanumeric characters and the symbol _")
            return
        elif os.path.exists(os.path.join(cwd, name)):
            self.output.error("Module \"{0}\" already exists under {1}".format(name, os.path.abspath(self.envvars.MODULES_PATH)))
            return

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE, True)

        repo = "{0}/{1}".format("${CONTAINER_REGISTRY_SERVER}", name.lower())
        if template == "csharp":
            dotnet = DotNet(self.envvars, self.output, self.utility)
            dotnet.install_module_template()
            dotnet.create_custom_module(name, repo, cwd)
        elif template == "nodejs":
            self.utility.check_dependency("yo azure-iot-edge-module --help".split(), "To add new Node.js modules, the Yeoman tool and Azure IoT Edge Node.js module generator")
            cmd = "yo azure-iot-edge-module -n {0} -r {1}".format(name, repo)
            self.output.header(cmd)
            self.utility.exe_proc(cmd.split(), shell=True, cwd=cwd)
        elif template == "python":
            self.utility.check_dependency("cookiecutter --help".split(), "To add new Python modules, the Cookiecutter tool")
            github_source = "https://github.com/Azure/cookiecutter-azure-iot-edge-module"
            branch = "master"
            cmd = "cookiecutter --no-input {0} module_name={1} image_repository={2} --checkout {3}".format(github_source, name, repo, branch)
            self.output.header(cmd)
            self.utility.exe_proc(cmd.split(), cwd=cwd)
        elif template == "csharpfunction":
            dotnet = DotNet(self.envvars, self.output, self.utility)
            dotnet.install_function_template()
            dotnet.create_function_module(name, repo, cwd)

        deployment_manifest.add_module_template(name)
        deployment_manifest.add_temp_sensor_route(name)
        deployment_manifest.save()

        self.output.footer("ADD COMPLETE")

    def build(self):
        self.build_push(no_push=True)

    def push(self, no_build=False):
        self.build_push(no_build=no_build)

    def build_push(self, no_build=False, no_push=False):
        self.output.header("BUILDING MODULES", suppress=no_build)

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE, True)
        modules_to_process = deployment_manifest.get_modules_to_process()

        var_dict = {}

        for module_dir_base, module_platform in modules_to_process:
            self.output.info("BUILDING MODULE: {0}".format(module_dir_base), suppress=no_build)

            module_dir = os.path.join(self.envvars.MODULES_PATH, module_dir_base)
            module_json = Module(self.output, self.utility, os.path.join(module_dir, "module.json"))

            for platform in module_json.platforms:
                if platform == module_platform:
                    # get the Dockerfile from module.json
                    dockerfile = module_json.get_dockerfile_by_platform(platform)

                    self.output.info("PROCESSING DOCKER FILE: " + dockerfile, suppress=no_build)

                    dockerfile_name = os.path.basename(dockerfile)
                    container_tag = "" if self.envvars.CONTAINER_TAG == "" else "-" + self.envvars.CONTAINER_TAG
                    tag_name = module_json.tag_version + container_tag
                    image_destination_name = os.path.expandvars("{0}:{1}-{2}".format(module_json.repository, tag_name, platform).lower())
                    var_dict["${{MODULES.{0}.{1}}}".format(module_dir_base, platform)] = image_destination_name

                    self.output.info("BUILDING DOCKER IMAGE: " + image_destination_name, suppress=no_build)

                    # cd to the module folder to build the docker image
                    project_dir = os.getcwd()
                    os.chdir(os.path.join(project_dir, module_dir))

                    # BUILD DOCKER IMAGE
                    if not no_build:
                        build_options = self.filter_build_options(module_json.build_options)
                        # TODO: apply build options
                        build_result = self.dock.docker_client.images.build(tag=image_destination_name, path=".", dockerfile=dockerfile_name)

                        self.output.info("DOCKER IMAGE DETAILS: {0}".format(build_result))

                    # CD BACK UP
                    os.chdir(project_dir)

                    if not no_push:
                        # PUSH TO CONTAINER REGISTRY
                        self.output.info("PUSHING DOCKER IMAGE TO: " + image_destination_name)

                        for line in self.dock.docker_client.images.push(repository=image_destination_name, stream=True, auth_config={
                                                                        "username": self.envvars.CONTAINER_REGISTRY_USERNAME, "password": self.envvars.CONTAINER_REGISTRY_PASSWORD}):
                            self.output.procout(self.utility.decode(line).replace("\\u003e", ">"))

            self.output.footer("BUILD COMPLETE", suppress=no_build)
            self.output.footer("PUSH COMPLETE", suppress=no_push)
        self.utility.set_config(force=True, var_dict=var_dict)

    @staticmethod
    def filter_build_options(build_options):
        """Remove build options which will be ignored"""
        filtered_build_options = []
        for build_option in build_options:
            build_option = build_option.strip()
            parsed_option = re.compile(r"\s+").split(build_option)
            if parsed_option and ["--rm", "--tag", "-t", "--file", "-f"].index(parsed_option[0]) < 0:
                filtered_build_options.append(build_option)

        return filtered_build_options
