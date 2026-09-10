import numpy as np
from ..utilities.np_utils import (FloatArray, FloatOrArray, IntArray, IntOrArray)
# from numpy import pi, sin, radians

from .wooden_reel import Drum, Flange, Core, TensionRod, Pipe, WoodenReel, Product
from .lumber import Lumber
from .reel_materials import WoodMaterial, SteelMaterial


def number_of_wraps(
        flange_diameter: FloatOrArray,
        drum_diameter: FloatOrArray,
        product_diameter: FloatOrArray,
) -> IntOrArray:
    """Calculates the number of wraps that can fit on the reel to the nearest integer value."""

    flange_diameter: FloatArray = np.asarray(flange_diameter)
    drum_diameter: FloatArray = np.asarray(drum_diameter)
    product_diameter: FloatArray = np.asarray(product_diameter)

    flange_width: FloatArray = 0.5 * (flange_diameter - drum_diameter)

    wraps: FloatArray = (flange_width / product_diameter - 0.5) / np.sin(np.radians(60.0)) + 1.0

    return wraps.astype(int)


def turns_per_wrap(
        drum_length: FloatOrArray,
        product_diameter: FloatOrArray,
) -> IntOrArray:
    """Calculates the number of turns that can fit on the reel to the nearest integer value."""

    drum_length: FloatArray = np.asarray(drum_length)
    product_diameter: FloatArray = np.asarray(product_diameter)

    turns: FloatArray = drum_length / product_diameter

    return turns.astype(int)


def mean_radius_of_a_wrap(
        drum_diameter: FloatOrArray,
        product_diameter: FloatOrArray,
        wrap_number: int = 1,
) -> FloatOrArray:
    """Calculate the mean diameter of a wrap of pipe on the drum."""

    drum_diameter: FloatArray = np.asarray(drum_diameter)
    product_diameter: FloatArray = np.asarray(product_diameter)
    wrap_number: int = int(wrap_number)

    if wrap_number == 1:
        return 0.5 * drum_diameter + 0.5 * product_diameter

    elif wrap_number > 1:
        return (product_diameter * np.sin(np.radians(60.0)) +
                mean_radius_of_a_wrap(drum_diameter, product_diameter, wrap_number - 1))

    else:
        return 0.0


def mean_wrap_radii(
        flange_diameter: float,
        drum_diameter: float,
        product_diameter: float,
) -> FloatOrArray:
    """Returns a list of radii for each wrap."""

    flange_diameter: FloatArray = np.asarray(flange_diameter)
    drum_diameter: FloatArray = np.asarray(drum_diameter)
    product_diameter: FloatArray = np.asarray(product_diameter)

    wraps: IntOrArray = number_of_wraps(flange_diameter, drum_diameter, product_diameter)

    diams: FloatArray = np.asarray([
        mean_radius_of_a_wrap(drum_diameter, product_diameter, wrap_number=i)
        for i in range(1, wraps + 1)
    ])

    return diams


# TODO: I AM HERE !!!



def max_product_weight(
        reel: WoodenReel,
        product: Product,
) -> float:
    """Calculates the weight of the maximum amount of product wrapped on the reel."""
    turns = turns_per_wrap(reel.drum.length, product.diameter)
    radii = mean_wrap_radii(reel.flange.diameter, reel.drum.diameter, product.diameter)
    weight: float = 0.0
    for r in radii:
        weight += product.weight_ppf / 6.0 * r * pi * turns

    return weight


def radial_pressure_from_wrap(
        mean_wrap_radius: float,
        product_diameter: float,
        tension: float,
) -> float:
    """Calculate the radial pressure from a wrap in psi."""
    return tension / (mean_wrap_radius * product_diameter)


def pressure_on_drum(
        reel: WoodenReel,
        product: Product,
) -> float:
    """Calculate the drum load due to pressure from the wraps.  The pressure comes from
    the outer two wraps (Ref. Blodget, Steel Rolls 5.3.7)."""
    radii = mean_wrap_radii(reel.flange.diameter, reel.drum.diameter, product.diameter)
    p1 = radial_pressure_from_wrap(radii[-1], product.diameter, product.back_tension)

    if len(radii) > 1:
        p2 = radial_pressure_from_wrap(
            radii[-2], product.diameter, product.back_tension
        )
    else:
        p2 = 0.0

    return p1 + p2


def drum_hoop_stress(
        drum: Drum,
        pressure: float,
        product_weight: float,
        allowable_stress: float | None = None,
) -> tuple[float, float]:
    """Returns the hoop stress and the stress utilization if the allowable stress is supplied."""
    force = pressure * drum.diameter * drum.length + product_weight
    area = 2 * drum.thickness * drum.length
    stress = force / area
    utilization = -1.0
    if allowable_stress:
        utilization = stress / allowable_stress
    return stress, utilization


def max_allowable_pressure_on_core(
        num_cores: int,
        core: Core,
        drum_length: float,
        wood_material: WoodMaterial,
) -> float:
    return (
            0.35
            * wood_material.modulus
            / (1 - wood_material.poisson_ratio ** 2)
            * (core.ply_thickness * core.num_plies / (drum_length / (num_cores + 1))) ** 2
    )


def core_pressure(
        core: Core,
        drum_diameter: float,
        drum_length: float,
        radial_drum_pressure: float,
        num_cores: int = 1,
        allowable_stress: float | None = None,
) -> tuple[float, float]:
    """Returns the circumferential pressure on the core and the stress utilization
    if the allowable stress is supplied."""
    circumferential_area_of_core = (
            pi * core.diameter * core.ply_thickness * core.num_plies
    )
    area_of_drum_supported = pi * drum_diameter * drum_length / (num_cores + 1)
    pressure = (
            radial_drum_pressure * area_of_drum_supported / circumferential_area_of_core
    )
    utilization = -1.0
    if allowable_stress:
        utilization = pressure / allowable_stress
    return pressure, utilization


