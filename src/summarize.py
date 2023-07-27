import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

import numpy as np
import pandas as pd
from typing import List


class Summarizer:
    def __init__(self):
        self.summarize_parser = None
        self.settings = None

    def configurate(self, settings: Namespace):
        self.settings = settings

    def run(self):
        print("Summarize is running. Settings:")
        data = self.get_data_from_sources(self.settings.src_folders)
        summarized_data = self.convert_to_pandas(self.summarize_data(data))
        summarized_by_folder = self.summarize_by_folder(summarized_data)
        self.save_data(summarized_data, summarized_by_folder, self.settings.output_file)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.summarize_parser: ArgumentParser = sub_parsers.add_parser("summarize", prog="summarize")

        self.ck_parser.add_argument("--config_file", help="Path to config file")
        self.ck_parser.add_argument("--src_folders", help="Path to source folders. One or more.", nargs="+",
                                    required=True)
        self.ck_parser.add_argument("--output_file", help="Path to output file", required=True)
        return self.ck_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.summarize_parser.parse_known_args(args)[0]

    # Parse data from json, from sources
    def get_data_from_sources(self, src_folders: list[str]):
        data = {}
        for src_folder in src_folders:
            if not Path(src_folder).exists():
                print(f"Folder {src_folder} does not exist")
            else:
                data[src_folder] = {}
                for src_file in Path(src_folder).glob("*.json"):
                    with open(src_file, "r") as f:
                        data[src_folder][src_file.stem] = json.loads(f.read())
                    for key, val in data[src_folder][src_file.stem].items():
                        data[src_folder][src_file.stem][key] = int(val)

        return data

    def summarize_data(self, data: dict):
        summarized_data = {Path(src_folder).stem: {} for src_folder in data}
        for src_folder, src_files in data.items():
            for src_file, src_data in src_files.items():
                sim_ticks = src_data.get("simTicks", np.nan)
                bp_lookups = src_data.get("branchPred.lookups", np.nan)
                bp_incorrect = src_data.get("branchPred.condIncorrect", np.nan)
                summarized_data[Path(src_folder).stem][Path(src_file).stem] = {
                    f"Number of ticks": sim_ticks,
                    f"BP lookups": bp_lookups,
                    f"Ticks per BP": round(sim_ticks / float(bp_lookups),
                                           2) if bp_lookups != np.nan and sim_ticks != np.nan else np.nan,
                    f"BP incorrect": bp_incorrect,
                    f"BP incorrect %": round(bp_incorrect / float(bp_lookups) * 100,
                                             2) if bp_lookups != np.nan and bp_incorrect != np.nan else np.nan,
                }
        return summarized_data

    def summarize_by_folder(self, summarized_data: dict):
        summarized_by_folder = {}
        for src_folder, data_frame in summarized_data.items():
            summarized_by_folder[src_folder] = {}
            summarized_by_folder[src_folder]["BP incorrect %"] = round(
                data_frame.loc['BP incorrect'].sum() / data_frame.loc['BP lookups'].sum() * 100, 2)
        return pd.DataFrame(summarized_by_folder)

    def convert_to_pandas(self, summarized_data: dict):
        for src_folder, src_files in summarized_data.items():
            summarized_data[src_folder] = pd.DataFrame(src_files)
        return summarized_data

    def save_data(self, summarized_data: dict, summarized_by_folder, dest_file: str):
        with open(Path(dest_file), "w") as f:
            # Use pandas to print data to file
            f.write("Summarized data:\n")
            summarized_by_folder.plot.bar()
            f.write(summarized_by_folder.to_string())
            f.write("\n\n")
            for src_folder, src_files in summarized_data.items():
                f.write(f"Folder: {src_folder}\n")
                f.write(pd.DataFrame(src_files).to_string())
                f.write("\n\n")
