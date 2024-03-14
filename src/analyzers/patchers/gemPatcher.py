import logging
import sys
from argparse import Namespace
from pathlib import Path

from src.analyzers.patchers import ATTACH_DIR


class GemPatcher:
    def __init__(self, settings: Namespace):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)

        launch_dir = Path(sys.argv[0]).parent
        self.template_path = launch_dir.joinpath(ATTACH_DIR, "gemTemplate.c")
        self.empty_test_path = launch_dir.joinpath(ATTACH_DIR, "empty.c")

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        if src_test.is_file():
            with open(dest_test, "w+") as file:
                file.write(f'#include "{src_test.absolute()}"\n')
                file.write(f'#include "{self.template_path.absolute()}"\n')
            return True

        return False

    def patch_tests_in_dir(self, src_dir: Path, dest_dir: Path) -> None:
        dest_dir.mkdir(parents=True, exist_ok=False)
        for src_test in src_dir.iterdir():
            src_test = src_dir.joinpath(src_test)
            dest_test = dest_dir.joinpath(src_test.name)
            self.patch_test(src_test, dest_test)

    def patch(self, test_dir: Path, dst_dir: Path) -> None:
        self.patch_tests_in_dir(test_dir.absolute(), dst_dir)
        self.patch_test(self.empty_test_path, dst_dir.joinpath(self.empty_test_path.name))
