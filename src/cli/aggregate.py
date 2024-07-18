import logging
import os
import shlex
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

    def create_analyzer(self, config_file: Path, settings_analyze: Dict[str, Any]) -> Analyze:
        analyze = Analyze()
        full_conf_path = Path(self.settings["path_to_configs"]).joinpath(config_file)
        if os.access(full_conf_path, mode=os.R_OK):
            cfg_settings = self.settings["configurator"].read_cfg_file(full_conf_path)
            settings_analyze = self.settings["configurator"].get_true_settings(
                    cfg_settings,
                    settings_analyze,
                )
            # if user set absolute path in config, we will save by it
            if not Path(settings_analyze["out_dir"]).is_absolute():
                name = full_conf_path.name.split(".")[0]
                sub_dir_name = f"{name}-{datetime.now().strftime('%y-%m-%d-%H-%M-%S-%f')}"
                sub_dir = Path(self.settings["dest_dir"]).joinpath(sub_dir_name)
                while sub_dir.exists():
                    sub_dir_name = sub_dir_name + "_new"
                    sub_dir = sub_dir.with_name(sub_dir_name)
                settings_analyze["out_dir"] = sub_dir.joinpath(settings_analyze["out_dir"])

            settings_analyze["log_level"] = self.settings["log_level"]
            analyze.configurate(settings_analyze)

        return analyze

    def clean_output_dir(self) -> None:
        shutil.rmtree(self.settings["dest_dir"])

    def run(self) -> None:
        self.logger.info("Aggregate is running. Settings:")
        self.logger.info(pformat(self.settings))

        # configure and run generator
        args_generate = shlex.split(self.settings["Wg"])
        configurator = self.settings["configurator"]
        settings_generate = configurator.parse_args(args_generate, self.settings["generate"].default_params)
        settings_generate["log_level"] = self.settings["log_level"]

        self.settings["generate"].configurate(settings_generate)
        self.settings["generate"].run()

        # configure and run analyzer
        self.output_analyze_dirs = self.run_analyzers()

        # configure and run summarizer
        args_summarize = shlex.split(self.settings["Ws"])
        settings_summarize = configurator.parse_args(args_summarize, self.settings["summarize"].default_params)
        settings_summarize["src_dirs"] = self.output_analyze_dirs
        settings_summarize["log_level"] = self.settings["log_level"]
        settings_summarize["out_dir"] = Path(self.settings["dest_dir"]).joinpath(settings_summarize["out_dir"])

        self.settings["summarize"].configurate(settings_summarize)
        self.settings["summarize"].run()

    def configurate(self, settings: Dict[str, Any]) -> None:
        self.settings = {**self.settings, **settings}
        self.logger.setLevel(self.settings["log_level"])

        # TODO: this is draft and should be rewritted
        args_analyze = shlex.split(self.settings["Wz"])
        configurator = self.settings["configurator"]
        settings_analyze = configurator.parse_args(args_analyze, self.settings["analyze"].default_params)
        self.analyzes = [self.create_analyzer(cfg, settings_analyze) for cfg in self.settings["configs"]]
