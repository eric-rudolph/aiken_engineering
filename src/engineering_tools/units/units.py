from scipy.constants import *
from enum import Enum, auto

# define some additional common units
m: float = 1.0
N: float = 1.0
s: float = 1.0
kg: float = 1.0
J: float = 1.0
kJ: float = 1000
mm: float = 1 / 1000 * m
cm: float = 1 / 100 * m
ksi: float = 1000 * psi
MPa: float = N / mm ** 2
kPa: float = 1000 * N / m ** 2
kN: float = 1000 * N
ft: float = 12 * inch
psf: float = 144 * psi
kip: float = 1000 * pound_force
L: float = .001 * m ** 3


class UnitSystem(Enum):
    SI = auto()
    US = auto()
