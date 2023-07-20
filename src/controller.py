from pathlib import Path
from builders.builder import Builder
from profilers.perfProfiler import PerfProfiler
from src.configurator import Configurator
from src.generator import Generator


class Controller:
    def __init__(self):
        self.configurator = Configurator()
        self.glb_settings = {
            "compiled_folder": "compiled",
            "source_folder": "src",
            "analyse_folder": "analyse",
        }
        self.configurate()
        self.builder: Builder = Builder(self.glb_settings)
        self.generator = Generator(self.glb_settings)

    def run(self):
        self.generate_test()
        self.profile()
        self.pack()

    def configurate(self):
        self.glb_settings = self.configurator.configurate(self.glb_settings)
        self.configurator.clean_output_folder(Path(self.glb_settings["dest_folder"]))
        self.configurator.create_folders(self.glb_settings)

    def generate_test(self):
        self.generator.generate(self.glb_settings["repeats"])

    def build(self):
        self.builder = Builder(self.glb_settings)
        source_folder = (
            f'{self.glb_settings["dest_folder"]}/{self.glb_settings["source_folder"]}'
        )
        destination_folder = (
            f'{self.glb_settings["dest_folder"]}/{self.glb_settings["compiled_folder"]}'
        )
        self.builder.build(Path(source_folder), Path(destination_folder))

    def profile(self):
        p = PerfProfiler(self.builder)
        src_dir = (
            f'{self.glb_settings["dest_folder"]}/{self.glb_settings["source_folder"]}'
        )
        analize_dir = (
            f"{self.glb_settings['dest_folder']}/{self.glb_settings['analyse_folder']}"
        )
        p.profile(Path(src_dir), Path(analize_dir))

    def pack(self):
        pass
