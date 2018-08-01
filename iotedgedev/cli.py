# -*- coding: utf-8 -*-

from __future__ import absolute_import

import hashlib
import os
import sys

import click
from fstrings import f

from .azurecli import AzureCli
from .dockercls import Docker
from .envvars import EnvVars
from .iothub import IoTHub
from .modules import Modules
from .output import Output
from .runtime import Runtime
from .solution import Solution
from .utility import Utility
from .edge import Edge


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)

output = Output()
envvars = EnvVars(output)
envvars.load()

azure_cli = AzureCli(output, envvars)
default_subscriptionId = None
azure_cli_processing_complete = False


class OrganizedGroup(click.Group):
    """A subclass of click.Group which allows specifying an `order` parameter (0 by default) to sort the commands and groups"""

    def __init__(self, *args, **kwargs):
        self.orders = {}
        super(OrganizedGroup, self).__init__(*args, **kwargs)

    def get_help(self, ctx):
        self.list_commands = self.list_commands_for_help
        return super(OrganizedGroup, self).get_help(ctx)

    def list_commands_for_help(self, ctx):
        """reorder the list of commands when listing the help"""
        commands = super(OrganizedGroup, self).list_commands(ctx)
        return (c[1] for c in sorted(
            (self.orders.get(command, 0), command)
            for command in commands))

    def command(self, *args, **kwargs):
        """Behaves the same as `click.Group.command()` except capture
        a priority for listing command names in help.
        """
        order = kwargs.pop('order', 0)
        orders = self.orders

        def decorator(f):
            cmd = super(OrganizedGroup, self).command(*args, **kwargs)(f)
            orders[cmd.name] = order
            return cmd

        return decorator

    def group(self, *args, **kwargs):
        """Behaves the same as `click.Group.group()` except capture
        a priority for listing command names in help.
        """
        order = kwargs.pop('order', 0)
        orders = self.orders

        def decorator(f):
            cmd = super(OrganizedGroup, self).group(*args, **kwargs)(f)
            orders[cmd.name] = order
            return cmd

        return decorator


@click.group(context_settings=CONTEXT_SETTINGS, cls=OrganizedGroup)
@click.version_option()
def main():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Edge solutions", order=1)
def solution():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Edge runtime", order=1)
def runtime():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Edge simulator", order=1)
def simulator():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage Azure IoT Hub and IoT Edge devices", order=1)
def iothub():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage Docker", order=1)
def docker():
    pass


@solution.command(context_settings=CONTEXT_SETTINGS, help="Create a new Azure IoT Edge Solution")
@click.argument("name",
                required=True)
@click.option("--module",
              "-m",
              required=False,
              default=envvars.get_envvar("DEFAULT_MODULE_NAME", default="filtermodule"),
              show_default=True,
              help="Specify the name of the default IoT Edge module.")
@click.option("--template",
              "-t",
              default="csharp",
              show_default=True,
              required=False,
              type=click.Choice(["csharp", "nodejs", "python", "csharpfunction"]),
              help="Specify the template used to create the default IoT Edge module.")
def create(name, module, template):
    utility = Utility(envvars, output)
    sol = Solution(output, utility)
    sol.create(name, module, template)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Creates Solution and Azure Resources")
@click.pass_context
def init(ctx):
    utility = Utility(envvars, output)

    if len(os.listdir(os.getcwd())) == 0:
        solcmd = "iotedgedev solution ."
        output.header(solcmd)
        utility.call_proc(solcmd.split())

    azsetupcmd = "iotedgedev azure --update-dotenv"
    output.header(azsetupcmd)
    utility.call_proc(azsetupcmd.split())

    # Had to use call_proc, because @click.invoke doesn't honor prompts


@solution.command(context_settings=CONTEXT_SETTINGS, help="Push, Deploy, Start, Monitor")
@click.pass_context
def e2e(ctx):
    ctx.invoke(init)
    envvars.load(force=True)
    ctx.invoke(push)
    ctx.invoke(deploy)
    ctx.invoke(start_runtime)
    ctx.invoke(monitor)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  help="Add a New IoT Edge Module.")
