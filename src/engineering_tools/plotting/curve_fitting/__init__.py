# Copyright (c) 2026 Aiken Engineering
# SPDX-License-Identifier: MIT

"""
Curve fit and plot utility for scatter data.  Accepts a variety of input types.
Plot shows original data, filtered data, and fitted curve with rendered equation.

 Supports the following input types:

 1. Dataframe with named columns:
    fit(data=df, x="x_column", y="y_column")

 2. DaraFrame y-series:
    fit(data=df, y="y_column")
    # x becomes 0,1,2,3,...

 3. Separate x and y arrays:
    fit(data=x_array, y=y_array)

 4. 1D y-series:
    fit(data=y_array)

 5. Nx2 array:
    fit(data=xy_array)
 """

from .graphfit import (
    FilterOptions,
    ChartOptions,
    FitResult,
    fit,
    plot,
    fit_and_plot,
    result_table)

__all__ = [
    "FilterOptions",
    "ChartOptions",
    "FitResult",
    "fit",
    "plot",
    "fit_and_plot",
    "result_table"]