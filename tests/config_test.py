from ledgerbase import config


def test_config_default():
    assert hasattr(config, "__name__")
