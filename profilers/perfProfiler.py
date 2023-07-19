import os.path
from pathlib import Path
from profile import Profile
from tempfile import mkdtemp
import glob


class PerfProfiler(Profile):
    def __init__(self):
        super().__init__()

        self.temp_dir: Path = Path(mkdtemp())
        with open(Path("profilers/perfProfiler/template.c"), "rt") as reader:
            strings = reader.read().split("\n")
            self.template: str = "\n".join(strings[1:])

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        if os.path.isfile(src_test):
            with open(dest_test, "wt") as writter:
                writter.write(f'#include "{os.path.abspath(src_test)}"\n')
                writter.write(self.template)
                return True
        return False

    def patch_tests_in_dir(self, src_dir: Path, dst_dir: Path) -> bool:
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src_test in glob.glob(str(src_dir) + "/*.c"):
            src_test = Path(src_test)
            self.patch_test(src_test, self.temp_dir.joinpath(src_test.name))
            return True
        return False
