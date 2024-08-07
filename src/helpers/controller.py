from typing import Dict, List, Optional

import typer
from typing_extensions import Annotated

from src.cli.aggregate import (
    Aggregate,
    DEFAULT_GENERATE_SETTINGS,
    DEFAULT_ANALYZE_SETTINGS,
    DEFAULT_SUMMARIZE_SETTINGS,
    DEFAULT_AGGREGATE_SETTINGS,
)
from src.cli.analyze import Analyze
from src.cli.generate import Generate
from src.cli.summarize import Summarize
from src.helpers.configurator import Configurator, LogLevel, ProfilerType
from src.protocols.utility import Utility

app = typer.Typer(help="This script generate and test code on some platforms", chain=True)
command_args = {}
configurator = Configurator()


@app.command("generate", help="Generate tests")
def init_generator(
    out_dir: Annotated[
        str, typer.Option(help="Path to output directory", metavar="OUT_DIR", show_default=False)
    ] = DEFAULT_GENERATE_SETTINGS["out_dir"],
    repeats: Annotated[
        int, typer.Option(help="Count of repeats to generated test", metavar="REPEATS", show_default=False)
    ] = DEFAULT_GENERATE_SETTINGS["repeats"],
    seed: Annotated[
        int, typer.Option(help="Integer to use as seed to random test generation", metavar="SEED", show_default=False)
    ] = DEFAULT_GENERATE_SETTINGS["seed"],
    log_level: Annotated[
        LogLevel, typer.Option(help="Log level of program", case_sensitive=True)
    ] = DEFAULT_GENERATE_SETTINGS["log_level"],
):
    command_args["utility"] = DEFAULT_GENERATE_SETTINGS["utility"]
    command_args["out_dir"] = out_dir
    command_args["repeats"] = repeats
    command_args["seed"] = seed
    command_args["log_level"] = log_level.value
    run_utility()


