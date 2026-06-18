"""
Top-level public API for engineering_tools.
"""

# TODO: Figure out what I really want in the top level API...

from engineering_tools.plotting import (
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

__all__ = [
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
]
