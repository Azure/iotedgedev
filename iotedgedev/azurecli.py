import json
import os
import signal
import subprocess
import sys
from io import StringIO
from threading import Thread, Timer

from azure.cli.core import get_default_cli
from fstrings import f
from queue import Empty, Queue

from . import telemetry

output_io_cls = StringIO


def get_query_argument_for_id_and_name(token):
    return "[?starts_with(@.id,'{0}') || contains(@.name,'{1}')]".format(token.lower(), token)


class AzureCli:
    def __init__(self,  output, envvars, cli=get_default_cli()):
        self.output = output
        self.envvars = envvars
        self.az_cli = cli
        self.process = None
        self._proc_terminated = False

    def decode(self, val):
        return val.decode("utf-8").strip()

    def is_posix(self):
        return self.envvars.is_posix()

    def prepare_az_cli_args(self, args, suppress_output=False):
        if suppress_output:
            args.extend(["--query", "\"[?n]|[0]\""])

        az_args = ["az"]+args
        return az_args

    def invoke_az_cli_outproc(self, args, error_message=None, stdout_io=None, stderr_io=None, suppress_output=False, timeout=None):
        try:
            if timeout:
                timeout = int(timeout)

            monitor_events = False
            if 'monitor-events' in args:
                monitor_events = True
                self._proc_terminated = False

            # Consider using functools
            if monitor_events:
                process = subprocess.Popen(self.prepare_az_cli_args(args, suppress_output),
                                           shell=not self.is_posix(),
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           preexec_fn=os.setsid if self.is_posix() else None,
                                           creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if not self.is_posix() else 0)
            elif stdout_io or stderr_io:
                process = subprocess.Popen(self.prepare_az_cli_args(args, suppress_output),
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           shell=not self.is_posix())
            else:
                process = subprocess.Popen(self.prepare_az_cli_args(args, suppress_output),
                                           shell=not self.is_posix())

            self.process = process

            timer = None
            if timeout:
                # This Timer will attempt to be accurate but its not always the case in practice
                timer = Timer(float(timeout),
                              self._terminate_process_tree,
                              args=['Timeout set to {0} seconds, which expired as expected.'.format(timeout)])
            try:
                if timer:
                    timer.start()

                if not monitor_events:
                    stdout_data, stderr_data = process.communicate()
                else:
                    return self._handle_monitor_event_process(process)

            finally:
                if timer:
                    timer.cancel()

            if stderr_data and b"invalid_grant" in stderr_data:
                self.output.error(self.decode(stderr_data))
                self.output.info(
                    "Your Azure CLI session has expired. Please re-run `iotedgedev iothub setup` to refresh your credentials.")
                self.logout()
                sys.exit()

            if stdout_io and stdout_data != "":
                stdout_io.writelines(self.decode(stdout_data))

            if stderr_io and stderr_data != "":
                stderr_io.writelines(self.decode(stderr_data))

            if process.returncode != 0:
                if error_message:
                    self.output.error(error_message)
                    self.output.line()
                return False

            if not stdout_io and not stderr_io:
                self.output.line()

        except Exception as e:
            if error_message:
                self.output.error(error_message)
            self.output.error(str(e))
            self.output.line()
            return False

        return True

    def _enqueue_stream(self, stream, queue):
        try:
            while not self._proc_terminated:
                queue.put(stream.readline().decode('utf8').rstrip())
        finally:
            stream.close()

    def _handle_monitor_event_process(self, process, error_message=None):
        stdout_queue = Queue()
        stderr_queue = Queue()

        stream_thread_map = {
            'stdout': Thread(target=self._enqueue_stream, args=(process.stdout, stdout_queue), daemon=True),
            'stderr': Thread(target=self._enqueue_stream, args=(process.stderr, stderr_queue), daemon=True)
        }

        stream_thread_map['stdout'].start()
        stream_thread_map['stderr'].start()

        try:
            while not self._proc_terminated:
                if not process.poll():
                    try:
                        self.output.echo(stdout_queue.get_nowait())
                    except Empty:
                        pass
                else:
                    err = None
                    try:
                        err = stderr_queue.get_nowait()
                    except Empty:
                        pass
                    # Avoid empty sys.excepthook errors from underlying future
                    # There is already a uAMQP issue in work for this
                    # https://github.com/Azure/azure-uamqp-python/issues/30
                    if err and "sys.excepthook" not in err:
                        err = err.lstrip()
                        err = err.lstrip('ERROR:')
                        if error_message:
                            err = "{}: {}".format(error_message, err)
                        self.output.error(err)
                    return False
        except KeyboardInterrupt:
            self.output.info('Terminating process...')
            self._terminate_process_tree()

        return True

    def _terminate_process_tree(self, msg=None):
        try:
            if self.process:
                if self.is_posix():
                    os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                else:
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)
                    self.process.kill()
                self._proc_terminated = True
                if msg:
                    self.output.info(msg)
                    self.output.line()
            return True
        except Exception:
            return False

    def invoke_az_cli(self, args, error_message=None, stdout_io=None):
        try:
            exit_code = self.az_cli.invoke(args, out_file=stdout_io)
            if exit_code and exit_code != 0:
                if error_message:
                    self.output.error(error_message)
                return False
        except Exception as e:
            if error_message:
                self.output.error(error_message)
            self.output.error(str(e))
            return False

        self.output.line()

        return True

    def add_extension(self, name):
        return self.invoke_az_cli_outproc(["extension", "add", "--name", name,
                                           "--yes"],
                                          f("Error while adding extension {name}."), suppress_output=True)

    def add_extension_with_source(self, source_url):
        return self.invoke_az_cli_outproc(["extension", "add", "--source", source_url,
                                           "--yes"],
                                          f("Error while add extension from source {source_url}."),
                                          suppress_output=True)

    def extension_exists(self, name):
        return self.invoke_az_cli_outproc(["extension", "show", "--name", name, "--output", "table"],
                                          f("Error while checking for extension {name}."), suppress_output=True)

    def user_has_logged_in(self):

        self.output.header("AUTHENTICATION")

        self.output.status(f("Retrieving Azure CLI credentials from cache..."))

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(
                ["account", "show"], stdout_io=io)

            if result:
                try:
                    self.output.prompt("Azure CLI credentials found.")
                    out_string = io.getvalue()
                    data = json.loads(out_string)
                    return data["id"]
                except Exception:
                    pass
        self.output.prompt(
            "Azure CLI credentials not found. Please follow instructions below to login to the Azure CLI.")
        return None

    def login_account(self, username, password):

        return self.invoke_az_cli_outproc(["login", "-u", username,
                                           "-p",  password],
                                          "Error while trying to login to Azure. Make sure your account credentials are correct", suppress_output=True)

    def login_sp(self, username, password, tenant):

        return self.invoke_az_cli_outproc(["login", "--service-principal", "-u", username,
                                           "-p",  password, "--tenant", tenant],
                                          "Error while trying to login to Azure. Make sure your service principal credentials are correct.", suppress_output=True)

    def login_interactive(self):
        return self.invoke_az_cli_outproc(["login"],
                                          "Error while trying to login to Azure.", suppress_output=True)

    def logout(self):
        return self.invoke_az_cli_outproc(["account", "clear"])

    def list_subscriptions(self):
        self.output.status("Retrieving Azure Subscriptions...")
        return self.invoke_az_cli_outproc(["account", "list", "--all", "--query", "[].{\"Subscription Name\":name, Id:id}", "--out", "table"],
                                          "Error while trying to list Azure subscriptions.")

    def get_default_subscription(self):

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(["account", "show"],
                                                "Error while trying to get the default Azure subscription id.", io)
            if result:
                out_string = io.getvalue()
                data = json.loads(out_string)
                return data["id"]
        return ''

    def get_subscription_id_starts_with(self, token):
        with output_io_cls() as io:
            query = get_query_argument_for_id_and_name(token)
            result = self.invoke_az_cli_outproc(["account", "list", "--query", query],
                                                "Could not find a subscription for which the id starts with or name contains '{0}'".format(token), io)

            if result:
                out_string = io.getvalue()
                if out_string:

                    data = json.loads(out_string)
                    if len(data) == 1:
                        return data[0]["id"]
                    elif len(data) > 1:
                        self.output.error(
                            "Found multiple subscriptions for which the ids start with or names contain '{0}'. Please enter more characters to further refine your selection.".format(token))
                        return token
                    else:
                        self.output.error("Could not find a subscription for which the id starts with or name contains '{0}'.".format(token))

        return ''

    def set_subscription(self, subscription):

        if len(subscription) < 36:
            subscription = self.get_subscription_id_starts_with(subscription)
            if len(subscription) < 36:
                return subscription

        if len(subscription) == 36:
            self.output.status(f("Setting Subscription to '{subscription}'..."))

            result = self.invoke_az_cli_outproc(["account", "set", "--subscription", subscription],
                                                "Error while trying to set Azure subscription.")
            if result:
                return subscription

        return None

    def resource_group_exists(self, name):
        self.output.status(f("Checking if Resource Group '{name}' exists..."))

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(["group", "exists", "-n", name],
                                                f("Resource Group {name} does not exist."), io)
            if result:
                out_string = io.getvalue()
                if out_string == "true":
                    return True

        self.output.prompt(f("Resource Group {name} does not exist."))

        return False

    def get_resource_group_location(self, name):

        self.output.status(f("Retrieving Resource Group '{name}' location..."))

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(["group", "show", "-n", name, "--query", "location", "--output", "tsv"],
                                                f("Could not retrieve Resource Group {name}'s location."), io)
            if result:
                return io.getvalue()
            else:
                return ''

    def create_resource_group(self, name, location):
        self.output.status(
            f("Creating Resource Group '{name}' at '{location}'..."))

        with output_io_cls() as io:

            result = self.invoke_az_cli_outproc(["group", "create", "--name", name, "--location", location],
                                                f("Could not create the new Resource Group {name} at location:{location}."), io)
        return result

    def list_resource_groups(self):
        self.output.header("RESOURCE GROUP")
        self.output.status("Retrieving Resource Groups...")

        with output_io_cls() as io:

            result = self.invoke_az_cli_outproc(["group", "list", "--query", "[].{\"Resource Group\":name, Location:location}", "--out", "table"], "Could not list the Resource Groups.", stdout_io=io)

            self.output.prompt(io.getvalue())
            self.output.line()

        return result

    def set_modules(self, device_id, connection_string, config):
        self.output.status(f("Deploying '{config}' to '{device_id}'..."))

        config = os.path.join(os.getcwd(), config)

        if not os.path.exists(config):
            raise FileNotFoundError('Deployment manifest file "{0}" not found. Please run `iotedgedev build` first'.format(config))

        telemetry.add_extra_props({'iothubhostname': connection_string.iothub_host.name_hash, 'iothubhostnamesuffix': connection_string.iothub_host.name_suffix})

        return self.invoke_az_cli_outproc(["iot", "edge", "set-modules", "-d", device_id, "-n", connection_string.iothub_host.hub_name, "-k", config, "-l", connection_string.connection_string],
                                          error_message=f("Failed to deploy '{config}' to '{device_id}'..."), suppress_output=True)

    def monitor_events(self, device_id, connection_string, hub_name, timeout=300):
        return self.invoke_az_cli_outproc(["iot", "hub", "monitor-events", "-d", device_id, "-n", hub_name, "-l", connection_string, '-t', str(timeout), '-y'],
                                          error_message=f("Failed to start monitoring events."), suppress_output=False, timeout=timeout)

    def get_free_iothub(self):
        with output_io_cls() as io:

            result = self.invoke_az_cli_outproc(["iot", "hub", "list"], f("Could not list IoT Hubs in subscription."), stdout_io=io)
            if result:
                out_string = io.getvalue()
                data = json.loads(out_string)
                for iot in data:
                    if iot["sku"]["name"] == "F1":
                        return (iot["name"], iot["resourcegroup"])
        return (None, None)

    def get_first_iothub(self, resource_group):

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(
                ["iot", "hub", "list", "--resource-group", resource_group, "--query", "[0]"], f("Could not get first IoT Hub."), io)

            if result:
                out_string = io.getvalue()
                if out_string:
                    data = json.loads(out_string)
                    return data["name"]
        return ''

    def list_iot_hubs(self, resource_group):
        self.output.header("IOT HUB")
        self.output.status(f("Retrieving IoT Hubs in '{resource_group}'..."))

        return self.invoke_az_cli_outproc(["iot", "hub", "list", "--resource-group", resource_group, "--query", "[].{\"IoT Hub\":name}", "--out", "table"],
                                          f("Could not list the IoT Hubs in {resource_group}."))

    def iothub_exists(self, value, resource_group):
        self.output.status(
            f("Checking if '{value}' IoT Hub exists..."))

        with output_io_cls() as io:

            result = self.invoke_az_cli_outproc(["iot", "hub", "show", "--name", value, "--resource-group",
                                                 resource_group, "--out", "table"], stderr_io=io)
        if not result:
            self.output.prompt(
                f("Could not locate the {value} in {resource_group}."))
        return result

    def create_iothub(self, value, resource_group, sku):
        self.output.status(
            f("Creating '{value}' in '{resource_group}' with '{sku}' sku..."))

        with output_io_cls() as io:
            with output_io_cls() as error_io:
                self.output.prompt(
                    "Creating IoT Hub. Please wait as this could take a few minutes to complete...")

                result = self.invoke_az_cli_outproc(["iot", "hub", "create", "--name", value, "--resource-group",
                                                     resource_group, "--sku", sku, "--query", "[].{\"IoT Hub\":name}", "--out", "table"],
                                                    f("Could not create the IoT Hub {value} in {resource_group} with sku {sku}."), stdout_io=io, stderr_io=error_io)
                if not result and error_io.getvalue():
                    self.output.error(error_io.getvalue())
                    self.output.line()
                elif io.getvalue():
                    self.output.prompt(io.getvalue())
                    self.output.line()
        return result

    def get_iothub_connection_string(self, value, resource_group):
        self.output.status(
            f("Retrieving '{value}' connection string..."))

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(["iot", "hub", "connection-string", "show", "--hub-name", value,
                                                 "--resource-group", resource_group],
                                                f("Could not create the IoT Hub {value} in {resource_group}."), stdout_io=io)
            if result:
                out_string = io.getvalue()
                data = json.loads(out_string)
                if "cs" in data:
                    return data["cs"]
                else:
                    return data["connectionString"]

        return ''

    def edge_device_exists(self, value, iothub, resource_group):
        self.output.status(
            f("Checking if '{value}' device exists in '{iothub}'..."))

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(["iot", "hub", "device-identity", "show", "--device-id", value, "--hub-name", iothub,
                                                 "--resource-group", resource_group, "--out", "table"], stderr_io=io)
        if not result:
            self.output.prompt(
                f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}."))
        return result

    def list_edge_devices(self, iothub):
        self.output.header("EDGE DEVICE")
        self.output.status(
            f("Retrieving edge devices in '{iothub}'..."))

        return self.invoke_az_cli_outproc(["iot", "hub", "device-identity", "list", "--hub-name", iothub,
                                           "--edge-enabled", "--query", "[].{\"Device Id\":deviceId}", "--output", "table"],
                                          f("Could not list the edge devices  in {iothub} IoT Hub."))

    def create_edge_device(self, value, iothub, resource_group):
        self.output.status(
            f("Creating '{value}' edge device in '{iothub}'..."))

        return self.invoke_az_cli_outproc(["iot", "hub", "device-identity", "create", "--device-id", value, "--hub-name", iothub,
                                           "--resource-group", resource_group, "--edge-enabled", "--query", "[].{\"Device Id\":deviceId}", "--output", "table"],
                                          f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}."))

    def get_device_connection_string(self, value, iothub, resource_group):
        self.output.status(
            f("Retrieving '{value}' connection string..."))

        with output_io_cls() as io:
            result = self.invoke_az_cli_outproc(["iot", "hub", "device-identity", "connection-string", "show", "--device-id", value, "--hub-name", iothub,
                                                 "--resource-group", resource_group],
                                                f("Could not locate the {value} device in {iothub} IoT Hub in {resource_group}."), stdout_io=io)
            if result:
                out_string = io.getvalue()
                data = json.loads(out_string)
                if "cs" in data:
                    return data["cs"]
                else:
                    return data["connectionString"]

        return ''
