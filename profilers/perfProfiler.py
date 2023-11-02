from __future__ import annotations

import glob
import os.path
import subprocess
from pathlib import Path
from tempfile import mkdtemp
from typing import Dict

from src.builder import Builder


class PerfData:
    def __init__(self, data_dict: Dict[str, str] = {}):
        self.branches = int(data_dict.get("branches", -1))
        self.missed_branches = int(data_dict.get("missed_branches", -1))
        self.cache_bpu = int(data_dict.get("cache_BPU", -1))
        self.ticks = int(data_dict.get("cpu_clock", -1))
        self.instructions = int(data_dict.get("instructions", -1))

    def to_dict(self) -> Dict:
        data_dict: Dict = {}
        data_dict["branchPred.lookups"] = self.branches
        data_dict["branchPred.condIncorrect"] = self.missed_branches
        data_dict["branchPred.BTBUpdates"] = self.cache_bpu
        data_dict["simTicks"] = self.ticks
        data_dict["instructions"] = self.instructions
        return data_dict

    def __sub__(self, other) -> PerfData:
        if isinstance(other, PerfData):
            res: PerfData = PerfData()
            res.branches = self.branches - other.branches
            res.missed_branches = self.missed_branches - other.missed_branches
            res.cache_bpu = self.cache_bpu - other.cache_bpu
            res.ticks = self.ticks - other.ticks
            res.instructions = self.instructions - other.instructions
            return res
        else:
            raise TypeError

    def __str__(self) -> str:
        return str(self.to_dict())


class PerfProfiler:
    def __init__(self, builder: Builder):
        self.builder: Builder = builder
        self.temp_dir: Path = Path(mkdtemp())
        self.template_path = Path("profilers/attachments/perfTemplate.c")
        self.empty_test_path = Path("profilers/attachments/empty.c")

    def patch_test(self, src_test: Path, dest_test: Path) -> bool:
        dest_test.parent.mkdir(parents=True, exist_ok=True)
        if os.path.isfile(src_test):
            with open(dest_test, "wt") as writter:
                writter.write(f'#include "{src_test.absolute()}"\n')
                writter.write(f'#include "{self.template_path.absolute()}"\n')
                return True
        return False

    def add_empty_patched_test(self, destination_file: Path):
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        self.patch_test(self.empty_test_path, destination_file)

    def patch_tests_in_dir(self, src_dir: Path, dst_dir: Path):
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src_test in glob.glob(str(src_dir) + "/*.c"):
            src_test = Path(src_test)
            self.patch_test(src_test, dst_dir.joinpath(src_test.name))

    def output_to_dict(self, output: str) -> Dict[str, str]:
        data_dict: Dict[str, str] = {}
        for line in output.split("\n"):
            splitted = line.split(":")
            if len(splitted) >= 2:
                name, val = splitted[0], splitted[1]
                data_dict.update({name.strip(): val.strip()})
        return data_dict

    def get_stat(self, binary: Path) -> PerfData:
        execute_line = [
            "sudo",
            self.builder.settings.timeout_tool,
            self.builder.settings.timeout_duration,
            binary,
        ]
        try:
            if self.builder.settings.debug:
                print(f"perfProfiler is running. Executed command: {execute_line}")
            proc = subprocess.run(execute_line, stdout=subprocess.PIPE, check=True)
            # !!! process does not die, it just unhook from python
        except subprocess.TimeoutExpired:
            return PerfData()
        output = proc.stdout.decode()
        data = PerfData(self.output_to_dict(output))
        return data

    def get_stats_dir(self, dir: Path) -> Dict[str, PerfData]:
        data_dict: Dict[str, PerfData] = {}
        for binary in os.listdir(dir):
            data = self.get_stat(dir.joinpath(binary))
            if data.ticks >= 0:
                data_dict[binary.split(".")[0]] = data
        return data_dict

    def profile(self, test_dir: Path) -> Dict[str, Dict]:
        src_dir = self.temp_dir.joinpath("src/")
        build_dir = self.temp_dir.joinpath("bins/")

        self.patch_tests_in_dir(test_dir, src_dir)
        self.add_empty_patched_test(src_dir.joinpath(self.empty_test_path.name))
        self.builder.build(src_dir, build_dir)
        analyzed = self.get_stats_dir(build_dir)

        res: Dict[str, Dict] = {}
        for key in analyzed:
            if key != "empty":
                analyzed[key] = analyzed[key] - analyzed[self.empty_test_path.name.split(".")[0]]
                res.update({key: analyzed[key].to_dict()})

        return res
