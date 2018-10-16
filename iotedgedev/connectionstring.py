from .utility import Utility


class ConnectionString:
    def __init__(self, value):
        self.connection_string = value
        self.data = dict()

        if self.connection_string:
            parts = self.connection_string.split(';')
            if len(parts) > 0:
                for part in parts:
                    subpart = part.split('=', 1)
                    if len(subpart) == 2:
                        self.data[subpart[0].lower()] = subpart[1].strip()

            if self.data:
                self.iothub_host = IoTHubHost(self["hostname"])
                self.shared_access_key = self["sharedaccesskey"]

    def __getitem__(self, key):
        return self.data[key]


class IoTHubConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        if self.connection_string:
            self.shared_access_key_name = self["sharedaccesskeyname"]


class DeviceConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        if self.connection_string:
            self.device_id = self["deviceid"]


class IoTHubHost:
    def __init__(self, hostname):
        self.name = hostname
        if self.name and "." in self.name:
            self.hub_name = self.name.split('.')[0]
            # get connection string hostname hash to count distint IoT Hub number
            self.name_hash = Utility.get_sha256_hash(self.name)
            # get hostname suffix (e.g., azure-devices.net) to distinguish national clouds
            self.name_suffix = self.name[self.name.index(".")+1:]
        else:
            self.hub_name = ""
            self.name_hash = ""
            self.name_suffix = ""
