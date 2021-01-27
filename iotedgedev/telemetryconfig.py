import os

import configparser

from .decorators import suppress_all_exceptions

PRIVACY_STATEMENT = """
Welcome to iotedgedev!
-------------------------
Telemetry
---------
The iotedgedev collects usage data in order to improve your experience.
The data is anonymous and does not include commandline argument values.
The data is collected by Microsoft.

You can change your telemetry settings by updating '{0}' to 'no' in {1}
"""


class TelemetryConfig(object):
    DEFAULT_DIRECT = 'DEFAULT'
    FIRSTTIME_SECTION = 'firsttime'
    TELEMETRY_SECTION = 'collect_telemetry'

    def __init__(self):
        self.config_parser = configparser.ConfigParser({
            self.FIRSTTIME_SECTION: 'yes'
        })
        self.setup()

    @suppress_all_exceptions()
    def setup(self):
        config_path = self.get_config_path()
        config_folder = os.path.dirname(config_path)
        if not os.path.exists(config_folder):
            os.makedirs(config_folder)
        if not os.path.exists(config_path):
            self.dump()
        else:
            self.load()
            self.dump()

    @suppress_all_exceptions()
    def load(self):
        with open(self.get_config_path(), 'r') as f:
            if hasattr(self.config_parser, 'read_file'):
                self.config_parser.read_file(f)

    @suppress_all_exceptions()
    def dump(self):
        with open(self.get_config_path(), 'w') as f:
            self.config_parser.write(f)

    @suppress_all_exceptions()
    def get(self, direct, section):
        return self.config_parser.get(direct, section)

    @suppress_all_exceptions()
    def get_boolean(self, direct, section):
        return self.config_parser.getboolean(direct, section)

    @suppress_all_exceptions()
    def set(self, direct, section, val):
        if val is not None:
            self.config_parser.set(direct, section, val)
            self.dump()

    @suppress_all_exceptions()
    def check_firsttime(self):
        if self.get(self.DEFAULT_DIRECT, self.FIRSTTIME_SECTION) != 'no':
            self.set(self.DEFAULT_DIRECT, self.FIRSTTIME_SECTION, 'no')
            print(PRIVACY_STATEMENT.format(self.TELEMETRY_SECTION, self.get_config_path()))
            self.set(self.DEFAULT_DIRECT, self.TELEMETRY_SECTION, 'yes')
            self.dump()

    @suppress_all_exceptions()
    def get_config_path(self):
        config_folder = self.get_config_folder()
        if config_folder:
            return os.path.join(config_folder, 'setting.ini')
        return None

    @suppress_all_exceptions()
    def get_config_folder(self):
        return os.path.join(os.path.expanduser("~"), '.iotedgedev')
