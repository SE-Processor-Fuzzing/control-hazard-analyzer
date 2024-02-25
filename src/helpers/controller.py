from argparse import Namespace

from src.cli.aggregate import Aggregate
from src.cli.analyze import Analyze
from src.helpers.configurator import Configurator
from src.cli.generate import Generate
from src.cli.summarize import Summarize
from src.protocols.utility import IUtility


class Controller:
    def __init__(self):
        self.settings = {}
        self.generator = Generate()
        self.analyze = Analyze()
        self.summarize = Summarize()
        self.aggregate = Aggregate()
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