@click.argument("name",
                required=True)
@click.option("--template",
              "-t",
              required=True,
              type=click.Choice(["csharp", "nodejs", "python", "csharpfunction"]),
              help="Specify the template used to create the new IoT Edge module.")
@click.pass_context
def add(ctx, name, template):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    mod = Modules(envvars, utility, output, dock)
    mod.add(name, template)


main.add_command(add)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Build the solution")
@click.option("--push",
              "-p",
              default=False,
              required=False,
              is_flag=True,
              help="Push modules to container registry.")
@click.option("--deploy",
              "-d",
              default=False,
              required=False,
              is_flag=True,
              help="Deploys modules to Edge device using deployment.json in the config folder.")
@click.pass_context
def build(ctx, push, deploy):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    mod = Modules(envvars, utility, output, dock)
    mod.build()


main.add_command(build)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Pushes Active Modules to Container Registry")
@click.option('--deploy',
              "-d",
              default=False,
              required=False,
              is_flag=True,
              help="Deploys modules to Edge device using deployment.json in the config folder.")
@click.option('--no-build',
              default=False,
              required=False,
              is_flag=True,
              help="Informs the push command to not build modules before pushing to container registry.")
@click.pass_context
def push(ctx, deploy, no_build):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    mod = Modules(envvars, utility, output, dock)
    mod.push(no_build=no_build)


main.add_command(push)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Deploys Solution to IoT Edge Device")
@click.pass_context
def deploy(ctx):
    utility = Utility(envvars, output)
    edge = Edge(envvars, utility, output, azure_cli)
    edge.deploy()


main.add_command(deploy)


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="start",
                 help="Starts IoT Edge Runtime")
def start_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.start()


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="restart",
                 help="Restarts IoT Edge Runtime")
@click.pass_context
def restart_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.restart()


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="stop",
                 help="Stops IoT Edge Runtime")
def stop_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.stop()


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="status",
                 help="Edge Runtime Status")
def status_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.status()


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="start",
                   help="Starts IoT Edge Simulator")
def start_simulator(ctx):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.start()


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="restart",
                   help="Restarts IoT Edge Simulator")
def restart_simulator(ctx):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.restart()


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="stop",
                   help="Stops IoT Edge Simulator")
def stop_simulator(ctx):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.stop()


@iothub.command(context_settings=CONTEXT_SETTINGS, help="Monitor Messages from IoT Edge to IoT Hub")
@click.option('--timeout',
              required=False,
              help="Number of milliseconds to monitor for events.")
@click.pass_context
def monitor(ctx, timeout):
    utility = Utility(envvars, output)
    ih = IoTHub(envvars, utility, output)
    ih.monitor_events(timeout)


