from . import RechtModel, Projectile, ShieldMaterial


class PolycarbonateShield(RechtModel):
    def __init__(self, projectile: Projectile):
        super().__init__(projectile=projectile,
                         # fixme - the Recht formulation for Polycarbonate is not getting the same values
                         #  as in the Table 3.2 pg 59.
                         shield_material=ShieldMaterial(
                             density=1.2e3,
                             bulk_modulus=4.0e9,
                             youngs_modulus=2.4e9,
                             yield_strength=100.0e6,
                             compressive_shear_strength=65.0e6))
