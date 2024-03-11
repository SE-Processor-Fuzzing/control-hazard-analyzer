from argparse import ArgumentParser
from typing import Any, Protocol, Sequence


class SubParser(Protocol):
    def add_parser(
        self,
        name: str,
        *,
        help: str | None = ...,
        aliases: Sequence[str] = ...,
        prog: str | None = ...,
        usage: str | None = ...,
        description: str | None = ...,
        epilog: str | None = ...,
        parents: Sequence[ArgumentParser] = ...,
        formatter_class: Any = ...,
        prefix_chars: str = ...,
        fromfile_prefix_chars: str | None = ...,
        argument_default: Any = ...,
        conflict_handler: str = ...,
        add_help: bool = ...,
        allow_abbrev: bool = ...,
        exit_on_error: bool = ...
    ) -> ArgumentParser: ...
