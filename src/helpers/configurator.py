import json
from argparse import ArgumentParser, Namespace
from typing import Any, Dict, Optional

from src.protocols.utility import Utility


class Configurator:
    def __init__(self) -> None:
        self.args: Optional[Namespace] = None

        self.parser = ArgumentParser(
            description="This script generate and test code on some platforms",
        )

        self.sub_parser = self.parser.add_subparsers(
            required=True,
            title="analyze and summarize",
            help="aggregate is shell above: analyze (code generator + profiler), summarize",
            dest="name_of_subparsers",
            metavar="utility {aggregate, generate, analyze, summarize}",
        )

    def parse_sub_parsers(self, utilities: Dict[str, Utility]) -> tuple[Namespace, list[str]]:
        for name, utility in utilities.items():
            utility.add_parser_arguments(self.sub_parser).set_defaults(utility=name)

        return self.parser.parse_known_args()

    def configurate(self, utilities: Dict[str, Utility]) -> Namespace:
        self.args = self.parse_sub_parsers(utilities)[0]
        config = self.read_cfg_file(
            getattr(self.args, "config_file", None),
            self.args.section_in_config if hasattr(self.args, "section_in_config") else None,
        )

        return Namespace(**{**vars(self.args), **utilities, **config})

    def read_cfg_file(self, config_file: str | None, section: str | None = None) -> Dict[str, Any]:
        if config_file is None:
            return dict()
        with open(config_file, mode="r") as f:
            config: Dict[str, Any] = json.load(f)
        return config if section is None else {**config["DEFAULT"], **config[section]}

    def get_true_settings(self, parser: ArgumentParser, settings: Dict[str, Any], args: Namespace) -> Dict[str, Any]:
        result: Dict[str, Any] = settings
        dct_args = {**vars(args)}
        for arg in dct_args:
            if arg in settings:
                if dct_args[arg] != parser.get_default(arg):
                    settings[arg] = dct_args[arg]
            else:
                settings[arg] = dct_args[arg]
        return result
