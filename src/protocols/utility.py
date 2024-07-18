from typing import Protocol, Any, Dict


class Utility(Protocol):
    def run(self) -> None: ...

    def configurate(self, settings: Dict[str, Any]) -> None: ...
