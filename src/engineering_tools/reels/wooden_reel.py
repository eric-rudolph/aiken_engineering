from dataclasses import dataclass
from numpy import pi
from .lumber import Lumber


@dataclass
class Drum:
    diameter: float
    length: float
    thickness: float = 0.0
    circumference: float = 0.0
    lumber: Lumber = Lumber.TWO_BY_FOUR

    def __post_init__(self):
        self.thickness = self.lumber.thickness
        self.circumference = pi * self.diameter


@dataclass(frozen=True)
class Flange:
    diameter: float
    thickness: float
    groove_depth: float
    lumber: Lumber = Lumber.TWO_BY_SIX


@dataclass(frozen=True)
class Core:
    ply_thickness: float
    num_plies: int
    diameter: float


@dataclass(frozen=True)
class TensionRod:
    diameter: float

    @property
    def cross_section_area(self):
        return pi * self.diameter * self.diameter / 4.0


@dataclass(frozen=True)
class Pipe:
    diameter: float
    cross_section_area: float
    moment_of_inertia: float
    radius_of_gyration: float
    length: float

    @property
    def Ixx(self):
        return self.moment_of_inertia

    @property
    def rg(self):
        return self.radius_of_gyration


@dataclass(frozen=True)
class WoodenReel:
    drum: Drum
    flange: Flange
    core: Core
    num_cores: int
    tension_rod: TensionRod
    num_tension_rods: int
    arbor_pipe: Pipe
    spacer_pipe: Pipe
    num_spacer_pipes: int
    # TODO: add a function to calculate the weight
    weight: float = 0.0

@dataclass(frozen=True)
class Product:
    diameter: float
    weight_ppf: float
    back_tension: float