import logging
from argparse import Namespace
from pathlib import Path

from src.analyzers.patchers.basePatcher import BasePatcher


class GemPatcher:
    def __init__(self, settings: Namespace):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)

        self.patcher = BasePatcher(settings, ["gemTemplate.c"])

    def patch(self, test_dir: Path, dst_dir: Path) -> None:
        return self.patcher.patch(test_dir, dst_dir)