@app.command("analyze", help="Build, run tests, and subsequent analysis of test execution")
def init_analyzer(
    config_file: Annotated[
        Optional[str], typer.Option(help="Path to configuration file", metavar="CONFIG_FILE", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["config_file"],
    out_dir: Annotated[
        str, typer.Option(help="Path to output directory", metavar="OUT_DIR", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["out_dir"],
    test_dir: Annotated[
        str, typer.Option(help="Path to directory with tests", metavar="TEST_DIR", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["test_dir"],
    timeout: Annotated[
        int,
        typer.Option(
            help="Number of seconds after which the test will be stopped", metavar="TIMEOUT", show_default=False
        ),
    ] = DEFAULT_ANALYZE_SETTINGS["timeout"],
    compiler: Annotated[
        str, typer.Option(help="Path to compiler", metavar="COMPILER", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["compiler"],
    compiler_args: Annotated[
        str, typer.Option(help="Pass arguments on to the compiler", metavar="COMPILER_ARGS", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["compiler_args"],
    profiler: Annotated[ProfilerType, typer.Option(help="Type of profiler")] = DEFAULT_ANALYZE_SETTINGS["profiler"],
    gem5_home: Annotated[
        str, typer.Option(help="Path to home gem5", metavar="GEM5_HOME", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["gem5_home"],
    gem5_bin: Annotated[
        str, typer.Option(help="Path to execute gem5", metavar="GEM5_BIN", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["gem5_bin"],
    target_isa: Annotated[
        str, typer.Option(help="Type of architecture being simulated", metavar="TARGET_ISA", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["target_isa"],
    sim_script: Annotated[
        str, typer.Option(help="Path to simulation Script", metavar="SIM_SCRIPT", show_default=False)
    ] = DEFAULT_ANALYZE_SETTINGS["sim_script"],
    log_level: Annotated[LogLevel, typer.Option(help="Log level of program")] = DEFAULT_ANALYZE_SETTINGS["log_level"],
):
    command_args["utility"] = DEFAULT_ANALYZE_SETTINGS["utility"]
    command_args["config_file"] = config_file
    command_args["out_dir"] = out_dir
    command_args["test_dir"] = test_dir
    command_args["timeout"] = timeout
    command_args["compiler"] = compiler
    command_args["compiler_args"] = compiler_args
    command_args["profiler"] = profiler.value
    command_args["gem5_home"] = gem5_home
    command_args["gem5_bin"] = gem5_bin
    command_args["target_isa"] = target_isa
    command_args["sim_script"] = sim_script
    command_args["log_level"] = log_level.value
    configurator.configurate(command_args)
    run_utility()


@app.command(
    "summarize",
    help='Summarize the results of "analyze", and display the results by generating an interactive diagram',
)
def init_summarizer(
    src_dirs: Annotated[
        List[str] | None, typer.Option(help="Path to source dirs", metavar="SRC_DIRS", show_default=False)
    ] = None,
    out_dir: Annotated[
        str, typer.Option(help="Path to output directory", metavar="OUT_DIR", show_default=False)
    ] = DEFAULT_SUMMARIZE_SETTINGS["out_dir"],
    no_show_graph: Annotated[
        bool, typer.Option("--no-show-graph", help="Shows a graph of BP incorrect %%", show_default=False)
    ] = DEFAULT_SUMMARIZE_SETTINGS["no_show_graph"],
    no_save_graph: Annotated[
        bool,
        typer.Option("--no-save-graph", help="Saves a graph of BP incorrect %% in graph.png", show_default=False),
    ] = DEFAULT_SUMMARIZE_SETTINGS["no_save_graph"],
    log_level: Annotated[LogLevel, typer.Option(help="Log level of program")] = DEFAULT_SUMMARIZE_SETTINGS["log_level"],
):
    command_args["utility"] = DEFAULT_SUMMARIZE_SETTINGS["utility"]
    command_args["src_dirs"] = src_dirs
    command_args["out_dir"] = out_dir
    command_args["no_show_graph"] = no_show_graph
    command_args["no_save_graph"] = no_save_graph
    command_args["log_level"] = log_level.value
    run_utility()


@app.command("aggregate", help="Run generate, analyze and summarize in sequence")
def init_aggregator(
    config_file: Annotated[
        str, typer.Option(help="Path to .cfg file", metavar="CONFIG_FILE", show_default=False)
    ] = DEFAULT_AGGREGATE_SETTINGS["config_file"],
    section_in_config: Annotated[
        str,
        typer.Option(
            help="Set the custom section " "in config file (DEFAULT by default)",
            metavar="SECTION_IN_CONFIG",
            show_default=False,
        ),
    ] = DEFAULT_AGGREGATE_SETTINGS["section_in_config"],
    dest_dir: Annotated[
        str,
        typer.Option(help="Path to dist dir, if not exit it will be created", metavar="OUT_DIR", show_default=False),
    ] = DEFAULT_AGGREGATE_SETTINGS["dest_dir"],
    async_analyze: Annotated[
        bool,
        typer.Option(
            "--async-analyze",
            help="Run analyze steps simultaneously " "(not recommended with perf)",
            metavar="ASYNC_ANALYZE",
            show_default=False,
        ),
    ] = DEFAULT_AGGREGATE_SETTINGS["async_analyze"],
    log_level: Annotated[LogLevel, typer.Option(help="Log level of program")] = DEFAULT_AGGREGATE_SETTINGS["log_level"],
):
    command_args["utility"] = DEFAULT_AGGREGATE_SETTINGS["utility"]
    command_args["config_file"] = config_file
    command_args["section_in_config"] = section_in_config
    command_args["dest_dir"] = dest_dir
    command_args["async_analyze"] = async_analyze
    command_args["log_level"] = log_level.value
    configurator.configurate(command_args)
    run_utility()


def run_utility():
    """Execute the utility specified in command_args"""
    util_name = command_args["utility"]
    utility = command_args[util_name]
    utility.configurate(command_args)
    utility.run()


class Controller:
    def __init__(self) -> None:
        """Initialize the Controller with available utilities"""
        self.utilities: Dict[str, Utility] = {
            "generate": Generate(),
            "analyze": Analyze(),
            "summarize": Summarize(),
            "aggregate": Aggregate(),
        }

        for command in self.utilities:
            command_args[command] = self.utilities[command]

    def run(self) -> None:
        """Run the application with typer"""
        command_args["configurator"] = configurator
        app()
