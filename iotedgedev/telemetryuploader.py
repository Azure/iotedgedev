import json
import sys

from applicationinsights import TelemetryClient
from applicationinsights.channel import (SynchronousQueue, SynchronousSender,
                                         TelemetryChannel)
from applicationinsights.exceptions import enable
from urllib.request import Request, urlopen

from iotedgedev.decorators import suppress_all_exceptions


class LimitedRetrySender(SynchronousSender):
    def __init__(self):
        super(LimitedRetrySender, self).__init__()

    def send(self, data_to_send):
        """ Override the default resend mechanism in SenderBase. Stop resend when it fails."""
        request_payload = json.dumps([a.write() for a in data_to_send])

        req = Request(self._service_endpoint_uri, bytearray(request_payload, 'utf-8'),
                      {'Accept': 'application/json', 'Content-Type': 'application/json; charset=utf-8'})
        try:
            urlopen(req, timeout=10)
        except Exception:
            pass


@suppress_all_exceptions()
def upload(data_to_save):
    data_to_save = json.loads(data_to_save)

    for instrumentation_key in data_to_save:
        client = TelemetryClient(instrumentation_key=instrumentation_key,
                                 telemetry_channel=TelemetryChannel(queue=SynchronousQueue(LimitedRetrySender())))
        enable(instrumentation_key)
        for record in data_to_save[instrumentation_key]:
            name = record['name']
            raw_properties = record['properties']
            properties = {}
            measurements = {}
            for k, v in raw_properties.items():
                if isinstance(v, str):
                    properties[k] = v
                else:
                    measurements[k] = v
            client.track_event(name, properties, measurements)
        client.flush()


if __name__ == '__main__':
    # If user doesn't agree to upload telemetry, this scripts won't be executed. The caller should control.
    upload(sys.argv[1])
