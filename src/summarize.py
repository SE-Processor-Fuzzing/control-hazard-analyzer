from argparse import ArgumentParser, Namespace


class Summarizer:
    def __init__(self):
        self.ck_parser = None
        self.settings = None

    def configurate(self, settings: Namespace):
        self.settings = settings

    def run(self):
        print("Summarize is running. Settings:")
        print(self.settings)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.ck_parser: ArgumentParser = sub_parsers.add_parser("summarize", prog="summarize")

        self.ck_parser.add_argument("--config_file", help="Path to config file")
        self.ck_parser.add_argument("--src_folder", help="Path to source folder")
        self.ck_parser.add_argument("--dest_folder", help="Path to destination folder")
        return self.ck_parser
