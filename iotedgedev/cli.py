# -*- coding: utf-8 -*-

from __future__ import absolute_import

import hashlib
import os
import sys

import click
from fstrings import f

from .azurecli import AzureCli
from .dockercls import Docker
from .edge import Edge
from .envvars import EnvVars
from .iothub import IoTHub
from .modules import Modules
from .organizedgroup import OrganizedGroup
from .output import Output
from .runtime import Runtime
from .solution import Solution
from .utility import Utility

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'], max_content_width=120)

output = Output()
envvars = EnvVars(output)
envvars.load()

azure_cli = AzureCli(output, envvars)
default_subscriptionId = None
azure_cli_processing_complete = False


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


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Hub and IoT Edge devices", order=1)
def iothub():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage Docker", order=1)
def docker():
    pass


@solution.command(context_settings=CONTEXT_SETTINGS,
                  short_help="Create a new IoT Edge solution",
                  help="Create a new IoT Edge solution, where NAME is the solution folder name. "
                       "Use \".\" as NAME to create in the current folder.")
@click.argument("name",
                required=True)
@click.option("--module",
              "-m",
              required=False,
              default=envvars.get_envvar("DEFAULT_MODULE_NAME", default="filtermodule"),
              show_default=True,
              help="Specify the name of the default module")
@click.option("--template",
              "-t",
              default="csharp",
              show_default=True,
              required=False,
              type=click.Choice(["csharp", "nodejs", "python", "csharpfunction"]),
              help="Specify the template used to create the default module")
def create(name, module, template):
    utility = Utility(envvars, output)
    sol = Solution(output, utility)
    sol.create(name, module, template)


main.add_command(create)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  help="Create a new IoT Edge solution and provision Azure resources",
                  # hack to prevent Click truncating help messages
                  short_help="Create a new IoT Edge solution and provision Azure resources")
def init():
    utility = Utility(envvars, output)

    if len(os.listdir(os.getcwd())) == 0:
        solcmd = "iotedgedev solution create ."
        output.header(solcmd)
        utility.call_proc(solcmd.split())

    azsetupcmd = "iotedgedev iothub setup --update-dotenv"
    output.header(azsetupcmd)
    # Had to use call_proc, because @click.invoke doesn't honor prompts
    utility.call_proc(azsetupcmd.split())


@solution.command(context_settings=CONTEXT_SETTINGS, help="Push, deploy, start, monitor")
@click.pass_context
def e2e(ctx):
    ctx.invoke(init)
    envvars.load(force=True)
    ctx.invoke(push)
    ctx.invoke(deploy)
    ctx.invoke(start_runtime)
    ctx.invoke(monitor)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  short_help="Add a new module to the solution",
                  help="Add a new module to the solution, where NAME is the module name")
@click.argument("name",
                required=True)
@click.option("--template",
              "-t",
              required=True,
              type=click.Choice(["csharp", "nodejs", "python", "csharpfunction"]),
              default="csharp",
              show_default=True,
              help="Specify the template used to create the new module")
def add(name, template):
    mod = Modules(envvars, output)
    mod.add(name, template)


main.add_command(add)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Build the solution")
@click.option("--push",
              "-p",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Push module images to container registry")
@click.option("--deploy",
              "-d",
              "do_deploy",  # an alias to prevent conflict with the deploy function
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Deploy modules to Edge device using deployment.json in the config folder")
@click.pass_context
def build(ctx, push, do_deploy):
    mod = Modules(envvars, output)
    mod.build_push(no_push=not push)

    if do_deploy:
        ctx.invoke(deploy)


main.add_command(build)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Push module images to container registry")
@click.option('--deploy',
              "-d",
              "do_deploy",  # an alias to prevent conflict with the deploy method
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Deploy modules to Edge device using deployment.json in the config folder")
@click.option('--no-build',
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Inform the push command to not build modules images before pushing to container registry")
@click.pass_context
def push(ctx, do_deploy, no_build):
    mod = Modules(envvars, output)
    mod.push(no_build=no_build)

    if do_deploy:
        ctx.invoke(deploy)


main.add_command(push)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Deploy solution to IoT Edge device")
def deploy():
    utility = Utility(envvars, output)
    edge = Edge(envvars, utility, output, azure_cli)
    edge.deploy()


main.add_command(deploy)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  help="Expand environment variables and placeholders in *.template.json and copy to config folder",
                  # hack to prevent Click truncating help messages
                  short_help="Expand environment variables and placeholders in *.template.json and copy to config folder")
def genconfig():
    mod = Modules(envvars, output)
    mod.build_push(no_build=True, no_push=True)


main.add_command(genconfig)


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="start",
                 help="Start IoT Edge runtime")
def start_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.start()


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="restart",
                 help="Restart IoT Edge runtime")
def restart_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.restart()


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="stop",
                 help="Stop IoT Edge runtime")
