import logging

import pytest
from hypothesis import settings, HealthCheck, given, strategies as st

from src.cli.generate import Generate


def test_init_sets_attributes_to_none():
    generator_instance = Generate()
    assert generator_instance.settings is None
    assert generator_instance.repeats is None
    assert generator_instance.out_dir is None


@given(rep=st.integers())
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_configurate_with_different_repeats_type(tmp_path, rep):
    generator_instance = Generate()
    settings = {"utility": "generate", "out_dir": tmp_path, "repeats": rep, "log_level": logging.INFO}
    generator_instance.configurate(settings)
    assert generator_instance.settings == settings
    assert generator_instance.logger.level == logging.INFO
    assert generator_instance.out_dir == tmp_path
    assert generator_instance.repeats == rep


def test_configurate_with_missing_settings():
    generator_instance = Generate()
    settings = {"log_level": "INFO"}  # missing out_dir, and repeats
    with pytest.raises(KeyError):
        generator_instance.configurate(settings)
