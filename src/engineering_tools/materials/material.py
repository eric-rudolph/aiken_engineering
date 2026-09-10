from dataclasses import dataclass
from ..units import units as u


@dataclass
class Material:
    """Elastic material properties.  Defaults to A36 Steel, SI units."""
    name: str = "ASTM A36"
    yield_strength: float = 36_000.0 * u.psi
    tensile_strength: float = 52_000.0 * u.psi
    elastic_modulus: float = 2.9e7 * u.psi
    poisson_ratio: float = 0.3
    unit_system: u.UnitSystem = u.UnitSystem.US

    @property
    def Fy(self):
        return self.yield_strength

    @Fy.setter
    def Fy(self, value: float):
        self.yield_strength = value

    @property
    def UTS(self):
        return self.tensile_strength

    @UTS.setter
    def UTS(self, value: float):
        self.tensile_strength = value

    @property
    def E(self):
        return self.elastic_modulus

    @E.setter
    def E(self, value: float):
        self.elastic_modulus = value

    @property
    def v(self):
        return self.poisson_ratio

    @v.setter
    def v(self, value: float):
        self.poisson_ratio = value

    def __repr__(self):
        if self.unit_system == u.UnitSystem.SI:
            return f"Material(yield_strength={self.Fy / u.MPa:.0f} MPa)"
        else:
            return f"Material(yield_strength={self.Fy / u.psi:.0f} psi)"


## STRUCTURAL STEEL MATERIALS
A36 = Material()
A53GRB = Material("A36", 35.0 * u.ksi, 60.0 * u.ksi)
A500GRB = Material("A500 Gr B (Tube)", 46.0 * u.ksi, 58.0 * u.ksi)
A992 = Material("A992", 50.0 * u.ksi, 65.0 * u.ksi)
A572GR42 = Material("A572 Gr 42", 42.0 * u.ksi, 60.0 * u.ksi)
A572GR50 = Material("A572 Gr 50", 50.0 * u.ksi, 65.0 * u.ksi)
A572GR55 = Material("A572 Gr 55", 55.0 * u.ksi, 70.0 * u.ksi)
A572GR60 = Material("A572 Gr 60", 60.0 * u.ksi, 75.0 * u.ksi)
A572GR65 = Material("A572 Gr 65", 65.0 * u.ksi, 80.0 * u.ksi)

## STEEL FASTENER MATERIALS
B7 = Material("A193 Gr B7", 105.0 * u.ksi, 125.0 * u.ksi)
