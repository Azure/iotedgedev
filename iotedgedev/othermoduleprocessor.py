from distutils.dir_util import copy_tree


class OtherModuleProcessor ():
    def __init__(self):
        self.exe_dir = "."

    def build(self):
        return True

    def publish(self):
        pass
