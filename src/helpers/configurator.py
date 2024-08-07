import json
from enum import Enum
from typing import Any, Dict


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ProfilerType(str, Enum):
    PERF = "perf"
    GEM5 = "gem5"


class Configurator:
    """Class for handling configuration files and argument parsing"""

    def configurate(self, args: Dict[str, Any], default_args: Dict[str, Any]):
        """Update the provided arguments with configuration file contents if specified.
        Arguments priority: default_args < config_args < provided_args

        :param args: Dictionary of arguments
        :param default_args: Dictionary of default arguments
        """
        config_file = args.get("config_file")
        section_in_config = args.get("section_in_config")

        if config_file:
            config = self.read_cfg_file(config_file, section_in_config)
            for key, value in config.items():
                if key in args:
                    if args[key] == default_args[key]:
                        args[key] = value
                else:
                    args[key] = value

    def read_cfg_file(self, config_file: str | None, section: str | None = None) -> Dict[str, Any]:
        """Read a configuration file and return its contents

        :param config_file: Path to the configuration file
        :param section: Specific section in the configuration file to read
        :return: Dictionary of configuration settings
        """
        if config_file is None:
            return dict()
        with open(config_file, mode="r") as f:
            config: Dict[str, Any] = json.load(f)
        return config if section is None else {**config["DEFAULT"], **config[section]}

    def get_true_settings(self, settings: Dict[str, Any], args: Dict[str, Any]) -> Dict[str, Any]:
        """Get the final settings by updating the default settings with the configs settings

        :param settings: Default settings
        :param args: Provided arguments to override the default settings
        :return: Updated settings
        """
        result: Dict[str, Any] = settings
        for arg in args:
            if arg not in settings:
                settings[arg] = args[arg]
        return result
