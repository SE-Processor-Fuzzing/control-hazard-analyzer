import logging
import shlex
import shutil
from pathlib import Path
from pprint import pformat
from typing import Dict, Any

from src.analyzers.gemAnalyzer import GemAnalyzer
from src.analyzers.perfAnalyzer import PerfAnalyzer
from src.analyzers.sshAnalyzer import SshAnalyzer
from src.helpers.backGroundBuilder import BGBuilder
from src.helpers.builder import Builder
from src.helpers.packer import Packer
from src.protocols.analyzer import Analyzer
from src.protocols.collector import DictSI
from src.protocols.utility import Utility


class Analyze(Utility):
    """Class for configuring and executing test analysis based on the parameters passed to the 'analyze' command,
    creating directories for analysis, performing the analysis, then writing the results
    """

    def __init__(self) -> None:
        self.analyzer: Analyzer | None = None
        self.packer = Packer()
        self.builder: Builder | None = None
        self.test_dir: Path | None = None
        self.analyze_dir: Path | None = None
        self.settings: Dict[str, Any] | None = None
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Dict[str, Any]) -> None:
        """Initialize local variables with passed parameters

        :param settings: Passed parameters to the command
        """
        self.settings = settings
        self.logger.setLevel(self.settings["log_level"])
        self.test_dir = Path(settings["test_dir"])
        self.analyze_dir = Path(settings["out_dir"])
        self.settings["compiler_args"] = shlex.split(settings["compiler_args"])
        self.builder = Builder(self.settings)
        match settings["profiler"]:
            case "perf":
                self.analyzer = PerfAnalyzer(self.builder, settings)
            case "gem5":
                self.analyzer = GemAnalyzer(self.builder, settings)
            case "ssh":
                self.analyzer = SshAnalyzer(BGBuilder(settings, self.builder), settings)
            case _:
                raise Exception(f'"{settings["profiler"]}" is unknown profiler')

    def run(self) -> None:
        """Print log info, then check that input tests directory's path is passed,
        and output directory's path also passed, create directories for analysis, start the analysis,
        and pack the results
        """
        self.logger.info("Analyze running. Settings:")
        self.logger.info(pformat(self.settings))
        if self.analyze_dir is None or self.test_dir is None:
            self.logger.warn("analyze_dir or test_dir are partially unknown. Exiting...")
            return
        self.create_empty_dir(self.analyze_dir)
        data = self.analyze(self.test_dir)
        self.fin_analyzer()
        self.pack(self.analyze_dir, data)

    def create_empty_dir(self, dir_path: Path) -> None:
        """Ensure the specified directory is empty by removing it if it exists and then creating a new empty directory

        :param dir_path: The path to the directory to be created
        """
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)

    def analyze(self, test_dir: Path) -> Dict[str, DictSI]:
        """Execute and analyze tests from the specified test directory

        :param test_dir: The directory containing the test files to be analyzed
        :return: A dictionary containing the results of the analysis
        """
        print(f"[+]: Execute and analyze tests from {test_dir.absolute().as_posix()}")
        if self.analyzer is None:
            self.logger.warn("Analyzer is not provided.")
            return {}
        return self.analyzer.analyze(test_dir)

    def fin_analyzer(self) -> None:
        """Finalize the analyzer, performing any necessary cleanup actions"""
        if self.analyzer is not None:
            self.analyzer.fin()

    def pack(self, analyze_dir: Path, analyzed_data: Dict[str, DictSI]) -> None:
        """Save the results of the analysis to the specified directory

        :param analyze_dir: The directory where the analysis results will be saved
        :param analyzed_data: The data resulting from the analysis
        """
        print(f"[+]: Save analysis' results to {analyze_dir.absolute().as_posix()}")
        self.packer.pack(analyze_dir, analyzed_data)
