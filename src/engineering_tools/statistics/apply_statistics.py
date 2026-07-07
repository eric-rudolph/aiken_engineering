from dataclasses import dataclass
from functools import update_wrapper
from typing import Callable, Any, Mapping

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from numpy.typing import NDArray
from math import ceil

FloatArray = NDArray[np.float64]


@dataclass
class NormalParameter:
    """
    Describes an engineering input having a normal distribution.

    specified: Value normally entered into the engineering calculations.
    mean: Mean of the actual population.
    standard-deviation: Standard deviation of the population.
    units: Units used when displaying the parameter.
    label: optional display name.  If omitted, the function argument name is used.
    """

    specified: float
    mean: float
    standard_deviation: float
    units: str = ""
    label: str = ""

    def __post_init__(self):
        if self.standard_deviation <= 0.0:
            raise ValueError("Standard deviation must be greater than zero.")

    def sample(
            self,
            rng: np.random.Generator,
            sample_size: int,
    ) -> FloatArray:
        return rng.normal(loc=self.mean,
                          scale=self.standard_deviation,
                          size=sample_size)

    def pdf(self, value: FloatArray) -> FloatArray:
        """Evaluate the normal probability density function."""
        z = (value - self.mean) / self.standard_deviation
        coef = 1.0 / (self.standard_deviation * np.sqrt(2.0 * np.pi))
        return coef * np.exp(-0.5 * z ** 2)

    def plot_range(
            self,
            number_of_standard_deviations: float = 4.0,
    ) -> tuple[float, float]:
        num = number_of_standard_deviations
        lower = self.mean - num * self.standard_deviation
        upper = self.mean + num * self.standard_deviation
        padding = 0.25 * self.standard_deviation

        lower = min(lower, self.specified - padding)
        upper = max(upper, self.specified + padding)

        return lower, upper


@dataclass
class AnalysisSummary:
    nominal_result: float
    simulation_mean: float
    simulation_standard_deviation: float
    minimum: float
    percentile_5: float
    median: float
    percentile_95: float
    maximum: float


@dataclass
class AnalysisResult:
    input_samples: dict[str, FloatArray]
    output_samples: FloatArray
    nominal_inputs: dict[str, float]
    nominal_result: float
    parameters: dict[str, NormalParameter]
    output_name: str
    output_units: str

    @property
    def summary(self) -> AnalysisSummary:
        values = self.output_samples

        return AnalysisSummary(
            nominal_result=self.nominal_result,
            simulation_mean=float(np.mean(values)),
            simulation_standard_deviation=float(np.std(values, ddof=1)),
            minimum=float(np.min(values)),
            percentile_5=float(np.percentile(values, 5.0)),
            median=float(np.median(values)),
            percentile_95=float(np.percentile(values, 95.0)),
            maximum=float(np.max(values)),
        )

    def probability_below(self, limit: float) -> float:
        """Return the estimated probability that the output is below the limit."""
        return float(np.mean(self.output_samples < limit))

    def probability_above(self, limit: float) -> float:
        """Return the estimated probability that the output is above the limit."""
        return float(np.mean(self.output_samples > limit))

    def plot(
            self,
            *,
            histogram_bins: int = 60,
            figure_width: float = 12.0,
            subplot_height: float = 4.0,
    ) -> Figure:
        """Plot the input distributions and calculated output distribution."""
        plot_count = len(self.parameters) + 1
        column_count = 2
        row_count = ceil(plot_count / column_count)

        figure, axes = plt.subplots(
            nrows=row_count,
            ncols=column_count,
            figsize=(figure_width, subplot_height * row_count),
            squeeze=False,
        )

        flattened_axes = axes.ravel()

        for axis, (argument_name, parameter) in zip(flattened_axes, self.parameters.items()):
            self._plot_input_distribution(
                axis=axis,
                argument_name=argument_name,
                parameter=parameter,
            )

        output_axis = flattened_axes[len(self.parameters)]
        self._plot_output_distribution(
            axis=output_axis,
            histogram_bins=histogram_bins,
        )

        for axis in flattened_axes[plot_count:]:
            axis.set_visible(False)

        figure.tight_layout()

        return figure

    @staticmethod
    def _plot_input_distribution(
            *,
            axis: plt.Axes,
            argument_name: str,
            parameter: NormalParameter,
    ) -> None:
        lower, upper = parameter.plot_range()
        x_values = np.linspace(lower, upper, 500)
        y_values = parameter.pdf(x_values)

        display_name = parameter.label or argument_name
        unit_suffix = f" [{parameter.units}]" if parameter.label else ""

        axis.plot(x_values, y_values, label="Actual population distribution")
        axis.axvline(parameter.mean, linestyle="--", label=f"Population mean = {parameter.mean:.4g}")
        axis.axvline(parameter.specified, linestyle="-", label=f"Specified value = {parameter.specified:.4g}")
        axis.axvspan(
            parameter.mean - parameter.standard_deviation,
            parameter.mean + parameter.standard_deviation,
            alpha=0.15,
            label=f"Mean ± 1 standard deviation",
        )

        axis.set_title(display_name)
        axis.set_xlabel(f"{display_name}{unit_suffix}")
        axis.set_ylabel("Probability density")
        axis.legend()

    def _plot_output_distribution(
            self,
            *,
            axis: plt.Axes,
            histogram_bins: int,
    ) -> None:
        summary = self.summary
        unit_suffix = f" [{self.output_units}]" if self.output_units else ""

        axis.hist(
            self.output_samples,
            bins=histogram_bins,
            density=True,
            alpha=0.65,
            label="Calculated output distribution"
        )

        axis.axvline(self.nominal_result, linestyle="-",
                     label=f"Result using specified value = {self.nominal_result:.4g}")
        axis.axvline(summary.simulation_mean, linestyle="--", label=f"Monte Carlo mean = {summary.simulation_mean:.4g}")
        axis.axvspan(
            summary.percentile_5,
            summary.percentile_95,
            alpha=0.15,
            label="5th-95th percentile",
        )

        axis.set_title(f"{self.output_name} Distribution")
        axis.set_xlabel(f"{self.output_name}{unit_suffix}")
        axis.set_ylabel("Probability density")
        axis.legend()


