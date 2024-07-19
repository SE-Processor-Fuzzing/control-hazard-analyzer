import json
from enum import Enum
from typing import Any, Dict, List


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
    def configurate(self, args: Dict[str, Any]):
        """Update the provided arguments with configuration file contents if specified

        :param args: Dictionary of arguments
        """
        config_file = args.get("config_file")
        section_in_config = args.get("section_in_config")

        if config_file:
            config = self.read_cfg_file(config_file, section_in_config)
            args.update(config)

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
            if arg in settings:
                if args[arg] != settings[arg]:
                    settings[arg] = args[arg]
            else:
                settings[arg] = args[arg]
        return result

    def parse_args(self, args: List[str], default_params: Dict[str, Any]) -> Dict[str, Any]:
        """Parse command line arguments and update the default parameters

       :param args: List of command line arguments
       :param default_params: Default parameters to update
       :return: Updated parameters
       """
        for i in range(0, len(args), 2):
            key = args[i].lstrip("--").replace("-", "_")
            value = args[i + 1]
            if key in default_params:
                default_params[key] = value

        return default_params
