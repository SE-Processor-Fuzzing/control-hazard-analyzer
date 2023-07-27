import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional


class Generator:
    def __init__(self):
        self.settings: Optional[Namespace] = None
        self.analyze_parser: Optional[ArgumentParser] = None
        self.repeats: Optional[int] = None

    def configurate(self, settings: Namespace) -> None:
        self.out_dir: Path = Path(settings.out_dir)
        self.repeats = int(settings.repeats)

    def generate_tests(self, target_dir: Path, count: int, verbose: bool = False):
        if verbose:
            print(f"Generate tests to '{target_dir.absolute()}'")

        for i in range(count):
            shutil.copy("test.c", target_dir.joinpath(f"test_{i}.c"))

    def create_empty_dir(self, dir: Path):
        if dir.exists():
            shutil.rmtree(dir)
        dir.mkdir(parents=True)

    def run(self) -> None:
        self.create_empty_dir(self.out_dir)
        self.generate_tests(self.out_dir, self.repeats, verbose=True)

    def add_sub_parser(self, sub_parser) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parser.add_parser("generate", prog="generate")
        self.analyze_parser.add_argument("--out_dir", default="tests", help="Path to output folder")
        self.analyze_parser.add_argument("--repeats", type=int, default=1, help="Count of repeats to generated test")
        return self.analyze_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.analyze_parser.parse_known_args(args)[0]
