# Copyright (c) 2026 Aiken Engineering
# SPDX-License-Identifier: MIT

"""
Plotting utilities for engineering_tools.

This subpackage provides:
- Matplotlib style configuration
- Engineering-focused plotting helpers
- Domain-specific plotting functions
"""

from engineering_tools.plotting.styles import (
    ENGINEERING_STYLE,
    PRESENTATION_STYLE,
    REPORT_STYLE,
    engineering_style,
    presentation_style,
    report_style,
    reset_style,
    use_engineering_style,
    use_presentation_style,
    use_report_style,
)

from engineering_tools.plotting.colors import (
    RGB255,
    RGB01,
    ANSYS_COLORS,
    ANSYS_LISTED_CMAP,
    ANSYS_LINEAR_CMAP,
    validate_rgb255,
    rgb255_to_rgb01,
    rgb255_sequence_to_rgb01,
    make_listed_colormap,
    make_linear_colormap,
)

from engineering_tools.plotting.scatter import (
    scatter_with_filter
)

__all__ = [
    # Styles
    "ENGINEERING_STYLE",
    "PRESENTATION_STYLE",
    "REPORT_STYLE",
    "engineering_style",
    "presentation_style",
    "report_style",
    "reset_style",
    "use_engineering_style",
    "use_presentation_style",
    "use_report_style",

    # Colors
    "RGB255",
    "RGB01",
    "ANSYS_COLORS",
    "ANSYS_LISTED_CMAP",
    "ANSYS_LINEAR_CMAP",
    "validate_rgb255",
    "rgb255_to_rgb01",
    "rgb255_sequence_to_rgb01",
    "make_listed_colormap",
    "make_linear_colormap",

    # Scatter
    "scatter_with_filter"
]
