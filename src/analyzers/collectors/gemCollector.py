import logging
import re
import shlex
import signal
import subprocess
from pathlib import Path
from typing import Dict, Set, Any

from src.protocols.collector import DictSI


class GemCollector:
    BINARY_PLACEHOLDER = "{{GEM5_TARGET_BINARY}}"

    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings["log_level"])

        self.gem5_home = Path(self.settings.get("gem5_home", ""))
        self.target_isa = self.settings.get("target_isa", "").lower()

        self.gem5_bin_path = self.settings.get(
            "gem5_bin_path",
            self.gem5_home.joinpath("build", self.target_isa.upper(), "gem5.opt"),
        )

        self.sim_script_path = self.settings.get(
            "sim_script_path",
            self.gem5_home.joinpath("configs/deprecated/example/se.py"),
        )

        self.sim_script_args = self.settings.get(
            "sim_script_args", f"--cpu-type=O3CPU --caches -c {self.BINARY_PLACEHOLDER}"
        )
        self.sim_script_args = shlex.split(self.sim_script_args)

        if self.target_isa == "":
            raise Exception("No target isa provided")

    def get_stats_from_file(self, stat_path: Path) -> DictSI:
        stats: DictSI = {}
        with open(stat_path, "r") as file:
            for line in file.readlines():
                if re.search("branch", line) and not re.search("Ratio", line):
                    temp = re.split(r"\s{2,}", line)
                    temp[0] = re.sub("system.cpu.", "", temp[0])
                    stats[temp[0]] = int(temp[1])

        return stats

    def get_stats_from_dir(self, stats_dir: Path) -> Dict[str, DictSI]:
        stats_dict: Dict[str, DictSI] = {}
        for stat_path in stats_dir.iterdir():
            test_name = stat_path.name.split(".")[0]
            stats_dict[test_name] = self.get_stats_from_file(stats_dir.joinpath(stat_path))

        return stats_dict

    def run_bins_in_dir(self, bin_dir: Path, dest_dir: Path) -> Set[str]:
        fully_runned: set[str] = set()
        dest_dir.mkdir(parents=True, exist_ok=True)
        for binary in bin_dir.iterdir():
            if binary.is_dir():
                continue

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
                f"--outdir={bin_dir.joinpath('m5out')}",
                f"--stats-file={stat_file}",
                self.sim_script_path,
            ] + script_args
            self.logger.info(f"gemAnalyzer is running. Executed line: {execute_line}")

            proc = subprocess.Popen(execute_line, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            try:
                proc.wait(self.settings["timeout"])
            except subprocess.TimeoutExpired:
                proc.send_signal(signal.SIGINT)
                is_full_run = False
                while proc.poll() is None:
                    pass

            if is_full_run:
                fully_runned.add(bin_path.name.split(".")[0])

        return fully_runned

    def correct(self, analyzed: Dict[str, DictSI], full_runned: Set[str]) -> Dict[str, DictSI]:
        for file_name in analyzed.keys():
            if file_name == "empty" or not analyzed[file_name]:
                continue
            for key in analyzed["empty"].keys():
                analyzed[file_name][key] -= analyzed["empty"][key]
            analyzed[file_name]["isFull"] = file_name in full_runned

        analyzed.pop("empty")
        return analyzed

    def collect(self, bin_dir: Path) -> Dict[str, DictSI]:
        stats_dir = bin_dir.joinpath("stats/")

        full_runned = self.run_bins_in_dir(bin_dir, stats_dir)
        analyzed = self.get_stats_from_dir(stats_dir)

        return self.correct(analyzed, full_runned)
