import shlex
import shutil
from argparse import Namespace, ArgumentParser
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Optional

from profilers.gemProfiler import GemProfiler
from profilers.perfProfiler import PerfProfiler
from profilers.profiler import IProfiler
from src.builder import Builder
from src.packer import Packer


class Analyzer:
    def __init__(self):
        self.profiler: Optional[IProfiler] = None
        self.packer: Optional[Packer] = None
        self.builder: Optional[Builder] = None
        self.test_dir: Optional[Path] = None
        self.analyze_dir: Optional[Path] = None
        self.analyze_parser: Optional[ArgumentParser] = None
        self.settings: Optional[Namespace] = None

    def configurate(self, settings: Namespace):
        self.settings = settings
        self.test_dir: Path = Path(settings.test_dir)
        self.analyze_dir: Path = Path(settings.out_dir)
        self.settings.compiler_args = shlex.split(settings.compiler_args)
        self.builder: Builder = Builder(self.settings)
        self.packer = Packer()
        self.profiler: IProfiler
        if settings.profiler == "perf":
            self.profiler = PerfProfiler(self.builder)
        elif settings.profiler == "gem5":
            self.profiler = GemProfiler(self.builder, settings)
        else:
            raise Exception(f'"{settings.profiler}" is unknown profiler')

    def run(self):
        if self.settings.debug:
            print("Analyze running. Settings:")
            pprint(vars(self.settings))
        self.create_empty_dir(self.analyze_dir)
        data = self.profile(self.test_dir)
        self.pack(self.analyze_dir, data)

    def create_empty_dir(self, dir: Path):
        if dir.exists():
            shutil.rmtree(dir)
        dir.mkdir(parents=True)

    def profile(self, test_dir: Path) -> Dict[str, Dict]:
        if self.settings.debug:
            print(f"Execute and analyze tests from '{test_dir.absolute()}'")
        return self.profiler.profile(test_dir)

    def pack(self, analyze_dir: Path, analyzed_data: Dict[str, Dict]):
        if self.settings.debug:
            print(f"Save analysis' results to '{analyze_dir.absolute()}'")
        return self.packer.pack(analyze_dir, analyzed_data)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parsers.add_parser("analyze", prog="analyze")
        self.analyze_parser.add_argument("--config_file", default=None, help="Path to config file")
        self.analyze_parser.add_argument("--out_dir", default="analyze", help="Path to output folder")
        self.analyze_parser.add_argument("--test_dir", default="tests", help="Path to directory with tests")
        self.analyze_parser.add_argument("--compiler", default="gcc", help="Path to compiler")
        self.analyze_parser.add_argument("--compiler_args", default="", help="Pass arguments on to the compiler")
        self.analyze_parser.add_argument(
            "--profiler", choices=["perf", "gem5"], default="perf", help="Type of profiler"
        )
        self.analyze_parser.add_argument("--gem5_home", default="./", help="Path to home gem5")
        self.analyze_parser.add_argument("--gem5_bin", default="./", help="Path to execute gem5")
        self.analyze_parser.add_argument("--target_isa", default="", help="Type of architecture being simulated")
        self.analyze_parser.add_argument("--sim_script", default="./", help="Path to simulation Script")

        return self.analyze_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.analyze_parser.parse_known_args(args)[0]
