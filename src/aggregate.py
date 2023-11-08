import os
import random
import shlex
import shutil
import stat
from argparse import ArgumentParser, Namespace
from pathlib import Path
from pprint import pprint
from typing import List


class Aggregator:
    def __init__(self):
        self.output_analyze = None
        self.settings = {
            "source_folder": "source",
            "compiled_folder": "dest",
            "analyse_folder": "analyze",
        }
        self.settings = Namespace(**self.settings)
        self.shell_parser = None

    def create_folders(self):
        os.makedirs(self.settings.dest_folder, exist_ok=True)
        os.makedirs(
            os.path.join(self.settings.dest_folder, self.settings.source_folder),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(self.settings.dest_folder, self.settings.compiled_folder),
            exist_ok=True,
        )
        os.makedirs(
            os.path.join(self.settings.dest_folder, self.settings.analyse_folder),
            exist_ok=True,
        )
        os.chmod(self.settings.dest_folder, stat.S_IWRITE)

    def clean_output_folder(self):
        shutil.rmtree(self.settings.dest_folder)

    def run(self):
        if self.settings.debug:
            pprint("Aggregate is running. Settings:")
            pprint(vars(self.settings))

        args_generate = shlex.split(self.settings.Wg)
        settings_generate = self.settings.generate.parse_args(args_generate)
        settings_generate.debug = self.settings.debug

        self.settings.generate.configurate(settings_generate)
        self.settings.generate.run()
        self.output_analyze = {}

        for config_file in self.settings.configs:
            full_conf_path: Path = Path(self.settings.path_to_configs).joinpath(
                config_file
            )
            if os.access(full_conf_path, mode=os.R_OK):
                args_analyze = shlex.split(self.settings.Wz)
                settings_analyze = self.settings.analyze.parse_args(args_analyze)
                cfg_settings = self.settings.configurator.read_cfg_file(full_conf_path)
                settings_analyze = Namespace(
                    **self.settings.configurator.get_true_settings(
                        self.settings.analyze.analyze_parser,
                        cfg_settings,
                        settings_analyze,
                    )
                )
                if not os.path.isabs(settings_analyze.out_dir):
                    settings_analyze.out_dir = os.path.join(
                        self.settings.dest_folder, settings_analyze.out_dir
                    )
                os.makedirs(settings_analyze.out_dir, exist_ok=True)
                if os.listdir(settings_analyze.out_dir):
                    settings_analyze.out_dir = f"{settings_analyze.out_dir}-{settings_analyze.profiler}-{random.getrandbits(16)}"
                settings_analyze.debug = self.settings.debug
                self.settings.analyze.configurate(settings_analyze)
                self.settings.analyze.run()

    def configurate(self, settings: Namespace):
        self.settings = settings

    def add_sub_parser(self, sub_parsers) -> ArgumentParser:
        self.shell_parser: ArgumentParser = sub_parsers.add_parser(
            "aggregate", prog="aggregate"
        )

        self.shell_parser.add_argument(
            "--config_file", default="config.json", help="Path to .cfg file"
        )
        self.shell_parser.add_argument(
            "--section_in_config",
            default="DEFAULT",
            help="Set the custom section in config file (DEFAULT by default)",
        )
        self.shell_parser.add_argument(
            "--dest_folder",
            default="out",
            help="Path to dist folder, if not exit it will be created",
        )
        self.shell_parser.add_argument(
            "--Wg", default="", help="Pass arguments to generate"
        )
        self.shell_parser.add_argument(
            "--Wz", default="", help="Pass arguments to analyze"
        )
        self.shell_parser.add_argument(
            "--Ws", default="", help="Pass arguments to summarize"
        )
        self.shell_parser.add_argument(
            "--debug", action="store_true", help="Turn on helping prints"
        )
        return self.shell_parser

    def parse_args(self, args: List[str]) -> Namespace:
        return self.shell_parser.parse_known_args(args)[0]
