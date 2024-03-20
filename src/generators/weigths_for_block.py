from dataclasses import dataclass
from typing import Tuple


@dataclass
class WeightsForBlocks:
    def_block: int = 1
    calc_block: int = 1
    for_block: int = 1
    if_block: int = 1
    blocks_cut: Tuple[int, int] = (1, 2)  # interval of the number of blocks in each {...}
