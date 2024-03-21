import logging
import os
import shlex
import shutil
import threading
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path
from pprint import pformat
from queue import Queue
from typing import List

from src.cli.analyze import Analyze
from src.protocols.subparser import SubParser


class Aggregate:
    def __init__(self) -> None:
        self.settings = Namespace()
        self.logger = logging.getLogger(__name__)

    def _run_analyzer(self, analyze: Analyze, chan: Queue):
        analyze.run()
        if analyze.settings is None:
            raise LookupError("Didn't find settings for analyze")
        chan.put(analyze.settings.out_dir)

    # TODO: this is a draft method and should be removed or rewritted with asincio
    def run_analyzers(self) -> List[str]:
        output_analyze_dirs: List[str] = []
        chan = Queue()
        for analyze in self.analyzes:
            if self.settings.async_analyze:
                threading.Thread(target=self._run_analyzer, args=(analyze, chan)).start()
            else:
                self._run_analyzer(analyze, chan)

        for _ in self.analyzes:
            output_analyze_dirs.append(chan.get())

        return output_analyze_dirs

    def create_analyzer(self, config_file: Path, settings_analyze: Namespace) -> Analyze:
        analyze = Analyze()
        full_conf_path = Path(self.settings.path_to_configs).joinpath(config_file)
        if os.access(full_conf_path, mode=os.R_OK):
            cfg_settings = self.settings.configurator.read_cfg_file(full_conf_path)
            settings_analyze = Namespace(
                **self.settings.configurator.get_true_settings(
                    self.settings.analyze.analyze_parser,
                    cfg_settings,
                    settings_analyze,
                )
            )
            # if user set absolute path in config, we will save by it
            if not Path(settings_analyze.out_dir).is_absolute():
                name = full_conf_path.name.split(".")[0]
                sub_dir_name = f"{name}-{datetime.now().strftime('%y-%m-%d-%H-%M-%S-%f')}"
                sub_dir = Path(self.settings.dest_dir).joinpath(sub_dir_name)
                while sub_dir.exists():
                    sub_dir_name = sub_dir_name + "_new"
                    sub_dir = sub_dir.with_name(sub_dir_name)
                settings_analyze.out_dir = sub_dir.joinpath(settings_analyze.out_dir)

            settings_analyze.log_level = self.settings.log_level
            analyze.configurate(settings_analyze)

        return analyze

    def clean_output_dir(self) -> None:
        shutil.rmtree(self.settings.dest_dir)

    def run(self) -> None:
        self.logger.info("Aggregate is running. Settings:")
        self.logger.info(pformat(vars(self.settings)))

        # configure and run generator
        args_generate = shlex.split(self.settings.Wg)
        settings_generate = self.settings.generate.parse_args(args_generate)
        settings_generate.log_level = self.settings.log_level

        self.settings.generate.configurate(settings_generate)
        self.settings.generate.run()

        # configure and run analyzer
        self.output_analyze_dirs = self.run_analyzers()

        # configure and run summarizer
        args_summarize = shlex.split(self.settings.Ws)
        settings_summarize = self.settings.summarize.parse_args(args_summarize)
        settings_summarize.src_dirs = self.output_analyze_dirs
        settings_summarize.log_level = self.settings.log_level
        settings_summarize.out_dir = Path(self.settings.dest_dir).joinpath(settings_summarize.out_dir)

        self.settings.summarize.configurate(settings_summarize)
        self.settings.summarize.run()

    def configurate(self, settings: Namespace) -> None:
        self.settings = Namespace(**{**vars(settings), **vars(self.settings)})
        self.logger.setLevel(self.settings.log_level)

        # TODO: this is draft and should be rewritted
        args_analyze = shlex.split(self.settings.Wz)
        settings_analyze = self.settings.analyze.parse_args(args_analyze)
        self.analyzes = [self.create_analyzer(cfg, settings_analyze) for cfg in self.settings.configs]

    def add_parser_arguments(self, subparser: SubParser) -> ArgumentParser:
        shell_parser: ArgumentParser = subparser.add_parser("aggregate", prog="aggregate")

        shell_parser.add_argument("--config-file", default="config.json", help="Path to .cfg file")
        shell_parser.add_argument(
            "--section-in-config",
            default="DEFAULT",
            help="Set the custom section in config file (DEFAULT by default)",
        )
        shell_parser.add_argument(
            "--dest-dir",
            default="out",
            help="Path to dist dir, if not exit it will be created",
        )
        shell_parser.add_argument(
            "--async-analyze", action="store_true", help="Run analyze steps simultaneously (not recommended with perf)"
        )
        shell_parser.add_argument("--Wg", default="", help="Pass arguments to generate")
        shell_parser.add_argument("--Wz", default="", help="Pass arguments to analyze")
        shell_parser.add_argument("--Ws", default="", help="Pass arguments to summarize")
        shell_parser.add_argument(
            "--log-level",
            default="WARNING",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            help="Log level of program",
        )
        self.shell_parser = shell_parser
        return shell_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.shell_parser.parse_known_args(args)[0]
