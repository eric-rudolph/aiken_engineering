from dataclasses import dataclass
import numpy as np


@dataclass
class FluidJetElement:
    pressure: float
    diameter: float
    cv: float = 1.0
    cd: float = 1.0
    rho: float = 1000.0

    @property
    def area(self):
        return np.pi * (self.diameter / 2) ** 2


def volumetric_flow_rate(fluid_jet_element: FluidJetElement) -> float:
    """
    Q = Cd * A * sqrt(2 * p / rho)
    """
    Cd = fluid_jet_element.cd
    A = fluid_jet_element.area
    p = fluid_jet_element.pressure
    rho = fluid_jet_element.rho

    return Cd * A * np.sqrt(2 * p / rho)


def jet_velocity(fluid_jet_element: FluidJetElement) -> float:
    """
    v = Cv * sqrt(2 * p / rho)
    """
    Cv = fluid_jet_element.cv
    p = fluid_jet_element.pressure
    rho = fluid_jet_element.rho

    return Cv * np.sqrt(2 * p / rho)


def jet_force_on_plate(
        fluid_jet_element: FluidJetElement,
        impinging_angle: float = np.pi / 2):
    """
    F = Q * rho * V * sin(theta)
    """
    Q = volumetric_flow_rate(fluid_jet_element)
    V = jet_velocity(fluid_jet_element)
    rho = fluid_jet_element.rho
    theta = impinging_angle

    return Q * rho * V * np.sin(theta)
