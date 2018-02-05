class IoTHub:
    def __init__(self, envvars, output, utility):
        self.envvars = envvars
        self.envvars.check()
        self.output = output
        self.utility = utility

    def monitor_events(self):
        try:
            self.utility.call_proc(['iothub-explorer', '--login', self.envvars.IOTHUB_CONNECTION_STRING, 'monitor-events', self.envvars.DEVICE_CONNECTION_INFO.DeviceId], shell=True)
        except Exception as ex:
            self.output.error("Problem while trying to call iothub-explorer. Please ensure that you have installed the iothub-explorer npm package with: npm i -g iothub-explorer.")
            self.output.error(str(ex))