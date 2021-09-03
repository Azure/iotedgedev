from iotedgedev.output import Output
from iotedgedev.envvars import EnvVars
from iotedgedev.azurecli import AzureCli


class Edge:
    def __init__(self, envvars: EnvVars, output: Output, azure_cli: AzureCli):
        self.envvars = envvars
        self.output = output
        self.azure_cli = azure_cli

    def deploy(self, manifest_file: str):

        self.output.header("DEPLOYING CONFIGURATION")

        self.envvars.verify_envvar_has_val("IOTHUB_CONNECTION_STRING", self.envvars.IOTHUB_CONNECTION_INFO)
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_INFO)
        self.envvars.verify_envvar_has_val("DEPLOYMENT_CONFIG_FILE", self.envvars.DEPLOYMENT_CONFIG_FILE)

        if self.azure_cli.set_modules(config=manifest_file,
                                      connection_string=self.envvars.IOTHUB_CONNECTION_INFO,
                                      device_id=self.envvars.DEVICE_CONNECTION_INFO.device_id):
            self.output.footer("DEPLOYMENT COMPLETE")

    def tag(self, tags):
        self.output.header("UPDATE DEVICE TAG")
        if not tags:
            tags = self.envvars.get_envvar("DEVICE_TAGS", True)
        self.envvars.verify_envvar_has_val("IOTHUB_CONNECTION_STRING", self.envvars.IOTHUB_CONNECTION_INFO)
        self.envvars.verify_envvar_has_val("DEVICE_CONNECTION_STRING", self.envvars.DEVICE_CONNECTION_INFO)

        if self.azure_cli.set_device_tag(connection_string=self.envvars.IOTHUB_CONNECTION_INFO, device_id=self.envvars.DEVICE_CONNECTION_INFO.device_id, tags=tags):
            self.output.footer("TAG UPDATE COMPLETE")
