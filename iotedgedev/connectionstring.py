class ConnectionString:
    def __init__(self, value):
        self.value = value
        self.data = dict()

        if self.value: 
            parts = value.split(';')
            if len(parts) > 0:
                for part in parts:
                    subpart = part.split('=', 1)
                    if len(subpart) == 2:
                        self.data[subpart[0].lower()] = subpart[1].strip()

            if self.data:
                self.HostName = self["hostname"]
                self.SharedAccessKey = self["sharedaccesskey"]

    def __getitem__(self, key):
        return self.data[key]


class IoTHubConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        if self.value:
            self.SharedAccessKeyName = self["sharedaccesskeyname"]


class DeviceConnectionString(ConnectionString):
    def __init__(self, value):
        ConnectionString.__init__(self, value)

        if self.value:
            self.DeviceId = self["deviceid"]
