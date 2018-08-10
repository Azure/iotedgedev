import os

import pytest

from iotedgedev.config import Config

pytestmark = pytest.mark.unit


def test_firsttime(request):
    config = Config()

    def clean():
        config_path = config.get_config_path()
        if os.path.exists(config_path):
            os.remove(config_path)
    request.addfinalizer(clean)

    clean()
    config = Config()

    assert config.get(config.DEFAULT_DIRECT, config.FIRSTTIME_SECTION) == 'yes'
    assert config.get(config.DEFAULT_DIRECT, config.TELEMETRY_SECTION) is None

    config.check_firsttime()

    assert config.get(config.DEFAULT_DIRECT, config.FIRSTTIME_SECTION) == 'no'
    assert config.get(config.DEFAULT_DIRECT, config.TELEMETRY_SECTION) == 'yes'
