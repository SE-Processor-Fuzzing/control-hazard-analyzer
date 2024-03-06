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
        self.default_additional_flags: list[str] = []

    def set_default_additional_flags(self, additional_flags: list[str]) -> None:
        self.default_additional_flags = additional_flags

    def build(
        self,
        src_file: Path,
        destination_file: Path,
        additional_flags: list[str] | None = None,
    ) -> None:
        if additional_flags is None:
            additional_flags = self.default_additional_flags

        destination_file.parent.mkdir(parents=True, exist_ok=True)
        execute_line = (
            [self.settings.compiler, src_file]
            + self.settings.compiler_args
            + ["-o", destination_file]
            + additional_flags
        )
        self.logger.info(f"Builder(Analyze) is running. Executed command:{execute_line}")

        subprocess.run(execute_line, check=True)

    def build_dir(
        self,
        src_dir: Path,
        destination_dir: Path,
        additional_flags: list[str] | None = None,
    ):
        list_of_src_files = os.listdir(src_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        for test_file in list_of_src_files:
            self.build(src_dir.joinpath(test_file), destination_dir.joinpath(f"{test_file}.out"), additional_flags)
