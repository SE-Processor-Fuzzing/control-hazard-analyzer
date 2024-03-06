from queue import Queue
from typing import Dict, Protocol

from src.helpers.backGroundBuilder import ChanSignal


class QueueCollector(Protocol):
    def collect(self, build_channel: Queue[ChanSignal]) -> Dict[str, Dict]:
        ...
