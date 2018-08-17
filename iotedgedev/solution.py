import os


class Solution:
    def __init__(self, output, utility):
        self.output = output
        self.utility = utility

    def create(self, name, module, template):
        if name == ".":
            dir_path = os.getcwd()
        else:
            dir_path = os.path.join(os.getcwd(), name)

        if not self.utility.is_dir_empty(dir_path):
            self.output.prompt("Directory is not empty. Run 'iotedgedev iothub' or clean the directory.")
            return

        self.output.header("CREATING AZURE IOT EDGE SOLUTION: {0}".format(name))

        self.utility.ensure_dir(dir_path)

        self.utility.copy_from_template_dir("deployment.template.json", dir_path, replacements={"%MODULE%": module})
        self.utility.copy_from_template_dir(".gitignore", dir_path)
        self.utility.copy_from_template_dir(".env.tmp", dir_path, dest_file=".env")

        mod_cmd = "iotedgedev solution add {0} --template {1}".format(module, template)
        self.output.header(mod_cmd)
        self.utility.call_proc(mod_cmd.split(), cwd=name)

        self.output.footer("Azure IoT Edge Solution Created")
        if name != ".":
            self.output.info("Execute 'cd {0}' to navigate to your new solution.".format(name))
