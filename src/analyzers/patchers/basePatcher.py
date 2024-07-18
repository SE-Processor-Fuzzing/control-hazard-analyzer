import glob
import logging
import sys
from pathlib import Path
from typing import Dict, Any

ATTACH_DIR = "src/analyzers/patchers/attachments/"


class BasePatcher:
    def __init__(self, settings: Dict[str, Any], templates: list[str]):
        self.settings = settings

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings["log_level"])

        launch_dir = Path(sys.argv[0]).parent
        self.empty_test_path = launch_dir.joinpath(ATTACH_DIR, "empty.c")
        self.template_paths = [launch_dir.joinpath(ATTACH_DIR, name) for name in templates]

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        dest_test.parent.mkdir(parents=True, exist_ok=True)
        if src_test.is_file():
            with open(dest_test, "wt") as writter:
                for tmp_pth in self.template_paths:
                    writter.write(f'#include "{tmp_pth.absolute()}"\n')
                writter.write(f'#include "{src_test.absolute()}"\n')
                return True
        return False

    def add_empty_patched_test(self, destination_file: Path) -> None:
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        self.patch_test(self.empty_test_path, destination_file)

    def patch_tests_in_dir(self, src_dir: Path, dst_dir: Path) -> None:
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src_test in glob.glob(str(src_dir) + "/*.c"):
            src_test_path = Path(src_test)
            self.patch_test(src_test_path, dst_dir.joinpath(src_test_path.name))

    def patch(self, test_dir: Path, dst_dir: Path) -> None:
        self.patch_tests_in_dir(test_dir, dst_dir)
        self.add_empty_patched_test(dst_dir.joinpath(self.empty_test_path.name))
