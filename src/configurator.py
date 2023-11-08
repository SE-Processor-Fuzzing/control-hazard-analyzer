import json
from argparse import Namespace, ArgumentParser
from typing import Any, Mapping, Dict, Optional

from src.utility import IUtility


class Configurator:
    def __init__(self):
        self.generator_parser: Optional[ArgumentParser] = None
        self.shell_parser: Optional[ArgumentParser] = None
        self.analyze_parser: Optional[ArgumentParser] = None
        self.summarize_parser: Optional[ArgumentParser] = None
        self.args: Optional[Namespace] = None

        self.parser = ArgumentParser(
            prog="aggregate",
            description="This script generate and test code on some platforms",
        )

        self.sub_parser = self.parser.add_subparsers(
            required=True,
            title="analyze and summarize",
            help="aggregate is shell above: analyze (code generator + profiler), summarize",
            dest="name_of_subparsers",
            metavar="utility {aggregate, generate, analyze, summarize}",
        )

    def parse_sub_parsers(self, settings: Mapping[str, IUtility]):
        self.analyze_parser = settings["analyze"].add_sub_parser(self.sub_parser)
        self.generator_parser = settings["generate"].add_sub_parser(self.sub_parser)
        self.summarize_parser = settings["summarize"].add_sub_parser(self.sub_parser)
        self.shell_parser = settings["aggregate"].add_sub_parser(self.sub_parser)
        self.analyze_parser.set_defaults(utility=settings["analyze"])
        self.summarize_parser.set_defaults(utility=settings["summarize"])
        self.shell_parser.set_defaults(utility=settings["aggregate"])
        self.generator_parser.set_defaults(utility=settings["generate"])
        return self.parser.parse_known_args()

    def configurate(self, settings: Mapping[str, Any] = None) -> Namespace:
        if settings is None:
            settings = {}
        self.args = self.parse_sub_parsers(settings)[0]
        config = self.read_cfg_file(
            getattr(self.args, "config_file", None),
            self.args.section_in_config
            if hasattr(self.args, "section_in_config")
            else None,
        )

        return Namespace(**{**vars(self.args), **settings, **config})

    def read_cfg_file(self, config_file: str, section: str = None) -> Dict[str, Any]:
        if config_file is None:
            return dict()
        with open(config_file, mode="r") as f:
            config: Dict[str, Any] = json.load(f)
        return config if section is None else {**config["DEFAULT"], **config[section]}

    def get_true_settings(
        self, parser: ArgumentParser, settings: Dict[str, Any], args: Namespace
    ) -> Dict[str, Any]:
        result: Dict[str, Any] = settings
        dct_args = {**vars(args)}
        for arg in dct_args:
            if arg in settings:
                if dct_args[arg] != parser.get_default(arg):
                    settings[arg] = dct_args[arg]
            else:
                settings[arg] = dct_args[arg]
        return result
