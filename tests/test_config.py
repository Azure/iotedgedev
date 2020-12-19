import os

import pytest

from .version import test_py2, minversion

if not test_py2:
    from iotedgedev.telemetryconfig import TelemetryConfig

pytestmark = pytest.mark.unit

@minversion
def test_firsttime(request):
    config = TelemetryConfig()

    def clean():
        config_path = config.get_config_path()
        if os.path.exists(config_path):
            os.remove(config_path)
    request.addfinalizer(clean)

    clean()
    config = TelemetryConfig()

    assert config.get(config.DEFAULT_DIRECT, config.FIRSTTIME_SECTION) == 'yes'
    assert config.get(config.DEFAULT_DIRECT, config.TELEMETRY_SECTION) is None

    config.check_firsttime()

    assert config.get(config.DEFAULT_DIRECT, config.FIRSTTIME_SECTION) == 'no'
    assert config.get(config.DEFAULT_DIRECT, config.TELEMETRY_SECTION) == 'yes'
