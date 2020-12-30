import os

from .modules import Modules
from .utility import Utility

class Simulator:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.utility = Utility(self.envvars, self.output)

    def setup(self, gateway_host, iothub_connection_string=""):
        self.output.header("Setting Up IoT Edge Simulator")
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_STRING)

        cmd = ["iotedgehubdev", "setup", "-c", self.envvars.DEVICE_CONNECTION_STRING]
        if gateway_host:
            cmd.extend(["-g", gateway_host])
        if iothub_connection_string:
            cmd.extend(["-i", iothub_connection_string])
        self.utility.exe_proc(cmd)

    def start_single(self, inputs, port):
        self.output.header("Starting IoT Edge Simulator in Single Mode")

        cmd = ["iotedgehubdev", "start", "-i", inputs]
        if port:
            cmd.extend(["-p", str(port)])
        self.utility.exe_proc(cmd)

    def start_solution(self, manifest_file, default_platform, verbose=True, build=False):
        if build:
            mod = Modules(self.envvars, self.output)
            manifest_file = mod.build(manifest_file, default_platform)

        if not os.path.exists(manifest_file):
            raise FileNotFoundError("Deployment manifest {0} not found. Please build the solution before starting IoT Edge simulator.".format(self.envvars.DEPLOYMENT_CONFIG_FILE_PATH))

        self.output.header("Starting IoT Edge Simulator in Solution Mode")

        cmd = ["iotedgehubdev", "start", "-d", manifest_file]
        if verbose:
            cmd.append("-v")
        self.utility.call_proc(cmd)

    def stop(self):
        self.output.header("Stopping IoT Edge Simulator")
        self.utility.call_proc(["iotedgehubdev", "stop"])

    def modulecred(self, local, output_file):
        self.output.header("Getting Target Module Credentials")

        cmd = ["iotedgehubdev", "modulecred"]
        if local:
            cmd.append("-l")
        if output_file:
            cmd.extend(["-o", output_file])
        self.utility.exe_proc(cmd)