def validate_option(ctx, param, value):
    global default_subscriptionId
    global azure_cli_processing_complete

    if param.name == "credentials":
        if value and value[0] and value[1]:
            output.param("CREDENTIALS", value, "Setting Credentials...", azure_cli_processing_complete)

            if not azure_cli.login_account(*value):
                sys.exit()

    if param.name == "service_principal":
        if value and value[0] and value[1] and value[2]:
            output.param("SERVICE PRINCIPAL", value, "Setting Credentials...", azure_cli_processing_complete)

            if not azure_cli.login_sp(*value):
                sys.exit()

    if param.name == "subscription":
        output.param("SUBSCRIPTION", value, f("Setting Subscription to '{value}'..."), azure_cli_processing_complete)

        # first verify that we have an existing auth token in cache, otherwise login using interactive
        if not default_subscriptionId:
            default_subscriptionId = azure_cli.user_has_logged_in()
            if not default_subscriptionId and not azure_cli.login_interactive():
                sys.exit()

        if default_subscriptionId != value:
            if not azure_cli.set_subscription(value):
                raise click.BadParameter(f('Please verify that your subscription Id or Name is correct'))

    if param.name == "resource_group_name":
        output.param("RESOURCE GROUP NAME", value, f("Setting Resource Group Name to '{value}'..."), azure_cli_processing_complete)

        envvars.RESOURCE_GROUP_NAME = value
        if not azure_cli.resource_group_exists(value):
            if not azure_cli.create_resource_group(value, envvars.RESOURCE_GROUP_LOCATION):
                raise click.BadParameter(f('Could not find Resource Group {value}'))
        else:
            # resource group exist, so don't ask for location
            envvars.RESOURCE_GROUP_LOCATION = azure_cli.get_resource_group_location(value)

    if param.name == "resource_group_location":
        output.param("RESOURCE GROUP LOCATION", value, f("Setting Resource Group Location to '{value}'..."), azure_cli_processing_complete)

        envvars.RESOURCE_GROUP_LOCATION = value

    if param.name == "iothub_sku":

        output.param("IOT HUB SKU", value, f("Setting IoT Hub SKU to '{value}'..."), azure_cli_processing_complete)
        envvars.IOTHUB_SKU = value

    if param.name == "iothub_name":
        output.param("IOT HUB", value, f("Setting IoT Hub to '{value}'..."), azure_cli_processing_complete)
        envvars.IOTHUB_NAME = value
        if not azure_cli.extension_exists("azure-cli-iot-ext"):
            azure_cli.add_extension("azure-cli-iot-ext")
        if not azure_cli.iothub_exists(value, envvars.RESOURCE_GROUP_NAME):
            # check if the active subscription already contains a free IoT Hub
            # if yes ask if the user wants to create an S1
            # otherwise exit
            if envvars.IOTHUB_SKU == "F1":
                free_iot_name, free_iot_rg = azure_cli.get_free_iothub()
                if free_iot_name:
                    output.info("You already have a Free IoT Hub SKU in your subscription, so you must either use that existing IoT Hub or create a new S1 IoT Hub. "
                                "Enter (F) to use the existing Free IoT Hub or enter (S) to create a new S1 IoT Hub:")
                    user_response = sys.stdin.readline().strip().upper()
                    if user_response == "S":
                        envvars.IOTHUB_SKU = "S1"
                    elif user_response == "F":
                        envvars.IOTHUB_NAME = free_iot_name
                        envvars.RESOURCE_GROUP_NAME = free_iot_rg
                        return free_iot_name
                    else:
                        sys.exit()
            if not azure_cli.create_iothub(value, envvars.RESOURCE_GROUP_NAME, envvars.IOTHUB_SKU):
                raise click.BadParameter(f('Could not create IoT Hub {value} in {envvars.RESOURCE_GROUP_NAME}'))

    if param.name == "edge_device_id":
        output.param("EDGE DEVICE", value, f("Setting Edge Device to '{value}'..."), azure_cli_processing_complete)

        envvars.EDGE_DEVICE_ID = value
        if not azure_cli.edge_device_exists(value, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME):
            if not azure_cli.create_edge_device(value, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME):
                raise click.BadParameter(f('Could not create IoT Edge Device {value} in {envvars.IOTHUB_NAME} in {envvars.RESOURCE_GROUP_NAME}'))

        output.header("CONNECTION STRINGS")
        envvars.IOTHUB_CONNECTION_STRING = azure_cli.get_iothub_connection_string(envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME)
        envvars.DEVICE_CONNECTION_STRING = azure_cli.get_device_connection_string(envvars.EDGE_DEVICE_ID, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME)

        if envvars.IOTHUB_CONNECTION_STRING and envvars.DEVICE_CONNECTION_STRING:
            output.info(f("IOTHUB_CONNECTION_STRING=\"{envvars.IOTHUB_CONNECTION_STRING}\""))
            output.info(f("DEVICE_CONNECTION_STRING=\"{envvars.DEVICE_CONNECTION_STRING}\""))

        azure_cli_processing_complete = True

        output.line()

    return value


