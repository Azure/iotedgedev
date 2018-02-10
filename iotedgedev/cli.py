# -*- coding: utf-8 -*-

"""Console script for iotedgedev."""
from __future__ import absolute_import

import click
import sys
from fstrings import f
from .dockercls import Docker
from .modules import Modules
from .runtime import Runtime
from .project import Project
from .utility import Utility
from .envvars import EnvVars
from .output import Output
from .iothub import IoTHub
from .azurecli import AzureCli


output = Output()
envvars = EnvVars(output)
azure_cli = AzureCli(output, envvars)
default_subscriptionId = None

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option()
@click.option(
    '--set-config',
    default=False,
    required=False,
    is_flag=True,
    help="Expands Environment Variables in /config/*.json and copies to /build/config.")
def main(set_config, az_cli=None):
    global azure_cli
    if(az_cli):
        azure_cli = az_cli

    if(set_config):
        utility = Utility(envvars, output)
        utility.set_config()
    else:
        ctx = click.get_current_context()
        if ctx.invoked_subcommand is None:
            click.echo(ctx.get_help())
            sys.exit()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--create',
    default=".",
    required=False,
    help="Creates a new Azure IoT Edge project. Use `--create .` to create in current folder. Use `--create TEXT` to create in a subfolder.")
def project(create):
    if create:
        proj = Project(output)
        proj.create(create)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--monitor-events',
    default=False,
    required=False,
    is_flag=True,
    help="Displays events that are sent from IoT Hub device to IoT Hub.")
def iothub(monitor_events):
    if monitor_events:
        utility = Utility(envvars, output)
        ih = IoTHub(envvars, output, utility)
        ih.monitor_events()


def validate_option(ctx, param, value):
    global default_subscriptionId

    if param.name == "credentials":
        if value and value[0] and value[1]:
            if not azure_cli.login(*value):
                sys.exit()

    if param.name == "subscription":
        # first verify that we have an existing auth token in cache, otherwise login using interactive
        if not default_subscriptionId:
            default_subscriptionId = azure_cli.user_has_logged_in()
            if not default_subscriptionId and not azure_cli.login_interactive():
                sys.exit()

        if default_subscriptionId != value:
            if not azure_cli.set_subscription(value):
                raise click.BadParameter(
                    f('Please verify that your subscription Id or Name is correct'))


    if param.name == "resource_group_location":
        envvars.RESOURCE_GROUP_LOCATION = value

    if param.name == "resource_group_name":
        envvars.RESOURCE_GROUP_NAME = value
        if not azure_cli.resource_group_exists(value):
            if not azure_cli.create_resource_group(value, envvars.RESOURCE_GROUP_LOCATION):
                raise click.BadParameter(
                    f('Could not find Resource Group {value}'))

    if param.name == "iothub_sku":
        envvars.IOTHUB_SKU = value

    if param.name == "iothub_name":
        envvars.IOTHUB_NAME = value
        if not azure_cli.extension_exists("azure-cli-iot-ext"):
            azure_cli.add_extension("azure-cli-iot-ext")
        if not azure_cli.iothub_exists(value, envvars.RESOURCE_GROUP_NAME):
            #check if the active subscription already contains a free IoT Hub
            # if yes ask if the user wants to create an S1
            # otherwise exit 
            if envvars.IOTHUB_SKU == "F1":
                free_iot_name, free_iot_rg = azure_cli.get_free_iothub()
                if free_iot_name:
                    output.info("You already have a Free IoT Hub SKU in your subscription, so you must either use that existing IoT Hub or create a new S1 IoT Hub. Enter (F) to use the existing Free IoT Hub or enter (S) to create a new S1 IoT Hub")
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
                raise click.BadParameter(
                    f('Could not create IoT Hub {value} in {envvars.RESOURCE_GROUP_NAME}'))

    if param.name == "edge_device_id":
        envvars.EDGE_DEVICE_ID = value
        if not azure_cli.edge_device_exists(value, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME):
            if not azure_cli.create_edge_device(value, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME):
                raise click.BadParameter(
                    f('Could not create IoT Edge Device {value} in {envvars.IOTHUB_NAME} in {envvars.RESOURCE_GROUP_NAME}'))

        envvars.IOTHUB_CONNECTION_STRING = azure_cli.get_iothub_connection_string(
            envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME)
        envvars.DEVICE_CONNECTION_STRING = azure_cli.get_device_connection_string(
            envvars.EDGE_DEVICE_ID, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME)

        if envvars.IOTHUB_CONNECTION_STRING and envvars.DEVICE_CONNECTION_STRING:
            output.info(
                f("IOTHUB_CONNECTION_STRING=\"{envvars.IOTHUB_CONNECTION_STRING}\""))
            output.info(
                f("DEVICE_CONNECTION_STRING=\"{envvars.DEVICE_CONNECTION_STRING}\""))

    return value

