import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import List, Optional

import src.blocks_rendering as br


class Generator:
    def __init__(self):
        self.settings: Optional[Namespace] = None
        self.analyze_parser: Optional[ArgumentParser] = None
        self.repeats: Optional[int] = None
        self.out_dir: Optional[Path] = None

    def configurate(self, settings: Namespace) -> None:
        self.settings = settings
        self.out_dir = Path(settings.out_dir)
        self.repeats = int(settings.repeats)

    def generate_tests(
        self, target_dir: Path, count: int, total_blocks: int = 100, blocks_cap: int = 2, vars_cap: int = 2
    ):
        if self.settings.debug:
            print(f"Generate tests to '{target_dir.absolute()}'")
        for i in range(count):
            br.generate_test(target_dir.joinpath(f"test_{i}.c"), total_blocks, blocks_cap, vars_cap)

    def create_empty_dir(self, dir: Path):
        if dir.exists():
            shutil.rmtree(dir)
        dir.mkdir(parents=True)

    def run(self) -> None:
        self.create_empty_dir(self.out_dir)
        self.generate_tests(self.out_dir, self.repeats)

    def add_sub_parser(self, sub_parser) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parser.add_parser("generate", prog="generate")
        self.analyze_parser.add_argument("--out_dir", default="tests", help="Path to output folder")
        self.analyze_parser.add_argument("--repeats", type=int, default=1, help="Count of repeats to generated test")
        self.analyze_parser.add_argument("--debug", action="store_true", help="Turn on helping prints")
        return self.analyze_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.analyze_parser.parse_known_args(args)[0]
