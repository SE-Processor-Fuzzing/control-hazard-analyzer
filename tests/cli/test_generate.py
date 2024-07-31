import logging
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, call
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


@st.composite
def temp_path_strategy(draw):
    temp_dir = tempfile.mkdtemp()
    path_name = draw(
        st.text(min_size=1, alphabet=st.characters(blacklist_characters="/", blacklist_categories={"Cc", "Cs"}))
    )
    return Path(temp_dir) / path_name


@given(temp_path_strategy())
def test_create_empty_dir_when_not_exist(temp_path):
    generator_instance = Generate()

    if temp_path.exists():
        shutil.rmtree(temp_path)

    generator_instance.create_empty_dir(temp_path)

    assert temp_path.exists()
    assert temp_path.is_dir()
    assert not any(temp_path.iterdir())


@given(temp_path_strategy())
def test_create_empty_dir_when_exist(temp_path):
    generator_instance = Generate()

    temp_path.mkdir(parents=True, exist_ok=True)

    (temp_path / "test_file.txt").touch()
    (temp_path / "sub_dir").mkdir()

    generator_instance.create_empty_dir(temp_path)

    assert temp_path.exists()
    assert temp_path.is_dir()
    assert not any(temp_path.iterdir())  # Directory should be empty


@st.composite
def generate_params_strategy(draw):
    target_dir = draw(st.builds(Path, st.text(min_size=1)))
    count = draw(st.integers(min_value=1, max_value=10))
    return target_dir, count


@given(generate_params_strategy())
def test_generate_tests(params):
    target_dir, count = params
    max_depth = 6  # constant value
    generator = Generate()

    with patch.object(generator, "_generate_test") as mock_generate_test, patch("builtins.print") as mock_print:
        generator.generate_tests(target_dir, count)

        mock_print.assert_called_once_with(f"[+]: Generate tests to '{target_dir.absolute()}'")

        expected_calls = [call(target_dir.joinpath(f"test_{i}.c"), max_depth) for i in range(count)]
        mock_generate_test.assert_has_calls(expected_calls, any_order=False)


def test_generate_test_not_a_file(caplog):
    generator = Generate()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        generator._generate_test(temp_path, 6)

        assert f"Provided path {temp_path} is not a file. Skipping this test." in caplog.text


def test_generate_test_is_a_file(caplog):
    generator = Generate()
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / "test_file.c"
        temp_path.touch()

        generator._generate_test(temp_path, 6)
        assert f"Write test into {temp_path}" in caplog.text
        with open(temp_path, "r") as f:
            assert f.read() != ""


def test_run_without_outdir_and_repeats(caplog):
    generator = Generate()  # out_dir and repeats are not configured

    generator.run()
    assert "Out dir or repeats values are not provided. Exiting..." in caplog.text


def test_run_with_correct_params(caplog):
    generator = Generate()
    generator.out_dir = Path("/tmp/test_out_dir")
    generator.repeats = 10

    with patch.object(generator, "create_empty_dir") as mock_create_empty_dir, patch.object(
        generator, "generate_tests"
    ) as mock_generate_tests:

        generator.run()

        mock_create_empty_dir.assert_called_once_with(generator.out_dir)
        mock_generate_tests.assert_called_once_with(generator.out_dir, generator.repeats)
