import json
from fstrings import f
from io import StringIO
from azure.cli.core import get_default_cli


class AzureCli:
    def __init__(self,  output, cli=get_default_cli()):
        self.output = output
        self.az_cli = cli

    def invoke_az_cli(self, args, error_message=None, io=None):
        try:
            exit_code = self.az_cli.invoke(args, out_file=io)
            if exit_code and exit_code != 0:
                if error_message:
                    self.output.error(error_message)
                return False
        except Exception as e:
            if error_message:
                self.output.error(error_message)
            self.output.error(str(e))
            return False

        self.output.footer("Success")

        return True

    def add_extension(self, name):
        self.output.header(f("Adding extension {name}"))

        return self.invoke_az_cli(["extension", "add", "--name", name,
                                   "--yes"],
                                  f("Error while adding extension {name}."))

    def extension_exists(self, name):
        self.output.header(f("Checking for extension {name}"))

        return self.invoke_az_cli(["extension", "show", "--name", name, "--output", "table"],
                                  f("Error while checking for extension {name}."))

    def user_has_logged_in(self):
        self.output.header("Checking for cached credentials")

        io = StringIO()
        result = self.invoke_az_cli(["account", "show"], io=io)

        if result:
            out_string = io.getvalue()
            self.output.info(out_string)
            data = json.loads(out_string)
            return data["id"]
        return None

    def login(self, username, password):
        self.output.header("Logging in to Azure")

        return self.invoke_az_cli(["login", "-u", username,
                                   "-p",  password, "-o", "table"],
                                  "Error while trying to login to Azure. Try logging in with the interactive login mode (do not use the --azure-credentials).")

    def login_interactive(self):
        self.output.header("Interactive login to Azure")

        return self.invoke_az_cli(["login", "--o", "table"],
                                  "Error while trying to login to Azure.")

    def logout(self):
        self.output.header("Logout from Azure")

        return self.invoke_az_cli(["account", "clear"])

    def list_subscriptions(self):
        self.output.header("Listing Subscriptions")

        return self.invoke_az_cli(["account", "list", "--out", "table"],
                                  "Error while trying to list Azure subscriptions.")

    def get_default_subscription(self):
        self.output.header("Getting default subscription id")

        io = StringIO()
        result = self.invoke_az_cli(["account", "show"],
                                    "Error while trying to get the default Azure subscription id.", io)
        if result:
            out_string = io.getvalue()
            data = json.loads(out_string)
            return data["id"]
        return ''

    def set_subscription(self, subscription):
        self.output.header("Setting Subscription")

        return self.invoke_az_cli(["account", "set", "--subscription", subscription],
                                  "Error while trying to set Azure subscription.")

    def resource_group_exists(self, name):
        self.output.header("Checking for Resource Group")

        io = StringIO()
        result = self.invoke_az_cli(["group", "exists", "-n", name, "--debug"],
                                    "Resource Group does not exist.", io)

        if result:
            out_string = io.getvalue()
            self.output.info(out_string)
            return out_string == "true\n"
        return False

    def create_resource_group(self, name, location):
        self.output.header(f("Creating Resource Group {name} at location:{location}"))

        return self.invoke_az_cli(["group", "create", "--name", name, "--location", location],
                                  f("Could not create the new Resource Group {name} at location:{location}."))


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

    def create_iothub(self, value, resource_group, sku):
        self.output.header(
            f("Creating {value} in {resource_group} with sku {sku}"))

        return self.invoke_az_cli(["iot", "hub", "create", "--name", value, "--resource-group",
                                   resource_group, "--sku", sku, "--out", "table"],
                                  f("Could not create the IoT Hub {value} in {resource_group} with sku {sku}."))

    def get_iothub_connection_string(self, value, resource_group):
        self.output.header(
            f("Getting connection string for {value} in {resource_group} "))

        io = StringIO()
        result = self.invoke_az_cli(["iot", "hub", "show-connection-string", "--hub-name", value,
                                     "--resource-group", resource_group],
                                    f("Could not create the IoT Hub {value} in {resource_group}."), io)
        if result:
            out_string = io.getvalue()
            self.output.info(out_string)
            data = json.loads(out_string)
            return data["cs"]
        return ''

    def edge_device_exists(self, value, iothub, resource_group):
        self.output.header(
            f("Checking if {value} device exists in {iothub} IoT Hub in {resource_group}"))

        return self.invoke_az_cli(["iot", "hub", "device-identity", "show", "--device-id", value, "--hub-name", iothub,
                                   "--resource-group", resource_group, "--out", "table"],
                                  f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}."))

    def create_edge_device(self, value, iothub, resource_group):
        self.output.header(
            f("Creating {value} edge device in {iothub} IoT Hub in {resource_group}"))

        return self.invoke_az_cli(["iot", "hub", "device-identity", "create", "--device-id", value, "--hub-name", iothub,
                                   "--resource-group", resource_group, "--edge-enabled", "--output", "table"],
                                  f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}."))

    def get_device_connection_string(self, value, iothub, resource_group):
        self.output.header(
            f("Getting the connection string for {value} edge device in {iothub} IoT Hub in {resource_group}"))

        io = StringIO()

        result = self.invoke_az_cli(["iot", "hub", "device-identity", "show-connection-string", "--device-id", value, "--hub-name", iothub,
                                     "--resource-group", resource_group],
                                    f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}."), io)
        if result:
            out_string = io.getvalue()
            self.output.info(out_string)
            data = json.loads(out_string)
            return data["cs"]

        return ''
