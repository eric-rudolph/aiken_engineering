from dataclasses import dataclass
from typing import Callable, Literal

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.optimize import curve_fit
from .curve_model import *

ArrayLike = np.ndarray | list[float] | tuple[float, ...]


@dataclass
class FilterOptions:
    x_min: float | None = None
    x_max: float | None = None
    y_min: float | None = None
    y_max: float | None = None
    monotonic: Literal["none", "increasing", "decreasing"] = "none"
    sigma_clip: bool = False
    sigma_clip_threshold: float = 3.0
    custom_filter: Callable[[np.ndarray, np.ndarray], np.ndarray] = None


@dataclass
class ChartOptions:
    """
    Options for customizing the appearance of the curve fit plot.
        title: str
        xlabel: str
        ylabel: str
        xlim: tuple[float | None, float | None] | None
        ylim: tuple[float | None, float | None] | None
        log_x: bool
        log_y: bool
        figsize: tuple[float, float]
        show_legend: bool
        show_equation: bool
        equation_position: tuple[float, float]
        equation_sig_figs: int
        equation_fontsize: int = 10
        curve_color: str = "black"
        scatter_color: str = "darkgray"
        filter_color: str = "lightgray"
    """
    title: str = "Curve Fit"
    xlabel: str = "X"
    ylabel: str = "Y"
    xlim: tuple[float | None, float | None] | None = None
    ylim: tuple[float | None, float | None] | None = None
    log_x: bool = False
    log_y: bool = False
    figsize: tuple[float, float] = (6.0, 4.0)
    show_legend: bool = False
    show_equation: bool = True
    equation_position: tuple[float, float] = (0.05, 0.95)
    equation_sig_figs: int = 4
    equation_fontsize: int = 10
    curve_color: str = "black"
    scatter_color: str = "darkgray"
    filter_color: str = "lightgray"


@dataclass
class FitResult:
    model_name: str
    param_names: tuple[str, ...]
    params: np.ndarray
    covariance: np.ndarray
    x: np.ndarray
    y: np.ndarray
    used_mask: np.ndarray
    filtered_mask: np.ndarray
    equation_latex: str
    residuals: np.ndarray
    residual_sigma: float
    r_squared: float


