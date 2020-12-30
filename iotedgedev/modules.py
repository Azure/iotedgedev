import os
import re
import shutil
import sys
from zipfile import ZipFile

import commentjson
from io import BytesIO
from urllib.request import urlopen

from . import telemetry
from .buildoptionsparser import BuildOptionsParser
from .buildprofile import BuildProfile
from .deploymentmanifest import DeploymentManifest
from .dockercls import Docker
from .dotnet import DotNet
from .module import Module
from .utility import Utility
from .constants import Constants

class Modules:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.utility = Utility(self.envvars, self.output)

    def add(self, name, template, group_id):
        self.output.header("ADDING MODULE {0}".format(name))

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.utility, self.envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE, True)

        cwd = self.envvars.MODULES_PATH
        self.utility.ensure_dir(cwd)

        if name.startswith("_") or name.endswith("_"):
            raise ValueError("Module name cannot start or end with the symbol _")
        elif not re.match("^[a-zA-Z0-9_]+$", name):
            raise ValueError("Module name can only contain alphanumeric characters and the symbol _")
        elif os.path.exists(os.path.join(cwd, name)):
            raise ValueError("Module \"{0}\" already exists under {1}".format(name, os.path.abspath(self.envvars.MODULES_PATH)))

        telemetry.add_extra_props({"template": template})

        repo = "{0}/{1}".format("${CONTAINER_REGISTRY_SERVER}", name.lower())
        if template == "c":
            github_prefix = "https://github.com/Azure"
            git_repo = "azure-iot-edge-c-module"
            branch = "master"
            url = "{0}/{1}/archive/{2}.zip".format(github_prefix, git_repo, branch)
            response = urlopen(url)

            temp_dir = os.path.join(os.path.expanduser("~"), '.iotedgedev')
            self.utility.ensure_dir(temp_dir)
            zip_file_prefix = "{0}-{1}".format(git_repo, branch)
            temp_template_dir = os.path.join(temp_dir, zip_file_prefix)
            if os.path.exists(temp_template_dir):
                shutil.rmtree(temp_template_dir)

            with ZipFile(BytesIO(response.read())) as zip_f:
                zip_f.extractall(temp_dir)

            shutil.move(temp_template_dir, os.path.join(cwd, name))

            module = Module(self.envvars, self.utility, os.path.join(cwd, name))
            module.repository = repo
            module.dump()
        elif template == "csharp":
            dotnet = DotNet(self.output, self.utility)
            dotnet.install_module_template()
            dotnet.create_custom_module(name, repo, cwd)
        elif template == "java":
            self.utility.check_dependency("mvn --help".split(), "To add new Java modules, the Maven tool")
            cmd = ["mvn",
                   "archetype:generate",
                   "-DarchetypeGroupId=com.microsoft.azure",
                   "-DarchetypeArtifactId=azure-iot-edge-archetype",
                   "-DgroupId={0}".format(group_id),
                   "-DartifactId={0}".format(name),
                   "-Dversion=1.0.0-SNAPSHOT",
                   "-Dpackage={0}".format(group_id),
                   "-Drepository={0}".format(repo),
                   "-B"]

            self.output.header(" ".join(cmd))
            self.utility.exe_proc(cmd, shell=not self.envvars.is_posix(), cwd=cwd)
        elif template == "nodejs":
            self.utility.check_dependency("yo azure-iot-edge-module --help".split(), "To add new Node.js modules, the Yeoman tool and Azure IoT Edge Node.js module generator")
            cmd = "yo azure-iot-edge-module -n {0} -r {1}".format(name, repo)
            self.output.header(cmd)
            self.utility.exe_proc(cmd.split(), shell=not self.envvars.is_posix(), cwd=cwd)
        elif template == "python":
            self.utility.check_dependency("cookiecutter --help".split(), "To add new Python modules, the Cookiecutter tool")
            github_source = "https://github.com/Azure/cookiecutter-azure-iot-edge-module"
            branch = "master"
            cmd = "cookiecutter --no-input {0} module_name={1} image_repository={2} --checkout {3}".format(github_source, name, repo, branch)
            self.output.header(cmd)
            self.utility.exe_proc(cmd.split(), cwd=cwd)
        elif template == "csharpfunction":
            dotnet = DotNet(self.output, self.utility)
            dotnet.install_function_template()
            dotnet.create_function_module(name, repo, cwd)

        deployment_manifest.add_module_template(name)
        deployment_manifest.dump()

        debug_create_options = self._get_debug_create_options(template)
        if os.path.exists(self.envvars.DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE):
            deployment_manifest_debug = DeploymentManifest(self.envvars, self.output, self.utility, self.envvars.DEPLOYMENT_CONFIG_DEBUG_TEMPLATE_FILE, True)
            deployment_manifest_debug.add_module_template(name, debug_create_options, True)
            deployment_manifest_debug.dump()

        self._update_launch_json(name, template, group_id)

        self.output.footer("ADD COMPLETE")

    def build(self, template_file, platform):
        return self.build_push(template_file, platform, no_push=True)

    def push(self, template_file, platform, no_build=False):
        return self.build_push(template_file, platform, no_build=no_build)

    def build_push(self, template_file, default_platform, no_build=False, no_push=False, fail_on_validation_error=False):
        self.output.header("BUILDING MODULES", suppress=no_build)

        template_file_folder = os.path.dirname(template_file)
        bypass_modules = self.utility.get_bypass_modules()
        validation_success = True

        # map image placeholder to tag.
        # sample: ('${MODULES.filtermodule.amd64}', 'localhost:5000/filtermodule:0.0.1-amd64')
        placeholder_tag_map = {}
        # map image tag to BuildProfile object
        tag_build_profile_map = {}
        # image tags to build
        # sample: 'localhost:5000/filtermodule:0.0.1-amd64'
        tags_to_build = set()

        deployment_manifest = DeploymentManifest(self.envvars, self.output, self.utility, template_file, True, True)

        # get image tags for ${MODULES.modulename.xxx} placeholder
        modules_path = os.path.join(template_file_folder, self.envvars.MODULES_PATH)
        if os.path.isdir(modules_path):
            for folder_name in os.listdir(modules_path):
                project_folder = os.path.join(modules_path, folder_name)
                if os.path.exists(os.path.join(project_folder, "module.json")):
                    module = Module(self.envvars, self.utility, project_folder)
                    self._update_module_maps("MODULES.{0}".format(folder_name), module, placeholder_tag_map, tag_build_profile_map, default_platform)

        # get image tags for ${MODULEDIR<relative path>.xxx} placeholder
        user_modules = deployment_manifest.get_user_modules()
        for module_name, module_info in user_modules.items():
            image = module_info["settings"]["image"]
            match_result = re.search(Constants.moduledir_placeholder_pattern, image)
            if (match_result is not None):
                module_dir = match_result.group(1)
                module = Module(self.envvars, self.utility, os.path.join(template_file_folder, module_dir))
                self._update_module_maps("MODULEDIR<{0}>".format(module_dir), module, placeholder_tag_map, tag_build_profile_map, default_platform)

        replacements = {}
        for module_name, module_info in user_modules.items():
            image = module_info["settings"]["image"]
            if image in placeholder_tag_map:
                tag = placeholder_tag_map[image]
                replacements[module_name] = tag
                if not self.utility.in_asterisk_list(module_name, bypass_modules):
                    tags_to_build.add(tag)

        if not no_build or not no_push:
            docker = Docker(self.envvars, self.utility, self.output)
            for tag in tags_to_build:
                if tag in tag_build_profile_map:
                    # BUILD DOCKER IMAGE
                    if not no_build:
                        build_profile = tag_build_profile_map.get(tag)

                        dockerfile = build_profile.dockerfile
                        self.output.info("PROCESSING DOCKERFILE: {0}".format(dockerfile))
                        self.output.info("BUILDING DOCKER IMAGE: {0}".format(tag))

                        build_options = build_profile.extra_options
                        build_options_parser = BuildOptionsParser(build_options)
                        sdk_options = build_options_parser.parse_build_options()

                        context_path = build_profile.context_path

                        # A hack to work around Python Docker SDK's bug with Linux container mode on Windows
                        # https://github.com/docker/docker-py/issues/2127
                        dockerfile_relative = os.path.relpath(dockerfile, context_path)
                        if docker.get_os_type() == "linux" and sys.platform == "win32":
                            dockerfile_relative = dockerfile_relative.replace("\\", "/")

                        build_args = {"tag": tag, "path": context_path, "dockerfile": dockerfile_relative}
                        build_args.update(sdk_options)

                        response = docker.docker_api.build(**build_args)
                        docker.process_api_response(response)
                    if not no_push:
                        docker.init_registry()

                        # PUSH TO CONTAINER REGISTRY
                        self.output.info("PUSHING DOCKER IMAGE: " + tag)
                        registry_key = None
                        for key, registry in self.envvars.CONTAINER_REGISTRY_MAP.items():
                            # Split the repository tag in the module.json (ex: Localhost:5000/filtermodule)
                            if registry.server.lower() == tag.split('/')[0].lower():
                                registry_key = key
                                break
                        if registry_key is None:
                            self.output.info("Could not find registry credentials with name {0} in environment variable. Pushing anonymously.".format(tag.split('/')[0].lower()))
                            response = docker.docker_client.images.push(repository=tag, stream=True)
                        else:
                            response = docker.docker_client.images.push(repository=tag, stream=True, auth_config={
                                "username": self.envvars.CONTAINER_REGISTRY_MAP[registry_key].username,
                                "password": self.envvars.CONTAINER_REGISTRY_MAP[registry_key].password})
                        docker.process_api_response(response)
                self.output.footer("BUILD COMPLETE", suppress=no_build)
                self.output.footer("PUSH COMPLETE", suppress=no_push)

        self.output.info("Expanding image placeholders")
        deployment_manifest.expand_image_placeholders(replacements)
        self.output.info("Converting createOptions")
        deployment_manifest.convert_create_options()
        self.output.info("Deleting template schema version")
        template_schema_ver = deployment_manifest.get_template_schema_ver()
        deployment_manifest.del_key(["$schema-template"])

        self.utility.ensure_dir(self.envvars.CONFIG_OUTPUT_DIR)
        gen_deployment_manifest_name = Utility.get_deployment_manifest_name(template_file, template_schema_ver, default_platform)
        gen_deployment_manifest_path = os.path.join(self.envvars.CONFIG_OUTPUT_DIR, gen_deployment_manifest_name)

        self.output.info("Expanding '{0}' to '{1}'".format(os.path.basename(template_file), gen_deployment_manifest_path))
        deployment_manifest.dump(gen_deployment_manifest_path)

        self.output.info("Validating generated deployment manifest %s" % gen_deployment_manifest_path)
        validation_success = deployment_manifest.validate_deployment_manifest()

        if fail_on_validation_error and not validation_success:
            raise Exception("Deployment manifest validation failed. Please see previous logs for more details.")

        return gen_deployment_manifest_path

    def _update_module_maps(self, placeholder_base, module, placeholder_tag_map, tag_build_profile_map, default_platform):
        try:
            for platform in module.platforms:
                # get the Dockerfile from module.json
                dockerfile = module.get_dockerfile_by_platform(platform)
                container_tag = "" if self.envvars.CONTAINER_TAG == "" else "-" + self.envvars.CONTAINER_TAG
                tag = "{0}:{1}{2}-{3}".format(module.repository.lower(), module.tag_version, container_tag, platform)
                placeholder_tag_map["${{{0}.{1}}}".format(placeholder_base, platform)] = tag
                placeholder_tag_map[tag] = tag

                if platform == default_platform:
                    placeholder_tag_map["${{{0}}}".format(placeholder_base)] = tag
                elif platform == default_platform + ".debug":
                    placeholder_tag_map["${{{0}.{1}}}".format(placeholder_base, "debug")] = tag

                tag_build_profile_map[tag] = BuildProfile(dockerfile, module.context_path, module.build_options)
        except FileNotFoundError:
            pass

    def _get_debug_create_options(self,  template):
        if template == "c":
            return {"HostConfig": {"Privileged": True}}
        elif template == "java":
            return {"HostConfig": {"PortBindings": {"5005/tcp": [{"HostPort": "5005"}]}}}
        elif template == "nodejs":
            return {"ExposedPorts": {"9229/tcp": {}},
                    "HostConfig": {"PortBindings": {"9229/tcp": [{"HostPort": "9229"}]}}}
        elif template == "python":
            return {"ExposedPorts": {"5678/tcp": {}},
                    "HostConfig": {"PortBindings": {"5678/tcp": [{"HostPort": "5678"}]}}}
        else:
            return {}

    def _update_launch_json(self, name, template, group_id):
        new_launch_json = self._get_launch_json(name, template, group_id)
        if new_launch_json is not None:
            self._merge_launch_json(new_launch_json)

    def _get_launch_json(self, name, template, group_id):
        replacements = {}
        replacements["%MODULE%"] = name
        replacements["%MODULE_FOLDER%"] = name

        launch_json_file = None
        is_function = False
        if template == "c":
            launch_json_file = "launch_c.json"
            replacements["%APP_FOLDER%"] = "/app"
        elif template == "csharp":
            launch_json_file = "launch_csharp.json"
            replacements["%APP_FOLDER%"] = "/app"
        elif template == "java":
            launch_json_file = "launch_java.json"
            replacements["%GROUP_ID%"] = group_id
        elif template == "nodejs":
            launch_json_file = "launch_node.json"
        elif template == "csharpfunction":
            launch_json_file = "launch_csharp.json"
            replacements["%APP_FOLDER%"] = "/app"
            is_function = True
        elif template == "python":
            launch_json_file = "launch_python.json"
            replacements["%APP_FOLDER%"] = "/app"

        if launch_json_file is not None:
            launch_json_file = os.path.join(os.path.split(__file__)[0], "template", launch_json_file)
            launch_json_content = Utility.get_file_contents(launch_json_file)
            for key, value in replacements.items():
                launch_json_content = launch_json_content.replace(key, value)
            launch_json = commentjson.loads(launch_json_content)
            if is_function and launch_json is not None and "configurations" in launch_json:
                # for Function modules, there shouldn't be launch config for local debug
                launch_json["configurations"] = list(filter(lambda x: x["request"] != "launch", launch_json["configurations"]))
            return launch_json

    def _merge_launch_json(self, new_launch_json):
        vscode_dir = os.path.join(os.getcwd(), ".vscode")
        self.utility.ensure_dir(vscode_dir)
        launch_json_file = os.path.join(vscode_dir, "launch.json")
        if os.path.exists(launch_json_file):
            launch_json = commentjson.loads(Utility.get_file_contents(launch_json_file))
            launch_json['configurations'].extend(new_launch_json['configurations'])
            with open(launch_json_file, "w") as f:
                commentjson.dump(launch_json, f, indent=2)
        else:
            with open(launch_json_file, "w") as f:
                commentjson.dump(new_launch_json, f, indent=2)
