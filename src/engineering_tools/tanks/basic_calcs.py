def head(calculation_elevation_ft: float,
         fill_height_ft: float,
         specific_gravity: float,
         over_pressure_psi: float = 0.0):
    """Return the pressure (psi) - Ref API 650."""
    h = calculation_elevation_ft
    fh = fill_height_ft
    sg = specific_gravity
    op = over_pressure_psi

    p = (fh - h) * sg * 62.4 / 144 + op

    return p
