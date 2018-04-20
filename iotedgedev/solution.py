import os
import zipfile

class Solution:
    def __init__(self, output, utility):
        self.output = output
        self.utility = utility

    def create(self, name):
        if not self.utility.is_dir_empty(name):
            self.output.prompt("Directory is not empty. Run 'iotedgedev azure' or clean the directory.")
            return

        self.output.header("CREATING AZURE IOT EDGE SOLUTION: {0}".format(name))

        try:
            template_zip = os.path.join(os.path.split(
                __file__)[0], "template", "template.zip")
        except Exception as ex:
            self.output.error("Error while trying to load template.zip")
            self.output.error(str(ex))

        if name == ".":
            name = ""

        zipf = zipfile.ZipFile(template_zip)
        zipf.extractall(name)

        os.rename(os.path.join(name, ".env.tmp"), os.path.join(name, ".env"))
        self.output.footer("Azure IoT Edge Solution Created")
        if name != "":
            self.output.info("Execute 'cd {0}' to navigate to your new solution.".format(name))
