import hashlib
import socket
import sys

import click
from fstrings import f

from .azurecli import AzureCli
from .constants import Constants
from .decorators import add_module_options, with_telemetry
from .dockercls import Docker
from .edge import Edge
from .envvars import EnvVars
from .iothub import IoTHub
from .modules import Modules
from .organizedgroup import OrganizedGroup
from .output import Output
from .simulator import Simulator
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
@with_telemetry
def main():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Edge solutions", order=1)
@with_telemetry
def solution():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Edge simulator", order=1)
@with_telemetry
def simulator():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage IoT Hub and IoT Edge devices", order=1)
@with_telemetry
def iothub():
    pass


@main.group(context_settings=CONTEXT_SETTINGS, help="Manage Docker", order=1)
@with_telemetry
def docker():
    pass


@solution.command(context_settings=CONTEXT_SETTINGS,
                  short_help="Create a new IoT Edge solution",
                  help="Create a new IoT Edge solution, where NAME is the solution folder name. "
                       "Use \".\" as NAME to create in the current folder.")
@click.argument("name",
                required=True)
@click.option("--edge-runtime-version",
              "-er",
              default="1.2",
              show_default=True,
              required=False,
              help="Specify the IoT Edge Runtime Version. Currently available 1.0, 1.1, 1.2")
@add_module_options(envvars, init=True)
@with_telemetry
def new(name, module, template, edge_runtime_version, group_id):
    if edge_runtime_version is not None:
        if (str(edge_runtime_version) != "1.0" and str(edge_runtime_version) != "1.1" and str(edge_runtime_version) != "1.2"):
            output.info('-edge-runtime-version `{0}` is not valid. Currently supported versions are 1.0, 1.1, 1.2'.format(edge_runtime_version))
            sys.exit()
    utility = Utility(envvars, output)
    sol = Solution(output, utility)
    sol.create(name, module, template, edge_runtime_version, group_id)


main.add_command(new)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  help="Create a new IoT Edge solution and provision Azure resources",
                  # hack to prevent Click truncating help messages
                  short_help="Create a new IoT Edge solution and provision Azure resources")
@click.option("--edge-runtime-version",
              "-er",
              default="1.2",
              show_default=True,
              required=False,
              help="Specify the IoT Edge Runtime Version. Currently available 1.0, 1.1, 1.2")
@add_module_options(envvars, init=True)
@with_telemetry
def init(module, template, group_id, edge_runtime_version):
    if edge_runtime_version is not None:
        if (str(edge_runtime_version) != "1.0" and str(edge_runtime_version) != "1.1" and str(edge_runtime_version) != "1.2"):
            output.info('-edge-runtime-version `{0}` is not valid. Currently supported versions are 1.0, 1.1, 1.2'.format(edge_runtime_version))
            sys.exit()
    utility = Utility(envvars, output)

    if template == "java":
        solcmd = "iotedgedev new . --module {0} --template {1} --edge-runtime-version {2} --group-id {3}".format(module, template, edge_runtime_version, group_id)
    else:
        solcmd = "iotedgedev new . --module {0} --template {1} --edge-runtime-version {2}".format(module, template, edge_runtime_version)
    output.header(solcmd)
    ret = utility.call_proc(solcmd.split())

    if ret == 0:
        azsetupcmd = "iotedgedev iothub setup --update-dotenv"
        output.header(azsetupcmd)
        # Had to use call_proc, because @click.invoke doesn't honor prompts
        utility.call_proc(azsetupcmd.split())


main.add_command(init)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Push, deploy, start, monitor")
@click.pass_context
@with_telemetry
def e2e(ctx):
    ctx.invoke(init)
    ctx.invoke(push)
    ctx.invoke(deploy)
    ctx.invoke(monitor)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  short_help="Add a new module to the solution",
                  help="Add a new module to the solution, where NAME is the module name")
@add_module_options(envvars)
@with_telemetry
def add(name, template, group_id):
    mod = Modules(envvars, output)
    mod.add(name, template, group_id)


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
@click.option("--file",
              "-f",
              "template_file",
              default=envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE,
              show_default=True,
              required=False,
              help="Specify the deployment manifest template file")
@click.option("--platform",
              "-P",
              default=envvars.DEFAULT_PLATFORM,
              show_default=True,
              required=False,
              help="Specify the platform")
@click.pass_context
@with_telemetry
def build(ctx, push, do_deploy, template_file, platform):
    mod = Modules(envvars, output)
    mod.build_push(template_file, platform, no_push=not push)

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
              help="Inform the push command to not build module images before pushing to container registry")
