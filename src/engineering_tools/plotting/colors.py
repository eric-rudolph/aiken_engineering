"""
Custom color palettes and colormaps for engineering plots.


Color sequences are stored as 8-bit RGB tuples by default:

    (R, G, B)

where each channel is in the range 0 to 255.

Helper functions are provided to convert these colors into Matplotlib-friendly
formats.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeAlias

from matplotlib.colors import LinearSegmentedColormap, ListedColormap

RGB255: TypeAlias = tuple[int, int, int]
RGB01: TypeAlias = tuple[float, float, float]

ANSYS_COLORS: list[RGB255] = [
    (0, 0, 255),
    (0, 160, 255),
    (0, 255, 255),
    (0, 255, 255),
    (0, 255, 0),
    (178, 255, 0),
    (255, 255, 0),
    (255, 145, 0),
    (255, 0, 0),
]


def validate_rgb255(colors: Sequence[RGB255]) -> None:
    """
    Validate a sequence of 8-bit RGB colors.

    Parameters
    ----------
    colors : Sequence[RGB255]
        Sequence of 8-bit RGB colors - tuples should containe three integers
        in the range 0 to 255.

    Raises
    ------
    ValueError
        If any color in the sequence is not a valid 8-bit RGB color.
    """

    for color in colors:
        if len(color) != 3:
            raise ValueError(f"Expected RGB tuple with 3 channels, got {color!r}.")

        for channel in color:
            if not isinstance(channel, int):
                raise ValueError(f"Expected integer channel in range 0 to 255, got {channel!r}.")

            if not 0 <= channel <= 255:
                raise ValueError(f"Expected integer channel in range 0 to 255, got {channel!r}.")


def rgb255_to_rgb01(color: RGB255) -> RGB01:
    """
    Convert a single RGB color from 0-255 range to 0-1 range.

    Matplotlib generally expects RGB colors in the range 0 to 1.

    Examples
    --------
    >>> rgb255_to_rgb01((255, 128, 0))
    (1.0, 0.5019607843137255, 0.0)
    """
    validate_rgb255([color])
    return tuple(channel / 255 for channel in color)


def rgb255_sequence_to_rgb01(colors: Sequence[RGB255]) -> list[RGB01]:
    """
    Convert a sequence of 8-bit RGB colors to Matplotlib 0-1 colors.
    """
    validate_rgb255(colors)
    return [rgb255_to_rgb01(color) for color in colors]


def make_listed_colormap(colors: Sequence[RGB255],
                         *,
                         name: str = "custom_colormap"
                         ) -> ListedColormap:
    """
    Create a Matplotlib ListedColormap from 8-bit RGB colors.

    A ListedColromap is useful when you want discrete color bands.

    Examples
    ________
    >>> cmap = make_listed_colormap(ANSYS_COLORS, name="ansys")
    """
    rgb01_colors = rgb255_sequence_to_rgb01(colors)
    return ListedColormap(rgb01_colors, name=name)


def make_linear_colormap(colors: Sequence[RGB255],
                         *,
                         name: str = "custom_linear_colormap",
                         n_colors: int = 256,
                         ) -> LinearSegmentedColormap:
    """
    Create a smooth Matplotlib LinearSegmentedColormap from 8-bit RGB colors.

    A LinearSegmentedColormap is useful when you want smooth interpolation
    between colors.

    Examples
    --------
    >>> cmap = make_linear_colormap(ANSYS_COLORS, name="ansys_smooth")
    """
    rgb01_colors = rgb255_sequence_to_rgb01(colors)
    return LinearSegmentedColormap.from_list(name, rgb01_colors, N=n_colors)


ANSYS_LISTED_CMAP = make_listed_colormap(ANSYS_COLORS, name="ansys")
ANSYS_LINEAR_CMAP = make_linear_colormap(ANSYS_COLORS, name="ansys_smooth")

AIKEN_COLORS = {
    "red": rgb255_to_rgb01((101, 20, 0)),
    "yellow": rgb255_to_rgb01((252, 238, 33)),
    "paleyellow": rgb255_to_rgb01((254, 248, 166)),
    "darkgreen": rgb255_to_rgb01((0, 104, 55)),
    "green": rgb255_to_rgb01((51, 134, 95)),
    "palegreen": rgb255_to_rgb01((153, 195, 175)),
    "darkblue": rgb255_to_rgb01((0, 85, 141)),
    "blue": rgb255_to_rgb01((0, 113, 188)),
    "paleblue": rgb255_to_rgb01((102, 153, 187)),
    "lightblue": rgb255_to_rgb01((204, 221, 232)),
    "black": rgb255_to_rgb01((0, 0, 0)),
    "darkgray": rgb255_to_rgb01((64, 64, 64)),
    "gray": rgb255_to_rgb01((128, 128, 128)),
    "lightgray": rgb255_to_rgb01((179, 179, 179)),
    "palegray": rgb255_to_rgb01((230, 230, 230)),
    "white": rgb255_to_rgb01((255, 255, 255)),
}
