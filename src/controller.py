from argparse import Namespace

from BIOhazard import BIOhazard
from src.bulbul import Bulbul
from src.ckrasota import Ckrasota
from src.configurator import Configurator


class Controller:
    def __init__(self):
        self.settings = {}
        self.bulbul = Bulbul()
        self.ckrasota = Ckrasota()
        self.biohazard = BIOhazard()
        self.settings["bulbul"] = self.bulbul
        self.settings["ckrasota"] = self.ckrasota
        self.settings["biohazard"] = self.biohazard
        self.settings = Namespace(**self.settings)

    def run(self):
        c = Configurator()
        self.settings = c.configurate(vars(self.settings))
        self.settings.utility.configurate(self.settings)
        self.settings.utility.run()
