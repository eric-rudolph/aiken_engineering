from dataclasses import dataclass
import numpy as np
from .impact_helpers import check_float


@dataclass
class Projectile:
    mass: float
    diameter: float
    velocity: float

    @property
    def area(self) -> float:
        if not check_float(self.diameter):
            raise TypeError("Projectile diameter must be a float")
        return np.pi / 4 * self.diameter ** 2
