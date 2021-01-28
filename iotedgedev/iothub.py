from .version import PY35


class IoTHub:
    def __init__(self, envvars, utility, output, azure_cli):
        self.envvars = envvars
        self.output = output
        self.utility = utility
        self.azure_cli = azure_cli

    def monitor_events(self, timeout=0):

        self.envvars.verify_envvar_has_val("IOTHUB_CONNECTION_STRING", self.envvars.IOTHUB_CONNECTION_STRING)
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_STRING)

        if timeout is None:
            timeout = 0

        self.output.header("MONITOR EVENTS")
        self.output.status("It may take 1-2 minutes before you start to see messages below.")

        if PY35:
            self.monitor_events_cli(timeout)
        else:
            self.monitor_events_node(timeout)

    def monitor_events_node(self, timeout=0):
        try:

            cmd = ['iothub-explorer', '--login', self.envvars.IOTHUB_CONNECTION_STRING, 'monitor-events', self.envvars.DEVICE_CONNECTION_INFO.device_id]

            if timeout != 0:
                cmd.extend(['--duration', timeout])

            self.utility.call_proc(cmd, shell=not self.envvars.is_posix())

        except Exception as ex:
            self.output.error("Problem while trying to call iothub-explorer. Please ensure that you have installed the iothub-explorer npm package with: npm i -g iothub-explorer.")
            self.output.error(str(ex))

    def monitor_events_cli(self, timeout=0):
        self.azure_cli.monitor_events(self.envvars.DEVICE_CONNECTION_INFO.device_id,
                                      self.envvars.IOTHUB_CONNECTION_INFO.connection_string,
                                      self.envvars.IOTHUB_CONNECTION_INFO.iothub_host.hub_name,
                                      timeout)
