import logging
from pathlib import Path

import pytest

from src.cli.analyze import Analyze
from src.analyzers.gemAnalyzer import GemAnalyzer
from src.analyzers.perfAnalyzer import PerfAnalyzer
from src.helpers.packer import Packer


def test_init_sets_attributes_to_none():
    analyzer_instance = Analyze()
    assert analyzer_instance.analyzer is None
    assert analyzer_instance.packer is None
    assert analyzer_instance.builder is None
    assert analyzer_instance.test_dir is None
    assert analyzer_instance.analyze_dir is None
    assert analyzer_instance.settings is None


def test_configurate(tmp_path):
    analyzer_instance = Analyze()
    settings = {}
    settings["utility"] = "analyze"
    settings["config_file"] = "config.json"
    settings["out_dir"] = tmp_path.as_posix() + "/out_dir"
    settings["test_dir"] = tmp_path.as_posix() + "/test_dir"
    settings["timeout"] = 10
    settings["compiler"] = "gcc"
    settings["compiler_args"] = ""  # might need additional tests
    settings["profiler"] = "gem5"
    settings["gem5_home"] = "./"
    settings["gem5_bin"] = "./"
    settings["target_isa"] = "X86"
    settings["sim_script"] = "./"
    settings["log_level"] = logging.INFO
    analyzer_instance.configurate(settings)

    assert analyzer_instance.settings == settings
    assert isinstance(analyzer_instance.packer, Packer)
    assert analyzer_instance.logger.level == logging.INFO
    assert analyzer_instance.test_dir == Path(settings["test_dir"])
    assert analyzer_instance.analyze_dir == Path(settings["out_dir"])


def test_configurate_with_gem5_analyzer(tmp_path):
    analyzer_instance = Analyze()
    settings = {}
    settings["utility"] = "analyze"
    settings["config_file"] = "config.json"
    settings["out_dir"] = tmp_path.as_posix() + "/out_dir"
    settings["test_dir"] = tmp_path.as_posix() + "/test_dir"
    settings["timeout"] = 10
    settings["compiler"] = "gcc"
    settings["compiler_args"] = ""
    settings["profiler"] = "gem5"
    settings["gem5_home"] = "./"
    settings["gem5_bin"] = "./"
    settings["target_isa"] = "X86"
    settings["sim_script"] = "./"
    settings["log_level"] = logging.INFO
    analyzer_instance.configurate(settings)
    assert isinstance(analyzer_instance.analyzer, GemAnalyzer)


def test_configurate_with_perf_analyzer(tmp_path):
    analyzer_instance = Analyze()
    settings = {}
    settings["utility"] = "analyze"
    settings["config_file"] = "config.json"
    settings["out_dir"] = tmp_path.as_posix() + "/out_dir"
    settings["test_dir"] = tmp_path.as_posix() + "/test_dir"
    settings["timeout"] = 10
    settings["compiler"] = "gcc"
    settings["compiler_args"] = ""
    settings["profiler"] = "perf"
    settings["gem5_home"] = "./"
    settings["gem5_bin"] = "./"
    settings["target_isa"] = "X86"
    settings["sim_script"] = "./"
    settings["log_level"] = logging.INFO
    analyzer_instance.configurate(settings)
    assert isinstance(analyzer_instance.analyzer, PerfAnalyzer)


# add test via ssh


def test_configurate_with_unknown_analyzer(tmp_path):
    analyzer_instance = Analyze()
    settings = {}
    settings["utility"] = "analyze"
    settings["config_file"] = "config.json"
    settings["out_dir"] = tmp_path.as_posix() + "/out_dir"
    settings["test_dir"] = tmp_path.as_posix() + "/test_dir"
    settings["timeout"] = 10
    settings["compiler"] = "gcc"
    settings["compiler_args"] = ""
    settings["profiler"] = "unknown_analyzer"
    settings["gem5_home"] = "./"
    settings["gem5_bin"] = "./"
    settings["target_isa"] = "X86"
    settings["sim_script"] = "./"
    settings["log_level"] = logging.INFO
    with pytest.raises(Exception) as exc_info:
        analyzer_instance.configurate(settings)
    print("!!!!!!!!!!!")
    print(exc_info.value.args[0])
    assert exc_info.value.args[0] == f'"{settings["profiler"]}" is unknown profiler'


def test_configurate_with_missing_settings():
    analyzer_instance = Analyze()
    settings = {}
    settings["log_level"] = logging.INFO
    with pytest.raises(KeyError):
        analyzer_instance.configurate(settings)


def test_configurate_with_empty_settings():
    analyzer_instance = Analyze()
    settings = {}
    settings["utility"] = ""
    settings["config_file"] = ""
    settings["out_dir"] = ""
    settings["test_dir"] = ""
    settings["timeout"] = 0
    settings["compiler"] = ""
    settings["compiler_args"] = ""
    settings["profiler"] = ""
    settings["gem5_home"] = ""
    settings["gem5_bin"] = ""
    settings["target_isa"] = ""
    settings["sim_script"] = ""
    settings["log_level"] = logging.INFO
    with pytest.raises(Exception):
        analyzer_instance.configurate(settings)
