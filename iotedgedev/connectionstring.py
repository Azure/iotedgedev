from .utility import Utility


class ConnectionString:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
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
                self.shared_access_key = None
                if("sharedaccesskey" in self.data):
                    self.shared_access_key = self["sharedaccesskey"]
                else:
                    # unexpected input of connection. Set to None and throw error
                    self.connection_string = None

    def __getitem__(self, key):
        return self.data[key]


class IoTHubConnectionString(ConnectionString):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)

        if self.connection_string:
            self.shared_access_key_name = self["sharedaccesskeyname"]


class DeviceConnectionString(ConnectionString):
    def __init__(self, connection_string: str):
        super().__init__(connection_string)

        if("deviceid" in self.data):
            self.device_id = self["deviceid"]
        else:
            self.device_id = None


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
