import shutil


class Generator:
    def __init__(self, settings: dict):
        self.settings = settings

    def generate(self, repeats=1, output_filename_template="test"):
        for i in range(repeats):
            shutil.copy("test.c",
                        f'{self.settings["dest_folder"]}/'
                        f'{self.settings["source_folder"]}/{output_filename_template}_{i}.c')
