from argparse import ArgumentParser, Namespace
from typing import List


class Summarizer:
    def __init__(self):
        self.summarize_parser = None
        self.settings = None

    def configurate(self, settings: Namespace):
        self.settings = settings

    def run(self):
        print("Summarize is running. Settings:")
        print(self.settings)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.summarize_parser: ArgumentParser = sub_parsers.add_parser("summarize", prog="summarize")

        self.summarize_parser.add_argument("--config_file", help="Path to config file")
        self.summarize_parser.add_argument("--src_folder", help="Path to source folder")
        self.summarize_parser.add_argument("--dest_folder", help="Path to destination folder")
        return self.summarize_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.summarize_parser.parse_known_args(args)[0]
