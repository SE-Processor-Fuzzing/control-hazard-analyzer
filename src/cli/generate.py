import logging
import shutil
from argparse import ArgumentParser, Namespace
from pathlib import Path
from pprint import pformat
from typing import List, Optional

from src.generators.code_gen import gen_test
from src.protocols.subparser import SubParser


class Generate:
    def __init__(self) -> None:
        self.settings: Optional[Namespace] = None
        self.repeats: Optional[int] = None
        self.out_dir: Optional[Path] = None
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Namespace) -> None:
        self.settings = settings
        self.logger.setLevel(self.settings.log_level)
        self.out_dir = Path(settings.out_dir)
        self.repeats = int(settings.repeats)

    def generate_tests(
        self,
        target_dir: Path,
        count: int,
        max_depth: int = 6,
    ) -> None:
        print(f"[+]: Generate tests to '{target_dir.absolute()}'")
        for i in range(count):
            self._generate_test(target_dir.joinpath(f"test_{i}.c"), max_depth)

    def _generate_test(self, file: Path, max_depth: int) -> None:
        test = gen_test(max_depth)
        if file.is_dir():
            self.logger.warn(f"Provided path {file} are not a file. Skipping this test.")
            return
        with open(file, "w") as f:
            self.logger.info(f"Write test into {file}")
            f.write(test)

    def create_empty_dir(self, dir_path: Path) -> None:
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)

    def run(self) -> None:
        self.logger.info("Generate is running. Settings:")
        self.logger.info(pformat(vars(self.settings)))
        if self.out_dir is None or self.repeats is None:
            self.logger.warn("Out dir or repeats values are not provided. Exiting...")
            return
        self.create_empty_dir(self.out_dir)
        self.generate_tests(self.out_dir, self.repeats)

    def add_parser_arguments(self, subparser: SubParser) -> ArgumentParser:
        generate_parser = subparser.add_parser("generate")
        generate_parser.add_argument("--out_dir", default="tests", help="Path to output dir")
        generate_parser.add_argument("--repeats", type=int, default=1, help="Count of repeats to generated test")
        generate_parser.add_argument(
            "--log_level",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log level of program",
        )
        self.generate_parser = generate_parser
        return generate_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.generate_parser.parse_known_args(args)[0]
