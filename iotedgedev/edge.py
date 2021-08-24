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
                                      connection_string=self.envvars.DEVICE_CONNECTION_INFO.device_id,
                                      device_id=self.envvars.IOTHUB_CONNECTION_INFO):
            self.output.footer("DEPLOYMENT COMPLETE")

    def deployment(self, manifest_file: str, layered_deployment_name: str, priority: str, target_condition: str):

        self.output.header("DEPLOYING CONFIGURATION")

        self.envvars.verify_envvar_has_val("IOTHUB_CONNECTION_STRING", self.envvars.IOTHUB_CONNECTION_INFO)
        if not target_condition:
            self.envvars.get_envvar("LAYERED_DEPLOYMENT_TARGET_CONDITION", True)
        self.envvars.verify_envvar_has_val("DEPLOYMENT_CONFIG_FILE", self.envvars.DEPLOYMENT_CONFIG_FILE)

        if self.azure_cli.create_deployment(config=manifest_file,
                                            connection_string=self.envvars.IOTHUB_CONNECTION_INFO,
                                            layered_deployment_name=layered_deployment_name,
                                            target_condition=target_condition,
                                            priority=priority):
            self.output.footer("DEPLOYMENT COMPLETE")

    def tag(self, tags):
        self.output.header("UPDATE DEVICE TAG")

        self.envvars.verify_envvar_has_val("IOTHUB_CONNECTION_STRING", self.envvars.IOTHUB_CONNECTION_INFO)
        self.envvars.verify_envvar_has_val("EDGE_DEVICE_ID", self.envvars.EDGE_DEVICE_ID)

        if self.azure_cli.set_device_tag(connection_string=self.envvars.IOTHUB_CONNECTION_INFO, device_id=self.envvars.EDGE_DEVICE_ID, tags=tags):
            self.output.footer("TAG UPDATE COMPLETE")
