import logging
import os
import shutil
import threading
from datetime import datetime
from pathlib import Path
from pprint import pformat
from queue import Queue
from typing import List, Dict, Any

from src.cli.analyze import Analyze
from src.protocols.utility import Utility


class Aggregate(Utility):
    def __init__(self) -> None:
        self.settings: Dict[str, Any] = {}
        self.logger = logging.getLogger(__name__)
        self.default_analyze_settings = {
            "utility": "analyze",
            "config_file": None,
            "out_dir": "analyze",
            "test_dir": "tests",
            "timeout": 10,
            "compiler": "gcc",
            "compiler_args": "",
            "profiler": "perf",
            "gem5_home": "./",
            "gem5_bin": "./",
            "target_isa": "",
            "sim_script": "./",
            "log_level": "WARNING",
        }

        self.default_generate_settings = {
            "utility": "generate",
            "out_dir": "tests",
            "repeats": 1,
            "log_level": "WARNING",
        }

        self.default_summarize_settings = {
            "utility": "summarize",
            "src_dirs": [],
            "out_dir": "summarize",
            "no_show_graph": False,
            "no_save_graph": False,
            "log_level": "WARNING",
        }

    def _run_analyzer(self, analyze: Analyze, chan: Queue):
        analyze.run()
        if analyze.settings is None:
            raise LookupError("Didn't find settings for analyze")
        chan.put(analyze.settings["out_dir"])

    # TODO: this is a draft method and should be removed or rewritted with asincio
    def run_analyzers(self) -> List[str]:
        output_analyze_dirs: List[str] = []
        chan = Queue()
        for analyze in self.analyzes:
            if self.settings["async_analyze"]:
                threading.Thread(target=self._run_analyzer, args=(analyze, chan)).start()
            else:
                self._run_analyzer(analyze, chan)

        for _ in self.analyzes:
            output_analyze_dirs.append(chan.get())

        return output_analyze_dirs

    def create_analyzer(self, config_file: Path) -> Analyze:
        analyze = Analyze()
        full_conf_path = Path(self.settings["path_to_configs"]).joinpath(config_file)
        if os.access(full_conf_path, mode=os.R_OK):
            cfg_settings = self.settings["configurator"].read_cfg_file(full_conf_path)
            self.default_analyze_settings = self.settings["configurator"].get_true_settings(
                cfg_settings,
                self.default_analyze_settings,
            )
            # if user set absolute path in config, we will save by it
            if not Path(self.default_analyze_settings["out_dir"]).is_absolute():
                name = full_conf_path.name.split(".")[0]
                sub_dir_name = f"{name}-{datetime.now().strftime('%y-%m-%d-%H-%M-%S-%f')}"
                sub_dir = Path(self.settings["dest_dir"]).joinpath(sub_dir_name)
                while sub_dir.exists():
                    sub_dir_name = sub_dir_name + "_new"
                    sub_dir = sub_dir.with_name(sub_dir_name)
                self.default_analyze_settings["out_dir"] = sub_dir.joinpath(self.default_analyze_settings["out_dir"])

            self.default_analyze_settings["log_level"] = self.settings["log_level"]
            analyze.configurate(self.default_analyze_settings)

        return analyze

    def clean_output_dir(self) -> None:
        shutil.rmtree(self.settings["dest_dir"])

    def run(self) -> None:
        self.logger.info("Aggregate is running. Settings:")
        self.logger.info(pformat(self.settings))

        # # configure and run generator
        self.default_generate_settings["log_level"] = self.settings["log_level"]
        self.settings["generate"].configurate(self.default_generate_settings)
        self.settings["generate"].run()

        # configure and run analyzer
        self.output_analyze_dirs = self.run_analyzers()

        # configure and run summarizer
        self.default_summarize_settings["src_dirs"] = self.output_analyze_dirs
        self.default_summarize_settings["log_level"] = self.settings["log_level"]
        self.default_summarize_settings["out_dir"] = str(
            Path(self.settings["dest_dir"]).joinpath(self.default_summarize_settings["out_dir"])
        )

        self.settings["summarize"].configurate(self.default_summarize_settings)
        self.settings["summarize"].run()

    def configurate(self, settings: Dict[str, Any]) -> None:
        self.settings = {**self.settings, **settings}
        self.logger.setLevel(self.settings["log_level"])
        self.analyzes = [self.create_analyzer(cfg) for cfg in self.settings["configs"]]