def list_edge_devices_and_set_default():
    if not azure_cli.list_edge_devices(envvars.IOTHUB_NAME):
        sys.exit()
    return "iotedgedev-edgedevice-dev"
    
def list_iot_hubs_and_set_default():
    if not azure_cli.list_iot_hubs(envvars.RESOURCE_GROUP_NAME):
        sys.exit()
    return "iotedgedev-iothub-dev"


def list_resource_groups_and_set_default():
    if not azure_cli.list_resource_groups():
        sys.exit()
    return "iotedgedev-rg-dev"

def list_subscriptions_and_set_default():
    global default_subscriptionId
    # first verify that we have an existing auth token in cache, otherwise login using interactive
    if not default_subscriptionId:
        default_subscriptionId = azure_cli.user_has_logged_in()

        if not default_subscriptionId and not azure_cli.login_interactive():
            sys.exit()

    if not azure_cli.list_subscriptions():
        sys.exit()
    default_subscriptionId = azure_cli.get_default_subscription()
    return default_subscriptionId


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--setup',
    required=True,
    is_flag=True,
    help="Reads the required Azure resources configuration from your subscription. Creates new Azure resources or uses an existing one.")
@click.option(
    '--credentials',
    required=False,
    hide_input=True,
    default=(None, None),
    type=(str, str),
    callback=validate_option,
    help="The credentials (username password) to use to login to Azure. If --credentials not specified, you will login in the interactive mode.")
@click.option(
    '--subscription',
    default=lambda: list_subscriptions_and_set_default(),
    required=True,
    callback=validate_option,
    prompt="The Azure subscription name or id to use",
    help="The Azure subscription name or id to use.")
@click.option(
    '--resource-group-location',
    required=False,
    default='westus',
    type=click.Choice(['australiaeast','australiasoutheast','brazilsouth','canadacentral','canadaeast','centralindia','centralus','eastasia','eastus','eastus2','japanwest','japaneast','northeurope','northcentralus','southindia','uksouth','ukwest','westus','westeurope','southcentralus','westcentralus','westus2']),
    callback=validate_option,
    help="The location of the new Resource Group. If --resource-group-location not specified, the default will be West US.")
@click.option(
    '--resource-group-name',
    required=True,
    default=lambda: list_resource_groups_and_set_default(),
    type=str,
    callback=validate_option,
    prompt="The name of the Resource Group to use or create. Creates a new Resource Group if not found",
    help="The name of the Resource Group to use or create. Creates a new Resource Group if not found.")
@click.option(
    '--iothub-sku',
    required=False,
    default='F1',
    type=click.Choice(['F1', 'S1', 'S2', 'S3']),
    callback=validate_option,
    help="The SKU of the new IoT Hub. If --iothub-sku not specified, the default will be F1 (free).")
@click.option(
    '--iothub-name',
    required=True,
    default=lambda: list_iot_hubs_and_set_default(),
    type=str,
    callback=validate_option,
    prompt='The IoT Hub name to be used. Creates a new IoT Hub if not found',
    help='The IoT Hub name to be used. Creates a new IoT Hub if not found.')
@click.option(
    '--edge-device-id',
    required=True,
    default=lambda: list_edge_devices_and_set_default(),
    type=str,
    callback=validate_option,
    prompt='The IoT Edge Device Id to be used. Creates a new Edge Device if not found',
    help='The IoT Edge Device Id to be used. Creates a new Edge Device if not found.')
@click.option(
    '--update-dotenv',
    required=True,
    default=False,
    is_flag=True,
    prompt='Update the current .env with these connection strings?',    
    help='If set, the current .env will be updated with the corresponding connection strings.')
