from dataclasses import dataclass


@dataclass
class ShieldMaterial:
    density: float | None = None
    yield_strength: float | None = None
    youngs_modulus: float | None = None
    poisson: float | None = None
    bulk_modulus: float | None = None
    compressive_shear_strength: float | None = None

