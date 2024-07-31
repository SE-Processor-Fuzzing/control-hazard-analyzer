import pytest
from hypothesis import settings, HealthCheck, given, strategies as st
import logging
from src.cli.summarize import Summarize

import numpy as np
import pandas as pd
from pandas import DataFrame

import json
from pathlib import Path


@pytest.fixture
def summarizer_instance():
    summarizer_instance = Summarize()
    settings = {}
    settings["utility"] = "summarize"
    settings["src_dirs"] = ["src_dirs"]
    settings["out_dir"] = "out_dir"
    settings["no_show_graph"] = False
    settings["no_save_graph"] = False
    settings["log_level"] = logging.INFO
    summarizer_instance.configurate(settings)
    return summarizer_instance


def test_init():
    summarizer_instance = Summarize()
    assert summarizer_instance.filename_out_grapg == "graph.png"
    assert summarizer_instance.filename_out_data == "results.data"


def test_configurate(tmp_path):
    summarizer_instance = Summarize()
    settings = {}
    settings["utility"] = "summarize"
    settings["src_dirs"] = ["src_dirs"]
    settings["out_dir"] = tmp_path.as_posix() + "/out_dir"
    settings["no_show_graph"] = False
    settings["no_save_graph"] = False
    settings["log_level"] = logging.INFO
    summarizer_instance.configurate(settings)
    assert summarizer_instance.settings == settings
    assert summarizer_instance.logger.level == logging.INFO


def create_perf_like_data(
    path,
    filename="test_file.data",
    lookups=0,
    condIncorrect=0,
    condCorrect=0,
    BTBUpdates=0,
    simTicks=0,
    instructions=0,
    isFull=True,
):
    doc = path / filename
    doc.write_text(
        json.dumps(
            {
                "branchPred.lookups": lookups,
                "branchPred.condIncorrect": condIncorrect,
                "branchPred.condCorrect": condCorrect,
                "branchPred.BTBUpdates": BTBUpdates,
                "simTicks": simTicks,
                "instructions": instructions,
                "isFull": isFull,
            }
        )
    )
    return doc


def test_get_data_from_sources_empty_dir(summarizer_instance, tmp_path):
    # caplog.set_level(logging.CRITICAL, logger="root.baz")
    dir = tmp_path / "src_dir"
    dir.mkdir()
    data = summarizer_instance.get_data_from_sources([dir])

    assert len(data) == 0


def test_get_data_from_sources_two_empty_dirs(summarizer_instance, tmp_path):
    dir = tmp_path / "src_dir"
    dir.mkdir()
    dir1 = dir / "dir1"
    dir1.mkdir()
    dir2 = dir / "dir2"
    dir2.mkdir()
    data = summarizer_instance.get_data_from_sources([dir1, dir2])

    assert len(data) == 0


def test_get_data_from_sources_one_source(tmp_path):
    summarizer_instance = Summarize()
    dir = tmp_path / "src_dir"
    dir.mkdir()
    create_perf_like_data(path=dir, filename="test_file.data")
    gotten_data = summarizer_instance.get_data_from_sources([dir])
    assert len(gotten_data) == 1
    assert dir.as_posix() in gotten_data.keys()


def test_get_data_from_sources_two_scources_in_one_dir(tmp_path):
    summarizer_instance = Summarize()
    dir = tmp_path / "src_dir"
    dir.mkdir()
    create_perf_like_data(path=dir, filename="test_file1.data")
    create_perf_like_data(path=dir, filename="test_file2.data")
    gotten_data = summarizer_instance.get_data_from_sources([dir])
    assert len(gotten_data) == 1
    assert dir.as_posix() in gotten_data.keys()
    assert len(gotten_data[dir.as_posix()]) == 2
    assert "test_file1" in gotten_data[dir.as_posix()]
    assert "test_file2" in gotten_data[dir.as_posix()]


def test_get_data_from_sources_one_source_one_empty_dir(tmp_path):
    summarizer_instance = Summarize()
    dir = tmp_path / "src_dir"
    dir.mkdir()
    dir1 = dir / "dir1"
    dir1.mkdir()
    dir2 = dir / "dir2"
    dir2.mkdir()
    create_perf_like_data(path=dir1, filename="test_file1.data")
    gotten_data = summarizer_instance.get_data_from_sources([dir1, dir2])
    assert len(gotten_data) == 1


@given(
    lookups=st.integers(min_value=0),
    condIncorrect=st.integers(min_value=0),
    condCorrect=st.integers(min_value=0),
    BTBUpdates=st.integers(min_value=0),
    simTicks=st.integers(min_value=0),
    instructions=st.integers(min_value=0),
    isFull=st.booleans(),
)
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_prepare_data(
    tmp_path,
    lookups,
    condIncorrect,
    condCorrect,
    BTBUpdates,
    simTicks,
    instructions,
    isFull,
):
    summarizer_instance = Summarize()
    dir = tmp_path / "src_dir"
    dir.mkdir()
    data = create_perf_like_data(
        path=dir,
        filename="test_file.data",
        lookups=lookups,
        condIncorrect=condIncorrect,
        condCorrect=condCorrect,
        BTBUpdates=BTBUpdates,
        simTicks=simTicks,
        instructions=instructions,
        isFull=isFull,
    )
    gotten_data = summarizer_instance.get_data_from_sources([dir])
    prepared_data = summarizer_instance.prepare_data(gotten_data)

    data.unlink()
    dir.rmdir()
    assert prepared_data[dir.as_posix()]["test_file"]["Number of ticks"] == simTicks
    assert prepared_data[dir.as_posix()]["test_file"]["BP lookups"] == lookups
    assert prepared_data[dir.as_posix()]["test_file"]["Ticks per BP"] == round(
        simTicks / float(lookups) if lookups != 0 else 0, 2
    )
    assert prepared_data[dir.as_posix()]["test_file"]["BP incorrect"] == condIncorrect
    assert prepared_data[dir.as_posix()]["test_file"]["BP incorrect %"] == round(
        condIncorrect / float(lookups) * 100 if lookups != 0 else 0, 2
    )
    assert prepared_data[dir.as_posix()]["test_file"]["Full launch"] == isFull