def _prepare_xy_data(data: pd.DataFrame | ArrayLike,
                     x: str | None = None,
                     y: str | ArrayLike | None = None, ) -> tuple[np.ndarray, np.ndarray]:
    """
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

    if isinstance(data, pd.DataFrame):
        if y is None:
            raise ValueError("y must specified 'column_name' when data is a DataFrame")

        y_values = pd.to_numeric(data[y], errors="coerce").to_numpy(dtype=float)

        if x is None:
            x_values = np.arange(len(y_values), dtype=float)
        else:
            x_values = pd.to_numeric(data[x], errors="coerce").to_numpy(dtype=float)

    else:
        arr = np.asarray(data, dtype=float)

        if y is not None:
            x_values = arr
            y_values = np.asarray(y, dtype=float)

        elif arr.ndim == 1:
            y_values = arr
            x_values = np.arange(len(y_values), dtype=float)

        elif arr.ndim == 2 and arr.shape[1] >= 2:
            x_values = arr[:, 0]
            y_values = arr[:, 1]
        else:
            raise ValueError("Data must be a DataFrame, a 1D y-series, an Nx2 array, "
                             "or separate x/y arrays.")

    if len(x_values) != len(y_values):
        raise ValueError("x and y must be the same length")

    return x_values.astype(float), y_values.astype(float)


def _apply_range_filters(x: np.ndarray,
                         y: np.ndarray,
                         mask: np.ndarray,
                         filters: FilterOptions) -> np.ndarray:
    new_mask = mask.copy()

    if filters.x_min is not None:
        new_mask &= x >= filters.x_min
    if filters.x_max is not None:
        new_mask &= x <= filters.x_max
    if filters.y_min is not None:
        new_mask &= y >= filters.y_min
    if filters.y_max is not None:
        new_mask &= y <= filters.y_max

    return new_mask


def _apply_monotonic_filter(x: np.ndarray,
                            y: np.ndarray,
                            mask: np.ndarray,
                            mode: Literal["none", "increasing", "decreasing"]) -> np.ndarray:
    if mode == "none":
        return mask.copy()

    new_mask = np.zeros_like(mask, dtype=bool)
    valid_indices = np.where(mask)[0]
    sorted_indices = valid_indices[np.argsort(x[valid_indices])]

    last_y = None

    for idx in sorted_indices:
        current_y = y[idx]

        if last_y is None:
            new_mask[idx] = True
            last_y = current_y
            continue

        if (mode == "increasing") and (current_y >= last_y):
            new_mask[idx] = True
            last_y = current_y
            continue

        if (mode == "decreasing") and (current_y <= last_y):
            new_mask[idx] = True
            last_y = current_y

    return new_mask


def _apply_custom_filter(x: np.ndarray,
                         y: np.ndarray,
                         mask: np.ndarray,
                         custom_filter: Callable[[np.ndarray, np.ndarray], np.ndarray] | None,
                         ) -> np.ndarray:
    if custom_filter is None:
        return mask.copy()

    custom_mask = np.asarray(custom_filter(x, y), dtype=bool)

    if custom_mask.shape != mask.shape:
        raise ValueError("Custom filter must return a mask with the same shape as the input mask.")

    return mask & custom_mask


def _fit_once(x: np.ndarray,
              y: np.ndarray,
              mask: np.ndarray,
              model: CurveModel) -> tuple[np.ndarray, np.ndarray]:
    x_fit = x[mask]
    y_fit = y[mask]

    if len(x_fit) < model.min_points:
        raise ValueError(f"{model.name} requires at least {model.min_points} usable points to fit.")

    p0 = model.initial_guess(x_fit, y_fit)

    params, covariance = curve_fit(model.func, x_fit, y_fit, p0=p0, maxfev=20_000)

    return params, covariance


def _apply_sigma_clip(x: np.ndarray,
                      y: np.ndarray,
                      mask: np.ndarray,
                      model: CurveModel,
                      sigma_multiplier: float) -> np.ndarray:
    params, _ = _fit_once(x, y, mask, model)

    residuals = y[mask] - model.func(x[mask], *params)
    sigma = float(np.std(residuals))

    if sigma <= 0 or not np.isfinite(sigma):
        return mask.copy()

    all_residuals = np.full_like(y, np.nan, dtype=float)
    all_residuals[mask] = y[mask] - model.func(x[mask], *params)

    return mask & (np.abs(all_residuals) <= sigma_multiplier * sigma)


def fit(data: pd.DataFrame | ArrayLike,
        x: str | None = None,
        y: str | ArrayLike | None = None,
        model: str = "linear",
        filters: FilterOptions | None = None) -> FitResult:
    """
    Fit data to a predefined curve model.

    Examples
    --------
    DataFrame:
        result = fit(df, x="time", y="force", model="linear")

    y-series:
        result = fit(y_values, model="quadratic")

    separate arrays:
        result = fit(x_values, y=y_values, model="exponential")

    Nx2 array:
        result = fit(xy_array, model="power")
    """

    if filters is None:
        filters = FilterOptions()

    model_key = model.lower()

    if model_key not in CURVE_MODELS:
        valid = ", ".join(CURVE_MODELS)
        raise ValueError(f"Invalid model '{model}'. Valid models are: {valid}")

    curve_model = CURVE_MODELS[model_key]

    x_values, y_values = _prepare_xy_data(data, x, y)

    mask = curve_model.domain(x_values, y_values)
    mask = _apply_range_filters(x_values, y_values, mask, filters)
    mask = _apply_monotonic_filter(x_values, y_values, mask, filters.monotonic)
    mask = _apply_custom_filter(x_values, y_values, mask, filters.custom_filter)

    if filters.sigma_clip:
        mask = _apply_sigma_clip(x_values, y_values, mask, curve_model, filters.sigma_clip)

    params, covariance = _fit_once(x_values, y_values, mask, curve_model)

    y_pred = curve_model.func(x_values[mask], *params)
    residuals = y_values[mask] - y_pred

    ss_res = float(np.sum(residuals ** 2))
    ss_tot = float(np.sum((y_values[mask] - np.mean(y_values[mask])) ** 2))

    if ss_tot > 0:
        r_squared = 1.0 - (ss_res / ss_tot)
    else:
        r_squared = np.nan

    residual_sigma = float(np.std(residuals))

    filtered_mask = np.isfinite(x_values) & np.isfinite(y_values) & ~mask

    return FitResult(
        model_name=curve_model.name,
        param_names=curve_model.param_names,
        params=params,
        covariance=covariance,
        x=x_values,
        y=y_values,
        used_mask=mask,
        filtered_mask=filtered_mask,
        equation_latex=curve_model.equation_latex(params, 4),
        residuals=residuals,
        residual_sigma=residual_sigma,
        r_squared=r_squared
    )


def _curve_x_values(x_used: np.ndarray,
                    model_name: str,
                    log_x: bool,
                    n: int = 1000) -> np.ndarray:
    x_min: float = float(np.min(x_used))
    x_max: float = float(np.max(x_used))

    if x_min == x_max:
        x_min -= 0.5
        x_max += 0.5

    needs_positive_x: bool = model_name in {"logarithmic", "power"} or log_x

    if needs_positive_x:
        positive_x = x_used[x_used > 0]

        if len(positive_x) == 0:
            raise ValueError("Positive x values are required for this model.")

        x_min = max(float(np.min(positive_x)), 1e-12)
        x_max = float(np.max(positive_x))

        return np.geomspace(x_min, x_max, n)

    return np.linspace(x_min, x_max, n)


def plot(result: FitResult,
         chart: ChartOptions | None = None):
    """
    Plot original data, filtered data, and fitted curve.

    Returns
    -------
    fig, ax
    """

    if chart is None:
        chart = ChartOptions()

    curve_model = CURVE_MODELS[result.model_name]

    fig, ax = plt.subplots(figsize=chart.figsize)

    # plot all data in grey
    ax.scatter(result.x, result.y, color=chart.scatter_color, alpha=0.5, s=1,
               label='Original Data', zorder=1)

    # overlay filtered/excluded data in light grey.
    ax.scatter(result.x[result.filtered_mask], result.y[result.filtered_mask],
               color=chart.filter_color, alpha=1.0, s=1, label='Filtered Data', zorder=2)

    # plot curve
    curve_x = _curve_x_values(result.x[result.used_mask],
                              model_name=result.model_name,
                              log_x=chart.log_x)

    curve_y = curve_model.func(curve_x, *result.params)

    ax.plot(curve_x, curve_y, color=chart.curve_color,
            linewidth=1.5,
            label="Curve fit", zorder=3)

    if chart.show_equation:
        equation_text = curve_model.equation_latex(result.params, chart.equation_sig_figs)

        ax.text(chart.equation_position[0], chart.equation_position[1],
                equation_text, va="top", ha="left",
                transform=ax.transAxes,
                fontsize=chart.equation_fontsize,
                bbox={"boxstyle": "round",
                      "facecolor": "white",
                      "edgecolor": "black",
                      "alpha": 0.85})

    ax.set_title(chart.title)
    ax.set_xlabel(chart.xlabel)
    ax.set_ylabel(chart.ylabel)

    if chart.xlim is not None:
        ax.set_xlim(*chart.xlim)

    if chart.ylim is not None:
        ax.set_ylim(*chart.ylim)

    if chart.log_x:
        ax.set_xscale("log")

    if chart.log_y:
        ax.set_yscale("log")

    if chart.show_legend:
        ax.legend()

    fig.tight_layout()

    return fig, ax


def fit_and_plot(data: pd.DataFrame | ArrayLike,
                 x: str | None = None,
                 y: str | ArrayLike | None = None,
                 model: str = "linear",
                 filters: FilterOptions | None = None,
                 chart: ChartOptions | None = None):
    """
    This is a convenience function for application in notebooks.

    Returns
    -------
    result, fig, ax
    """

    result = fit(data=data, x=x, y=y, model=model, filters=filters)

    fig, ax = plot(result, chart=chart)

    return result, fig, ax


def result_table(result: FitResult) -> pd.DataFrame:
    """
    Return fitted parameters as a DataFrame.
    """
    return pd.DataFrame(
        {"parameter": result.param_names,
         "value": result.params}
    )


def equation_latex(result: FitResult, sig_figs: int = 4) -> str:
    """
    Return the equation as a LaTeX string.
    """
    curve_model = CURVE_MODELS[result.model_name]
    return curve_model.equation_latex(result.params, sig_figs)
