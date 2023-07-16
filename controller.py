from builders.builder import Builder
from configurator import *


class Controller:

    def __init__(self):
        self.glb_settings = dict()
        self.configurator = Configurator()
        self.builder = Builder(self.glb_settings)

    def run(self):
        self.configurate()
        self.generate_test()
        self.build()
        self.profile()
        self.pack()
    def configurate(self):
        self.configurator.configurate(self.glb_settings)



    def generate_test(self):
        pass

    def build(self):
        self.builder.build()

    def profile(self):
        pass

    def pack(self):
        pass
