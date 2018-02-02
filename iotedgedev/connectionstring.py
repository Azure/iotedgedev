class ConnectionString:
    def __init__(self, value):
        self.value = value
        self.data = dict()

        parts = value.split(';')
        for part in parts:
            subpart = part.split('=', 1)
            self.data[subpart[0].lower()] = subpart[1].strip()

        self.HostName = self["hostname"]
        self.SharedAccessKey = self["sharedaccesskey"]

    def __getitem__(self, key):
        return self.data[key]


class IoTHubConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        self.SharedAccessKeyName = self["sharedaccesskeyname"]


class DeviceConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        self.DeviceId = self["deviceid"]
