import re
import pytest
from typer.testing import CliRunner
from src.helpers.controller import app, command_args
from hypothesis import given, strategies as st


@pytest.fixture(autouse=True)
def reset_command_args():
    command_args.clear()
    yield
    command_args.clear()


runner = CliRunner()


def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r"\x1b\[([0-9;]*[mK])")
    return ansi_escape.sub("", text)


def test_run_chapy_with_no_args():
    result = runner.invoke(app)
    output = remove_ansi_escape_sequences(result.output)
    assert result.exit_code == 2
    assert "Try 'root --help' for help." in output
    assert "Missing command." in output


def test_pass_incorrect_option():
    result = runner.invoke(app, ["--activate"])
    output = remove_ansi_escape_sequences(result.output)
    assert result.exit_code == 2
    assert "No such option: --activate" in output


def test_pass_incorrect_command():
    result = runner.invoke(app, ["activate"])
    assert result.exit_code == 2
    assert "No such command 'activate'" in result.output


def test_pass_command_as_option():
    result = runner.invoke(app, ["--generate"])
    output = remove_ansi_escape_sequences(result.output)
    assert result.exit_code == 2
    assert "No such option: --generate" in output


def test_pass_option_as_command():
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 2
    assert "No such command 'help'" in result.output


def test_run_chapy_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "This script generate and test code on some platforms" in result.output
    assert "Options" in result.output
    assert "Commands" in result.output


@pytest.mark.parametrize("command", ["generate", "analyze", "summarize", "aggregate"])
def test_run_utility_help(command):
    result = runner.invoke(app, [command, "--help"])
    assert result.exit_code == 0
    assert "Usage: " in result.output
    assert command in result.output
    assert "Options" in result.output
    assert "Commands" not in result.output


@pytest.mark.parametrize("command", ["generate", "analyze", "summarize", "aggregate"])
def test_pass_incorrect_type_log_level(command):
    result = runner.invoke(app, [command, "--log-level", "OTHER"])
    output = remove_ansi_escape_sequences(result.output)
    assert result.exit_code == 2
    assert "Error" in output
    assert "Invalid value for '--log-level': 'OTHER' is not one of" in output


def test_run_generate_with_default_options():
    runner.invoke(app, ["generate"])
    assert command_args["utility"] == "generate"
    assert command_args["out_dir"] == "chapy-tests"
    assert command_args["repeats"] == 1
    assert command_args["log_level"] == "WARNING"


@given(
    repeats=st.integers(min_value=1, max_value=100),
    out_dir=st.text(min_size=1, max_size=20),
    log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]),
)
def test_run_generate_with_custom_options(repeats, out_dir, log_level):
    runner.invoke(app, ["generate", "--out-dir", out_dir, "--repeats", repeats, "--log-level", log_level])
    assert command_args["utility"] == "generate"
    assert command_args["out_dir"] == out_dir
    assert command_args["repeats"] == repeats
    assert command_args["log_level"] == log_level


def test_generate_pass_incorrect_type_repeats():
    result = runner.invoke(app, ["generate", "--repeats", "not_int"])
    output = remove_ansi_escape_sequences(result.output)
    assert result.exit_code == 2
    assert "Error" in output
    assert "Invalid value for '--repeats': 'not_int' is not a valid integer." in output


def test_run_analyze_with_default_options():
    runner.invoke(app, ["analyze"])
    assert command_args["utility"] == "analyze"
    assert command_args["config_file"] is None
    assert command_args["out_dir"] == "analyze"
    assert command_args["test_dir"] == "chapy-tests"
    assert command_args["timeout"] == 10
    assert command_args["compiler"] == "gcc"
    assert command_args["compiler_args"] == ""
    assert command_args["profiler"] == "perf"
    assert command_args["gem5_home"] == "./"
    assert command_args["gem5_bin"] == "./"
    assert command_args["target_isa"] == ""
    assert command_args["sim_script"] == "./"
    assert command_args["log_level"] == "WARNING"


def test_analyze_pass_incorrect_profiler():
    result = runner.invoke(app, ["analyze", "--profiler", "OTHER"])
    output = remove_ansi_escape_sequences(result.output)
    assert result.exit_code == 2
    assert "Error" in output
    assert "Invalid value for '--profiler': 'OTHER' is not one of" in output


def test_run_summarize_with_default_options():
    runner.invoke(app, ["summarize"])
    assert command_args["utility"] == "summarize"
    assert command_args["src_dirs"] is None
    assert command_args["out_dir"] == "summarize"
    assert command_args["no_show_graph"] is False
    assert command_args["no_save_graph"] is False
    assert command_args["log_level"] == "WARNING"


def test_summarize_pass_incorrect_bool_option():
    result = runner.invoke(app, ["summarize", "--no-show-graph", "True"])
    assert result.exit_code == 2
    assert "Error" in result.output
    assert "No such command 'True'." in result.output


def test_summarize_pass_correct_bool_option():
    runner.invoke(app, ["summarize", "--no-show-graph"])
    assert command_args["no_show_graph"] is True


def test_run_aggregate_with_default_options():
    runner.invoke(app, ["aggregate"])
    assert command_args["utility"] == "aggregate"
    assert command_args["config_file"] == "config.json"
    assert command_args["section_in_config"] == "DEFAULT"
    assert command_args["dest_dir"] == "out"
    assert command_args["async_analyze"] is False
    assert command_args["log_level"] == "WARNING"
