from .modules import Modules
from .utility import Utility


class Simulator:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.utility = Utility(self.envvars, self.output)

    def setup(self):
        self.output.header("Setting Up Edge Simulator")
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_STRING)
        self.utility.exe_proc("iotedgehubdev setup -c {0}".format(self.envvars.DEVICE_CONNECTION_STRING).split())

    def start_single(self, inputs):
        self.output.header("Starting Edge Simulator in Single Mode")
        self.utility.call_proc("iotedgehubdev start -i {0}".format(inputs).split())

    def start_solution(self, verbose=True, no_build=False):
        if not no_build:
            mod = Modules(self.envvars, self.output)
            mod.build()

        self.output.header("Starting Edge Simulator in Solution Mode")
        self.utility.call_proc("iotedgehubdev start -d {0} {1}".format(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH, "-v" if verbose else "").split())

    def stop(self):
        self.output.header("Stopping Edge Simulator")
        self.utility.exe_proc("iotedgehubdev stop".split())

    def modulecred(self, local, output_file):
        self.output.header("Getting target module credentials")
        self.utility.exe_proc("iotedgehubdev modulecred {0} {1}".format("-l" if local else "", "-o " + output_file if output_file else "").split())