def stop_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.stop()


@runtime.command(context_settings=CONTEXT_SETTINGS,
                 name="status",
                 help="Show IoT Edge runtime status")
def status_runtime():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.status()


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="start",
                   help="Start IoT Edge simulator")
def start_simulator():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.start()


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="restart",
                   help="Restart IoT Edge simulator")
def restart_simulator():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.restart()


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="stop",
                   help="Stop IoT Edge simulator")
def stop_simulator():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    run.stop()


@iothub.command(context_settings=CONTEXT_SETTINGS,
                help="Monitor messages from IoT Edge device to IoT Hub",
                # hack to prevent Click truncating help messages
                short_help="Monitor messages from IoT Edge device to IoT Hub")
@click.option("--timeout",
              "-t",
              required=False,
              help="Specify number of milliseconds to monitor for messages")
def monitor(timeout):
    utility = Utility(envvars, output)
    ih = IoTHub(envvars, utility, output, azure_cli)
    ih.monitor_events(timeout)


main.add_command(monitor)


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


@iothub.command(context_settings=CONTEXT_SETTINGS,
                help="Retrieve or create required Azure resources",
                name="setup")
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
              "-u",
              envvar=envvars.get_envvar_key_if_val("UPDATE_DOTENV"),
              required=True,
              default=False,
              show_default=True,
              is_flag=True,
              prompt='Update the .env file with connection strings?',
              help='If True, the current .env will be updated with the IoT Hub and Device connection strings.')
def setup_iothub(credentials,
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
                help="Pull Edge runtime images from Microsoft Container Registry and push to your specified container registry. "
                     "Also, update config files to use CONTAINER_REGISTRY_* instead of the Microsoft Container Registry. See CONTAINER_REGISTRY environment variables.",
                short_help="Pull Edge runtime images from MCR and push to your specified container registry",
                name="setup")
def setup_registry():
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    dock.setup_registry()


@docker.command(context_settings=CONTEXT_SETTINGS, help="Remove all the containers and images")
@click.option("--module",
              "-m",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Remove only the Edge module containers and images, not EdgeAgent or EdgeHub")
@click.option("--container",
              "-c",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Remove all the containers")
@click.option("--image",
              "-i",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Remove all the images")
def clean(module, container, image):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    if module:
        dock.remove_modules()

    if container:
        dock.remove_containers()

    if image:
        dock.remove_images()


@docker.command(context_settings=CONTEXT_SETTINGS,
                help="Open a new terminal window for EdgeAgent, EdgeHub and each edge module and save to LOGS_PATH. "
                     "You can configure the terminal command with LOGS_CMD.",
                short_help="Open a new terminal window for EdgeAgent, EdgeHub and each edge module and save to LOGS_PATH")
@click.option("--show",
              "-l",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Open a new terminal window for EdgeAgent, EdgeHub and each edge module. You can configure the terminal command with LOGS_CMD.")
@click.option("--save",
              "-s",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Save EdgeAgent, EdgeHub and each Edge module logs to LOGS_PATH.")
def log(show, save):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    dock.handle_logs_cmd(show, save)


main.add_command(log)

if __name__ == "__main__":
    main()
