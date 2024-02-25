from __future__ import annotations
from argparse import Namespace

import glob
import logging
from pathlib import Path
from src.analyzers.patchers import ATTACH_DIR
import sys


class PerfPatcher:
    def __init__(self, settings: Namespace):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)
        launch_dir = Path(sys.argv[0]).parent
        self.template_path = launch_dir.joinpath(ATTACH_DIR, "perfTemplate.c")
        self.empty_test_path = launch_dir.joinpath(ATTACH_DIR, "empty.c")

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        dest_test.parent.mkdir(parents=True, exist_ok=True)
        if src_test.is_file():
            with open(dest_test, "wt") as writter:
                writter.write(f'#include "{self.template_path.absolute()}"\n')
                writter.write(f'#include "{src_test.absolute()}"\n')
                return True
        return False

    def add_empty_patched_test(self, destination_file: Path):
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        self.patch_test(self.empty_test_path, destination_file)

    def patch_tests_in_dir(self, src_dir: Path, dst_dir: Path):
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src_test in glob.glob(str(src_dir) + "/*.c"):
            src_test = Path(src_test)
            self.patch_test(src_test, dst_dir.joinpath(src_test.name))

    def patch(self, test_dir: Path, dst_dir: Path):
        self.patch_tests_in_dir(test_dir, dst_dir)
        self.add_empty_patched_test(dst_dir.joinpath(self.empty_test_path.name))
