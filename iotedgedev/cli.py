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
azure_cli = AzureCli(output)
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

    if param.name == "azure_credentials":
        if value:
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
                    f('Could not switch to subscription {value}'))

    if param.name == "resource_group_name":
        if not azure_cli.resource_group_exists(value):
            raise click.BadParameter(
                f('Could not find Resource Group {value}'))
        else:
            envvars.RESOURCE_GROUP_NAME = value

    if param.name == "iothub_name":
        if not azure_cli.extension_exists("azure-cli-iot-ext"):
            azure_cli.add_extension("azure-cli-iot-ext")
        envvars.IOTHUB_NAME = value
        if not azure_cli.iothub_exists(value, envvars.RESOURCE_GROUP_NAME):
            if not azure_cli.create_iothub_free(value, envvars.RESOURCE_GROUP_NAME):
                if not azure_cli.create_iothub(value, envvars.RESOURCE_GROUP_NAME, "S1"):
                    raise click.BadParameter(
                        f('Could not create IoT Hub {value} in {envvars.RESOURCE_GROUP_NAME}'))

    if param.name == "edge_device_id":
        if not azure_cli.edge_device_exists(value, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME):
            if not azure_cli.create_edge_device(value, envvars.IOTHUB_NAME, envvars.RESOURCE_GROUP_NAME):
                raise click.BadParameter(
                    f('Could not create IoT Edge Device {value} in {envvars.IOTHUB_NAME} in {envvars.RESOURCE_GROUP_NAME}'))

    return value


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
    help="Reads the required Azure components configuration from your subscription. Creates new Azure resources or uses existing ones.")
@click.option(
    '--azure-credentials',
    required=False,
    hide_input=True,
    nargs=2,
    callback=validate_option,
    help="The credentials (username password) to use to login to Azure. Leave empty to login in interactive mode.")
@click.option(
    '--subscription',
    default=lambda: list_subscriptions_and_set_default(),
    required=True,
    callback=validate_option,
    prompt='The Azure subscription name or id to use',
    help='The Azure subscription name or id to use.')
@click.option(
    '--resource-group-name',
    required=True,
    default=lambda: list_resource_groups_and_set_default(),
    type=str,
    callback=validate_option,
    prompt='The name of the new Resource Group to use',
    help='The name of the new Resource Group to use.')
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
    default=lambda: "iotedgedev-edgedevice-dev",
    type=str,
    callback=validate_option,
    prompt='The IoT Edge Device Id to use or create',
    help='The IoT Edge Device Id to use or create.')
@click.option(
    '--update-dotenv',
    required=False,
    is_flag=True,
    help='If set, the current .env will be updated with the corresponding connection strings.')
def azure(setup, azure_credentials, subscription, resource_group_name, iothub_name, edge_device_id, update_dotenv):

    iothub_connection_string = azure_cli.get_iothub_connection_string(
        iothub_name, resource_group_name)
    device_connection_string = azure_cli.get_device_connection_string(
        edge_device_id, iothub_name, resource_group_name)

    if iothub_connection_string and device_connection_string:
        output.info(
            f("IOTHUB_CONNECTION_STRING=\"{iothub_connection_string}\""))
        output.info(
            f("DEVICE_CONNECTION_STRING=\"{device_connection_string}\""))

    if update_dotenv:
        envvars.save_envvar("IOTHUB_CONNECTION_STRING",
                            iothub_connection_string)
        envvars.save_envvar("DEVICE_CONNECTION_STRING",
                            device_connection_string)
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