def create_prepared_data(
    num_dirs=1,
    num_files_per_dir=1,
    sim_ticks=10,
    bp_lookups=9,
    ticks_per_bp=8,
    bp_incorrect=7,
    bp_incorrect_percent=6.0,
    is_full=True,
):
    prepared_data = {}
    for dir_index in range(num_dirs):
        dir_name = f"/path/to/dir{dir_index}"
        prepared_data[dir_name] = {}
        for file_index in range(num_files_per_dir):
            file_name = f"test{file_index}"
            prepared_data[dir_name][file_name] = {
                "Number of ticks": sim_ticks,
                "BP lookups": bp_lookups,
                "Ticks per BP": ticks_per_bp,
                "BP incorrect": bp_incorrect,
                "BP incorrect %": bp_incorrect_percent,
                "Full launch": is_full,
            }
    return prepared_data


@given(
    sim_ticks=st.integers(min_value=0),
    bp_lookups=st.integers(min_value=0),
    condCorrect=st.integers(min_value=0),
    ticks_per_bp=st.integers(min_value=0),
    bp_incorrect=st.integers(min_value=0),
    bp_incorrect_percent=st.decimals(min_value=0, max_value=100),
    isFull=st.booleans(),
)
def test_convert_to_pandas_single_file(
    sim_ticks,
    bp_lookups,
    condCorrect,
    ticks_per_bp,
    bp_incorrect,
    bp_incorrect_percent,
    isFull,
):
    summarizer_instance = Summarize()
    data = create_prepared_data(
        1,
        1,
        sim_ticks,
        bp_lookups,
        ticks_per_bp,
        bp_incorrect,
        bp_incorrect_percent,
        isFull,
    )
    df = summarizer_instance.convert_to_pandas(data)

    dir_name = list(data.keys())[0]
    file_name = list(data[dir_name].keys())[0]
    expected_df = pd.DataFrame(
        {
            "Number of ticks": [data[dir_name][file_name]["Number of ticks"]],
            "BP lookups": [data[dir_name][file_name]["BP lookups"]],
            "Ticks per BP": [data[dir_name][file_name]["Ticks per BP"]],
            "BP incorrect": [data[dir_name][file_name]["BP incorrect"]],
            "BP incorrect %": [data[dir_name][file_name]["BP incorrect %"]],
            "Full launch": [data[dir_name][file_name]["Full launch"]],
        },
        index=pd.MultiIndex.from_tuples([(dir_name, file_name)], names=["dir", "test"]),
    )
    assert df.values.tolist() == expected_df.values.tolist()


@given(
    bp_lookups=st.integers(min_value=1),
    bp_incorrect=st.integers(min_value=1),
)
def test_calculate_mean_of_dir(bp_lookups, bp_incorrect):
    summarizer_instance = Summarize()
    data = create_prepared_data(2, 2, bp_lookups=bp_lookups, bp_incorrect=bp_incorrect)
    df = summarizer_instance.convert_to_pandas(data)
    mean_data = summarizer_instance.calculate_mean_of_dir(df)
    expected_mean_data = DataFrame(
        {
            "dir1": {"BP incorrect %": round(bp_incorrect / bp_lookups * 100, 2)},
            "dir2": {"BP incorrect %": round(bp_incorrect / bp_lookups * 100, 2)},
        }
    )
    assert mean_data.values.tolist() == expected_mean_data.values.tolist()


def test_calculate_mean_of_dir_with_zero_issue():
    summarizer_instance = Summarize()
    data = create_prepared_data(2, 2, bp_lookups=0, bp_incorrect=0)
    df = summarizer_instance.convert_to_pandas(data)
    mean_data = summarizer_instance.calculate_mean_of_dir(df)
    expected_mean_data = DataFrame(
        {
            "dir1": {"BP incorrect %": 0},
            "dir2": {"BP incorrect %": 0},
        }
    )
    assert mean_data.values.tolist() == expected_mean_data.values.tolist()


def test_calculate_mean_of_dir_with_nan_issue():
    summarizer_instance = Summarize()
    data = create_prepared_data(2, 2, bp_lookups=np.nan, bp_incorrect=np.nan)
    df = summarizer_instance.convert_to_pandas(data)
    mean_data = summarizer_instance.calculate_mean_of_dir(df)
    expected_mean_data = DataFrame(
        {
            "dir1": {"BP incorrect %": 0},
            "dir2": {"BP incorrect %": 0},
        }
    )
    assert mean_data.values.tolist() == expected_mean_data.values.tolist()


def test_save_mean_data(tmp_path):
    summarizer_instance = Summarize()
    data = create_prepared_data(1, 2)
    df = summarizer_instance.convert_to_pandas(data)
    mean_data = summarizer_instance.calculate_mean_of_dir(df)

    src_dirs = [Path("/dir1"), Path("/dir2")]
    out_dir = tmp_path / "output"
    out_dir.mkdir()

    summarizer_instance.save_mean_data(mean_data, src_dirs, out_dir)

    output_file = out_dir / summarizer_instance.filename_out_data
    assert output_file.exists()

    with open(output_file, "r") as f:
        content = f.read()
        assert "Summarized data:" in content
        assert "dir: /dir1" in content
        assert "dir: /dir2" in content
