import logging
import os
import subprocess
from argparse import Namespace
from pathlib import Path


class Builder:
    def __init__(self, settings: Namespace):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)

    def build(
        self,
        src_dir: Path,
        destination_dir: Path,
        additional_flags: list[str] = [],
    ):
        list_of_src_files = os.listdir(src_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)
        for test_file in list_of_src_files:
            execute_line = (
                [self.settings.compiler, src_dir.joinpath(test_file)]
                + self.settings.compiler_args
                + ["-o", destination_dir.joinpath(f"{test_file}.out")]
                + additional_flags
            )
            self.logger.info(f"Builder(Analyze) is running. Executed command:{execute_line}")

            subprocess.run(execute_line, check=True)
