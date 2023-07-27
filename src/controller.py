from argparse import Namespace

from src.aggregate import Aggregator
from src.analyze import Analyzer
from src.configurator import Configurator
from src.generate import Generator
from src.summarize import Summarizer
from src.utility import IUtility


class Controller:
    def __init__(self):
        self.settings = {}
        self.generator = Generator()
        self.analyze = Analyzer()
        self.summarize = Summarizer()
        self.aggregate = Aggregator()
        self.settings["analyze"]: IUtility = self.analyze
        self.settings["summarize"]: IUtility = self.summarize
        self.settings["aggregate"]: IUtility = self.aggregate
        self.settings["generate"]: IUtility = self.generator
        self.settings = Namespace(**self.settings)

    def run(self):
        c = Configurator()
        self.settings.configurator = c
        self.settings = c.configurate(vars(self.settings))
        self.settings.utility.configurate(self.settings)
        self.settings.utility.run()
