from .decorators import suppress_all_exceptions
from .utility import Utility


class ConnectionString:
    def __init__(self, value):
        self.ConnectionString = value
        self.data = dict()

        if self.ConnectionString:
            parts = self.ConnectionString.split(';')
            if len(parts) > 0:
                for part in parts:
                    subpart = part.split('=', 1)
                    if len(subpart) == 2:
                        self.data[subpart[0].lower()] = subpart[1].strip()

            if self.data:
                self.HostName = self["hostname"]
                if self.HostName:
                    self.HubName = self.HostName.split('.')[0]
                self.SharedAccessKey = self["sharedaccesskey"]

    def __getitem__(self, key):
        return self.data[key]

    @suppress_all_exceptions()
    def hash_hostname(self):
        """Get connection string hostname hash and suffix to count distint IoT Hub number"""
        if not self.data or not self.HostName:
            return ("", "")

        hostname = self.HostName

        # get hostname suffix (e.g., azure-devices.net) to distinguish national clouds
        if "." in hostname:
            hostname_suffix = hostname[hostname.index(".")+1:]
        else:
            hostname_suffix = ""

        return (Utility.get_sha256_hash(hostname), hostname_suffix)


class IoTHubConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        if self.ConnectionString:
            self.SharedAccessKeyName = self["sharedaccesskeyname"]


class DeviceConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        if self.ConnectionString:
            self.DeviceId = self["deviceid"]
