class BuildProfile:
    def __init__(self, dockerfile, context_path, extra_options):
        self.dockerfile = dockerfile
        self.context_path = context_path
        self.extra_options = extra_options