def tension_rod_tension_lifting_eye_to_horizon(
        tension_rod: TensionRod,
        num_tension_rods: int,
        drum: Drum,
        product_weight: float,
        allowable_stress: float | None = None,
        angular_span_deg: float = 90.0,
) -> tuple[float, float]:
    """Returns the tension_rod tensile stress and the stress utilization if the allowable stress is supplied."""
    angular_span = radians(angular_span_deg)
    distance_moment_reaction = drum.diameter * sin(angular_span / 2.0)
    area_of_tension_rods = (
            tension_rod.cross_section_area * num_tension_rods / (2.0 * pi / angular_span)
    )
    bending_moment = 1.5 * product_weight * drum.length / 8.0
    tension = bending_moment / distance_moment_reaction
    tensile_stress = tension / area_of_tension_rods
    utilization = -1.0
    if allowable_stress:
        utilization = tensile_stress / allowable_stress
    return tensile_stress, utilization


def elastic_critical_buckling_stress(
        elastic_modulus: float,
        effective_length: float,
        radius_of_gyration: float,
        buckling_end_condition: float = 1.0,
) -> float:
    e = elastic_modulus
    l = effective_length
    r = radius_of_gyration
    k = buckling_end_condition
    return pi ** 2 * e / (k * l / r) ** 2


def allowable_compressive_stress(
        elastic_critical_buckling_stress: float,
        yield_strength: float,
) -> float:
    fy = yield_strength
    fe = elastic_critical_buckling_stress
    return fy / 1.67 * (0.658 ** (fy / fe))


def pipe_compression_due_to_lifting(
        pipe: Pipe,
        pipe_material: SteelMaterial,
        product_weight: float,
        reel_weight: float,
        amplification_factor: float,
        num_pipes: int = 1,
) -> tuple[float, float]:
    """Returns the compressive stress in the pipe experienced during lifting and the stress utilization."""
    # TODO: the below calculation could be adjusted by the number of cores shortening the effective length
    E: float = pipe_material.modulus
    fe: float = elastic_critical_buckling_stress(
        E, pipe.length, pipe.radius_of_gyration
    )
    fa: float = allowable_compressive_stress(fe, pipe_material.yield_strength)
    compressive_pressure = (
            (product_weight + reel_weight)
            * amplification_factor
            / pipe.cross_section_area
            / num_pipes
    )
    utilization: float = compressive_pressure / fa
    return compressive_pressure, utilization


def drum_shear_stress(
        drum: Drum,
        groove_depth: float,
        product_weight: float,
        amplification_factor: float,
        allowable_shear_stress: float | None = None,
) -> tuple[float, float]:
    """Returns the shear stress in the drum at each flange and the stress utilization if
    the allowable stress is supplied."""
    force_shear = product_weight / 2.0
    num_boards: float = drum.circumference / drum.lumber.width
    num_per_sector: int = int(num_boards / 4.0)
    # determine force distributed to the boards
    n = int(num_per_sector / 2.0)
    k = 2.0 * sum(cos(pi / 4 * i / n) for i in range(n + 1))
    top_board_force = 1.5 * force_shear * amplification_factor / 2.0 / k
    # half angle shear
    shear_stress = top_board_force / (cos(pi / 4.0) * groove_depth * drum.lumber.width)

    utilization = -1.0
    if allowable_shear_stress:
        utilization: float = shear_stress / allowable_shear_stress
    return shear_stress, utilization


def flange_bending(
        reel: WoodenReel,
        pressure: float,
        num_wraps: int,
        material: WoodMaterial,
) -> tuple[float, float]:
    """Returns the flange bending stress and the stress utilization.
    The bending stress is caused by the force from the outer wrap because the outer wrap causes deflection and
    the load from the inner wraps is relieved."""
    a: float = reel.flange.diameter / 2.0
    b: float = reel.drum.diameter / 2.0
    E: float = material.modulus
    v: float = material.poisson_ratio
    t: float = reel.flange.thickness
    linear_load = pressure * (a - b) / num_wraps

    # Model the flange as a flat plate, Roark's 17th Edition, Table 11.2, Case 1k
    # Constants for Roark's
    D: float = E * t ** 3 / (12.0 * (1 - v ** 2))
    C9: float = b / a * ((1 + v) / 2 * log(a / b) + (1 - v) / 4 * (1 - (b / a) ** 2))
    C7: float = (1 - v ** 2) * (a / b - b / a) / 2

    moment = linear_load * a ** 3 / b ** 2 * (1 - v ** 2) * C9 / C7

    bending_stress: float = 6.0 * moment / t ** 2

    utilization: float = bending_stress / material.allowable_bending_stress

    return bending_stress, utilization


def side_lift_bolt_tension() -> tuple[float, float]:
    return -1.0, -1.0


def side_lift_wood_shear() -> tuple[float, float]:
    return -1.0, -1.0


def side_lift_pipe_tension(
        pipe: Pipe,
        reel_weight: float,
        product_weight: float,
        amplification_factor: float,
        allowable_stress: float | None = None,
        n: int = 4,
) -> tuple[float, float]:
    """Returns the pipe tension stress from lifting with 4 points (uses N-1 for lifting)."""
    w: float = reel_weight + product_weight
    daf: float = amplification_factor
    a: float = pipe.cross_section_area
    stress: float = w * daf / ((n - 1) * a)

    utilization: float = -1.0
    if allowable_stress:
        utilization: float = stress / allowable_stress

    return stress, utilization
