from __future__ import annotations

import sys
from typing import Any, Dict, List, Tuple, TypeAlias

from src.protocols.collector import DictSI

TestRes: TypeAlias = Tuple[bytes | None, bool]


class PerfData:
    def __init__(self, data_dict: Dict[str, str] | None = None, is_full: bool = True):
        if data_dict is None:
            data_dict = {}

        self.branches = int(data_dict.get("branches", -1))
        self.missed_branches = int(data_dict.get("missed_branches", -1))
        self.cache_bpu = int(data_dict.get("cache_BPU", -1))
        self.ticks = int(data_dict.get("cpu_clock", -1))
        self.instructions = int(data_dict.get("instructions", -1))
        self.is_full = is_full

    def to_dict(self) -> DictSI:
        data_dict: DictSI = {}
        data_dict["branchPred.lookups"] = self.branches
        data_dict["branchPred.condIncorrect"] = self.missed_branches
        data_dict["branchPred.BTBUpdates"] = self.cache_bpu
        data_dict["simTicks"] = self.ticks
        data_dict["instructions"] = self.instructions
        data_dict["isFull"] = self.is_full
        return data_dict

    def __sub__(self, other: Any) -> PerfData:
        if isinstance(other, PerfData):
            res: PerfData = PerfData()
            res.branches = self.branches - other.branches
            res.missed_branches = self.missed_branches - other.missed_branches
            res.cache_bpu = self.cache_bpu - other.cache_bpu
            res.ticks = self.ticks - other.ticks
            res.instructions = self.instructions - other.instructions
            res.is_full = self.is_full
            return res
        else:
            raise TypeError

    def __str__(self) -> str:
        return str(self.to_dict())

    def max(self, const: int) -> None:
        self.branches = max(self.branches, const)
        self.missed_branches = max(self.missed_branches, const)
        self.cache_bpu = max(self.cache_bpu, const)
        self.ticks = max(self.ticks, const)
        self.instructions = max(self.instructions, const)


class PerfParser:
    @staticmethod
    def output_to_dict(output: str) -> Dict[str, str]:
        data_dict: Dict[str, str] = {}
        for line in output.split("\n"):
            splitted = line.split(":")
            if len(splitted) >= 2:
                name, val = splitted[0], splitted[1]
                data_dict.update({name.strip(): val.strip()})
        return data_dict

    @staticmethod
    def test_res_to_data(out_tup: TestRes) -> PerfData:
        stream, is_full = out_tup
        dic: Dict[str, str] = {}
        if stream is not None:
            dic = PerfParser.output_to_dict(stream.decode())
        return PerfData(dic, is_full)

    @staticmethod
    def get_meddian(stats: List[PerfData]) -> PerfData | None:
        def _get_meddian(stats: List[PerfData]) -> PerfData | None:
            def missed_pct(dt: PerfData) -> float:
                if dt.branches == 0:
                    dt.branches = 1
                return dt.missed_branches / dt.branches

            stats.sort(key=missed_pct)
            if len(stats) > 0:
                return stats[(len(stats) // 2)]
            return None

        stats = stats.copy()
        average = _get_meddian(stats)
        full_stats: List[PerfData] = []
        for stat in stats:
            if stat.is_full:
                full_stats.append(stat)
        full_average = _get_meddian(full_stats)
        if full_average is not None:
            average = full_average

        return average

    @staticmethod
    def correct(out_res: Dict[str, List[TestRes]], key_empty_test: str = "empty") -> Dict[str, DictSI]:
        analyzed_buf = {
            key: PerfParser.get_meddian(list(map(PerfParser.test_res_to_data, lst))) for key, lst in out_res.items()
        }
        analyzed_average: Dict[str, PerfData] = {}
        for key, val in analyzed_buf.items():
            if val is not None:
                analyzed_average[key] = val
            else:
                print(f"[-]: Error: can't get average result of '{key}' test", file=sys.stderr)

        analyzed_average[key_empty_test].max(0)
        corrected: Dict[str, DictSI] = {}
        for key in analyzed_average:
            if key != key_empty_test:
                analyzed_average[key] = analyzed_average[key] - analyzed_average[key_empty_test]
                corrected.update({key: analyzed_average[key].to_dict()})
        return corrected
