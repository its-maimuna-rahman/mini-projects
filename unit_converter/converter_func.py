from decimal import Decimal, getcontext

# High precision for astronomical / quantum scale numbers
getcontext().prec = 50


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _fmt(value):
    """
    Smart formatter.
    - Returns a plain rounded float for everyday numbers.
    - Returns scientific notation string for very large or very small numbers.
    - Uses Python's Decimal under the hood so enormous values never overflow.
    """
    d = Decimal(str(value))
    if Decimal("1e-6") <= abs(d) <= Decimal("1e15") or d == 0:
        # Round to 8 significant digits and strip trailing zeros
        return float(f"{float(d):.8g}")
    else:
        return f"{float(d):.6e}"


def _factor_convert(value, GivenIn, ConvertTo, factors, unit_labels):
    """
    Generic base-unit conversion used by most categories.
    factors  : dict {int -> Decimal or float}  — "how many BASE units = 1 of this unit"
    """
    if GivenIn == ConvertTo:
        return value, unit_labels[ConvertTo]

    if GivenIn not in factors or ConvertTo not in factors:
        return "Invalid scale selection.", ""

    base = Decimal(str(value)) * Decimal(str(factors[GivenIn]))
    result = base / Decimal(str(factors[ConvertTo]))
    return _fmt(result), unit_labels[ConvertTo]


# ─────────────────────────────────────────────────────────────────────────────
#  1. TEMPERATURE
# ─────────────────────────────────────────────────────────────────────────────

def temperature(temp, GivenIn, ConvertTo):
    """
    1: Celsius   2: Fahrenheit   3: Kelvin   4: Rankine
    Returns (result, unit_label)
    """
    labels = {1: "°C", 2: "°F", 3: "K", 4: "°R"}

    if GivenIn == ConvertTo:
        return temp, labels[ConvertTo]

    if not (1 <= GivenIn <= 4) or not (1 <= ConvertTo <= 4):
        return "Invalid scale. Choose 1 (Celsius), 2 (Fahrenheit), 3 (Kelvin), 4 (Rankine)", ""

    abs_zero = {1: -273.15, 2: -459.67, 3: 0, 4: 0}
    if temp < abs_zero[GivenIn]:
        return "Invalid input. Temperature is below Absolute Zero.", ""

    conversions = {
        (1, 2): lambda t: (t * 9 / 5) + 32,
        (1, 3): lambda t: t + 273.15,
        (1, 4): lambda t: (t + 273.15) * 9 / 5,
        (2, 1): lambda t: (t - 32) * 5 / 9,
        (2, 3): lambda t: (t - 32) * 5 / 9 + 273.15,
        (2, 4): lambda t: t + 459.67,
        (3, 1): lambda t: t - 273.15,
        (3, 2): lambda t: (t - 273.15) * 9 / 5 + 32,
        (3, 4): lambda t: t * 9 / 5,
        (4, 1): lambda t: (t - 491.67) * 5 / 9,
        (4, 2): lambda t: t - 459.67,
        (4, 3): lambda t: t * 5 / 9,
    }

    result = round(conversions[(GivenIn, ConvertTo)](temp), 8)
    return _fmt(result), labels[ConvertTo]


# ─────────────────────────────────────────────────────────────────────────────
#  2. LENGTH
# ─────────────────────────────────────────────────────────────────────────────