def list_edge_devices_and_set_default():
    if not azure_cli.list_edge_devices(envvars.IOTHUB_NAME):
        sys.exit()
    return "iotedgedev-edgedevice"


def list_iot_hubs_and_set_default():
    if not azure_cli.list_iot_hubs(envvars.RESOURCE_GROUP_NAME):
        sys.exit()

    first_iothub = azure_cli.get_first_iothub(envvars.RESOURCE_GROUP_NAME)
    if first_iothub:
        return first_iothub
    else:
        subscription_rg_hash = hashlib.sha1((default_subscriptionId + envvars.RESOURCE_GROUP_NAME).encode('utf-8')).hexdigest()[:6]
        return "iotedgedev-iothub-" + subscription_rg_hash


def list_resource_groups_and_set_default():
    if not azure_cli.list_resource_groups():
        sys.exit()
    return "iotedgedev-rg"


def list_subscriptions_and_set_default():
    global default_subscriptionId
    # first verify that we have an existing auth token in cache, otherwise login using interactive
    if not default_subscriptionId:
        default_subscriptionId = azure_cli.user_has_logged_in()

        if not default_subscriptionId and not azure_cli.login_interactive():
            sys.exit()

    output.header("SUBSCRIPTION")

    if not azure_cli.list_subscriptions():
        sys.exit()
    default_subscriptionId = azure_cli.get_default_subscription()
    return default_subscriptionId


def header_and_default(header, default, default2=None):
    output.header(header)
    if default == '' and default2 is not None:
        return default2
    return default


@iothub.command(context_settings=CONTEXT_SETTINGS, help="Retrieve or create the required Azure Resources.")
@click.option('--credentials',
              envvar=envvars.get_envvar_key_if_val("CREDENTIALS"),
              required=False,
              hide_input=True,
              default=(None, None),
              type=(str, str),
              callback=validate_option,
              help="Enter Azure Credentials (username password).")
@click.option('--service-principal',
              envvar=envvars.get_envvar_key_if_val("SERVICE_PRINCIPAL"),
              required=False,
              hide_input=True,
              default=(None, None, None),
              type=(str, str, str),
              callback=validate_option,
              help="Enter Azure Service Principal Credentials (username password tenant).")
@click.option('--subscription',
              envvar=envvars.get_envvar_key_if_val("SUBSCRIPTION_ID"),
              default=lambda: list_subscriptions_and_set_default(),
              required=True,
              callback=validate_option,
              prompt="Select an Azure Subscription Name or Id:",
              help="The Azure Subscription Name or Id.")
@click.option('--resource-group-location',
              envvar=envvars.get_envvar_key_if_val("RESOURCE_GROUP_LOCATION"),
              required=True,
              default=lambda: header_and_default('RESOURCE GROUP LOCATION', envvars.RESOURCE_GROUP_LOCATION, 'westus'),
              type=click.Choice(['australiaeast', 'australiasoutheast', 'brazilsouth', 'canadacentral', 'canadaeast', 'centralindia', 'centralus', 'eastasia', 'eastus', 'eastus2',
                                 'japanwest', 'japaneast', 'northeurope', 'northcentralus', 'southindia', 'uksouth', 'ukwest', 'westus', 'westeurope', 'southcentralus', 'westcentralus', 'westus2']),
              callback=validate_option,
              prompt="Enter a Resource Group Location:",
              help="The Resource Group Location.")
@click.option('--resource-group-name',
              envvar=envvars.get_envvar_key_if_val("RESOURCE_GROUP_NAME"),
              required=True,
              default=lambda: list_resource_groups_and_set_default(),
              type=str,
              callback=validate_option,
              prompt="Enter Resource Group Name (Creates a new Resource Group if not found):",
              help="The Resource Group Name (Creates a new Resource Group if not found).")
