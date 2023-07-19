import argparse
import configparser
import os
import shutil
import stat
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
        self.parser.add_argument("--dest_folder", default="out",
                                 help="Path to dist folder, if not exit it will be created")
        self.parser.add_argument("--repeats", default="1", help="Count of generated tests", type=int)

    def configurate(self, settings: Dict) -> Dict:
        result = dict()
        self.args, self.compiler_args = self.parser.parse_known_args()
        # default
        result["compiler"] = self.get_compiler()

        result["test_file"] = self.args.test_file
        result["config_file"] = self.args.config_file
        result["dest_folder"] = self.args.dest_folder
        result["repeats"] = self.args.repeats

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
        return self.args.compiler if (compiler := os.environ.get(
            "CC")) is None or self.args.compiler != self.parser.get_default("compiler") else compiler

    def create_folders(self, settings: dict):
        os.makedirs(settings["dest_folder"], exist_ok=True)
        os.makedirs(f"{settings['dest_folder']}/{settings['source_folder']}", exist_ok=True)
        os.makedirs(f"{settings['dest_folder']}/{settings['compiled_folder']}", exist_ok=True)
        os.makedirs(f"{settings['dest_folder']}/{settings['analyse_folder']}", exist_ok=True)
        os.chmod(settings['dest_folder'], stat.S_IWRITE)

    def clean_output_folder(self, dest_folder: str):
        shutil.rmtree(dest_folder)
