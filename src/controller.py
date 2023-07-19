from builders.builder import Builder
from src.configurator import Configurator


class Controller:

    def __init__(self):
        self.builder = None
        self.configurator = Configurator()
        self.glb_settings = {
            "compiled_folder": "compiled",
            "source_folder": "src",
            "analyse_folder": "analyse",
        }

    def run(self):
        self.configurate()
        self.generate_test()
        self.build()
        self.profile()
        self.pack()

    def configurate(self):
        self.glb_settings = self.configurator.configurate(self.glb_settings)
        self.configurator.clean_output_folder(self.glb_settings["dest_folder"])
        self.configurator.create_folders(self.glb_settings)

    def generate_test(self):
        pass

    def build(self):
        self.builder = Builder(self.glb_settings)
        self.builder.build()

    def profile(self):
        pass

    def pack(self):
        pass
