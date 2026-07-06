"""
Curve fit model definitions for use in the graphfit module.
"""
from dataclasses import dataclass
from typing import Callable
import numpy as np

ArrayLike = np.ndarray | list[float] | tuple[float, ...]


@dataclass(frozen=True)
class CurveModel:
    name: str
    func: Callable
    param_names: tuple[str, ...]
    min_points: int
    domain: Callable[[np.ndarray, np.ndarray], np.ndarray]
    initial_guess: Callable[[np.ndarray, np.ndarray], list[float]]
    equation_latex: Callable[[np.ndarray], str]


# Formatting helper functions

def _fmt_float(value: float, sig_figs: int = 4) -> str:
    return f"{value:.{sig_figs}g}"


def _fmt_signed_float(value: float, sig_figs: int = 4) -> str:
    if value < 0.0:
        return f"- {_fmt_float(value, sig_figs)}"
    return f"+ {_fmt_float(value, sig_figs)}"


# Curve model definitions

def _finite_domain(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.isfinite(x) & np.isfinite(y)


def _positive_x_domain(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.isfinite(x) & np.isfinite(y) & (x > 0)


def _linear(x: ArrayLike | float, a: float, b: float) -> ArrayLike | float:
    return a * x + b


def _quadratic(x: ArrayLike | float, a: float, b: float, c: float) -> ArrayLike | float:
    return a * x ** 2 + b * x + c


def _cubic(x: ArrayLike | float, a: float, b: float, c: float, d: float) -> ArrayLike | float:
    return a * x ** 3 + b * x ** 2 + c * x + d


def _exponential(x: ArrayLike | float, a: float, b: float, c: float) -> ArrayLike | float:
    return a * np.exp(b * x) + c


def _logarithmic(x: ArrayLike | float, a: float, b: float) -> ArrayLike | float:
    return a * np.log(x) + b


def _power(x: ArrayLike | float, a: float, b: float, c: float) -> ArrayLike | float:
    return a * np.power(x, b) + c


linear_curve_model = CurveModel(
    name="linear",
    func=_linear,
    param_names=("a", "b"),
    min_points=2,
    domain=_finite_domain,
    initial_guess=lambda x, y: [1.0, float(np.mean(y))],
    equation_latex=lambda p: rf"$y = {_fmt_float(p[0])}x "
                             rf"{_fmt_signed_float(p[1])}"
)

quadratic_curve_model = CurveModel(
    name="quadratic",
    func=_quadratic,
    param_names=("a", "b", "c"),
    min_points=3,
    domain=_finite_domain,
    initial_guess=lambda x, y: [1.0, 0.0, float(np.mean(y))],
    equation_latex=lambda p: rf"{_fmt_float(p[0])}x^2 "
                             rf"{_fmt_signed_float(p[1])}x "
                             rf"{_fmt_signed_float(p[2])}"
)

cubic_curve_model = CurveModel(
    name="cubic",
    func=_cubic,
    param_names=("a", "b", "c", "d"),
    min_points=4,
    domain=_finite_domain,
    initial_guess=lambda x, y: [1.0, 1.0, 1.0, float(np.mean(y))],
    equation_latex=lambda p: rf"{_fmt_float(p[0])}x^3 "
                             rf"{_fmt_signed_float(p[1])}x^2 "
                             rf"{_fmt_signed_float(p[2])}x "
                             rf"{_fmt_signed_float(p[3])}"
)

exponential_curve_model = CurveModel(
    name="exponential",
    func=_exponential,
    param_names=("a", "b", "c"),
    min_points=3,
    domain=_finite_domain,
    initial_guess=lambda x, y: [float(np.max(y) - np.mean(y) or 1.0),
                                0.01,
                                float(np.min(y))],
    equation_latex=lambda p: rf"{_fmt_float(p[0])}e^{{{_fmt_float(p[1])}x}} "
                             rf"{_fmt_signed_float(p[2])}"
)

logarithmic_curve_model = CurveModel(
    name="logarithmic",
    func=_logarithmic,
    param_names=("a", "b"),
    min_points=2,
    domain=_positive_x_domain,
    initial_guess=lambda x, y: [1.0, float(np.mean(y))],
    equation_latex=lambda p: rf"{_fmt_float(p[0])} \ln(x) "
                             rf"{_fmt_signed_float(p[1])})"
)

power_curve_model = CurveModel(
    name="power",
    func=_power,
    param_names=("a", "b", "c"),
    min_points=3,
    domain=_positive_x_domain,
    initial_guess=lambda x, y: [1.0, 1.0, 1.0],
    equation_latex=lambda p: rf"$y = {_fmt_float(p[0])}x^{{{_fmt_float(p[1])}}} "
                             rf"{_fmt_signed_float(p[2])}$"
)

CURVE_MODELS: dict[str, CurveModel] = {
    "linear": linear_curve_model,
    "quadratic": quadratic_curve_model,
    "cubic": cubic_curve_model,
    "exponential": exponential_curve_model,
    "logarithmic": logarithmic_curve_model,
    "power": power_curve_model,
}
