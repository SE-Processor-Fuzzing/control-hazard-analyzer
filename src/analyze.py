import shlex
import shutil
from argparse import Namespace, ArgumentParser
from pathlib import Path
from typing import Dict

from profilers.perfProfiler import PerfProfiler
from profilers.profiler import IProfiler
from src.builder import Builder
from src.packer import Packer


class Analyzer:
    def __init__(self):
        self.profiler = None
        self.packer = None
        self.builder = None
        self.test_dir = None
        self.analyze_dir = None
        self.analyze_parser = None
        self.settings = None

    def configurate(self, settings: Namespace):
        self.settings = settings
        self.test_dir: Path = Path(settings.test_dir)
        self.analyze_dir: Path = Path(settings.dest_folder).joinpath("analyze").joinpath(settings.sub_folder)
        self.settings.compiler_args = shlex.split(settings.compiler_args)
        self.builder: Builder = Builder(self.settings)
        self.packer = Packer()
        self.profiler: IProfiler
        if settings.profiler == "perf":
            self.profiler = PerfProfiler(self.builder)
        elif settings.profiler == "gem5":
            ...
        else:
            raise Exception(f'"{settings.choice}" is unknown profiler')

    def run(self):
        data = self.profile(self.test_dir, verbose=True)
        self.pack(self.analyze_dir, data, verbose=True)

    def profile(self, test_dir: Path, verbose: bool = False) -> Dict[str, Dict]:
        if verbose:
            print(f"Execute and analyze tests from '{test_dir.absolute()}'")
        return self.profiler.profile(test_dir)

    def pack(self, analyze_dir: Path, analyzed_data: Dict[str, Dict], verbose: bool = False):
        if verbose:
            print(f"Save analysis' results to '{analyze_dir.absolute()}'")
        return self.packer.pack(analyze_dir, analyzed_data)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parsers.add_parser("analyze", prog="analyze")
        self.analyze_parser.add_argument("--config_file", default="", help="Path to config file")
        self.analyze_parser.add_argument("--dest_folder", default="out", help="Path to output folder")
        self.analyze_parser.add_argument("--test_dir", default="./", help="Path to directory with tests")
        self.analyze_parser.add_argument(
            "--sub_folder",
            default="X86",
            help="Sub-folder in destination folder (usually the same as name of the architecture)",
        )
        self.analyze_parser.add_argument("--compiler", default="gcc", help="Path to compiler")
        self.analyze_parser.add_argument("--compiler_args", default="", help="Pass arguments on to the compiler")
        self.analyze_parser.add_argument(
            "--profiler", choices=["perf", "gem5"], default="perf", help="Type of profiler"
        )
        return self.analyze_parser

    def parse_args(self, args: list[str]) -> Namespace:
        return self.analyze_parser.parse_known_args(args)[0]
