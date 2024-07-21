import json
import logging
import os
from pathlib import Path
from pprint import pformat
from typing import Any, Dict, List, TypeVar

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backend_bases import Event
from matplotlib.patches import Patch
from pandas import DataFrame

from src.protocols.collector import DictSI
from src.protocols.utility import Utility

S = TypeVar("S")
DataType = Dict[str, Dict[str, Dict[str, S]]]


class Summarize(Utility):
    def __init__(self) -> None:
        self.filename_out_grapg = "graph.png"
        self.filename_out_data = "results.data"
        self.logger = logging.getLogger(__name__)

    def configurate(self, settings: Dict[str, Any]) -> None:
        """Initialize local variables with passed parameters

        :param settings: Passed parameters to the command
        """
        self.settings = settings
        self.logger.setLevel(self.settings["log_level"])

    def run(self) -> None:
        """Print log info, then perform analyze data collection, summarization, and plotting
        The results are saved to files and optionally displayed
        """
        self.logger.info("Summarize is running. Settings:")
        self.logger.info(pformat(self.settings))

        src_dirs: List[Path] = [Path(s) for s in self.settings["src_dirs"]]
        data = self.get_data_from_sources(src_dirs)
        if len(data) == 0:
            return

        data_df = self.convert_to_pandas(self.prepare_data(data))
        self.logger.debug(f"Collected data:\n{data_df.head()}")
        mean_of_dir = self.calculate_mean_of_dir(data_df)
        out_dir = Path(self.settings["out_dir"])

        self.save_mean_data(mean_of_dir, src_dirs, out_dir)
        self.save_data_for_each_source(data_df, mean_of_dir, src_dirs, out_dir)

        data_df = self.filter_summarize_data(data_df)
        data_frame_plot = self.construct_data_for_plot(data_df)
        data_frame_plot = self.sort_data(data_frame_plot)
        clean_df_plot = DataFrame(
            {k: data_frame_plot.loc[k, "BP incorrect %"] for k in data_frame_plot.index.unique(level="dir")}
        )
        self.construct_plot(clean_df_plot, data_frame_plot.loc[:, ["BP lookups", "Full launch"]])

        if not self.settings["no_save_graph"]:
            self.save_plot(out_dir)

        if not self.settings["no_show_graph"]:
            self.show_plot()

    def get_data_from_sources(self, src_dirs: List[Path]) -> DataType[int]:
        """Collect data from the specified source directories

        :param src_dirs: A list of directories containing source analyze data files
        :return: A dictionary containing the collected data
        """
        data: Dict[str, Dict[str, DictSI]] = {}

        for src_dir in src_dirs:
            if not src_dir.exists():
                print(f"[-]: Directory {src_dir} does not exist")
                continue

            posix_dir_path = src_dir.as_posix()
            data[posix_dir_path] = {}
            for src_file in src_dir.glob("*"):
                with open(src_file, "r") as f:
                    data[posix_dir_path][src_file.stem] = json.loads(f.read())
                for key, val in data[posix_dir_path][src_file.stem].items():
                    data[posix_dir_path][src_file.stem][key] = int(val)

        return data

    def prepare_data(self, data: DataType[int]) -> DataType[int | float | bool]:
        """Prepare and transform the collected data by extracting and calculating specific metrics

        Extracts simulation ticks, branch predictor lookups, incorrect predictions, and full launch flags,
        then calculates ticks per branch prediction and the percentage of incorrect predictions

        :param data: The collected data
        :return: The prepared data with additional calculated metrics
        """
        result: DataType[int | float | bool] = {Path(src_dir).as_posix(): {} for src_dir in data}
        for src_dir, src_files in data.items():
            for src_file, src_data in src_files.items():
                sim_ticks = src_data.get("simTicks", np.nan)
                bp_lookups = src_data.get(
                    "branchPred.lookups",
                    src_data.get("branchPred.btb.lookups::total", np.nan),
                )
                bp_incorrect = src_data.get("branchPred.condIncorrect", np.nan)
                is_full = bool(src_data.get("isFull", False))
                result[src_dir][Path(src_file).stem] = {
                    "Number of ticks": sim_ticks,
                    "BP lookups": bp_lookups,
                    "Ticks per BP": (
                        round(sim_ticks / float(bp_lookups) if bp_lookups != 0 else 0, 2)
                        if bp_lookups != np.nan and sim_ticks != np.nan
                        else np.nan
                    ),
                    "BP incorrect": bp_incorrect,
                    "BP incorrect %": (
                        round(
                            (bp_incorrect / float(bp_lookups) * 100 if bp_lookups != 0 else 0),
                            2,
                        )
                        if bp_lookups != np.nan and bp_incorrect != np.nan
                        else np.nan
                    ),
                    "Full launch": is_full,
                }
        return result

    def calculate_mean_of_dir(self, data: DataFrame) -> DataFrame:
        """Calculate the mean percentage of BP incorrect for each directory

        :param data: The prepared data in a pandas DataFrame
        :return: A DataFrame containing the mean percentage of BP incorrect for each directory
        """
        mean_of_dir: Dict[str, Dict[str, Any]] = {}
        for src_dir in data.index.unique(level="dir"):
            mean_of_dir[src_dir] = {}
            mean_of_dir[src_dir]["BP incorrect %"] = round(
                data.loc[src_dir, "BP incorrect"].sum() / data.loc[src_dir, "BP lookups"].sum() * 100,
                2,
            )
        return DataFrame(mean_of_dir)

    def convert_to_pandas(self, data: Dict[str, Dict[Any, Any]]) -> DataFrame:
        """Convert the prepared data to a pandas DataFrame

        :param data: The prepared data
        :return: The data in a pandas DataFrame
        """
        df = pd.concat({key: DataFrame(value).T for key, value in data.items()})
        return df.rename_axis(["dir", "test"])

    def save_mean_data(self, mean_of_dir: DataFrame, src_dirs: List[Path], out_dir: Path) -> None:
        """Save the mean percentage of BP incorrect for each directory to a file

        :param mean_of_dir: The DataFrame containing the mean percentage of BP incorrect for each directory
        :param src_dirs: A list of directories containing source analyze data files
        :param out_dir: The directory where the results will be saved
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        with open(out_dir.joinpath(self.filename_out_data), "w") as f:
            # Use pandas to print data to file
            f.write("Summarized data:\n")
            f.write(mean_of_dir.to_string())
            f.write("\n\n")
            for src_dir in src_dirs:
                f.write(f"dir: {src_dir}\n")
                f.write(str(src_dir))
                f.write("\n\n\n")

    def save_data_for_each_source(
        self,
        data: DataFrame,
        mean_of_dir: DataFrame,
        src_dirs: List[Path],
        out_dir: Path,
    ) -> None:
        """Save the data for each source directory to a file

        :param data: The prepared data in a pandas DataFrame
        :param mean_of_dir: The DataFrame containing the mean percentage of BP incorrect for each directory
        :param src_dirs: A list of directories containing source analyze data files
        :param out_dir: The directory where the results will be saved
        """
        for src_dir in src_dirs:
            if not src_dir.exists():
                print(f"[-]: Directory {src_dir} does not exist")
                continue

            out_file = src_dir.parent.joinpath(os.path.basename(out_dir), self.filename_out_data)
            out_file.parent.mkdir(parents=True, exist_ok=True)
            with open(out_file, "w") as f:

                data_frame = data.loc[str(src_dir)]
                f.write(f"dir: {src_dir}\n")
                f.write("\n")
                f.write(data_frame.to_string())
                f.write("\n\n")
                f.write("Average % of BP incorrect: ")

                bp_incorrect = mean_of_dir.loc["BP incorrect %", str(src_dir)]
                f.write(str(bp_incorrect))

    def filter_summarize_data(self, data: DataFrame) -> DataFrame:
        """Filter and summarize the data for plotting

        :param data: The prepared data in a pandas DataFrame
        :return: The filtered and summarized data
        """
        result = data.copy()
        for key in data.index:
            if not (0 <= data.loc[key, "BP incorrect %"] <= 100):
                result.loc[key, "BP incorrect %"] = np.NaN
            if data.loc[key, "BP lookups"] < 50:
                result.loc[key, "BP incorrect %"] = np.NaN
            # if not data.loc[key, "Full launch"]:
            #     result.loc[key, "BP incorrect %"] = np.NaN
        return result

    def construct_data_for_plot(self, data: DataFrame) -> DataFrame:
        """Construct the data for plotting

        :param data: The filtered and summarized data in a pandas DataFrame
        :return: The data prepared for plotting
        """
        return data.loc[:, ["BP incorrect %", "BP lookups", "Full launch"]]

    def sort_data(self, data: DataFrame) -> DataFrame:
        """Sort the data for plotting by directory and the maximum 'BP incorrect %' within each test

        :param data: The data prepared for plotting in a pandas DataFrame
        :return: The sorted data with the index reset and sorted by 'dir' and the maximum 'BP incorrect %' within
        each test
        """
        data = data.reset_index(level=["dir", "test"])
        max_values = data.groupby("test")["BP incorrect %"].max()

        data = data.merge(max_values, on="test", suffixes=("", "_max"))

        df_sorted = data.sort_values(by=["dir", "BP incorrect %_max"], na_position="first")
        data = df_sorted.set_index(["dir", "test"]).drop("BP incorrect %_max", axis=1)
        return data

    def construct_plot(self, data: DataFrame, hovers: DataFrame) -> None:
        """Construct the plot for the summarized data

        :param data: The data to be plotted in a pandas DataFrame
        :param hovers: The data for hover annotations in the plot
        """
        ax = data.plot(kind="bar", rot=90)

        fig = ax.figure
        if fig is None:
            return
        bars = ax.patches
        for bar in bars:
            if hovers.iloc[bars.index(bar)].loc["Full launch"] == 0:
                bar.set_alpha(0.5)
        annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(-20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="b", ec="b", lw=2, alpha=0.3),
            arrowprops=dict(arrowstyle="->"),
        )
        annot.set_visible(False)

        def get_hover(bar: Patch) -> Any:
            """Get the hover text for a specific bar in the plot

            :param bar: The bar for which to get the hover text
            :return: The hover text corresponding to the bar, or "N/A" if the index is out of range
            """
            index = bars.index(bar)
            return hovers.iloc[index].to_string(name=False) if index < len(hovers) else "N/A"

        def update_annot(bar: Any) -> None:
            """Update the annotation position and text based on the given bar

            :param bar: The bar for which to update the annotation
            """
            x = bar.get_x() + bar.get_width() / 2.0
            y = bar.get_y() + bar.get_height()
            annot.xy = (x, y)
            text = f"{get_hover(bar)}"
            annot.set_text(text)
            # bbox = annot.get_bbox_patch()
            # if bbox is not None:
            #     bbox.set_alpha(0.3)

        def show_annotation(event: Event) -> Any:
            """Show the annotation if the mouse is over a bar, otherwise hide it

            :param event: The event triggering the annotation display
            """
            vis = annot.get_visible()
            for bar in bars:
                cont, _ = bar.contains(event)  # type: ignore
                if cont:
                    update_annot(bar)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return

            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()

        fig.canvas.mpl_connect("motion_notify_event", show_annotation)

    def show_plot(self) -> None:
        """Display the plot"""
        plt.show()

    def save_plot(self, out_dir: Path) -> None:
        """Save the plot to a file in the given directory

        :param out_dir: The directory where the plot will be saved
        """
        out_dir.mkdir(parents=True, exist_ok=True)
        plt.savefig(out_dir.joinpath(self.filename_out_grapg))