@click.option("--file",
              "-f",
              "template_file",
              default=envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE,
              show_default=True,
              required=False,
              help="Specify the deployment manifest template file")
@click.option("--platform",
              "-P",
              default=envvars.DEFAULT_PLATFORM,
              show_default=True,
              required=False,
              help="Specify the platform")
@click.pass_context
@with_telemetry
def push(ctx, do_deploy, no_build, template_file, platform):
    mod = Modules(envvars, output)
    mod.push(template_file, platform, no_build=no_build)

    if do_deploy:
        ctx.invoke(deploy)


main.add_command(push)


@solution.command(context_settings=CONTEXT_SETTINGS, help="Deploy solution to IoT Edge device")
@click.option("--file",
              "-f",
              "manifest_file",
              default=envvars.DEPLOYMENT_CONFIG_FILE_PATH,
              show_default=True,
              required=False,
              help="Specify the deployment manifest file")
@with_telemetry
def deploy(manifest_file):
    ensure_azure_cli_iot_ext()
    edge = Edge(envvars, output, azure_cli)
    edge.deploy(manifest_file)


main.add_command(deploy)


@solution.command(context_settings=CONTEXT_SETTINGS,
                  help="Expand environment variables and placeholders in deployment manifest template file and copy to config folder",
                  # hack to prevent Click truncating help messages
                  short_help="Expand environment variables and placeholders in deployment manifest template file and copy to config folder")
@click.option("--file",
              "-f",
              "template_file",
              default=envvars.DEPLOYMENT_CONFIG_TEMPLATE_FILE,
              show_default=True,
              required=False,
              help="Specify the deployment manifest template file")
@click.option("--platform",
              "-P",
              default=envvars.DEFAULT_PLATFORM,
              show_default=True,
              required=False,
              help="Specify the platform")
@click.option("--fail-on-validation-error",
              "fail_on_validation_error",
              is_flag=True,
              default=False,
              show_default=True,
              required=False,
              help="Fail the command when deployment manifest validation failed")
@with_telemetry
def genconfig(template_file, platform, fail_on_validation_error):
    mod = Modules(envvars, output)
    mod.build_push(template_file, platform, no_build=True, no_push=True, fail_on_validation_error=fail_on_validation_error)


main.add_command(genconfig)


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="setup",
                   short_help="Setup IoT Edge simulator. This must be done before starting",
                   help="Setup IoT Edge simulator. This must be done before starting")
@click.option("--gateway-host",
              "-g",
              help="GatewayHostName value for the module to connect.",
              required=False,
              default=socket.getfqdn(),
              show_default=True)
@click.option("--iothub-connection-string",
              "-i",
              help="Set Azure IoT Hub connection string. Note: Use double quotes when supplying this input.",
              required=False)
@with_telemetry
def setup_simulator(gateway_host, iothub_connection_string):
    sim = Simulator(envvars, output)
    sim.setup(gateway_host, iothub_connection_string)


main.add_command(setup_simulator)


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="start",
                   short_help="Start IoT Edge simulator",
                   help="Start IoT Edge simulator. To start in solution mode, use `iotedgdev simulator start -s [-v] [-b]`. "
                        "To start in single module mode, use `iotedgedev simulator start -i input1,input2 [-p 53000]`")
@click.option("--setup",
              "-u",
              is_flag=True,
              default=False,
              show_default=True,
              help="Setup IoT Edge simulator before starting.")
@click.option("--solution",
              "-s",
              is_flag=True,
              default=False,
              show_default=True,
              help="Start IoT Edge simulator in solution mode using the deployment.json in config folder.")
@click.option("--verbose",
              "-v",
              required=False,
              is_flag=True,
              default=False,
              show_default=True,
              help="Show the solution container logs.")
@click.option("--build",
              "-b",
              required=False,
              is_flag=True,
              default=False,
              show_default=True,
              help="Build the solution before starting IoT Edge simulator in solution mode.")
@click.option("--file",
              "-f",
              "manifest_file",
              default=envvars.DEPLOYMENT_CONFIG_FILE_PATH,
              show_default=True,
              required=False,
              help="Specify the deployment manifest file. When `--build` flag is set, specify a deployment manifest template and it will be built.")
@click.option("--platform",
              "-P",
              default=envvars.DEFAULT_PLATFORM,
              show_default=True,
              required=False,
              help="Specify the platform")
@click.option("--inputs",
              "-i",
              required=False,
              help="Start IoT Edge simulator in single module mode "
                   "using the specified comma-separated inputs of the target module, e.g., `input1,input2`.")
