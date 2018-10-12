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
                if self.HostName and "." in self.HostName:
                    self.HubName = self.HostName.split('.')[0]
                    # get connection string hostname hash to count distint IoT Hub number
                    self.HostNameHashed = Utility.get_sha256_hash(self.HostName)
                    # get hostname suffix (e.g., azure-devices.net) to distinguish national clouds
                    self.HostNameSuffix = self.HostName[self.HostName.index(".")+1:]
                else:
                    self.HubName = ""
                    self.HostNameHashed = ""
                    self.HostNameSuffix = ""
                self.SharedAccessKey = self["sharedaccesskey"]

    def __getitem__(self, key):
        return self.data[key]


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
