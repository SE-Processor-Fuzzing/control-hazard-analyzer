from argparse import Namespace, ArgumentParser
from pathlib import Path
import shlex
import shutil
from typing import Dict
from profilers.perfProfiler import PerfProfiler
from profilers.profiler import IProfiler

from src.builder import Builder
from src.packer import Packer


class Analyzer:
    def __init__(self):
        self.analyze_parser = None
        self.settings = None

    def configurate(self, settings: Namespace):
        self.settings = settings
        self.src_dir: Path = Path(settings.dest_folder).joinpath("src")
        self.analyze_dir: Path = Path(settings.dest_folder).joinpath("analyze")
        self.settings.compiler_args = shlex.split(settings.compiler_args)
        self.builder: Builder = Builder(self.settings)
        self.packer = Packer()
        self.profiler: IProfiler
        if (settings.choice == "perf"):
            self.profiler = PerfProfiler(self.builder)
        elif (settings.choice == "gem5"):
            ...
        else:
            raise Exception(f'"{settings.choice}" is unknown profiler')

    def run(self):
        self.generate_tests(self.src_dir, self.settings.repeats, verbose=True)
        data = self.profile(self.src_dir, verbose=True)
        self.pack(self.analyze_dir, data, verbose=True)

    def generate_tests(self, target_dir: Path, count: int, verbose: bool = False):
        if (verbose):
            print(f"Generate tests to '{target_dir.absolute()}'")

        for i in range(count):
            shutil.copy(
                "test.c",
                target_dir.joinpath(f'test_{i}.c')
            )

    def profile(self, test_dir: Path, verbose: bool = False) -> Dict[str, Dict]:
        if (verbose):
            print(f"Execute and analyze tests from '{test_dir.absolute()}'")
        return self.profiler.profile(test_dir)

    def pack(self, analyze_dir: Path, analyzed_data: Dict[str, Dict], verbose: bool = False):
        if (verbose):
            print(f"Save analysis' results to '{analyze_dir.absolute()}'")
        return self.packer.pack(analyze_dir, analyzed_data)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parsers.add_parser("analyze", prog="analyze")
        self.analyze_parser.add_argument("--config_file", help="Path to config file")
        self.analyze_parser.add_argument("--repeats", type=int, default=1, help="Count of repeats to generated test")
        self.analyze_parser.add_argument("--dest_folder", default="out", help="Path to output folder")
        self.analyze_parser.add_argument(
            "--sub_folder",
            default="X86",
            help="Sub-folder in destination folder (usually the same as name of the architecture)",
        )
        self.analyze_parser.add_argument("--compiler", default="gcc", help="Path to compiler")
        return self.analyze_parser
