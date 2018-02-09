from distutils.dir_util import copy_tree


class OtherModuleProcessor (object):

    def build(self, module_dir):
        return True

    def publish(self, module_dir):
        pass
