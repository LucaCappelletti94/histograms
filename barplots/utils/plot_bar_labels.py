from typing import Dict, List, Union

import pandas as pd
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from sanitize_ml_labels import sanitize_ml_labels

from .get_max_bar_position import get_max_bar_position
from .text_positions import text_positions


def sanitize_digits(digit: float, *args, **kwargs):
    return sanitize_ml_labels(str(digit))


def plot_bar_labels(
    axes: Axes,
    figure: Figure,
    df: pd.DataFrame,
    vertical: bool,
    levels: int,
    bar_width: float,
    space_width: float,
    minor_rotation: Union[float, str],
    major_rotation: Union[float, str],
    unique_minor_labels: bool,
    unique_major_labels: bool,
    unique_data_label: bool,
    custom_defaults: Dict[str, List[str]]
):
    """
    Parameters
    ------------
    minor_rotation: Union[float, str]
        Rotation for the minor ticks of the bars.
        By default, with the "auto" mode, the library tries to find
        the rotation with which we minimize the overlap for the provided
        labels, including also the overlap with minor and major.
    major_rotation: Union[float, str]
        Rotation for the major ticks of the bars.
        By default, with the "auto" mode, the library tries to find
        the rotation with which we minimize the overlap for the provided
        labels, including also the overlap with minor and major.
    unique_minor_labels: bool = True,
        Avoid replicating minor labels on the same axis in multiple subplots settings.
    unique_major_labels: bool = True,
        Avoid replicating major labels on the same axis in multiple subplots settings.
    unique_data_label: bool = True,
        Avoid replication of data axis label when using subplots.
    """
    other_positions = set()
    width = get_max_bar_position(df, bar_width, space_width)

    if unique_data_label:
        axes.set_ylabel("")

    if vertical:
        axes.locator_params(
            axis='y',
            nbins=5
        )
        axes.yaxis.set_major_formatter(
            plt.FuncFormatter(sanitize_digits)
        )
    else:
        axes.locator_params(
            axis='x',
            nbins=5
        )
        axes.xaxis.set_major_formatter(
            plt.FuncFormatter(sanitize_digits)
        )

    for level in reversed(range(max(levels-2, 0), levels)):
        positions, labels = zip(
            *text_positions(df, bar_width, space_width, level))
        labels = sanitize_ml_labels(labels, custom_defaults=custom_defaults)

        max_characters_number_in_labels = max((
            len(label)
            for label in labels
        ))

        positions = [
            round(pos, 5)
            for pos in positions
        ]
        positions = [
            position + width*0.0002 if position in other_positions else position
            for position in positions
        ]
        other_positions |= set(positions)
        minor = level == levels-1

        # Handle the automatic rotation of minor labels.
        if minor_rotation == "auto":
            if (
                minor and
                len(set(labels)) <= width * 5 / max_characters_number_in_labels and
                vertical
            ):
                adapted_minor_rotation = 90
            elif (
                minor and
                len(set(labels)) <= width * 20 / max_characters_number_in_labels and
                not vertical
            ):
                adapted_minor_rotation = 90
            else:
                adapted_minor_rotation = 0
        else:
            adapted_minor_rotation = minor_rotation

        # Handle the automatic rotation of major labels.
        if major_rotation == "auto":
            if (
                not minor and
                len(set(labels)) <= width * 5 / max_characters_number_in_labels and
                not vertical
            ):
                adapted_major_rotation = 90
            elif (
                not minor and
                len(set(labels)) >= width * 20 / max_characters_number_in_labels and
                vertical
            ):
                adapted_major_rotation = 90
            else:
                adapted_major_rotation = 0
        else:
            adapted_major_rotation = major_rotation

        if minor and unique_minor_labels:
            continue
        if not minor and unique_major_labels:
            continue

        if vertical:
            axes.set_xticks(positions, minor=minor)
            axes.set_xticklabels(labels, minor=minor, ha="center")
            if minor:
                axes.tick_params(
                    axis='x',
                    labelsize=9,
                    which='minor',
                    labelrotation=adapted_minor_rotation
                )

                if adapted_minor_rotation > 80:
                    length = 6 * max_characters_number_in_labels
                else:
                    length = 20

                axes.tick_params(
                    axis='x',
                    labelsize=10,
                    which='major',
                    direction='out',
                    length=length,
                    width=0
                )
            else:
                axes.tick_params(
                    axis='x',
                    labelsize=10,
                    which='major',
                    labelrotation=adapted_major_rotation
                )
        else:
            axes.set_yticks(positions, minor=minor)
            axes.set_yticklabels(labels, minor=minor, va="center")
            if minor:
                axes.tick_params(
                    axis='y',
                    which='minor',
                    labelsize=9,
                    labelrotation=adapted_minor_rotation
                )

                if adapted_minor_rotation > 80:
                    length = 20
                else:
                    length = 6 * max_characters_number_in_labels

                axes.tick_params(
                    axis='y',
                    which='major',
                    labelsize=10,
                    direction='out',
                    length=length,
                    # This is the size of the actual `tick`
                    # in the plot, which we do not want to show
                    # for the major ticks in this case and therefore
                    # we set it to zero.
                    width=0
                )
            else:
                axes.tick_params(
                    axis='y',
                    which='major',
                    labelrotation=adapted_major_rotation
                )
