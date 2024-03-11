from argparse import Namespace
from typing import Dict

from src.cli.aggregate import Aggregate
from src.cli.analyze import Analyze
from src.cli.generate import Generate
from src.cli.summarize import Summarize
from src.helpers.configurator import Configurator
from src.protocols.utility import Utility


class Controller:
    def __init__(self) -> None:
        self.utilities: Dict[str, Utility] = {}
        generator = Generate()
        analyze = Analyze()
        summarize = Summarize()
        aggregate = Aggregate()
        self.utilities["generate"] = generator
        self.utilities["analyze"] = analyze
        self.utilities["summarize"] = summarize
        self.utilities["aggregate"] = aggregate

    def run(self) -> None:
        c = Configurator()
        self.configurator = c
        self.settings = c.configurate(self.utilities)
        self.settings.configurator = c
        utility = self.utilities[self.settings.utility]
        utility.configurate(self.settings)
        utility.run()
