import os


class IoTHub:
    def __init__(self, envvars, utility, output):
        self.envvars = envvars
        self.output = output
        self.utility = utility

    def monitor_events(self, timeout=0):

        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_STRING)

        if timeout == None:
            timeout = 0

        try:
            self.output.status("It may take 1-2 minutes before you start to see messages below.")

            if timeout == 0:
                self.utility.call_proc(['iothub-explorer', '--login', self.envvars.IOTHUB_CONNECTION_STRING,
                                        'monitor-events', self.envvars.DEVICE_CONNECTION_INFO.DeviceId], shell=not self.envvars.is_posix())
            else:
                monitor_js = os.path.join(os.path.split(__file__)[0], "monitor.js")

                self.utility.call_proc(['node', monitor_js, self.envvars.IOTHUB_CONNECTION_STRING,
                                        self.envvars.DEVICE_CONNECTION_INFO.DeviceId, timeout], shell=not self.envvars.is_posix())
        except Exception as ex:
            self.output.error(
                "Problem while trying to call iothub-explorer. Please ensure that you have installed the iothub-explorer npm package with: npm i -g iothub-explorer.")
            self.output.error(str(ex))
