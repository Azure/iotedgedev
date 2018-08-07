import os
import sys

from .modules import Modules
from .utility import Utility


class Simulator:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.utility = Utility(self.envvars, self.output)

    def setup(self, gateway_host):
        self.output.header("Setting Up IoT Edge Simulator")
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_STRING)
        self.utility.exe_proc("iotedgehubdev setup -c {0} {1}".format(self.envvars.DEVICE_CONNECTION_STRING, "-g " + gateway_host if gateway_host else "").split())

    def start_single(self, inputs, port):
        self.output.header("Starting IoT Edge Simulator in Single Mode")
        self.utility.call_proc("iotedgehubdev start -i {0} {1}".format(inputs, "-p " + str(port) if port else "").split())

    def start_solution(self, verbose=True, build=False):
        if build:
            mod = Modules(self.envvars, self.output)
            mod.build()

        if not os.path.exists(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH):
            self.output.error("Deployment manifest {0} not found. Please build the solution before starting IoT Edge simulator.".format(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH))
            sys.exit(1)

        self.output.header("Starting IoT Edge Simulator in Solution Mode")
        self.utility.call_proc("iotedgehubdev start -d {0} {1}".format(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH, "-v" if verbose else "").split())

    def stop(self):
        self.output.header("Stopping IoT Edge Simulator")
        self.utility.exe_proc("iotedgehubdev stop".split())

    def modulecred(self, local, output_file):
        self.output.header("Getting Target Module Credentials")
        self.utility.exe_proc("iotedgehubdev modulecred {0} {1}".format("-l" if local else "", "-o " + output_file if output_file else "").split())
