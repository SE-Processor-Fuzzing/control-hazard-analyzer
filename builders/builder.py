import os
import subprocess
from typing import Dict


class Builder:
    def __init__(self, settings: Dict):
        self.settings = settings

    def build(self, src_folder: str, destination_folder: str):
        list_of_src_files = os.listdir(src_folder)
        print(list_of_src_files)
        for test_file in list_of_src_files:
            execute_line = [self.settings["compiler"], f"{src_folder}/{test_file}"] + self.settings["compiler_args"] + \
                           ["-o", f"{destination_folder}/{test_file}.out"]

            print(" ".join(execute_line))

            subprocess.run(
                execute_line,
                check=True,
            )
