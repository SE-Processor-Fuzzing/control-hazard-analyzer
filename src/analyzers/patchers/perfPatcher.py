import logging
from pathlib import Path
from typing import Dict, Any

from src.analyzers.patchers.basePatcher import BasePatcher


class PerfPatcher:
    def __init__(self, settings: Dict[str, Any]):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings["log_level"])

        events_file: str = settings.get("events", "classic.c")
        events_file = "perf_events/" + events_file

        self.patcher = BasePatcher(settings, [events_file, "perfTemplate.c"])

    def patch(self, test_dir: Path, dst_dir: Path) -> None:
        return self.patcher.patch(test_dir, dst_dir)
