"""
matplotlib style utilities for engineering plots.

This module defines rcParams dictionaries and helper functions for
applying styles temporarily or globally.

The main function is:

    use_engineering_style()

For temporary styling, use:

    with engineering_style():
        ...

"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig

ENGINEERING_STYLE: dict[str, object] = {
    # Figure
    "figure.figsize": (8, 5),
    "figure.dpi": 120,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",

    # Axes
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "axes.grid": True,
    "axes.formatter.use_mathtext": True,

    # ticks
    "xtick.top": True,
    "xtick.labelsize": 8,
    "xtick.direction": "in",
    "xtick.minor.visible": True,
    "ytick.right": True,
    "ytick.labelsize": 8,
    "ytick.direction": "in",
    "ytick.minor.visible": True,

    # Grid
    "grid.linewidth": 0.5,
    "grid.alpha": 0.35,

    # legend
    "legend.frameon": True,
    "legend.fontsize": "small",
    "legend.framealpha": 1.0,

    # Lines
    "lines.linewidth": 2.0,
}

REPORT_STYLE: dict[str, object] = {
    **ENGINEERING_STYLE,

    # Better for reports and saved figures
    "figure.figsize": (6.5, 4.5),
    "figure.dpi": 120,
    "savefig.dpi": 300,

    # Change text style
    # TODO: Finish developing the REPORT_STYLE
}

PRESENTATION_STYLE: dict[str, object] = {
    **ENGINEERING_STYLE,

    # Better for slides and large displays
    # TODO: Finish developing the PRESENTATION_STYLE

    # Larger Text

    # Heavier Lines

}


def use_engineering_style() -> None:
    """
    Apply the default engineering style globally.

    This modifies Matplotlib's rcParams for the current Python session.

    Examples
    --------
    >>> from engineering_tools import use_engineering_style
    >>> use_engineering_style()
    """

    mpl.rcParams.update(ENGINEERING_STYLE)


def use_report_style() -> None:
    """
    Apply the report style globally.  This style is useful for figures
    intended for documents and reports.

    This modifies Matplotlib's rcParams for the current Python session.

    Examples
    --------
    >>> from engineering_tools import use_report_style
    >>> use_report_style()
    """

    mpl.rcParams.update(REPORT_STYLE)


def use_presentation_style() -> None:
    """
    Apply the presentation style globally.  This style us useful for figures
    intended for slides and screen sharing.

    This modifies Matplotlib's rcParams for the current Python session.

    Examples
    --------
    >>> from engineering_tools import use_presentation_style
    >>> use_presentation_style()
    """

    mpl.rcParams.update(PRESENTATION_STYLE)


def reset_style() -> None:
    """
    Reset the Matplotlib style settings to Matplotlib defaults.
    """
    plt.rcdefaults()


@contextmanager
def engineering_style() -> Iterator[None]:
    """
    Temporarily apply the default engineering style.

    This does not permanently modify Matplotlib's global style outside
    the context manager.

    Examples
    --------
    >>> import matplotlib.pyplot as plt
    >>> from engineering_tools import engineering_style
    >>>
    >>> with engineering_style():
    ...     fig, ax = plt.subplots()
    ...     ax.plot([0, 1, 2], [0, 1, 4])
    ...     ax.set_xlabel("Time [s]")
    ...     ax.set_ylabel("Displacement [mm]")
    ...     plt.show()
    """
    with mpl.rc_context(rc=ENGINEERING_STYLE):
        yield


@contextmanager
def report_style() -> Iterator[None]:
    """
    Temporarily apply the report plotting style.
    """
    with mpl.rc_context(rc=REPORT_STYLE):
        yield


@contextmanager
def presentation_style() -> Iterator[None]:
    """
    Temporarily apply the presentation plotting style.
    """
    with mpl.rc_context(rc=PRESENTATION_STYLE):
        yield
