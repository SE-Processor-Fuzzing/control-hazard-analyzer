import logging
import shutil
from pathlib import Path
from pprint import pformat
from typing import Optional, Any, Dict
from src.generators.code_gen import gen_test
from src.protocols.utility import Utility


class Generate(Utility):
    def __init__(self) -> None:
        self.settings: Optional[Dict[str, Any]] = None
        self.repeats: Optional[int] = None
        self.out_dir: Optional[Path] = None
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Dict[str, Any]) -> None:
        self.settings = settings
        self.logger.setLevel(self.settings["log_level"])
        self.out_dir = Path(settings["out_dir"])
        self.repeats = int(settings["repeats"])

    def generate_tests(
        self,
        target_dir: Path,
        count: int,
        max_depth: int = 6,
    ) -> None:
        print(f"[+]: Generate tests to '{target_dir.absolute()}'")
        for i in range(count):
            self._generate_test(target_dir.joinpath(f"test_{i}.c"), max_depth)

    def _generate_test(self, file: Path, max_depth: int) -> None:
        test = gen_test(max_depth)
        if file.is_dir():
            self.logger.warn(f"Provided path {file} is not a file. Skipping this test.")
            return
        with open(file, "w") as f:
            self.logger.info(f"Write test into {file}")
            f.write(test)

    def create_empty_dir(self, dir_path: Path) -> None:
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)

    def run(self) -> None:
        self.logger.info("Generate is running. Settings:")
        self.logger.info(pformat(self.settings))
        if self.out_dir is None or self.repeats is None:
            self.logger.warn("Out dir or repeats values are not provided. Exiting...")
            return
        self.create_empty_dir(self.out_dir)
        self.generate_tests(self.out_dir, self.repeats)

    default_params = {
        "utility": "generate",
        "out_dir": "tests",
        "repeats": 1,
        "log_level": "WARNING"
    }
