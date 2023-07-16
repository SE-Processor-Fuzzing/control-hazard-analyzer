from typing import Dict
import argparse


class Configurator():
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog="BIOHazard",
            description="This script generate and test code on some platforms",
        )
        self.parser.add_argument("--test_file", default="test.c", help="Path to test file")
        self.parser.add_argument("--compiler", default="gcc", help="Path to C compiler")
        self.args, self.compiler_args = self.parser.parse_known_args()
    def configurate(self, setting: Dict):
        #default
        setting["compiler"] = self.args.compiler
        setting["test_file"] = self.args.test_file
        setting["compiler_args"] = self.compiler_args
        # just for debug
        # print(self.compiler_args)

