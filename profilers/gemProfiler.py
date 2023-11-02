import re
import os
import subprocess

from typing import Dict
from pathlib import Path
from tempfile import mkdtemp
from builders.builder import Builder


class GemProfiler:
    def __init__(self, builder: Builder):
        self.builder: Builder = builder
        self.temp_path = Path(mkdtemp())
        self.template_path = Path("profilers/attachments/gemTemplate.c")
        self.empty_test_path = Path("/home/joskiy/Projects/BIOHazard/profilers/attachments/empty.c")

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        if os.path.isfile(src_test):
            with open(dest_test, "w+") as file:
                file.write(f'#include "{src_test.absolute()}\n"')
                file.write(f'#include "{self.template_path.absolute()}\n"')
            return True

        return False

    def patch_tests_in_dir(self, src_dir: Path, dest_dir: Path) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        for src_test in os.listdir(src_dir):
            src_test = Path(src_test)
            self.patch_test(src_test, dest_dir.joinpath(src_test.name))

    def get_stats_from_file(self, stat_path: Path) -> Dict[str:int]:
        stats = {}
        with open(stat_path, "r") as file:
            for line in file.readlines():
                if re.search("branch", line) and not re.search("Ratio", line):
                    temp = re.split(r"\s{2,}", line)
                    temp[0] = re.sub("system.cpu.", "", temp[0])
                    stats[temp[0]] = int(temp[1])

        return stats

    def get_stats_from_dir(self, stats_dir: Path) -> Dict[str:Dict]:
        stats_dict = {}
        for stat_path in os.listdir(stats_dir):
            test_name = stat_path.split(".")[0]
            stats_dir[test_name] = self.get_stats(stat_path)

        return stats_dict

    def run_bins_in_dir(bin_dir: Path, dest_dir: Path) -> None:
        for binary in os.listdir(bin_dir):
            execute_line = ["sudo", binary]
            subprocess.run(execute_line, check=True)

    def correct(analyzed: Dict[str:Dict]) -> Dict[str:Dict]:
        for file_name in analyzed.keys():
            if file_name != "empty":
                analyzed[file_name] -= analyzed["empty"]

        return analyzed

    def profile(self, test_dir: Path) -> Dict[str:Dict]:
        src_dir = self.temp_path.joinpath("src")
        build_dir = self.temp_path.joinpath("bins")
        stats_dir = self.temp_path.joinpath("stats")

        self.patch_test(self.empty_test_path, src_dir)
        self.patch_tests_in_dir(test_dir, src_dir)
        self.builder.build(src_dir, build_dir)
        self.run_bins_in_dir(build_dir, stats_dir)

        analyzed = self.get_stats_from_dir(stats_dir)

        return self.correct(analyzed)
