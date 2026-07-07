
import pytest
from engineering_tools.impact import Projectile, PolycarbonateShield

@pytest.fixture
def projectile_list():
    return [Projectile(diameter=0.007, mass=0.0014, velocity=215.0)]

@pytest.fixture
def poly_carbonate_shield(projectile_list):
    return PolycarbonateShield(projectile_list[0])

def test_polycarbonate_shield_thickness(poly_carbonate_shield):
    assert poly_carbonate_shield.thickness() == pytest.approx(0.004, abs=0.001)