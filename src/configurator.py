import argparse
import configparser
import os
from typing import Dict


class Configurator:
    def __init__(self):
        self.args = None
        self.compiler_args = None
        self.parser = argparse.ArgumentParser(
            prog="BIOHazard",
            description="This script generate and test code on some platforms",
        )
        self.parser.add_argument("--test_file", default="test.c", help="Path to test file")
        self.parser.add_argument("--compiler", default="gcc", help="Path to C compiler")
        self.parser.add_argument("--config_file", default="config.cfg", help="Path to .cfg file")
        self.parser.add_argument("--section_in_config", default="DEFAULT",
                                 help="Set the custom section in config file (DEFAULT by default)")

    def configurate(self, settings: Dict) -> Dict:
        self.args, self.compiler_args = self.parser.parse_known_args()
        result = dict()
        # default
        result["compiler"] = self.get_compiler()
        result["test_file"] = self.args.test_file
        result["config_file"] = self.args.config_file
        result["compiler_args"] = self.compiler_args
        # just for debug
        # print(self.compiler_args)
        config_settings = self.read_cfg_file(result["config_file"], self.args.section_in_config)
        result = {**settings, **config_settings, **result}
        return result

    def read_cfg_file(self, config_file: str, section: str) -> Dict:
        parser = configparser.ConfigParser()
        parser.read(config_file)
        return dict(parser[section])

    def get_compiler(self):
        return self.args.compiler if (compiler := os.environ.get("CC")) is None else compiler
