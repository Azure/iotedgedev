"""
This module provides interfaces to interact with dotnet CLI
"""


class DotNet:
    def __init__(self, output, utility):
        self.output = output
        self.utility = utility
        # Fail fast if dotnet is not on path
        self.utility.check_dependency(["dotnet", "--version"], "To add new C# modules and C# Functions modules, the .NET Core SDK")

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
