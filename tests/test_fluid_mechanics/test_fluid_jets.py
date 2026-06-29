import pytest
from math import pi

from engineering_tools.fluid_mechanics.fluid_jets import (
    FluidJetElement,
    volumetric_flow_rate,
    jet_velocity,
    jet_force_on_plate,
)


@pytest.fixture
def fluid_jet_element():
    return FluidJetElement(650, 2, 0.8, 0.9, 998)


def test_area(fluid_jet_element):
    assert fluid_jet_element.area == pytest.approx(3.14159, rel=1e-2)


def test_volumetric_flow_rate(fluid_jet_element):
    assert volumetric_flow_rate(fluid_jet_element) == pytest.approx(3.226996, rel=1e-2)

def test_jet_velocity(fluid_jet_element):
    assert jet_velocity(fluid_jet_element) == pytest.approx(0.913054, rel=1e-2)

def test_jet_force_on_plate(fluid_jet_element):
    assert jet_force_on_plate(fluid_jet_element) == pytest.approx(2940.53, rel=1e-2)
    assert jet_force_on_plate(fluid_jet_element, pi/8) == pytest.approx(1125.29, rel=1e-2)