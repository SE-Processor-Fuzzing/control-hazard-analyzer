import os.path
from pathlib import Path
from profile import Profile


class PerfProfiler(Profile):
    def __init__(self):
        super().__init__()
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
