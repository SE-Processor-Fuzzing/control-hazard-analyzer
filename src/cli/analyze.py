import logging
import shlex
import shutil
from argparse import Namespace, ArgumentParser
from pathlib import Path
from pprint import pformat
from typing import Dict, List, Optional

from src.analyzers.gemProfiler import GemAnalyzer
from src.analyzers.perfProfiler import PerfAnalyzer
from src.analyzers.profiler import Analyzer
from src.helpers.builder import Builder
from src.helpers.packer import Packer


class Analyze:
    def __init__(self):
        self.analyzer: Optional[Analyzer] = None
        self.packer: Optional[Packer] = None
        self.builder: Optional[Builder] = None
        self.test_dir: Optional[Path] = None
        self.analyze_dir: Optional[Path] = None
        self.analyze_parser: Optional[ArgumentParser] = None
        self.settings: Optional[Namespace] = None
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Namespace):
        self.settings = settings
        self.logger.setLevel(self.settings.log_level)
        self.test_dir: Path = Path(settings.test_dir)
        self.analyze_dir: Path = Path(settings.out_dir)
        self.settings.compiler_args = shlex.split(settings.compiler_args)
        self.builder: Builder = Builder(self.settings)
        self.packer = Packer()
        self.analyzer: Analyzer
        if settings.profiler == "perf":
            self.analyzer = PerfAnalyzer(self.builder, settings)
        elif settings.profiler == "gem5":
            self.analyzer = GemAnalyzer(self.builder, settings)
        else:
            raise Exception(f'"{settings.profiler}" is unknown profiler')

    def run(self):
        self.logger.info("Analyze running. Settings:")
        self.logger.info(pformat(vars(self.settings)))
        self.create_empty_dir(self.analyze_dir)
        data = self.analyze(self.test_dir)
        self.pack(self.analyze_dir, data)

    def create_empty_dir(self, dir: Path):
        if dir.exists():
            shutil.rmtree(dir)
        dir.mkdir(parents=True)

    def analyze(self, test_dir: Path) -> Dict[str, Dict]:
        print(f"[+]: Execute and analyze tests from {test_dir.absolute().as_posix()}")
        return self.analyzer.analyze(test_dir)

    def pack(self, analyze_dir: Path, analyzed_data: Dict[str, Dict]):
        print(f"[+]: Save analysis' results to {analyze_dir.absolute().as_posix()}")
        return self.packer.pack(analyze_dir, analyzed_data)

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.analyze_parser: ArgumentParser = sub_parsers.add_parser("analyze", prog="analyze")
        self.analyze_parser.add_argument("--config_file", default=None, help="Path to config file")
        self.analyze_parser.add_argument("--out_dir", default="analyze", help="Path to output dir")
        self.analyze_parser.add_argument("--test_dir", default="tests", help="Path to directory with tests")
        self.analyze_parser.add_argument(
            "--timeout",
            default=10,
            help="Number of seconds after which the test will be stopped",
        )
        self.analyze_parser.add_argument("--compiler", default="gcc", help="Path to compiler")
        self.analyze_parser.add_argument("--compiler_args", default="", help="Pass arguments on to the compiler")
        self.analyze_parser.add_argument(
            "--profiler",
            choices=["perf", "gem5"],
            default="perf",
            help="Type of profiler",
        )
        self.analyze_parser.add_argument("--gem5_home", default="./", help="Path to home gem5")
        self.analyze_parser.add_argument("--gem5_bin", default="./", help="Path to execute gem5")
        self.analyze_parser.add_argument("--target_isa", default="", help="Type of architecture being simulated")
        self.analyze_parser.add_argument("--sim_script", default="./", help="Path to simulation Script")
        self.analyze_parser.add_argument(
            "--log_level",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log level of program",
        )

        return self.analyze_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.analyze_parser.parse_known_args(args)[0]
