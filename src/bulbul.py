from argparse import Namespace, ArgumentParser


class Bulbul:
    def __init__(self):
        self.bul_parser = None
        self.settings = None

    def configurate(self, settings: Namespace):
        self.settings = settings

    def run(self):
        print("bulbul is running. Settings:")
        print(self.settings)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.bul_parser: ArgumentParser = sub_parsers.add_parser("bulbul", prog="bulbul")
        self.bul_parser.add_argument("--config_file", help="Path to config file")
        self.bul_parser.add_argument("--repeats", type=int, default=1, help="Count of repeats to generated test")
        self.bul_parser.add_argument("--dest_folder", default="out", help="Path to output folder")
        self.bul_parser.add_argument(
            "--sub_folder",
            default="X86",
            help="Sub-folder in destination folder (usually the same as name of the architecture)",
        )
        self.bul_parser.add_argument("--compiler", default="gcc", help="Path to compiler")
        return self.bul_parser
