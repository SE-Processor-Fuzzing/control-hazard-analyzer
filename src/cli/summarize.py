import json
import logging
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from pprint import pformat
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.core.api import DataFrame

from src.protocols.collector import DictSI
from src.protocols.subparser import SubParser


class Summarize:
    def __init__(self) -> None:
        self.filename_out_grapg = "graph.png"
        self.filename_out_data = "results.data"
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Namespace) -> None:
        self.settings = settings
        self.logger.setLevel(self.settings.log_level)

    def run(self) -> None:
        self.logger.info("Summarize is running. Settings:")
        self.logger.info(pformat(vars(self.settings)))

        src_dirs: List[str] = self.settings.src_dirs
        data = self.get_data_from_sources(src_dirs)
        if len(data) == 0:
            print("[-]: No data to summarize")
            return

        prepared_data = self.convert_to_pandas(self.prepare_data(data))
        summarized_by_dir = self.summarize_by_dir(prepared_data)
        out_dir = Path(self.settings.out_dir)

        self.save_summarized_data(prepared_data, summarized_by_dir, out_dir)
        self.save_data_for_each_source(prepared_data, summarized_by_dir, src_dirs, out_dir)

        prepared_data = self.filter_summarize_data(prepared_data)
        data_frame_plot = self.construct_plot(prepared_data)
        data_frame_plot = self.sort_data(data_frame_plot)
        data_frame_plot.plot.bar()

        if not self.settings.no_show_graph:
            self.show_plot()

        if not self.settings.no_save_graph:
            self.save_plot(data_frame_plot, out_dir)

    def get_data_from_sources(self, src_dirs: List[str]) -> Dict[str, Dict[str, DictSI]]:
        data: Dict[str, Dict[str, DictSI]] = {}
        for src_dir in src_dirs:
            if not Path(src_dir).exists():
                print(f"[-]: Directory {src_dir} does not exist")
                continue

            data[src_dir] = {}
            for src_file in Path(src_dir).glob("*"):
                with open(src_file, "r") as f:
                    data[src_dir][src_file.stem] = json.loads(f.read())
                for key, val in data[src_dir][src_file.stem].items():
                    data[src_dir][src_file.stem][key] = int(val)

        return data

    def prepare_data(self, data: Dict[str, Dict[str, DictSI]]) -> Dict[str, Dict[str, Dict[str, int | float]]]:

        result: Dict[str, Dict[str, Dict[str, int | float]]] = {src_dir: {} for src_dir in data}
        for src_dir, src_files in data.items():
            for src_file, src_data in src_files.items():
                sim_ticks = src_data.get("simTicks", np.nan)
                bp_lookups = src_data.get("branchPred.lookups", np.nan)
                bp_incorrect = src_data.get("branchPred.condIncorrect", np.nan)
                result[Path(src_dir).as_posix()][Path(src_file).stem] = {
                    "Number of ticks": sim_ticks,
                    "BP lookups": bp_lookups,
                    "Ticks per BP": (
                        round(sim_ticks / float(bp_lookups) if bp_lookups != 0 else 0, 2)
                        if bp_lookups != np.nan and sim_ticks != np.nan
                        else np.nan
                    ),
                    "BP incorrect": bp_incorrect,
                    "BP incorrect %": (
                        round(bp_incorrect / float(bp_lookups) * 100 if bp_lookups != 0 else 0, 2)
                        if bp_lookups != np.nan and bp_incorrect != np.nan
                        else np.nan
                    ),
                }
        return result

    def summarize_by_dir(self, data: DataFrame) -> DataFrame:
        summarized_by_dir: Dict[str, Dict[str, Any]] = {}
        for src_dir in set(data.index.get_level_values(0)):
            summarized_by_dir[src_dir] = {}
            summarized_by_dir[src_dir]["BP incorrect %"] = round(
                data.loc[src_dir, "BP incorrect"].sum()
                / data.loc[src_dir, "BP lookups"].sum()
                * 100,  # pyright: ignore
                2,
            )
        return DataFrame(summarized_by_dir)

    def convert_to_pandas(self, data: Dict[str, Dict[Any, Any]]) -> DataFrame:
        return pd.concat({key: DataFrame(value).T for key, value in data.items()})

    def save_summarized_data(self, summarized_data: DataFrame, summarized_by_dir: DataFrame, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir.joinpath(self.filename_out_data), "w") as f:
            # Use pandas to print data to file
            f.write("Summarized data:\n")
            f.write(summarized_by_dir.to_string())  # pyright: ignore
            f.write("\n\n")
            for src_dir in set(summarized_data.index.get_level_values(0)):
                f.write(f"dir: {src_dir}\n")
                f.write(summarized_data.loc[src_dir].to_string())  # pyright: ignore
                f.write("\n\n\n")

    def save_data_for_each_source(
        self,
        summarized_data: DataFrame,
        summarized_by_dir: DataFrame,
        src_dirs: List[str],
        out_dir: Path,
    ) -> None:
        for src_dir in src_dirs:
            path = Path(src_dir)
            if not path.exists():
                print(f"[-]: Directory {src_dir} does not exist")
                continue

            path.parent.joinpath(os.path.basename(out_dir)).mkdir(parents=True, exist_ok=True)
            with open(
                path.parent.joinpath(os.path.basename(out_dir), self.filename_out_data),
                "w",
            ) as f:

                data_frame = summarized_data.loc[src_dir]  # pyright: ignore
                f.write(f"dir: {src_dir}\n")
                f.write("\n")
                f.write(data_frame.to_string())  # pyright: ignore
                f.write("\n\n")
                f.write("Average % of BP incorrect: ")

                bp_incorrect = summarized_by_dir.loc["BP incorrect %", src_dir]  # pyright: ignore
                f.write(str(bp_incorrect))

    def construct_plot(self, summarized_data: DataFrame) -> DataFrame:
        result = DataFrame(
            {k: summarized_data.loc[k, "BP incorrect %"] for k in set(summarized_data.index.get_level_values(0))}
        )
        return result

    def filter_summarize_data(self, data: DataFrame) -> DataFrame:
        result = data.copy()
        for key in data.index:
            if not (0 <= data.loc[key, "BP incorrect %"] <= 100):  # type: ignore
                result.loc[key, "BP incorrect %"] = np.NaN  # type: ignore
            if data.loc[key, "BP lookups"] < 50:  # type: ignore
                result.loc[key, "BP incorrect %"] = np.NaN  # type: ignore
        return result

    def sort_data(self, data: DataFrame) -> DataFrame:
        return data.loc[data.max(axis=1).sort_values(na_position="first").index]

    def filter_summarize_data(self, summarized_data: Dict[str, DataFrame]) -> Dict[str, DataFrame]:
        result = summarized_data.copy()
        for src_dir, frame in summarized_data.items():
            for test, _ in frame.items():  # pyright: ignore
                if not (0 <= frame.loc["BP incorrect %", test] <= 100):  # type: ignore
                    result[src_dir].loc["BP incorrect %", test] = np.NaN  # type: ignore
                if frame.loc["BP lookups", test] < 50:  # type: ignore
                    result[src_dir].loc["BP incorrect %", test] = np.NaN  # type: ignore
        return result

    def show_plot(self) -> None:
        plt.show()  # pyright: ignore[reportUnknownMemberType]

    def save_plot(self, data: DataFrame, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        data.plot.bar()
        plt.savefig(out_dir.joinpath(self.filename_out_grapg))  # pyright: ignore

    def add_parser_arguments(self, subparser: SubParser) -> ArgumentParser:
        summarize_parser = subparser.add_parser("summarize")

        summarize_parser.add_argument("--src_dirs", help="Path to source dirs", nargs="*")
        summarize_parser.add_argument("--out_dir", default="summarize", help="Path to output directory")
        summarize_parser.add_argument(
            "--no_show_graph",
            action="store_true",
            help="Shows a graph of BP incorrect %%",
        )
        summarize_parser.add_argument(
            "--no_save_graph",
            action="store_true",
            help="Saves a graph of BP incorrect %% in graph.png",
        )
        summarize_parser.add_argument(
            "--log_level",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log level of program",
        )
        self.summarize_parser = summarize_parser
        return summarize_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.summarize_parser.parse_known_args(args)[0]
