from argparse import Namespace
import os
from pathlib import Path
import subprocess


class Builder:
    def __init__(self, settings: Namespace):
        self.settings = settings

    def build(self, src_folder: Path, destination_folder: Path):
        list_of_src_files = os.listdir(src_folder)
        destination_folder.mkdir(parents=True, exist_ok=True)
        for test_file in list_of_src_files:
            execute_line = (
                [self.settings.compiler, src_folder.joinpath(test_file)]
                + self.settings.compiler_args
                + ["-o", destination_folder.joinpath(f"{test_file}.out")]
            )

            # print(" ".join(execute_line))

            subprocess.run(
                execute_line,
                check=True,
            )
