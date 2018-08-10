import os
import re
import sys

from .deploymentmanifest import DeploymentManifest
from .dockercls import Docker
from .dotnet import DotNet
from .module import Module
from .utility import Utility


class Modules:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.utility = Utility(self.envvars, self.output)

    def add(self, name, template):
        self.output.header("ADDING MODULE {0}".format(name))

        cwd = self.envvars.MODULES_PATH
        if not os.path.exists(cwd):
            os.makedirs(cwd)

        if name.startswith("_") or name.endswith("_"):
            raise ValueError("Module name cannot start or end with the symbol _")
        elif not re.match("^[a-zA-Z0-9_]+$", name):
            raise ValueError("Module name can only contain alphanumeric characters and the symbol _")
        elif os.path.exists(os.path.join(cwd, name)):
            raise ValueError("Module \"{0}\" already exists under {1}".format(name, os.path.abspath(self.envvars.MODULES_PATH)))

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.utility, self.envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE, True)

        repo = "{0}/{1}".format("${CONTAINER_REGISTRY_SERVER}", name.lower())
        if template == "csharp":
            dotnet = DotNet(self.envvars, self.output, self.utility)
            dotnet.install_module_template()
            dotnet.create_custom_module(name, repo, cwd)
        elif template == "nodejs":
            self.utility.check_dependency("yo azure-iot-edge-module --help".split(), "To add new Node.js modules, the Yeoman tool and Azure IoT Edge Node.js module generator", shell=True)
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
        deployment_manifest.save()

        self.output.footer("ADD COMPLETE")

    def build(self):
        self.build_push(no_push=True)

    def push(self, no_build=False):
        self.build_push(no_build=no_build)

    def build_push(self, no_build=False, no_push=False):
        self.output.header("BUILDING MODULES", suppress=no_build)

        bypass_modules = self.utility.get_bypass_modules()
        active_platform = self.utility.get_active_docker_platform()

        # map (module name, platform) tuple to tag.
        # sample: (('filtermodule', 'amd64'), 'localhost:5000/filtermodule:0.0.1-amd64')
        image_tag_map = {}
        # map image tag to (module name, dockerfile) tuple
        # sample: ('localhost:5000/filtermodule:0.0.1-amd64', ('filtermodule', '/test_solution/modules/filtermodule/Dockerfile.amd64'))
        tag_dockerfile_map = {}
        # map image tag to build options
        # sample: ('localhost:5000/filtermodule:0.0.1-amd64', ["--add-host=github.com:192.30.255.112"])
        tag_build_options_map = {}
        # image tags to build
        # sample: 'localhost:5000/filtermodule:0.0.1-amd64'
        tags_to_build = set()

        for module in os.listdir(self.envvars.MODULES_PATH):
            module_dir = os.path.join(self.envvars.MODULES_PATH, module)
            module_json = Module(self.output, self.utility, os.path.join(module_dir, "module.json"))
            for platform in module_json.platforms:
                # get the Dockerfile from module.json
                dockerfile = os.path.abspath(os.path.join(module_dir, module_json.get_dockerfile_by_platform(platform)))
                container_tag = "" if self.envvars.CONTAINER_TAG == "" else "-" + self.envvars.CONTAINER_TAG
                tag = "{0}:{1}{2}-{3}".format(module_json.repository, module_json.tag_version, container_tag, platform).lower()
                image_tag_map[(module, platform)] = tag
                tag_dockerfile_map[tag] = (module, dockerfile)
                tag_build_options_map[tag] = module_json.build_options
                if not self.utility.in_asterisk_list(module, bypass_modules) and self.utility.in_asterisk_list(platform, active_platform):
                    tags_to_build.add(tag)

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.utility, self.envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE, True)
        modules_to_process = deployment_manifest.get_modules_to_process()

        replacements = {}
        for module, platform in modules_to_process:
            key = (module, platform)
            if key in image_tag_map:
                tag = image_tag_map.get(key)
                replacements["${{MODULES.{0}.{1}}}".format(module, platform)] = tag
                if not self.utility.in_asterisk_list(module, bypass_modules):
                    tags_to_build.add(tag)

        for tag in tags_to_build:
            if tag in tag_dockerfile_map:
                module = tag_dockerfile_map.get(tag)[0]
                dockerfile = tag_dockerfile_map.get(tag)[1]
                self.output.info("BUILDING MODULE: {0}".format(module), suppress=no_build)
                self.output.info("PROCESSING DOCKERFILE: {0}".format(dockerfile), suppress=no_build)
                self.output.info("BUILDING DOCKER IMAGE: {0}".format(tag), suppress=no_build)

                docker = Docker(self.envvars, self.utility, self.output)
                # BUILD DOCKER IMAGE
                if not no_build:
                    # TODO: apply build options
                    build_options = self.filter_build_options(tag_build_options_map.get(tag, None))

                    context_path = os.path.abspath(os.path.join(self.envvars.MODULES_PATH, module))
                    dockerfile_relative = os.path.relpath(dockerfile, context_path)
                    # a hack to workaround Python Docker SDK's bug with Linux container mode on Windows
                    if docker.get_os_type() == "linux" and sys.platform == "win32":
                        dockerfile = dockerfile.replace("\\", "/")
                        dockerfile_relative = dockerfile_relative.replace("\\", "/")

                    build_result = docker.docker_client.images.build(tag=tag, path=context_path, dockerfile=dockerfile_relative)

                    self.output.info("DOCKER IMAGE DETAILS: {0}".format(build_result))

                if not no_push:
                    docker.init_registry()

                    # PUSH TO CONTAINER REGISTRY
                    self.output.info("PUSHING DOCKER IMAGE: " + tag)

                    response = docker.docker_client.images.push(repository=tag, stream=True, auth_config={
                        "username": self.envvars.CONTAINER_REGISTRY_USERNAME,
                        "password": self.envvars.CONTAINER_REGISTRY_PASSWORD})
                    docker.process_api_response(response)
            self.output.footer("BUILD COMPLETE", suppress=no_build)
            self.output.footer("PUSH COMPLETE", suppress=no_push)
        self.utility.set_config(force=True, replacements=replacements)

    @staticmethod
    def filter_build_options(build_options):
        """Remove build options which will be ignored"""
        if build_options is None:
            return None

        filtered_build_options = []
        for build_option in build_options:
            build_option = build_option.strip()
            parsed_option = re.compile(r"\s+").split(build_option)
            if parsed_option and ["--rm", "--tag", "-t", "--file", "-f"].index(parsed_option[0]) < 0:
                filtered_build_options.append(build_option)

        return filtered_build_options
