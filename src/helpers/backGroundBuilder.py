from dataclasses import dataclass
import logging
import os
from argparse import Namespace
from pathlib import Path
from queue import Queue
import threading
from typing import TypeAlias

from src.helpers.builder import Builder


class CSignal:
    class End:
        pass

    @dataclass
    class BuiltFile:
        f: Path


ChanSignal: TypeAlias = CSignal.BuiltFile | CSignal.End


class BGBuilder:
    # TODO: rewrite it more thread safety

    def __init__(self, settings: Namespace, builder: Builder | None = None):
        self.settings = settings
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(self.settings.log_level)

        if builder is None:
            builder = Builder(settings)
        self.builder = builder

    def build(
        self,
        src_file: Path,
        destination_file: Path,
        additional_flags: list[str] | None = None,
    ):
        self.builder.build(src_file, destination_file, additional_flags)

    def _build_dir(
        self,
        src_dir: Path,
        destination_dir: Path,
        out_channel: Queue[ChanSignal],
        additional_flags: list[str] | None = None,
    ):
        list_of_src_files = os.listdir(src_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        for test_file in list_of_src_files:
            out_file = destination_dir.joinpath(f"{test_file}.out")
            self.build(src_dir.joinpath(test_file), out_file, additional_flags)
            out_channel.put(CSignal.BuiltFile(out_file))

        out_channel.put(CSignal.End())

    def build_dir(
        self,
        src_dir: Path,
        destination_dir: Path,
        additional_flags: list[str] | None = None,
    ) -> Queue[ChanSignal]:
        out_channel: Queue[ChanSignal] = Queue()
        threading.Thread(
            target=self._build_dir,
            args=(src_dir, destination_dir, out_channel, additional_flags),
        ).start()
        return out_channel
