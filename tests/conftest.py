import os

import pytest

from iotedgedev.azurecli import AzureCli


def _hub_name_from_connection_string(connection_string):
    for part in str(connection_string).split(";"):
        if part.lower().startswith("hostname="):
            return part.split("=", 1)[1].split(".")[0]
    return None


def _rewrite_args(args):
    args = list(args)
    if not args or args[0] != "iot" or "-l" not in args:
        return args

    index = args.index("-l")
    connection_string = args[index + 1]
    hub_name = _hub_name_from_connection_string(connection_string)

    del args[index:index + 2]

    if hub_name and "-n" not in args:
        args += ["-n", hub_name]
    if "--auth-type" not in args:
        args += ["--auth-type", "login"]

    return args


@pytest.fixture(autouse=True)
def _iothub_data_plane_auth(monkeypatch):
    if os.environ.get("IOTHUB_AUTH_TYPE", "").lower() != "login":
        return

    original = AzureCli.invoke_az_cli_outproc

    def wrapped(self, args, *pargs, **kwargs):
        return original(self, _rewrite_args(args), *pargs, **kwargs)

    monkeypatch.setattr(AzureCli, "invoke_az_cli_outproc", wrapped)
