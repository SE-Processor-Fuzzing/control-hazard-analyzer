from argparse import Namespace

from src.aggregate import Aggregator
from src.bulbul import Bulbul
from src.ckrasota import Ckrasota
from src.configurator import Configurator


class Controller:
    def __init__(self):
        self.settings = {}
        self.bulbul = Bulbul()
        self.ckrasota = Ckrasota()
        self.aggregate = Aggregator()
        self.settings["bulbul"] = self.bulbul
        self.settings["ckrasota"] = self.ckrasota
        self.settings["aggregate"] = self.aggregate
        self.settings = Namespace(**self.settings)

    def run(self):
        c = Configurator()
        self.settings = c.configurate(vars(self.settings))
        self.settings.utility.configurate(self.settings)
        self.settings.utility.run()
