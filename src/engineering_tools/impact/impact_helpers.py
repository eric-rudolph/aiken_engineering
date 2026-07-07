import numpy as np


def check_float(value) -> bool:
    return isinstance(value, float) or np.issubdtype(value, np.floating)
