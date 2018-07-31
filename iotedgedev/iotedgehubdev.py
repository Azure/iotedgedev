class iotedgehubdev:
    def __init__(self, envvars, output, utility):
        self.envvars = envvars
        self.output = output
        self.utility = utility

    def setup(self):
        self.output.header("Setting Up Edge Simulator")
        self.utility.exe_proc("iotedgehubdev setup -c {0}".format(self.envvars.DEVICE_CONNECTION_STRING).split())

    def start_single(self, inputs):
        self.output.header("Starting Edge Simulator in Single Mode")
        self.utility.call_proc("iotedgehubdev start -i {0}".format(inputs).split())

    def start_solution(self):
        self.output.header("Starting Edge Simulator in Solution Mode")
        self.utility.call_proc("iotedgehubdev start -d {0} -v".format(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH).split())

    def stop(self):
        self.output.header("Stopping Edge Simulator")
        self.utility.exe_proc("iotedgehubdev stop".split())