@click.option('--iothub-sku',
              envvar=envvars.get_envvar_key_if_val("IOTHUB_SKU"),
              required=True,
              default=lambda: header_and_default('IOTHUB SKU', 'F1'),
              type=click.Choice(['F1', 'S1', 'S2', 'S3']),
              callback=validate_option,
              prompt="Enter IoT Hub SKU (F1|S1|S2|S3):",
              help="The IoT Hub SKU.")
@click.option('--iothub-name',
              envvar=envvars.get_envvar_key_if_val("IOTHUB_NAME"),
              required=True,
              default=lambda: list_iot_hubs_and_set_default(),
              type=str,
              callback=validate_option,
              prompt='Enter the IoT Hub Name (Creates a new IoT Hub if not found):',
              help='The IoT Hub Name (Creates a new IoT Hub if not found).')
@click.option('--edge-device-id',
              envvar=envvars.get_envvar_key_if_val("EDGE_DEVICE_ID"),
              required=True,
              default=lambda: list_edge_devices_and_set_default(),
              type=str,
              callback=validate_option,
              prompt='Enter the IoT Edge Device Id (Creates a new Edge Device if not found):',
              help='The IoT Edge Device Id (Creates a new Edge Device if not found).')
@click.option('--update-dotenv',
              envvar=envvars.get_envvar_key_if_val("UPDATE_DOTENV"),
              required=True,
              default=False,
              is_flag=True,
              prompt='Update the .env file with connection strings?',
              help='If True, the current .env will be updated with the IoT Hub and Device connection strings.')
def setup(setup,
          credentials,
          service_principal,
          subscription,
          resource_group_name,
          resource_group_location,
          iothub_sku,
          iothub_name,
          edge_device_id,
          update_dotenv):

    if update_dotenv:
        if envvars.backup_dotenv():
            envvars.save_envvar("IOTHUB_CONNECTION_STRING", envvars.IOTHUB_CONNECTION_STRING)
            envvars.save_envvar("DEVICE_CONNECTION_STRING", envvars.DEVICE_CONNECTION_STRING)
            output.info("Updated current .env file")


@docker.command(context_settings=CONTEXT_SETTINGS,
                help="Pulls Edge Runtime from Docker Hub and pushes to your specified container registry. "
                "Also, updates config files to use CONTAINER_REGISTRY_* instead of the Microsoft Docker hub. See CONTAINER_REGISTRY environment variables.")
def setup_registry():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    dock.setup_registry()


@docker.command(context_settings=CONTEXT_SETTINGS, help="Removes all the Docker containers and Images.")
@click.option('--remove-modules',
              default=False,
              required=False,
              is_flag=True,
              help="Removes only the edge modules Docker containers and images specified in ACTIVE_MODULES, not edgeAgent or edgeHub.")
@click.option('--remove-containers',
              default=False,
              required=False,
              is_flag=True,
              help="Removes all the Docker containers")
@click.option('--remove-images',
              default=False,
              required=False,
              is_flag=True,
              help="Removes all the Docker images.")
def clean(remove_modules, remove_containers, remove_images):

    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    if remove_modules:
        dock.remove_modules()

    if remove_containers:
        dock.remove_containers()

    if remove_images:
        dock.remove_images()


@docker.command(context_settings=CONTEXT_SETTINGS,
                help="Opens a new terminal window for edgeAgent, edgeHub and each edge module and saves to LOGS_PATH. "
                "You can configure the terminal command with LOGS_CMD.")
@click.option('--show-logs',
              default=False,
              required=False,
              is_flag=True,
              help="Opens a new terminal window for edgeAgent, edgeHub and each edge module. You can configure the terminal command with LOGS_CMD.")
@click.option('--save-logs',
              default=False,
              required=False,
              is_flag=True,
              help="Saves edgeAgent, edgeHub and each edge module logs to LOGS_PATH.")
def logs(show_logs, save_logs):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    dock.handle_logs_cmd(show_logs, save_logs)


if __name__ == "__main__":
    main()
