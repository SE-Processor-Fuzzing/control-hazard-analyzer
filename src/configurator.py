import argparse
import json
from argparse import Namespace
from typing import Any, Mapping, Dict


class Configurator:
    def __init__(self):
        self.shell_parser = None
        self.bul_parser = None
        self.ck_parser = None
        self.args = None
        self.compiler_args = None

        self.parser = argparse.ArgumentParser(
            prog="BIOHazard",
            description="This script generate and test code on some platforms",
        )

        self.sub_parser = self.parser.add_subparsers(
            required=True,
            title="bulbul and ckrasota",
            help="BIOhazard is shell above: bulbul (code generator), ckrasota (agregator)",
            dest="name_of_subparsers",
            metavar="utility {BIOhazard, bulbul, ckrasota}",
        )

    def parse_sub_parsers(self, settings: Mapping[str, Any]):
        self.bul_parser = settings["bulbul"].add_sub_parser(self.sub_parser)
        self.ck_parser = settings["ckrasota"].add_sub_parser(self.sub_parser)
        self.shell_parser = settings["biohazard"].add_sub_parser(self.sub_parser)
        self.bul_parser.set_defaults(utility=settings["bulbul"])
        self.ck_parser.set_defaults(utility=settings["ckrasota"])
        self.shell_parser.set_defaults(utility=settings["biohazard"])
        return self.parser.parse_known_args()

    def configurate(self, settings: Mapping[str, Any] = None) -> Namespace:
        if settings is None:
            settings = {}
        self.args = self.parse_sub_parsers(settings)[0]
        config = self.read_cfg_file(
            self.args.config_file,
            self.args.section_in_config if hasattr(self.args, "section_in_config") else None,
        )

        return Namespace(**{**vars(self.args), **settings, **config})

    def read_cfg_file(self, config_file: str, section: str = None) -> Dict[str, Any]:
        if config_file is None:
            return dict()
        with open(config_file, mode="r") as f:
            config: Dict[str, Any] = json.load(f)
        return config if section is None else {**config["DEFAULT"], **config[section]}
