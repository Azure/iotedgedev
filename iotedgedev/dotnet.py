"""
This module provides interfaces to interact with dotnet CLI
"""


class DotNet:
    def __init__(self, envvars, output, utility):
        self.envvars = envvars
        self.output = output
        self.utility = utility

    def install_module_template(self):
        cmd = "dotnet new -i Microsoft.Azure.IoT.Edge.Module"
        self.output.header(cmd)
        self.utility.exe_proc(cmd.split())

    def install_function_template(self):
        cmd = "dotnet new -i Microsoft.Azure.IoT.Edge.Function"
        self.output.header(cmd)
        self.utility.exe_proc(cmd.split())

    def create_custom_module(self, name, repo, cwd):
        cmd = "dotnet new aziotedgemodule -n {0} -r {1}".format(name, repo)
        self.output.header(cmd)
        self.utility.exe_proc(cmd.split(), cwd=cwd)

    def create_function_module(self, name, repo, cwd):
        cmd = "dotnet new aziotedgefunction -n {0} -r {1}".format(name, repo)
        self.output.header(cmd)
        self.utility.exe_proc(cmd.split(), cwd=cwd)

    def build_module(self, project_file):
        if project_file is None or project_file == "":
            return False

        self.utility.exe_proc(["dotnet", "build", project_file,
                               "-v", self.envvars.DOTNET_VERBOSITY])
        return True

    def publish_module(self, project_file):
        if project_file is None or project_file == "":
            return False

        self.utility.exe_proc(["dotnet", "publish", project_file, "-f", "netcoreapp2.0",
                               "-v", self.envvars.DOTNET_VERBOSITY])
        return True
