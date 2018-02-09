import os

class DotNetModuleProcessor(object):
    def __init__(self, envvars, utility, output):
        self.envvars = envvars
        self.utility = utility
        self.output = output
        
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
        project_files = [os.path.join(module_dir, f) for f in os.listdir(
            module_dir) if f.endswith("proj")]

        if len(project_files) == 0:
            self.output.error("No project file found for module.")
        else :
            self.utility.exe_proc(["dotnet", "publish", project_files[0], "-f", "netcoreapp2.0",
                               "-o", build_path, "-v", self.envvars.DOTNET_VERBOSITY])