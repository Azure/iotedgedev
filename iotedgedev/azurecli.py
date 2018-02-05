import json
from fstrings import f
from io import StringIO
from azure.cli.core import get_default_cli

class AzureCli:
    def __init__(self, envvars, output):
        self.envvars = envvars
        self.output = output
        self.az_cli = get_default_cli()

    def invoke_az_cli(self, args, error_message, io=None): 
        try:
            exit_code = self.az_cli.invoke(args, out_file=io)
            if exit_code and exit_code != 0:
                self.output.error(error_message)
                return False
        except Exception as e:
            self.output.error(error_message)
            self.output.error(str(e))
            return False

        self.output.footer("Success")

        return True

    def add_extension(self, name):
        self.output.header(f("Adding extension {name}"))

        return self.invoke_az_cli(["extension", "add", "--name",name,
                                   "--yes"],
                                  f("Error while adding extension {name}"))

    def extension_exists(self, name):
        self.output.header(f("Checking for extension {name}"))

        return self.invoke_az_cli(["extension", "show", "--name", name, "--output", "table"],
                                  f("Error while checking for extension {name}"))

    def login(self, username, password):
        self.output.header("Loging in to Azure")

        return self.invoke_az_cli(["login", "-u", username,
                                   "-p",  password, "--query", "\"[].[name, resourceGroup]\"", "-o", "table"],
                                  "Error while trying to login to Azure")

    def login_interactive(self):
        self.output.header("Interactive login to Azure")

        return self.invoke_az_cli(["login", "--query", "\"[].[name, resourceGroup]\"", "--o", "table"],
                                  "Error while trying to login to Azure")

    def list_subscriptions(self):
        self.output.header("Listing Subscriptions")

        return self.invoke_az_cli(["account", "list", "--out", "table"],
                                  "Error while trying to list Azure subscriptions")

    def set_subscription(self, subscription):
        self.output.header("Setting Subscription")

        return self.invoke_az_cli(["account", "set", "--subscription", subscription],
                                  "Error while trying to set Azure subscription")

    def resource_group_exists(self, name):
        self.output.header("Checking for Resource Group")

        return self.invoke_az_cli(["group", "exists", "-n", name],
                                  "Resource Group does not exist.")

    def list_resource_groups(self):
        self.output.header("Listing Resource Groups")

        return self.invoke_az_cli(["group", "list", "--out", "table"],
                                  "Could not list the Resource Groups.")

    def list_iot_hubs(self, resource_group):
        self.output.header(
            f("Listing IoT Hubs in {resource_group}"))

        return self.invoke_az_cli(["iot", "hub", "list", "--resource-group", resource_group, "--out", "table"],
                                  f("Could not list the IoT Hubs in {resource_group}."))

    def iothub_exists(self, value, resource_group):
        self.output.header(
            f("Checking if {value} IoT Hub exists in {resource_group}"))

        return self.invoke_az_cli(["iot", "hub", "show", "--name", value, "--resource-group",
                                   resource_group, "--out", "table"],
                                  f("Could not locate the {value} in {resource_group}."))

    def create_iothub_free(self, value, resource_group):
        self.output.header(
            f("Creating free (F1 sku) {value} in {resource_group} "))

        return self.invoke_az_cli(["iot", "hub", "create", "--name", value, "--resource-group",
                                   resource_group, "--out", "table"],
                                  f("Could not create free (F1 sku) IoT Hub {value} in {resource_group}."))

    def create_iothub(self, value, resource_group, sku):
        self.output.header(
            f("Creating {value} in {resource_group} with sku {sku}"))

        return self.invoke_az_cli(["iot", "hub", "create", "--name", value, "--resource-group",
                                   resource_group, "--sku", sku, "--out", "table"],
                                  f("Could not create the IoT Hub {value} in {resource_group}."))

    def get_iothub_connection_string(self, value, resource_group):
        self.output.header(
            f("Getting connection string for {value} in {resource_group} "))

        io = StringIO()
        result = self.invoke_az_cli(["iot", "hub", "show-connection-string", "--hub-name", value,
                                     "--resource-group", resource_group],
                                    f("Could not create the IoT Hub {value} in {resource_group}."), io)
        if result:
            data = json.loads(io.getvalue())
            return data["cs"]
        return ''

    def edge_device_exists(self, value, iothub, resource_group):
        self.output.header(
            f("Checking if {value} device exists in {iothub} IoT Hub in {resource_group}"))

        return self.invoke_az_cli(["iot", "hub", "device-identity", "show", "--device-id", value, "--hub-name", iothub,
                                   "--resource-group", resource_group, "--out", "table"],
                                  f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}"))

    def create_edge_device(self, value, iothub, resource_group):
        self.output.header(
            f("Creating {value} edge device in {iothub} IoT Hub in {resource_group}"))

        return self.invoke_az_cli(["iot", "hub", "device-identity", "create", "--device-id", value, "--hub-name", iothub,
                                   "--resource-group", resource_group, "--edge-enabled", "--output", "table"],
                                  f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}"))

    def get_device_connection_string(self, value, iothub, resource_group):
        self.output.header(
            f("Getting the connection string for {value} edge device in {iothub} IoT Hub in {resource_group}"))

        io = StringIO()

        result = self.invoke_az_cli(["iot", "hub", "device-identity", "show-connection-string", "--device-id", value, "--hub-name", iothub,
                                     "--resource-group", resource_group],
                                    f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}"), io)
        if result:
            data = json.loads(io.getvalue())
            return data["cs"]

        return ''
