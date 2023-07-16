import os
import subprocess
from typing import Dict


class Builder:
    def __init__(self, settings: Dict):
        self.settings = settings

    def build(self):
        # print(os.name)
        # print(os.getcwd())
        execute_line = [self.settings["compiler"], self.settings["test_file"]] + self.settings["compiler_args"]
        output = subprocess.run(
            execute_line,
            check=True,
        )
        # just for debug
        # print(" ".join(execute_line))
        # print(output)
