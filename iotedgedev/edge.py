class Edge:
    def __init__(self, envvars, output, azure_cli):
        self.envvars = envvars
        self.output = output
        self.azure_cli = azure_cli

    def deploy(self):

        self.output.header("DEPLOYING CONFIGURATION")

        self.envvars.verify_envvar_has_val("IOTHUB_CONNECTION_STRING", self.envvars.IOTHUB_CONNECTION_INFO)
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_INFO)
        self.envvars.verify_envvar_has_val("DEPLOYMENT_CONFIG_FILE", self.envvars.DEPLOYMENT_CONFIG_FILE)

        self.azure_cli.set_modules(self.envvars.DEVICE_CONNECTION_INFO.DeviceId, self.envvars.IOTHUB_CONNECTION_INFO.ConnectionString,
                                   self.envvars.IOTHUB_CONNECTION_INFO.HubName, self.envvars.DEPLOYMENT_CONFIG_FILE_PATH)

        self.output.footer("DEPLOYMENT COMPLETE")
