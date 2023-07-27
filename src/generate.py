from argparse import ArgumentParser, Namespace
from pathlib import Path
import shutil
from typing import List


class Generator:
    def __init__(self):
        self.settings = None
        self.analyze_parser = None
        self.repeats = None

    def configurate(self, settings: Namespace) -> None:
        self.src_dir: Path = Path(settings.dest_folder).joinpath("src")
        self.repeats = int(settings.repeats)

    def add_sub_parser(self, sub_parser) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parser.add_parser("generate", prog="generate")
        self.analyze_parser.add_argument("--dest_folder", default="out", help="Path to output folder")
        self.analyze_parser.add_argument("--repeats", type=int, default=1, help="Count of repeats to generated test")
        return self.analyze_parser

    def parse_args(self, args: List[str]) -> Namespace:
        ...

    def run(self) -> None:
        self.generate_tests(self.src_dir, self.repeats, verbose=True)

    def generate_tests(self, target_dir: Path, count: int, verbose: bool = False):
        if (verbose):
            print(f"Generate tests to '{target_dir.absolute()}'")

        for i in range(count):
            shutil.copy(
                "test.c",
                target_dir.joinpath(f'test_{i}.c')
            )
