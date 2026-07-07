import pytest
from math import pi
from engineering_tools.impact import Projectile

@pytest.fixture
def projectile():
    return Projectile(
        mass=1.0,
        diameter=2.0,
        velocity=1.0,
    )

def test_projectile_area(projectile):
    assert projectile.area == pytest.approx(pi)