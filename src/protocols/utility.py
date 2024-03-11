from argparse import ArgumentParser, Namespace
from typing import List, Protocol

from src.protocols.subparser import SubParser


class Utility(Protocol):
    def run(self) -> None: ...

    def configurate(self, settings: Namespace) -> None: ...

    def add_parser_arguments(self, subparser: SubParser) -> ArgumentParser: ...

    def parse_args(self, args: List[str]) -> Namespace: ...
