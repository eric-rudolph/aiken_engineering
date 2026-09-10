from dataclasses import dataclass


@dataclass(frozen=True)
class WoodMaterial:
    modulus: float
    modulus_of_rupture: float
    poisson_ratio: float
    compression_strength_perpendicular: float
    compression_strength_parallel: float
    hardness: float

    @property
    def E(self):
        return self.modulus

    @property
    def St(self):
        return self.modulus_of_rupture

    @property
    def v(self):
        return self.poisson_ratio

    @property
    def Q(self):
        return self.compression_strength_perpendicular

    @property
    def P(self):
        return self.compression_strength_parallel

    @property
    def allowable_bending_stress(self):
        return self.modulus_of_rupture / 3.0

    @property
    def allowable_stress_brittle_material(self):
        return 0.1 * self.modulus_of_rupture

    @property
    def allowable_stear_stress(self):
        return 0.05 * self.modulus_of_rupture


@dataclass(frozen=True)
class SteelMaterial:
    modulus: float = 2.95e7
    poisson_ratio: float = 0.3
    yield_strength: float = 0.0
    tensile_strength: float = 0.0

    @property
    def allowable_tensile_stress(self):
        return 0.6 * self.yield_strength

    @property
    def allowable_shear_stress(self):
        return 0.4 * self.yield_strength