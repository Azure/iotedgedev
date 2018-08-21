class BuildProfile:
    def __init__(self, module_name, dockerfile, context_path, extra_options):
        self.module_name = module_name
        self.dockerfile = dockerfile
        self.context_path = context_path
        self.extra_options = extra_options
