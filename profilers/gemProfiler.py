import os
import re
import shutil
import signal
import subprocess
from argparse import Namespace
from pathlib import Path
from tempfile import mkdtemp
from typing import Dict

from src.builder import Builder


class GemProfiler:
    def __init__(self, builder: Builder, settings: Namespace):
        self.settings = settings
        self.builder: Builder = builder
        self.temp_dir = Path(mkdtemp())
        self.template_path = Path("profilers/attachments/gemTemplate.c")
        self.empty_test_path = Path("profilers/attachments/empty.c")
        self.gem5_home = self.settings.__dict__.get("gem5_home", "")
        self.target_isa = self.settings.__dict__.get("target_isa", "")
        self.gem5_bin_path = self.settings.__dict__.get(
            "gem5_bin_path",
            os.path.join(self.gem5_home, "build", self.target_isa.capitalize(), "gem5.opt"),
        )
        self.sim_script_path = self.settings.__dict__.get(
            "sim_script_path",
            os.path.join(self.gem5_home, "configs/deprecated/example/se.py"),
        )
        if self.target_isa == "":
            raise Exception("No target isa provided")

    def __del__(self):
        shutil.rmtree(self.temp_dir)

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        if os.path.isfile(src_test):
            with open(dest_test, "w+") as file:
                file.write(f'#include "{src_test.absolute()}"\n')
                file.write(f'#include "{self.template_path.absolute()}"\n')
            return True

        return False

    def patch_tests_in_dir(self, src_dir: Path, dest_dir: Path) -> None:
        dest_dir.mkdir(parents=True, exist_ok=False)
        for src_test in os.listdir(src_dir):
            src_test = src_dir.joinpath(src_test)
            dest_test = dest_dir.joinpath(src_test.name)
            self.patch_test(src_test, dest_test)

    def get_stats_from_file(self, stat_path: Path) -> Dict[str, int]:
        stats = {}
        with open(stat_path, "r") as file:
            for line in file.readlines():
                if re.search("branch", line) and not re.search("Ratio", line):
                    temp = re.split(r"\s{2,}", line)
                    temp[0] = re.sub("system.cpu.", "", temp[0])
                    stats[temp[0]] = int(temp[1])

        return stats

    def get_stats_from_dir(self, stats_dir: Path) -> Dict[str, Dict]:
        stats_dict = {}
        for stat_path in os.listdir(stats_dir):
            test_name = stat_path.split(".")[0]
            stats_dict[test_name] = self.get_stats_from_file(stats_dir.joinpath(stat_path))

        return stats_dict

    def run_bins_in_dir(self, bin_dir: Path, dest_dir: Path) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        for binary in os.listdir(bin_dir):
            bin_path = bin_dir.joinpath(binary)
            execute_line = [
                self.gem5_bin_path,
                f"--outdir={self.temp_dir}/m5out",
                f"--stats-file={dest_dir}/{bin_path.name.split('.')[0]}.txt",
                self.sim_script_path,
                "--cpu-type=O3CPU",
                "--caches",
                "-c",
                bin_path,
            ]
            if self.settings.debug:
                print(f"gemProfiler is running. Executed line: {execute_line}")
            proc = subprocess.Popen(execute_line, stdout=subprocess.PIPE)
            try:
                proc.wait(self.builder.settings.timeout)
            except subprocess.TimeoutExpired:
                proc.send_signal(signal.SIGINT)

    def correct(self, analyzed: Dict[str, Dict]) -> Dict[str, Dict]:
        for file_name in analyzed.keys():
            if file_name != "empty":
                for key in analyzed["empty"].keys():
                    analyzed[file_name][key] -= analyzed["empty"][key]

        return analyzed

    def profile(self, test_dir: Path) -> Dict[str, Dict]:
        src_dir = self.temp_dir.joinpath("src/")
        build_dir = self.temp_dir.joinpath("bins/")
        stats_dir = self.temp_dir.joinpath("stats/")
        gem_additional_flags = [
            f"-I{os.path.join(self.gem5_home, 'include')}",
            f"-I{os.path.join(self.gem5_home, 'util/m5/src')}",
            "-fPIE",
            f"-Wl,-L{self.gem5_home}/util/m5/build/{self.target_isa}/out",
            "-Wl,-lm5",
            "--static",
        ]
        self.patch_tests_in_dir(test_dir.absolute(), src_dir)
        self.patch_test(self.empty_test_path, src_dir.joinpath(self.empty_test_path.name))
        self.builder.build(src_dir, build_dir, gem_additional_flags)
        self.run_bins_in_dir(build_dir, stats_dir)
        analyzed = self.get_stats_from_dir(stats_dir)

        return self.correct(analyzed)
