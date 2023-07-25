from argparse import Namespace

from src.aggregate import Aggregator
from src.analyze import Analyzer
from src.summarize import Summarizer
from src.configurator import Configurator


class Controller:
    def __init__(self):
        self.settings = {}
        self.analyze = Analyzer()
        self.summarize = Summarizer()
        self.aggregate = Aggregator()
        self.settings["analyze"] = self.analyze
        self.settings["summarize"] = self.summarize
        self.settings["aggregate"] = self.aggregate
        self.settings = Namespace(**self.settings)

    def run(self):
        c = Configurator()
        self.settings = c.configurate(vars(self.settings))
        self.settings.utility.configurate(self.settings)
        self.settings.utility.run()
