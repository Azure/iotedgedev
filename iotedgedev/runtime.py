class Runtime:
    def __init__(self, envvars, utility, output, dock):
        self.envvars = envvars
        self.utility = utility
        self.utility.set_config()
        self.dock = dock
        self.output = output

    def start(self):
        self.output.header("Starting Edge Runtime")
        self.utility.exe_proc(["iotedgectl", "--verbose",
                               self.envvars.RUNTIME_VERBOSITY, "start"])

    def stop(self):
        self.output.header("Stopping Edge Runtime")
        self.utility.exe_proc(["iotedgectl", "--verbose",
                               self.envvars.RUNTIME_VERBOSITY, "stop"])

    def setup(self):
        self.output.header("Setting Up Edge Runtime")
        self.utility.exe_proc(["iotedgectl", "--verbose", self.envvars.RUNTIME_VERBOSITY,
                               "setup", "--config-file", self.envvars.RUNTIME_CONFIG_FILE])

    def status(self):
        self.output.header("Getting Edge Runtime Status")
        self.utility.exe_proc(["iotedgectl", "--verbose", self.envvars.RUNTIME_VERBOSITY,
                               "status"])

    def restart(self):
        self.stop()
        self.dock.remove_modules()
        self.setup()
        self.start()