def length(value, GivenIn, ConvertTo):
    """
    1: Millimeter      2: Centimeter      3: Meter          4: Kilometer
    5: Inch            6: Foot            7: Yard           8: Mile
    9: Nautical Mile   10: Light-year     11: AU            12: Parsec
    13: Angstrom       14: Micrometer
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Length cannot be negative.", ""

    labels = {
        1: "mm", 2: "cm", 3: "m", 4: "km",
        5: "in", 6: "ft", 7: "yd", 8: "mi",
        9: "nmi", 10: "ly", 11: "AU", 12: "pc",
        13: "Å", 14: "μm",
    }
    # base = meter
    factors = {
        1: 0.001,
        2: 0.01,
        3: 1.0,
        4: 1000.0,
        5: 0.0254,
        6: 0.3048,
        7: 0.9144,
        8: 1609.344,
        9: 1852.0,
        10: 9.46073047258e15,
        11: 1.495978707e11,
        12: 3.085677581e16,
        13: 1e-10,
        14: 1e-6,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  3. MASS / WEIGHT
# ─────────────────────────────────────────────────────────────────────────────

def mass(value, GivenIn, ConvertTo):
    """
    1: Milligram       2: Gram            3: Kilogram       4: Metric Ton
    5: Ounce           6: Pound           7: Stone          8: Short Ton
    9: Long Ton        10: AMU
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Mass cannot be negative.", ""

    labels = {
        1: "mg", 2: "g", 3: "kg", 4: "t (metric)",
        5: "oz", 6: "lb", 7: "st", 8: "short ton",
        9: "long ton", 10: "amu",
    }
    # base = kilogram
    factors = {
        1: 1e-6,
        2: 0.001,
        3: 1.0,
        4: 1000.0,
        5: 0.028349523125,
        6: 0.45359237,
        7: 6.35029318,
        8: 907.18474,
        9: 1016.0469088,
        10: 1.66053906660e-27,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  4. AREA
# ─────────────────────────────────────────────────────────────────────────────

def area(value, GivenIn, ConvertTo):
    """
    1: mm²    2: cm²    3: m²     4: km²    5: in²    6: ft²
    7: yd²    8: Acre   9: Hectare   10: mi²
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Area cannot be negative.", ""

    labels = {
        1: "mm²", 2: "cm²", 3: "m²", 4: "km²",
        5: "in²", 6: "ft²", 7: "yd²", 8: "acre",
        9: "ha", 10: "mi²",
    }
    # base = square meter
    factors = {
        1: 1e-6,
        2: 1e-4,
        3: 1.0,
        4: 1e6,
        5: 0.00064516,
        6: 0.09290304,
        7: 0.83612736,
        8: 4046.8564224,
        9: 10000.0,
        10: 2589988.110336,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  5. VOLUME
# ─────────────────────────────────────────────────────────────────────────────

def volume(value, GivenIn, ConvertTo):
    """
    1: Milliliter       2: Liter            3: cm³           4: m³
    5: in³              6: ft³              7: yd³           8: fl oz (US)
    9: fl oz (UK)       10: Cup (US)        11: Pint (US)    12: Pint (UK)
    13: Quart (US)      14: Quart (UK)      15: Gallon (US)  16: Gallon (UK)
    17: Barrel (oil)
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Volume cannot be negative.", ""

    labels = {
        1: "mL", 2: "L", 3: "cm³", 4: "m³",
        5: "in³", 6: "ft³", 7: "yd³", 8: "fl oz (US)",
        9: "fl oz (UK)", 10: "cup (US)", 11: "pt (US)", 12: "pt (UK)",
        13: "qt (US)", 14: "qt (UK)", 15: "gal (US)", 16: "gal (UK)",
        17: "bbl (oil)",
    }
    # base = liter
    factors = {
        1: 0.001,
        2: 1.0,
        3: 0.001,
        4: 1000.0,
        5: 0.016387064,
        6: 28.316846592,
        7: 764.554857984,
        8: 0.0295735295625,
        9: 0.0284130625,
        10: 0.2365882365,
        11: 0.473176473,
        12: 0.56826125,
        13: 0.946352946,
        14: 1.1365225,
        15: 3.785411784,
        16: 4.54609,
        17: 158.987294928,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  6. SPEED / VELOCITY
# ─────────────────────────────────────────────────────────────────────────────

def speed(value, GivenIn, ConvertTo):
    """
    1: m/s    2: km/h   3: mph    4: knots   5: ft/s   6: Mach
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Speed cannot be negative.", ""

    labels = {1: "m/s", 2: "km/h", 3: "mph", 4: "kn", 5: "ft/s", 6: "Mach"}
    # base = m/s
    factors = {
        1: 1.0,
        2: 1 / 3.6,
        3: 0.44704,
        4: 0.514444,
        5: 0.3048,
        6: 343.0,   # Mach 1 at sea level, 20°C
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  7. ACCELERATION
# ─────────────────────────────────────────────────────────────────────────────

def acceleration(value, GivenIn, ConvertTo):
    """
    1: m/s²    2: ft/s²    3: g (standard gravity)
    Returns (result, unit_label)
    """
    labels = {1: "m/s²", 2: "ft/s²", 3: "g"}
    # base = m/s²
    factors = {1: 1.0, 2: 0.3048, 3: 9.80665}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  8. TIME
# ─────────────────────────────────────────────────────────────────────────────

def time(value, GivenIn, ConvertTo):
    """
    1: Nanosecond    2: Microsecond   3: Millisecond   4: Second
    5: Minute        6: Hour          7: Day           8: Week
    9: Month (avg)   10: Year (avg)   11: Decade       12: Century
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Time cannot be negative.", ""

    labels = {
        1: "ns", 2: "μs", 3: "ms", 4: "s",
        5: "min", 6: "hr", 7: "day", 8: "week",
        9: "month", 10: "year", 11: "decade", 12: "century",
    }
    # base = second
    factors = {
        1: 1e-9,
        2: 1e-6,
        3: 0.001,
        4: 1.0,
        5: 60.0,
        6: 3600.0,
        7: 86400.0,
        8: 604800.0,
        9: 2629746.0,       # average month (365.2425 days / 12)
        10: 31556952.0,     # average year (365.2425 days)
        11: 315569520.0,
        12: 3155695200.0,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  9. FORCE
# ─────────────────────────────────────────────────────────────────────────────

def force(value, GivenIn, ConvertTo):
    """
    1: Newton    2: Dyne    3: Pound-force    4: Kilogram-force    5: Kip
    Returns (result, unit_label)
    """
    labels = {1: "N", 2: "dyn", 3: "lbf", 4: "kgf", 5: "kip"}
    # base = Newton
    factors = {
        1: 1.0,
        2: 1e-5,
        3: 4.44822162,
        4: 9.80665,
        5: 4448.22162,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  10. PRESSURE
# ─────────────────────────────────────────────────────────────────────────────

def pressure(value, GivenIn, ConvertTo):
    """
    1: Pascal    2: Kilopascal    3: Megapascal    4: Bar
    5: Millibar  6: Atmosphere    7: Torr          8: mmHg    9: psi
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Absolute pressure cannot be negative.", ""

    labels = {
        1: "Pa", 2: "kPa", 3: "MPa", 4: "bar",
        5: "mbar", 6: "atm", 7: "Torr", 8: "mmHg", 9: "psi",
    }
    # base = Pascal
    factors = {
        1: 1.0,
        2: 1000.0,
        3: 1e6,
        4: 100000.0,
        5: 100.0,
        6: 101325.0,
        7: 133.322368,
        8: 133.322387415,
        9: 6894.757293,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  11. ENERGY / WORK
# ─────────────────────────────────────────────────────────────────────────────

def energy(value, GivenIn, ConvertTo):
    """
    1: Joule         2: Kilojoule      3: Megajoule     4: Calorie
    5: Kilocalorie   6: Watt-hour      7: Kilowatt-hour 8: Electronvolt
    9: BTU           10: Foot-pound    11: Erg
    Returns (result, unit_label)
    """
    labels = {
        1: "J", 2: "kJ", 3: "MJ", 4: "cal",
        5: "kcal", 6: "Wh", 7: "kWh", 8: "eV",
        9: "BTU", 10: "ft·lbf", 11: "erg",
    }
    # base = Joule
    factors = {
        1: 1.0,
        2: 1000.0,
        3: 1e6,
        4: 4.184,
        5: 4184.0,
        6: 3600.0,
        7: 3600000.0,
        8: 1.602176634e-19,
        9: 1055.05585262,
        10: 1.3558179483,
        11: 1e-7,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  12. POWER
# ─────────────────────────────────────────────────────────────────────────────

def power(value, GivenIn, ConvertTo):
    """
    1: Watt          2: Kilowatt       3: Megawatt
    4: HP (mech)     5: HP (metric)    6: BTU/hr
    Returns (result, unit_label)
    """
    labels = {
        1: "W", 2: "kW", 3: "MW",
        4: "hp (mech)", 5: "hp (metric)", 6: "BTU/hr",
    }
    # base = Watt
    factors = {
        1: 1.0,
        2: 1000.0,
        3: 1e6,
        4: 745.69987158,
        5: 735.49875,
        6: 0.29307107,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  13. FREQUENCY
# ─────────────────────────────────────────────────────────────────────────────

def frequency(value, GivenIn, ConvertTo):
    """
    1: Hertz    2: Kilohertz    3: Megahertz    4: Gigahertz    5: RPM
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Frequency cannot be negative.", ""

    labels = {1: "Hz", 2: "kHz", 3: "MHz", 4: "GHz", 5: "RPM"}
    # base = Hertz
    factors = {
        1: 1.0,
        2: 1000.0,
        3: 1e6,
        4: 1e9,
        5: 1 / 60.0,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  14. ELECTRIC CURRENT
# ─────────────────────────────────────────────────────────────────────────────

def current(value, GivenIn, ConvertTo):
    """
    1: Ampere    2: Milliampere    3: Microampere
    Returns (result, unit_label)
    """
    labels = {1: "A", 2: "mA", 3: "μA"}
    # base = Ampere
    factors = {1: 1.0, 2: 0.001, 3: 1e-6}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  15. VOLTAGE
# ─────────────────────────────────────────────────────────────────────────────

def voltage(value, GivenIn, ConvertTo):
    """
    1: Volt    2: Millivolt    3: Kilovolt    4: Megavolt
    Returns (result, unit_label)
    """
    labels = {1: "V", 2: "mV", 3: "kV", 4: "MV"}
    # base = Volt
    factors = {1: 1.0, 2: 0.001, 3: 1000.0, 4: 1e6}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  16. RESISTANCE
# ─────────────────────────────────────────────────────────────────────────────

def resistance(value, GivenIn, ConvertTo):
    """
    1: Ohm    2: Kilohm    3: Megohm
    Returns (result, unit_label)
    """
    labels = {1: "Ω", 2: "kΩ", 3: "MΩ"}
    factors = {1: 1.0, 2: 1000.0, 3: 1e6}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  17. ELECTRIC CHARGE
# ─────────────────────────────────────────────────────────────────────────────

def charge(value, GivenIn, ConvertTo):
    """
    1: Coulomb    2: mAh    3: Ah
    Returns (result, unit_label)
    """
    labels = {1: "C", 2: "mAh", 3: "Ah"}
    # base = Coulomb
    factors = {
        1: 1.0,
        2: 3.6,         # 1 mAh = 3.6 C
        3: 3600.0,      # 1 Ah  = 3600 C
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  18. CAPACITANCE
# ─────────────────────────────────────────────────────────────────────────────

def capacitance(value, GivenIn, ConvertTo):
    """
    1: Farad    2: Microfarad    3: Nanofarad    4: Picofarad
    Returns (result, unit_label)
    """
    labels = {1: "F", 2: "μF", 3: "nF", 4: "pF"}
    # base = Farad
    factors = {1: 1.0, 2: 1e-6, 3: 1e-9, 4: 1e-12}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  19. MAGNETIC FIELD
# ─────────────────────────────────────────────────────────────────────────────

def magnetic_field(value, GivenIn, ConvertTo):
    """
    1: Tesla    2: Gauss    3: Millitesla
    Returns (result, unit_label)
    """
    labels = {1: "T", 2: "G", 3: "mT"}
    # base = Tesla
    factors = {1: 1.0, 2: 1e-4, 3: 0.001}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  20. LUMINANCE / LIGHT
# ─────────────────────────────────────────────────────────────────────────────

def luminance(value, GivenIn, ConvertTo):
    """
    1: Candela    2: Lumen (per sr)    3: Lux (per m²)    4: Foot-candle
    Note: cd, lm, lx, fc are different physical quantities, but this converter
    treats them via their common practical equivalence at a 1 sr / 1 m² baseline
    for educational use. Candela is the base here (1 cd = 1 lm/sr).
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Cannot be negative.", ""

    labels = {1: "cd", 2: "lm", 3: "lx", 4: "fc"}
    # base = lux (illuminance)  — practical approximation at 1m distance
    factors = {
        1: 1.0,         # Candela (luminous intensity)
        2: 1.0,         # Lumen (luminous flux, 1 sr solid angle assumed)
        3: 1.0,         # Lux = lm/m², kept 1:1 for dimensional context
        4: 10.7639,     # 1 fc = 10.7639 lux
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  21. ANGLE
# ─────────────────────────────────────────────────────────────────────────────

def angle(value, GivenIn, ConvertTo):
    """
    1: Degree    2: Radian    3: Gradian    4: Arcminute    5: Arcsecond
    6: Revolution / Turn
    Returns (result, unit_label)
    """
    labels = {1: "°", 2: "rad", 3: "grad", 4: "arcmin", 5: "arcsec", 6: "rev"}
    # base = degree
    factors = {
        1: 1.0,
        2: 180.0 / 3.141592653589793238462643383279502884197,
        3: 0.9,
        4: 1 / 60.0,
        5: 1 / 3600.0,
        6: 360.0,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  22. DIGITAL STORAGE
# ─────────────────────────────────────────────────────────────────────────────

def digital_storage(value, GivenIn, ConvertTo):
    """
    SI  (powers of 10)          Binary  (powers of 2)
    1: bit                      9:  Kibibyte (KiB)
    2: Byte                     10: Mebibyte (MiB)
    3: Kilobyte (KB, 1000 B)    11: Gibibyte (GiB)
    4: Megabyte (MB)            12: Tebibyte (TiB)
    5: Gigabyte (GB)            13: Pebibyte (PiB)
    6: Terabyte (TB)
    7: Petabyte (PB)
    8: Kibibyte (KiB) — alias in menu, same as 9
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Cannot be negative.", ""

    labels = {
        1: "bit", 2: "B", 3: "KB", 4: "MB", 5: "GB", 6: "TB", 7: "PB",
        8: "KiB", 9: "MiB", 10: "GiB", 11: "TiB", 12: "PiB",
    }
    # base = bit
    factors = {
        1: 1,
        2: 8,
        3: 8 * 1000,
        4: 8 * 1000 ** 2,
        5: 8 * 1000 ** 3,
        6: 8 * 1000 ** 4,
        7: 8 * 1000 ** 5,
        8: 8 * 1024,
        9: 8 * 1024 ** 2,
        10: 8 * 1024 ** 3,
        11: 8 * 1024 ** 4,
        12: 8 * 1024 ** 5,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  23. DATA TRANSFER RATE
# ─────────────────────────────────────────────────────────────────────────────

def data_rate(value, GivenIn, ConvertTo):
    """
    1: bps    2: Kbps    3: Mbps    4: Gbps
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Cannot be negative.", ""

    labels = {1: "bps", 2: "Kbps", 3: "Mbps", 4: "Gbps"}
    # base = bits per second
    factors = {1: 1.0, 2: 1000.0, 3: 1e6, 4: 1e9}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  24. FUEL EFFICIENCY
# ─────────────────────────────────────────────────────────────────────────────

def fuel_efficiency(value, GivenIn, ConvertTo):
    """
    Note: mpg and km/L are inversely related to L/100km, so this category
    uses direct formula conversion rather than a single base factor.
    
    1: mpg (US)    2: mpg (UK)    3: L/100km    4: km/L
    Returns (result, unit_label)
    """
    if value <= 0:
        return "Invalid input. Must be greater than zero.", ""

    labels = {1: "mpg (US)", 2: "mpg (UK)", 3: "L/100km", 4: "km/L"}

    # Step 1: Convert everything to L/100km as intermediate base
    to_l100 = {
        1: lambda v: 235.214583 / v,   # mpg US  → L/100km
        2: lambda v: 282.480936 / v,   # mpg UK  → L/100km
        3: lambda v: v,                # already L/100km
        4: lambda v: 100.0 / v,        # km/L    → L/100km
    }

    # Step 2: Convert L/100km to target
    from_l100 = {
        1: lambda v: 235.214583 / v,
        2: lambda v: 282.480936 / v,
        3: lambda v: v,
        4: lambda v: 100.0 / v,
    }

    if GivenIn not in to_l100 or ConvertTo not in from_l100:
        return "Invalid scale selection.", ""
    if GivenIn == ConvertTo:
        return value, labels[ConvertTo]

    intermediate = to_l100[GivenIn](value)
    result = from_l100[ConvertTo](intermediate)
    return _fmt(result), labels[ConvertTo]


# ─────────────────────────────────────────────────────────────────────────────
#  25. DENSITY
# ─────────────────────────────────────────────────────────────────────────────

def density(value, GivenIn, ConvertTo):
    """
    1: kg/m³    2: g/cm³    3: lb/ft³    4: lb/in³
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Density cannot be negative.", ""

    labels = {1: "kg/m³", 2: "g/cm³", 3: "lb/ft³", 4: "lb/in³"}
    # base = kg/m³
    factors = {
        1: 1.0,
        2: 1000.0,
        3: 16.01846337,
        4: 27679.9047102,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  26. TORQUE
# ─────────────────────────────────────────────────────────────────────────────

def torque(value, GivenIn, ConvertTo):
    """
    1: Newton-meter    2: Pound-foot    3: Pound-inch    4: Kilogram-meter
    Returns (result, unit_label)
    """
    labels = {1: "N·m", 2: "lbf·ft", 3: "lbf·in", 4: "kgf·m"}
    # base = Newton-meter
    factors = {
        1: 1.0,
        2: 1.35581795,
        3: 0.11298483,
        4: 9.80665,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  27. DYNAMIC VISCOSITY
# ─────────────────────────────────────────────────────────────────────────────

def viscosity_dynamic(value, GivenIn, ConvertTo):
    """
    1: Pascal-second (Pa·s)    2: Poise (P)    3: Centipoise (cP)
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Viscosity cannot be negative.", ""

    labels = {1: "Pa·s", 2: "P", 3: "cP"}
    # base = Pa·s
    factors = {1: 1.0, 2: 0.1, 3: 0.001}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  28. KINEMATIC VISCOSITY
# ─────────────────────────────────────────────────────────────────────────────

def viscosity_kinematic(value, GivenIn, ConvertTo):
    """
    1: m²/s    2: Stokes (St)    3: Centistokes (cSt)
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Viscosity cannot be negative.", ""

    labels = {1: "m²/s", 2: "St", 3: "cSt"}
    # base = m²/s
    factors = {1: 1.0, 2: 1e-4, 3: 1e-6}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  29. RADIOACTIVITY / RADIATION
# ─────────────────────────────────────────────────────────────────────────────

def radiation_activity(value, GivenIn, ConvertTo):
    """
    Activity units:
    1: Becquerel (Bq)    2: Curie (Ci)
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Cannot be negative.", ""

    labels = {1: "Bq", 2: "Ci"}
    factors = {1: 1.0, 2: 3.7e10}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


def radiation_dose_absorbed(value, GivenIn, ConvertTo):
    """
    Absorbed dose:
    1: Gray (Gy)    2: Rad
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Cannot be negative.", ""

    labels = {1: "Gy", 2: "rad"}
    factors = {1: 1.0, 2: 0.01}
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


def radiation_dose_equivalent(value, GivenIn, ConvertTo):
    """
    Dose equivalent:
    1: Sievert (Sv)    2: Rem    3: Roentgen (R)  [exposure, approx]
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Cannot be negative.", ""

    labels = {1: "Sv", 2: "rem", 3: "R"}
    # base = Sievert
    factors = {
        1: 1.0,
        2: 0.01,
        3: 0.00877,     # 1 R ≈ 0.00877 Sv in tissue (approximate)
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)


# ─────────────────────────────────────────────────────────────────────────────
#  30. CONCENTRATION
# ─────────────────────────────────────────────────────────────────────────────

def concentration(value, GivenIn, ConvertTo):
    """
    Dimensionless / ratio-based concentration units.
    1: mol/L (Molarity, M)    2: mol/kg (Molality)
    3: ppm (mg/kg or mg/L)    4: ppb    5: % (w/v or v/v, 1% = 10000 ppm)

    Note: mol/L ↔ mol/kg conversion requires solution density (assumed water = 1 kg/L).
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Concentration cannot be negative.", ""

    labels = {1: "mol/L", 2: "mol/kg", 3: "ppm", 4: "ppb", 5: "%"}

    # For ppm / ppb / %: treat as mass-fraction-based (mg/kg scale)
    # base = ppm  (mg/kg)
    ppm_factors = {
        3: 1.0,
        4: 0.001,
        5: 10000.0,
    }

    # Molarity ↔ ppm is solute-dependent; mol/L and mol/kg are handled
    # via water-density approximation (1 kg/L)
    if GivenIn in ppm_factors and ConvertTo in ppm_factors:
        return _factor_convert(value, GivenIn, ConvertTo, ppm_factors, labels)

    if GivenIn == 1 and ConvertTo == 2:
        # mol/L → mol/kg  (assume density of water = 1 kg/L)
        return _fmt(value), labels[ConvertTo]

    if GivenIn == 2 and ConvertTo == 1:
        return _fmt(value), labels[ConvertTo]

    if GivenIn == ConvertTo:
        return value, labels[ConvertTo]

    return "Conversion between molar and mass-fraction units requires molar mass. Not supported directly.", ""


# ─────────────────────────────────────────────────────────────────────────────
#  31. FLOW RATE
# ─────────────────────────────────────────────────────────────────────────────

def flow_rate(value, GivenIn, ConvertTo):
    """
    1: L/s    2: L/min    3: L/hr    4: m³/s    5: gal/min (US)
    Returns (result, unit_label)
    """
    if value < 0:
        return "Invalid input. Flow rate cannot be negative.", ""

    labels = {1: "L/s", 2: "L/min", 3: "L/hr", 4: "m³/s", 5: "gal/min (US)"}
    # base = L/s
    factors = {
        1: 1.0,
        2: 1 / 60.0,
        3: 1 / 3600.0,
        4: 1000.0,
        5: 0.0630901964,
    }
    return _factor_convert(value, GivenIn, ConvertTo, factors, labels)