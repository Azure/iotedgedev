import os


class DotNetModuleProcessor(object):
    def __init__(self, envvars, utility, output, module_dir):
        self.envvars = envvars
        self.utility = utility
        self.output = output
        self.module_dir = module_dir
        self.exe_dir = self.envvars.DOTNET_EXE_DIR

    def build(self):
        project_file = self.get_project_file()
        if project_file == "":
            return False
        else:
            self.utility.exe_proc(["dotnet", "build", project_file,
                                   "-v", self.envvars.DOTNET_VERBOSITY])
            return True

    def publish(self):
        project_file = self.get_project_file()
        if project_file != "":
            self.utility.exe_proc(["dotnet", "publish", project_file, "-f", "netcoreapp2.0",
                                   "-v", self.envvars.DOTNET_VERBOSITY])

    def get_project_file(self):
        project_files = [os.path.join(self.module_dir, f) for f in os.listdir(
            self.module_dir) if f.endswith("proj")]

        if len(project_files) == 0:
            self.output.error("No project file found for module.")
            return ""
        else:
            return project_files[0]
