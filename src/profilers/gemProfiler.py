import logging
import re
import shlex
import shutil
import signal
import subprocess
from argparse import Namespace
from pathlib import Path
from tempfile import mkdtemp
from typing import Dict, Set

from src.helpers.builder import Builder


class GemProfiler:
    BINARY_PLACEHOLDER = "{{GEM5_TARGET_BINARY}}"

    def __init__(self, builder: Builder, settings: Namespace):
        self.settings = settings
        self.builder: Builder = builder
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)
        self.temp_dir = Path(mkdtemp())
        self.template_path = Path("src/profilers/attachments/gemTemplate.c")
        self.empty_test_path = Path("src/profilers/attachments/empty.c")
        self.gem5_home = Path(self.settings.__dict__.get("gem5_home", ""))
        self.target_isa = self.settings.__dict__.get("target_isa", "").lower()

        self.gem5_bin_path = self.settings.__dict__.get(
            "gem5_bin_path",
            self.gem5_home.joinpath("build", self.target_isa.capitalize(), "gem5.opt"),
        )

        self.sim_script_path = self.settings.__dict__.get(
            "sim_script_path",
            self.gem5_home.joinpath("configs/deprecated/example/se.py"),
        )

        self.sim_script_args = self.settings.__dict__.get(
            "sim_script_args", f"--cpu-type=O3CPU --caches -c {self.BINARY_PLACEHOLDER}"
        )
        self.sim_script_args = shlex.split(self.sim_script_args)

        self.build_additional_flags = [
            f"-I{self.gem5_home.joinpath('include')}",
            f"-I{self.gem5_home.joinpath('util/m5/src')}",
            "-fPIE",
            f"-Wl,-L{self.gem5_home}/util/m5/build/{self.target_isa}/out",
            "-Wl,-lm5",
            "--static",
        ]

        if self.target_isa == "":
            raise Exception("No target isa provided")

    def __del__(self):
        shutil.rmtree(self.temp_dir)

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
        for stat_path in stats_dir.iterdir():
            test_name = stat_path.name.split(".")[0]
            stats_dict[test_name] = self.get_stats_from_file(stats_dir.joinpath(stat_path))

        return stats_dict

    def run_bins_in_dir(self, bin_dir: Path, dest_dir: Path) -> Set[str]:
        fully_runned = set()
        dest_dir.mkdir(parents=True, exist_ok=True)
        for binary in bin_dir.iterdir():
            is_full_run = True
            bin_path = bin_dir.joinpath(binary)
            stat_file = f"{dest_dir}/{bin_path.name.split('.')[0]}.txt"
            script_args = list(
                map(
                    lambda x: x.replace(self.BINARY_PLACEHOLDER, str(bin_path)),
                    self.sim_script_args,
                )
            )
            execute_line = [
                self.gem5_bin_path,
                f"--outdir={self.temp_dir}/m5out",
                f"--stats-file={stat_file}",
                self.sim_script_path,
            ] + script_args
            self.logger.info(f"gemProfiler is running. Executed line: {execute_line}")

            proc = subprocess.Popen(execute_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                proc.wait(self.builder.settings.timeout)
            except subprocess.TimeoutExpired:
                proc.send_signal(signal.SIGINT)
                is_full_run = False
                while proc.poll() is None:
                    pass

            if is_full_run:
                fully_runned.add(bin_path.name.split(".")[0])

        return fully_runned

    def correct(self, analyzed: Dict[str, Dict], full_runned: Set[str]) -> Dict[str, Dict]:
        for file_name in analyzed.keys():
            if file_name == "empty" or not analyzed[file_name]:
                continue
            for key in analyzed["empty"].keys():
                analyzed[file_name][key] -= analyzed["empty"][key]
            analyzed[file_name]["isFull"] = file_name in full_runned

        analyzed.pop("empty")
        return analyzed

    def profile(self, test_dir: Path) -> Dict[str, Dict]:
        src_dir = self.temp_dir.joinpath("src/")
        build_dir = self.temp_dir.joinpath("bins/")
        stats_dir = self.temp_dir.joinpath("stats/")

        self.patch_tests_in_dir(test_dir.absolute(), src_dir)
        self.patch_test(self.empty_test_path, src_dir.joinpath(self.empty_test_path.name))
        self.builder.build(src_dir, build_dir, self.build_additional_flags)
        full_runned = self.run_bins_in_dir(build_dir, stats_dir)
        analyzed = self.get_stats_from_dir(stats_dir)

        return self.correct(analyzed, full_runned)