class EngineeringCalculations:
    """Wraps a normal engineering calculation and adds uncertainty analysis."""

    def __init__(self, function: Callable[..., float]) -> None:
        self.function = function
        update_wrapper(self, function)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Call the original engineering calculation normally."""
        return self.function(*args, **kwargs)

    def analyze(
            self,
            *,
            parameters: Mapping[str, NormalParameter],
            constants: Mapping[str, Any] | None = None,
            sample_count: int = 50_000,
            random_seed: int | None = None,
            output_name: str = "Calculated results",
            output_units: str = "",
    ) -> AnalysisResult:
        """
        Perform a Monte Carlo uncertainty analysis.
        parameters: Mapping between function argument names and uncertain parameters.
        constants: Function arguments that do not have uncertainty.
        sample_count: Number of Monte Carlo calculations.
        random_seed: Optional seed for reproducible results.
        """
        if sample_count < 2:
            raise ValueError("sample_count must be at least 2.")

        if not parameters:
            raise ValueError("Parameters must not be empty.")

        constants_dict = dict(constants or {})
        parameter_dict = dict(parameters)

        duplicate_names = (parameter_dict.keys() & constants_dict.keys())

        if duplicate_names:
            duplicates = ", ".join(sorted(duplicate_names))
            raise ValueError(f"Arguments cannot be both uncertain and constant: {duplicates}")

        rng = np.random.default_rng(random_seed)

        input_samples = {name: parameter.sample(rng, sample_count) for name, parameter in parameter_dict.items()}
        nominal_inputs = {name: parameter.specified for name, parameter in parameter_dict.items()}
        nominal_arguments = {**nominal_inputs, **constants_dict}
        nominal_result = float(self.function(**nominal_arguments))

        output_samples = self._evaluate_samples(
            input_samples=input_samples,
            constants=constants_dict,
            sample_count=sample_count)
        finite_mask = np.isfinite(output_samples)

        if not np.any(finite_mask):
            raise ValueError("The calculations produced no finite Monte Carlo results.")

        if not np.all(finite_mask):
            output_samples = output_samples[finite_mask]
            input_samples = {name: values[finite_mask] for name, values in input_samples.items()}

        return AnalysisResult(
            input_samples=input_samples,
            output_samples=output_samples,
            nominal_inputs=nominal_inputs,
            nominal_result=nominal_result,
            parameters=parameter_dict,
            output_name=output_name,
            output_units=output_units,
        )

    def _evaluate_samples(
            self,
            *,
            input_samples: dict[str, FloatArray],
            constants: dict[str, Any],
            sample_count: int,
    ) -> FloatArray:
        """
        First attempt is vectorized evaluation.  Fall back is to do individual calls
        when the engineering function does not support NumPy arrays.
        """
        vector_arguments = {**input_samples, **constants, **constants}

        try:
            result = np.asarray(self.function(**vector_arguments), dtype=float)

            if result.size == sample_count:
                return result.reshape(sample_count)

        except (TypeError, ValueError, FloatingPointError):
            pass

        output = np.empty(sample_count, dtype=float)

        for index in range(sample_count):
            arguments = {name: values[index] for name, values in input_samples.items()}
            arguments.update(constants)

            output[index] = self.function(**arguments)

        return output


def engineering_calculations(
        function: Callable[..., float],
) -> EngineeringCalculations:
    """Decorator used to create a Monte Carlo engineering calculation."""
    return EngineeringCalculations(function)
