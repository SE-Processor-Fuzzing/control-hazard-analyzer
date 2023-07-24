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
        self.bul_parser.add_argument("--repeats", type=int, help="Count of repeats to generated test", default=1)
        self.bul_parser.add_argument(
            "--arch",
            choices=["X86", "ARM", "RISCV"],
            help="Type of architecture (X86, ARM, RISCV)",
            default="X86",
        )
        self.bul_parser.add_argument("--dest_folder", help="Path to output folder", default="out")
        self.bul_parser.add_argument("--compiler", help="Path to compiler", default="gcc")
        return self.bul_parser
