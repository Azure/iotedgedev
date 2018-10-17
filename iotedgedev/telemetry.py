import datetime
import json
import os
import platform
import subprocess
import sys
import uuid
from collections import defaultdict
from functools import wraps

from . import telemetryuploader
from .telemetryconfig import TelemetryConfig
from .decorators import hash256_result, suppress_all_exceptions

PRODUCT_NAME = 'iotedgedev'


class TelemetrySession(object):
    def __init__(self, correlation_id=None):
        self.start_time = None
        self.end_time = None
        self.correlation_id = correlation_id or str(uuid.uuid4())
        self.command = 'command_name'
        self.parameters = []
        self.result = 'None'
        self.result_summary = None
        self.exception = None
        self.extra_props = {}
        self.machineId = self._get_hash_mac_address()
        self.events = defaultdict(list)

    def generate_payload(self):
        props = {
            'EventId': str(uuid.uuid4()),
            'CorrelationId': self.correlation_id,
            'MachineId': self.machineId,
            'ProductName': PRODUCT_NAME,
            'ProductVersion': _get_core_version(),
            'CommandName': self.command,
            'OS.Type': platform.system().lower(),
            'OS.Version': platform.version().lower(),
            'Result': self.result,
            'StartTime': str(self.start_time),
            'EndTime': str(self.end_time),
            'Parameters': ','.join(self.parameters)
        }

        if self.result_summary:
            props['ResultSummary'] = self.result_summary

        if self.exception:
            props['Exception'] = self.exception

        props.update(self.extra_props)

        self.events[_get_AI_key()].append({
            'name': '{}/command'.format(PRODUCT_NAME),
            'properties': props
        })

        payload = json.dumps(self.events)
        return _remove_symbols(payload)

    @suppress_all_exceptions()
    @hash256_result
    def _get_hash_mac_address(self):
        s = ''
        for index, c in enumerate(hex(uuid.getnode())[2:].upper()):
            s += c
            if index % 2:
                s += '-'

        s = s.strip('-')
        return s


_session = TelemetrySession()


def _user_agrees_to_telemetry(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        config = TelemetryConfig()
        if not config.get_boolean(config.DEFAULT_DIRECT, config.TELEMETRY_SECTION):
            return None
        return func(*args, **kwargs)

    return _wrapper


@suppress_all_exceptions()
def start(cmdname, params=[]):
    _session.command = cmdname
    _session.start_time = datetime.datetime.utcnow()
    if params is not None:
        _session.parameters.extend(params)


@suppress_all_exceptions()
def success():
    _session.result = 'Success'


@suppress_all_exceptions()
def fail(exception, summary):
    _session.exception = exception
    _session.result = 'Fail'
    _session.result_summary = summary


@suppress_all_exceptions()
def add_extra_props(props):
    if props is not None:
        _session.extra_props.update(props)


@_user_agrees_to_telemetry
@suppress_all_exceptions()
def flush():
    # flush out current information
    _session.end_time = datetime.datetime.utcnow()

    payload = _session.generate_payload()
    if payload:
        _upload_telemetry_with_user_agreement(payload)

    # reset session fields, retaining correlation id and application
    _session.__init__(correlation_id=_session.correlation_id)


@suppress_all_exceptions(fallback_return=None)
def _get_core_version():
    from iotedgedev import __version__ as core_version
    return core_version


@suppress_all_exceptions()
def _get_AI_key():
    from iotedgedev import __AIkey__ as key
    return key


# This includes a final user-agreement-check; ALL methods sending telemetry MUST call this.
@_user_agrees_to_telemetry
@suppress_all_exceptions()
def _upload_telemetry_with_user_agreement(payload, **kwargs):
    # Call telemetry uploader as a subprocess to prevent blocking iotedgedev process
    subprocess.Popen([sys.executable, os.path.realpath(telemetryuploader.__file__), payload], **kwargs)


def _remove_symbols(s):
    if isinstance(s, str):
        for c in '$%^&|':
            s = s.replace(c, '_')
    return s
