import os
from .dotnet import DotNet


class DotNetModuleProcessor(object):
    def __init__(self, envvars, utility, output, module_dir):
        self.envvars = envvars
        self.utility = utility
        self.output = output
        self.module_dir = module_dir
        self.exe_dir = self.envvars.DOTNET_EXE_DIR
        self.dotnet = DotNet(self.envvars, self.output, self.utility)

    def build(self):
        project_file = self.get_project_file()
        return self.dotnet.build_module(project_file)

    def publish(self):
        project_file = self.get_project_file()
        return self.dotnet.publish_module(project_file)

    def get_project_file(self):
        project_files = [os.path.join(self.module_dir, f) for f in os.listdir(
            self.module_dir) if f.endswith("proj")]

        if len(project_files) == 0:
            self.output.error("No project file found for module.")
            return ""
        else:
            return project_files[0]
