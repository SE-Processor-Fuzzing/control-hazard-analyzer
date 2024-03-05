from __future__ import annotations
from argparse import Namespace
import logging
from pathlib import Path
from typing import Dict

from src.analyzers.baseAnalyzer import BaseAnalyzer
from src.analyzers.collectors.perfCollector import PerfCollector
from src.analyzers.patchers.perfPatcher import PerfPatcher
from src.protocols.analyzer import Analyzer
from src.helpers.builder import Builder


class PerfAnalyzer:
    def __init__(self, builder: Builder, settings: Namespace):
        self.settings = settings
        self.builder: Builder = builder
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)

        self.base: Analyzer = BaseAnalyzer(PerfPatcher(settings), self.builder, PerfCollector(settings), settings)

    def analyze(self, test_dir: Path) -> Dict[str, Dict]:
        return self.base.analyze(test_dir)
