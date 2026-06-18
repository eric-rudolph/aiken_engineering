from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest

from engineering_tools import (
    ENGINEERING_STYLE,
    use_engineering_style,
)

@pytest.fixture(autouse=True)
def restore_matplotlib_style():
    """
    Restore Matplotlib defaults before and after each test.
    This keeps global rc Params changes from leaking between tests.
    """
    plt.rcdefaults()
    yield
    plt.rcdefaults()


def test_use_engineering_style_updates_rcparams():
    use_engineering_style()

    assert mpl.rcParams["axes.grid"] == ENGINEERING_STYLE["axes.grid"]

