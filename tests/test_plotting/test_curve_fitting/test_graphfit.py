import numpy as np
import pandas as pd
import pytest

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

import engineering_tools.plotting.curve_fitting.graphfit as gf

def test_linear_fit_exact_data():
    x = np.array([0, 1, 2, 3, 4, 5], dtype=float)
    y = 2.0 * x + 1.0

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
    )

    assert result.model_name == "linear"
    assert result.param_names == ("a", "b")
    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)
    assert result.r_squared == pytest.approx(1.0)
    assert np.all(result.used_mask)
    assert not np.any(result.filtered_mask)

def test_quadratic_fit_exact_data():
    x = np.array([-2, -1, 0, 1, 2, 3], dtype=float)
    y = 3.0 * x**2 + 2.0 * x + 5.0

    result = gf.fit(
        data=x,
        y=y,
        model="quadratic",
    )

    assert result.model_name == "quadratic"
    assert result.params[0] == pytest.approx(3.0)
    assert result.params[1] == pytest.approx(2.0)
    assert result.params[2] == pytest.approx(5.0)
    assert result.r_squared == pytest.approx(1.0)


def test_dataframe_input_with_named_columns():
    df = pd.DataFrame(
        {
            "time": [0, 1, 2, 3, 4],
            "force": [1, 3, 5, 7, 9],
        }
    )

    result = gf.fit(
        data=df,
        x="time",
        y="force",
        model="linear",
    )

    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_dataframe_y_series_uses_index_as_x():
    df = pd.DataFrame(
        {
            "force": [1, 3, 5, 7, 9],
        }
    )

    result = gf.fit(
        data=df,
        y="force",
        model="linear",
    )

    assert np.array_equal(result.x, np.array([0, 1, 2, 3, 4], dtype=float))
    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_one_dimensional_y_series_uses_index_as_x():
    y = np.array([1, 3, 5, 7, 9], dtype=float)

    result = gf.fit(
        data=y,
        model="linear",
    )

    assert np.array_equal(result.x, np.array([0, 1, 2, 3, 4], dtype=float))
    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_nx2_array_input():
    xy = np.array(
        [
            [0, 1],
            [1, 3],
            [2, 5],
            [3, 7],
            [4, 9],
        ],
        dtype=float,
    )

    result = gf.fit(
        data=xy,
        model="linear",
    )

    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_range_filter_excludes_points_outside_x_range():
    x = np.array([0, 1, 2, 3, 4, 5], dtype=float)
    y = 2.0 * x + 1.0

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
        filters=gf.FilterOptions(
            x_min=1.0,
            x_max=4.0,
        ),
    )

    expected_used = np.array([False, True, True, True, True, False])

    assert np.array_equal(result.used_mask, expected_used)
    assert np.array_equal(result.filtered_mask, ~expected_used)
    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_rising_monotonic_filter():
    x = np.array([0, 1, 2, 3, 4], dtype=float)
    y = np.array([1.0, 2.0, 1.5, 3.0, 2.5], dtype=float)

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
        filters=gf.FilterOptions(
            monotonic="increasing",
        ),
    )

    expected_used = np.array([True, True, False, True, False])

    assert np.array_equal(result.used_mask, expected_used)
    assert np.array_equal(result.filtered_mask, ~expected_used)


def test_falling_monotonic_filter():
    x = np.array([0, 1, 2, 3, 4], dtype=float)
    y = np.array([5.0, 4.0, 4.5, 3.0, 3.5], dtype=float)

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
        filters=gf.FilterOptions(
            monotonic="decreasing",
        ),
    )

    expected_used = np.array([True, True, False, True, False])

    assert np.array_equal(result.used_mask, expected_used)
    assert np.array_equal(result.filtered_mask, ~expected_used)


def test_custom_filter():
    x = np.array([0, 1, 2, 3, 4, 5], dtype=float)
    y = 2.0 * x + 1.0

    def keep_even_x(x_values, y_values):
        return x_values % 2 == 0

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
        filters=gf.FilterOptions(
            custom_filter=keep_even_x,
        ),
    )

    expected_used = np.array([True, False, True, False, True, False])

    assert np.array_equal(result.used_mask, expected_used)
    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_sigma_clip_removes_large_outlier():
    x = np.arange(21, dtype=float)
    y = 2.0 * x + 1.0

    y[10] = 1000.0

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
        filters=gf.FilterOptions(
            sigma_clip=True,
            sigma_clip_threshold=3.0,
        ),
    )

    assert not result.used_mask[10]
    assert result.filtered_mask[10]
    assert result.params[0] == pytest.approx(2.0)
    assert result.params[1] == pytest.approx(1.0)


def test_logarithmic_requires_positive_x():
    x = np.array([-1, 0, 1, 2], dtype=float)
    y = np.array([1, 2, 3, 4], dtype=float)

    result = gf.fit(
        data=x,
        y=y,
        model="logarithmic",
    )

    assert np.array_equal(
        result.used_mask,
        np.array([False, False, True, True]),
    )


def test_invalid_model_raises_value_error():
    x = np.array([0, 1, 2], dtype=float)
    y = np.array([1, 2, 3], dtype=float)

    with pytest.raises(ValueError):
        gf.fit(
            data=x,
            y=y,
            model="not_a_model",
        )


def test_too_few_points_raises_value_error():
    x = np.array([0, 1], dtype=float)
    y = np.array([1, 2], dtype=float)

    with pytest.raises(ValueError, match="requires at least"):
        gf.fit(
            data=x,
            y=y,
            model="quadratic",
        )


def test_custom_filter_wrong_shape_raises_value_error():
    x = np.array([0, 1, 2], dtype=float)
    y = np.array([1, 2, 3], dtype=float)

    def bad_filter(x_values, y_values):
        return np.array([True, False])

    with pytest.raises(ValueError, match="same shape"):
        gf.fit(
            data=x,
            y=y,
            model="linear",
            filters=gf.FilterOptions(
                custom_filter=bad_filter,
            ),
        )


def test_plot_returns_figure_and_axes():
    x = np.array([0, 1, 2, 3, 4], dtype=float)
    y = 2.0 * x + 1.0

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
    )

    fig, ax = gf.plot(
        result,
        chart=gf.ChartOptions(
            title="Test Plot",
            xlabel="X Label",
            ylabel="Y Label",
        ),
    )

    assert fig is not None
    assert ax is not None
    assert ax.get_title() == "Test Plot"
    assert ax.get_xlabel() == "X Label"
    assert ax.get_ylabel() == "Y Label"

    plt.close(fig)


def test_fit_and_plot_returns_result_figure_and_axes():
    x = np.array([0, 1, 2, 3, 4], dtype=float)
    y = 2.0 * x + 1.0

    result, fig, ax = gf.fit_and_plot(
        data=x,
        y=y,
        model="linear",
    )

    assert isinstance(result, gf.FitResult)
    assert fig is not None
    assert ax is not None

    plt.close(fig)


def test_result_table():
    x = np.array([0, 1, 2, 3], dtype=float)
    y = 2.0 * x + 1.0

    result = gf.fit(
        data=x,
        y=y,
        model="linear",
    )

    table = gf.result_table(result)

    assert list(table.columns) == ["parameter", "value"]
    assert list(table["parameter"]) == ["a", "b"]
    assert table.loc[0, "value"] == pytest.approx(2.0)
    assert table.loc[1, "value"] == pytest.approx(1.0)