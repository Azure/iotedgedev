import os
import zipfile


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
            self.output.prompt("Directory is not empty. Run 'iotedgedev azure' or clean the directory.")
            return

        self.output.header("CREATING AZURE IOT EDGE SOLUTION: {0}".format(name))

        try:
            template_zip = os.path.join(os.path.split(
                __file__)[0], "template", "template.zip")
        except Exception as ex:
            self.output.error("Error while trying to load template.zip")
            self.output.error(str(ex))

        zipf = zipfile.ZipFile(template_zip)
        zipf.extractall(name)

        self.utility.copy_template(os.path.join(dir_path, "deployment.template.json"), None, {"%MODULE%": module})

        os.rename(os.path.join(name, ".env.tmp"), os.path.join(name, ".env"))

        mod_cmd = "iotedgedev addmodule {0} --template {1}".format(module, template)
        self.output.header(mod_cmd)
        self.utility.call_proc(mod_cmd.split(), cwd=name)

        self.output.footer("Azure IoT Edge Solution Created")
        if name != ".":
            self.output.info("Execute 'cd {0}' to navigate to your new solution.".format(name))
