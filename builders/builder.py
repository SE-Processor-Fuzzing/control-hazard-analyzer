import subprocess
from typing import Dict


class Builder:
    def __init__(self, settings: Dict):
        self.settings = settings

    def build(self):
        # print(os.name)
        # print(os.getcwd())

        output_file = f"{self.settings['dest_folder']}/a.out"

        execute_line = [self.settings["compiler"], self.settings["test_file"]] + self.settings["compiler_args"] + \
                       ["-o", f"{self.settings['dest_folder']}/{self.settings['compiled_folder']}/a.out"]

        print(" ".join(execute_line))

        subprocess.run(
            execute_line,
            check=True,
        )