@click.option("--port",
              "-p",
              required=False,
              default=53000,
              show_default=True,
              help="Port of the service for sending message.")
@click.option("--iothub-connection-string",
              "-c",
              help="Set Azure IoT Hub connection string when setup IoT Edge simulator. Note: Use double quotes when supplying this input.",
              required=False)
@with_telemetry
def start_simulator(setup, solution, build, manifest_file, platform, verbose, inputs, port, iothub_connection_string):
    sim = Simulator(envvars, output)

    if setup:
        sim.setup(socket.getfqdn(), iothub_connection_string)

    if solution or not inputs:
        sim.start_solution(manifest_file, platform, verbose, build)
    else:
        sim.start_single(inputs, port)


main.add_command(start_simulator)


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   name="stop",
                   help="Stop IoT Edge simulator")
@with_telemetry
def stop_simulator():
    sim = Simulator(envvars, output)
    sim.stop()


main.add_command(stop_simulator)


@simulator.command(context_settings=CONTEXT_SETTINGS,
                   # short_help hack to prevent Click truncating help text (https://github.com/pallets/click/issues/486)
                   short_help="Get the credentials of target module such as connection string and certificate file path.",
                   help="Get the credentials of target module such as connection string and certificate file path.")
@click.option("--local",
              "-l",
              help="Set `localhost` to `GatewayHostName` for module to run on host natively.",
              is_flag=True,
              required=False,
              default=False,
              show_default=True)
@click.option("--output-file",
              "-o",
              help="Specify the output file to save the credentials. If the file exists, its content will be overwritten.",
              required=False)
@with_telemetry
def modulecred(local, output_file):
    sim = Simulator(envvars, output)
    sim.modulecred(local, output_file)


@iothub.command(context_settings=CONTEXT_SETTINGS,
                help="Monitor messages from IoT Edge device to IoT Hub",
                # hack to prevent Click truncating help messages
                short_help="Monitor messages from IoT Edge device to IoT Hub")
@click.option("--timeout",
              "-t",
              required=False,
              help="Specify number of seconds to monitor for messages")
@with_telemetry
def monitor(timeout):
    ensure_azure_cli_iot_ext()
    utility = Utility(envvars, output)
    ih = IoTHub(envvars, utility, output, azure_cli)
    ih.monitor_events(timeout)


main.add_command(monitor)


def ensure_azure_cli_iot_ext():
    if not azure_cli.extension_exists("azure-iot"):
        try:
            # Install fixed version of Azure CLI IoT extension
            azure_cli.add_extension_with_source(Constants.azure_cli_iot_ext_source_url)
        except Exception:
            # Fall back to install latest Azure CLI IoT extension when fail
            azure_cli.add_extension("azure-iot")


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
            subscription = azure_cli.set_subscription(value)
            if not subscription:
                raise click.BadParameter(f('Please verify that your subscription Id or Name is correct'))
            if len(subscription) < 36:
                value = click.prompt(param.prompt, default=default_subscriptionId)
                return validate_option(ctx, param, value)

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
        ensure_azure_cli_iot_ext()
        if not azure_cli.iothub_exists(value, envvars.RESOURCE_GROUP_NAME):
            # check if the active subscription already contains a free IoT Hub
            # if yes ask if the user wants to create an S1
            # otherwise exit
            if envvars.IOTHUB_SKU == "F1":
                free_iot_name, free_iot_rg = azure_cli.get_free_iothub()
                if free_iot_name:
                    output.info("You already have a Free IoT Hub SKU in your subscription, "
                                "so you must either use that existing IoT Hub or create a new S1 IoT Hub. "
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
@with_telemetry
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
@with_telemetry
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
@with_telemetry
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
                help="Open a new terminal window for EdgeAgent, EdgeHub and each Edge module and save to LOGS_PATH. "
                     "You can configure the terminal command with LOGS_CMD.",
                short_help="Open a new terminal window for EdgeAgent, EdgeHub and each Edge module and save to LOGS_PATH")
@click.option("--show",
              "-l",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Open a new terminal window for EdgeAgent, EdgeHub and each Edge module. You can configure the terminal command with LOGS_CMD.")
@click.option("--save",
              "-s",
              default=False,
              show_default=True,
              required=False,
              is_flag=True,
              help="Save EdgeAgent, EdgeHub and each Edge module logs to LOGS_PATH.")
@with_telemetry
def log(show, save):
    utility = Utility(envvars, output)
    dock = Docker(envvars, utility, output)
    dock.handle_logs_cmd(show, save)


main.add_command(log)

if __name__ == "__main__":
    main()
