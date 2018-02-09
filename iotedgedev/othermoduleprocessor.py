from distutils.dir_util import copy_tree

class OtherModuleProcessor (object):
    
    def build(self, module_dir):
        return True

    def publish(self, module_dir, build_path):
        copy_tree(module_dir, os.path.join("build", module_dir))