def azure(setup, 
    credentials, 
    subscription, 
    resource_group_location, 
    resource_group_name, 
    iothub_sku, 
    iothub_name, 
    edge_device_id, 
    update_dotenv):
    
    if update_dotenv:
        if envvars.backup_dotenv():

            envvars.save_envvar("IOTHUB_CONNECTION_STRING",
                                envvars.IOTHUB_CONNECTION_STRING)
            envvars.save_envvar("DEVICE_CONNECTION_STRING",
                                envvars.DEVICE_CONNECTION_STRING)
            output.info("Updated current .env file")

    # azure_cli.logout()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--build',
    default=False,
    required=False,
    is_flag=True,
    help="Builds and pushes modules specified in ACTIVE_MODULES Environment Variable to specified container registry.")
@click.option(
    '--deploy',
    default=False,
    required=False,
    is_flag=True,
    help="Deploys modules to Edge device using deployment.json in the /.config directory.")
def modules(build, deploy):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    mod = Modules(envvars, utility, output, dock)

    if build:
        mod.build()

    if deploy:
        mod.deploy()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--setup',
    default=False,
    required=False,
    is_flag=True,
    help="Setup Edge Runtime using runtime.json in build/config directory.")
@click.option(
    '--start',
    default=False,
    required=False,
    is_flag=True,
    help="Starts Edge Runtime. Calls iotedgectl start.")
@click.option(
    '--stop',
    default=False,
    required=False,
    is_flag=True,
    help="Stops Edge Runtime. Calls iotedgectl stop.")
@click.option(
    '--restart',
    default=False,
    required=False,
    is_flag=True,
    help="Restarts Edge Runtime. Calls iotedgectl stop, removes module containers and images, calls iotedgectl setup (with --config-file) and then calls iotedgectl start.")
@click.option(
    '--status',
    default=False,
    required=False,
    is_flag=True,
    help="Edge Runtime Status. Calls iotedgectl status.")
def runtime(setup, start, stop, restart, status):

    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    run = Runtime(envvars, utility, output, dock)

    if setup:
        run.setup()

    if start:
        run.start()

    if stop:
        run.stop()

    if restart:
        run.restart()

    if status:
        run.status()


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '--setup-registry',
    default=False,
    required=False,
    is_flag=True,
    help="Pulls Edge Runtime from Docker Hub and pushes to your specified container registry. Also, updates config files to use CONTAINER_REGISTRY_* instead of the Microsoft Docker hub. See CONTAINER_REGISTRY Environment Variables.")
@click.option(
    '--clean',
    default=False,
    required=False,
    is_flag=True,
    help="Removes all the Docker containers and Images.")
@click.option(
    '--remove-modules',
    default=False,
    required=False,
    is_flag=True,
    help="Removes only the edge modules Docker containers and images specified in ACTIVE_MODULES, not edgeAgent or edgeHub.")
@click.option(
    '--remove-containers',
    default=False,
    required=False,
    is_flag=True,
    help="Removes all the Docker containers")
@click.option('--remove-images', default=False, required=False,
              is_flag=True, help="Removes all the Docker images.")
@click.option(
    '--logs',
    default=False,
    required=False,
    is_flag=True,
    help="Opens a new terminal window for edgeAgent, edgeHub and each edge module and saves to LOGS_PATH. You can configure the terminal command with LOGS_CMD.")
@click.option(
    '--show-logs',
    default=False,
    required=False,
    is_flag=True,
    help="Opens a new terminal window for edgeAgent, edgeHub and each edge module. You can configure the terminal command with LOGS_CMD.")
@click.option(
    '--save-logs',
    default=False,
    required=False,
    is_flag=True,
    help="Saves edgeAgent, edgeHub and each edge module logs to LOGS_PATH.")
def docker(
        setup_registry,
        clean,
        remove_modules,
        remove_containers,
        remove_images,
        logs,
        show_logs,
        save_logs):

    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)

    if setup_registry:
        dock.setup_registry()

    if clean:
        remove_containers = True
        remove_images = True

    if remove_modules:
        dock.remove_modules()

    if remove_containers:
        dock.remove_containers()

    if remove_images:
        dock.remove_images()

    if logs:
        show_logs = True
        save_logs = True

    if show_logs or save_logs:
        dock.handle_logs_cmd(show_logs, save_logs)


main.add_command(runtime)
main.add_command(modules)
main.add_command(docker)
main.add_command(project)
main.add_command(iothub)
main.add_command(azure)


if __name__ == "__main__":
    main()
