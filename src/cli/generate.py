import logging
import shutil
import random as rd
from pathlib import Path
from pprint import pformat
from typing import Optional, Any, Dict
from src.generators.code_gen import gen_test
from src.protocols.utility import Utility


class Generate(Utility):
    """Class for configuring tests by parameters passed to 'generate' command, creating directory to store
    generated test files, generating tests, and writing them into the file
    """

    def __init__(self) -> None:
        self.settings: Optional[Dict[str, Any]] = None
        self.repeats: Optional[int] = None
        self.seed: Optional[int] = None
        self.out_dir: Optional[Path] = None
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Dict[str, Any]) -> None:
        """Initialize local variables with passed parameters

        :param settings: Passed parameters to the command
        """
        self.settings = settings
        self.logger.setLevel(self.settings["log_level"])
        self.out_dir = Path(settings["out_dir"])
        self.seed = None if settings["seed"] is None else int(settings["seed"])
        self.repeats = int(settings["repeats"])

    def generate_tests(self, target_dir: Path, count: int, max_depth: int = 6, base_seed: int | None = None) -> None:
        """Generate a specified number of test files with provided amount of depth in the target directory

        :param target_dir: The directory where the test files will be generated
        :param count: The number of test files to generate
        :param max_depth: The maximum depth of the nesting, by default 6 (team convention)
        :param base_seed: Seed on the basis of which seeds for tests are generated.
         Base-seed the base seed also serve as a seed for the first test
        """
        print(f"[+]: Generate tests to '{target_dir.absolute()}'")
        if base_seed is None:
            base_seed = rd.randint(1, 10000)
            self.logger.info(f"No seed provided, assigned base-seed: {base_seed}")
        elif isinstance(base_seed, int):
            self.logger.info(f"Provided base-seed: {base_seed}")
        else:
            print("Provided seed is not an integer. No test generated. Exiting...")
            self.logger.warn("Provided seed is not an integer. No test generated. Exiting...")
            return
        rd.seed(base_seed)
        test_seeds = [base_seed] + [rd.randint(1, 10000) for _ in range(count - 1)]

        for i in range(count):
            print(f"[+]: Seed for test {i}: {test_seeds[i]}")
            self.logger.info(f"Seed for test {i}: {test_seeds[i]}")
            self._generate_test(target_dir.joinpath(f"test_{i}.c"), max_depth, test_seeds[i])

    def _generate_test(self, file: Path, max_depth: int, seed: int) -> None:
        """Generate a single test file at the specified path with the given maximum depth

        :param file: The path to the test file to be created
        :param max_depth: The maximum depth of the nesting
        :param seed: Seed for exact test generation

        """
        test = gen_test(max_depth, seed)
        if file.is_dir():
            self.logger.warn(f"Provided path {file} is not a file. Skipping this test.")
            return
        with open(file, "w") as f:
            self.logger.info(f"Write test into {file}")
            f.write(test)

    def create_empty_dir(self, dir_path: Path) -> None:
        """Ensure specified directory is empty by removing it if it exists and then creating a new empty directory

        :param dir_path: The path to the directory to be created
        """
        if dir_path.exists():
            shutil.rmtree(dir_path)
        dir_path.mkdir(parents=True)

    def run(self) -> None:
        """Set up the logger with the passed parameters,
        then check that provided parameters are not empty, then create directories for tests,
        generate seeds for every test based on provided seed and start generating tests
        """
        self.logger.info("Generate is running. Settings:")
        self.logger.info(pformat(self.settings))
        if self.out_dir is None or self.repeats is None:
            self.logger.warn("Out dir or repeats values are not provided. Exiting...")
            return
        self.create_empty_dir(self.out_dir)
        self.generate_tests(self.out_dir, count=self.repeats, base_seed=self.seed)
