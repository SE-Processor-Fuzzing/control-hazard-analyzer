from argparse import Namespace, ArgumentParser
from typing import Protocol


class IUtility(Protocol):
    def run(self) -> None:
        ...

    def configurate(self, settings: Namespace) -> None:
        ...

    def add_sub_parser(self, sub_parser) -> ArgumentParser:
        ...

    def parse_args(self, args: list[str]) -> Namespace:
        ...
