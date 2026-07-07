from abc import ABC, abstractmethod
import numpy as np
from .impact_helpers import check_float
from . import ShieldMaterial, Projectile


class EmpiricalShieldModel(ABC):
    def __init__(self, shield_material: ShieldMaterial, projectile: Projectile):
        self.shield_material = shield_material
        self.projectile = projectile

    @abstractmethod
    def thickness(self) -> float:
        pass

    def _get_projectile_mass(self) -> float:
        mass = self.projectile.mass
        if not check_float(mass):
            raise TypeError("Projectile mass must be a float")
        return mass

    def _get_projectile_velocity(self) -> float:
        velocity = self.projectile.velocity
        if not check_float(velocity):
            raise TypeError("Projectile velocity must be a float")
        return velocity

    def _get_shield_bulk_modulus(self) -> float:
        bulk_modulus = self.shield_material.bulk_modulus
        if not check_float(bulk_modulus):
            raise TypeError("Shield bulk modulus must be a float")
        return bulk_modulus

    def _get_shield_density(self) -> float:
        rho = self.shield_material.density
        if not check_float(rho):
            raise TypeError("Shield density must be a float")
        return rho

    def _get_shield_yield_strength(self) -> float:
        yield_strength = self.shield_material.yield_strength
        if not check_float(yield_strength):
            raise TypeError("Shield yield strength must be a float")
        return yield_strength

    def _get_shield_youngs_modulus(self) -> float:
        youngs_modulus = self.shield_material.youngs_modulus
        if not check_float(youngs_modulus):
            raise TypeError("Shield Young's modulus must be a float")
        return youngs_modulus

    def _get_shield_compressive_shear_strength(self) -> float:
        tau = self.shield_material.compressive_shear_strength
        if not check_float(tau):
            raise TypeError("Shield compressive shear strength must be a float")
        return tau


class RechtModel(EmpiricalShieldModel):
    def __init__(self, shield_material: ShieldMaterial, projectile: Projectile):
        super().__init__(shield_material, projectile)
        print("Ref. Pressure tes safety, HSE, CRR 168/1998, pg. 51")
        print("Recht correlation for ductile materials.")

    def thickness(self) -> float:
        """Calculate the thickness of the shield to resist perforation by 50% of projectiles."""
        # fixme - this is not correct yet for polycarbonate materials
        m: float = self._get_projectile_mass()
        V: float = self._get_projectile_velocity()

        sigma_y: float = self._get_shield_bulk_modulus()
        E: float = self._get_shield_youngs_modulus()
        k: float = self._get_shield_bulk_modulus()
        rho: float = self._get_shield_density()
        tau: float = self._get_shield_compressive_shear_strength()

        A: float = self.projectile.area

        z: float = (E / sigma_y) / np.sqrt(1 + 2 * E / sigma_y)
        a: float = 2 * tau * np.log(2 * z)
        b: float = 0.25 * np.sqrt(k * rho)

        t: float = 1.61 * m / (b * A) * (V - (a / b) * np.log(1 + (b * V / A)))

        return t
