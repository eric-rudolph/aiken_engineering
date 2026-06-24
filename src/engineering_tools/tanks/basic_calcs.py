def head(calculation_elevation: float,
         fill_height: float,
         specific_gravity: float,
         over_pressure: float = 0.0):
    h = calculation_elevation
    fh = fill_height
    sg = specific_gravity
    op = over_pressure

    p = (fh - h) * sg * 62.4 / 144 + op

    return p
