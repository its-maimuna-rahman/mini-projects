import converter_func as cf


# ─────────────────────────────────────────────────────────────────────────────
#  INPUT HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def get_int_input(prompt, valid_range):
    """Keep asking until the user gives a valid integer within valid_range."""
    while True:
        try:
            value = int(input(prompt))
            if value in valid_range:
                return value
            print(f"  ✗ Please enter one of: {list(valid_range)}")
        except ValueError:
            print("  ✗ Invalid input. Please enter a whole number.")


def get_float_input(prompt):
    """Keep asking until the user gives a valid number."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  ✗ Invalid input. Please enter a numeric value.")


def _header(title):
    print("\n" + "=" * 63)
    print(f"||  {title.center(57)}  ||")
    print("=" * 63)


def _show_result(result, unit):
    """Print the result. Handles error strings returned by converter_func."""
    if unit == "":
        print(f"\n  ✗ Error: {result}")
    else:
        print(f"\n  ✔ Result : {result} {unit}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
#  1. TEMPERATURE
# ─────────────────────────────────────────────────────────────────────────────

def temp_covt():
    _header("Temperature Converter")
    value = get_float_input("  Enter temperature : ")
    print("""
  1. Celsius         2. Fahrenheit
  3. Kelvin          4. Rankine""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.temperature(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  2. LENGTH
# ─────────────────────────────────────────────────────────────────────────────

def len_covt():
    _header("Length Converter")
    value = get_float_input("  Enter length : ")
    print("""
   1. Millimeter      2. Centimeter     3. Meter        4. Kilometer
   5. Inch            6. Foot           7. Yard         8. Mile
   9. Nautical Mile   10. Light-year    11. AU          12. Parsec
   13. Angstrom       14. Micrometer""")
    in_scale  = get_int_input("  Current scale (1-14) : ", range(1, 15))
    out_scale = get_int_input("  Target  scale (1-14) : ", range(1, 15))
    result, unit = cf.length(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  3. MASS / WEIGHT
# ─────────────────────────────────────────────────────────────────────────────

def mass_covt():
    _header("Mass / Weight Converter")
    value = get_float_input("  Enter mass : ")
    print("""
   1. Milligram    2. Gram        3. Kilogram     4. Metric Ton
   5. Ounce        6. Pound       7. Stone        8. Short Ton
   9. Long Ton    10. AMU (atomic mass unit)""")
    in_scale  = get_int_input("  Current scale (1-10) : ", range(1, 11))
    out_scale = get_int_input("  Target  scale (1-10) : ", range(1, 11))
    result, unit = cf.mass(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  4. AREA
# ─────────────────────────────────────────────────────────────────────────────

def area_covt():
    _header("Area Converter")
    value = get_float_input("  Enter area : ")
    print("""
   1. mm²    2. cm²    3. m²     4. km²
   5. in²    6. ft²    7. yd²    8. Acre
   9. Hectare          10. mi²""")
    in_scale  = get_int_input("  Current scale (1-10) : ", range(1, 11))
    out_scale = get_int_input("  Target  scale (1-10) : ", range(1, 11))
    result, unit = cf.area(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  5. VOLUME
# ─────────────────────────────────────────────────────────────────────────────

def vol_covt():
    _header("Volume Converter")
    value = get_float_input("  Enter volume : ")
    print("""
   1. Milliliter       2. Liter          3. cm³           4. m³
   5. in³              6. ft³            7. yd³           8. fl oz (US)
   9. fl oz (UK)      10. Cup (US)      11. Pint (US)    12. Pint (UK)
  13. Quart (US)      14. Quart (UK)    15. Gallon (US)  16. Gallon (UK)
  17. Barrel (oil)""")
    in_scale  = get_int_input("  Current scale (1-17) : ", range(1, 18))
    out_scale = get_int_input("  Target  scale (1-17) : ", range(1, 18))
    result, unit = cf.volume(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  6. SPEED / VELOCITY
# ─────────────────────────────────────────────────────────────────────────────

def speed_covt():
    _header("Speed / Velocity Converter")
    value = get_float_input("  Enter speed : ")
    print("""
  1. m/s    2. km/h    3. mph    4. Knots    5. ft/s    6. Mach""")
    in_scale  = get_int_input("  Current scale (1-6) : ", range(1, 7))
    out_scale = get_int_input("  Target  scale (1-6) : ", range(1, 7))
    result, unit = cf.speed(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  7. ACCELERATION
# ─────────────────────────────────────────────────────────────────────────────

def accel_covt():
    _header("Acceleration Converter")
    value = get_float_input("  Enter acceleration : ")
    print("""
  1. m/s²    2. ft/s²    3. g (standard gravity)""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.acceleration(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  8. TIME
# ─────────────────────────────────────────────────────────────────────────────

def time_covt():
    _header("Time Converter")
    value = get_float_input("  Enter time : ")
    print("""
   1. Nanosecond    2. Microsecond   3. Millisecond   4. Second
   5. Minute        6. Hour          7. Day           8. Week
   9. Month        10. Year         11. Decade       12. Century""")
    in_scale  = get_int_input("  Current scale (1-12) : ", range(1, 13))
    out_scale = get_int_input("  Target  scale (1-12) : ", range(1, 13))
    result, unit = cf.time(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  9. FORCE
# ─────────────────────────────────────────────────────────────────────────────

def force_covt():
    _header("Force Converter")
    value = get_float_input("  Enter force : ")
    print("""
  1. Newton    2. Dyne    3. Pound-force    4. Kilogram-force    5. Kip""")
    in_scale  = get_int_input("  Current scale (1-5) : ", range(1, 6))
    out_scale = get_int_input("  Target  scale (1-5) : ", range(1, 6))
    result, unit = cf.force(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  10. PRESSURE
# ─────────────────────────────────────────────────────────────────────────────

def pressure_covt():
    _header("Pressure Converter")
    value = get_float_input("  Enter pressure : ")
    print("""
  1. Pascal    2. Kilopascal    3. Megapascal    4. Bar
  5. Millibar  6. Atmosphere    7. Torr          8. mmHg    9. psi""")
    in_scale  = get_int_input("  Current scale (1-9) : ", range(1, 10))
    out_scale = get_int_input("  Target  scale (1-9) : ", range(1, 10))
    result, unit = cf.pressure(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  11. ENERGY / WORK
# ─────────────────────────────────────────────────────────────────────────────

def energy_covt():
    _header("Energy / Work Converter")
    value = get_float_input("  Enter energy : ")
    print("""
   1. Joule          2. Kilojoule      3. Megajoule      4. Calorie
   5. Kilocalorie    6. Watt-hour      7. Kilowatt-hour  8. Electronvolt
   9. BTU           10. Foot-pound    11. Erg""")
    in_scale  = get_int_input("  Current scale (1-11) : ", range(1, 12))
    out_scale = get_int_input("  Target  scale (1-11) : ", range(1, 12))
    result, unit = cf.energy(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  12. POWER
# ─────────────────────────────────────────────────────────────────────────────

def power_covt():
    _header("Power Converter")
    value = get_float_input("  Enter power : ")
    print("""
  1. Watt    2. Kilowatt    3. Megawatt
  4. HP (mechanical)        5. HP (metric)    6. BTU/hr""")
    in_scale  = get_int_input("  Current scale (1-6) : ", range(1, 7))
    out_scale = get_int_input("  Target  scale (1-6) : ", range(1, 7))
    result, unit = cf.power(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  13. FREQUENCY
# ─────────────────────────────────────────────────────────────────────────────

def freq_covt():
    _header("Frequency Converter")
    value = get_float_input("  Enter frequency : ")
    print("""
  1. Hertz    2. Kilohertz    3. Megahertz    4. Gigahertz    5. RPM""")
    in_scale  = get_int_input("  Current scale (1-5) : ", range(1, 6))
    out_scale = get_int_input("  Target  scale (1-5) : ", range(1, 6))
    result, unit = cf.frequency(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  14. ELECTRIC CURRENT
# ─────────────────────────────────────────────────────────────────────────────

def current_covt():
    _header("Electric Current Converter")
    value = get_float_input("  Enter current : ")
    print("""
  1. Ampere    2. Milliampere    3. Microampere""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.current(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  15. VOLTAGE
# ─────────────────────────────────────────────────────────────────────────────

def voltage_covt():
    _header("Voltage Converter")
    value = get_float_input("  Enter voltage : ")
    print("""
  1. Volt    2. Millivolt    3. Kilovolt    4. Megavolt""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.voltage(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  16. RESISTANCE
# ─────────────────────────────────────────────────────────────────────────────

def resistance_covt():
    _header("Electrical Resistance Converter")
    value = get_float_input("  Enter resistance : ")
    print("""
  1. Ohm    2. Kilohm    3. Megohm""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.resistance(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  17. ELECTRIC CHARGE
# ─────────────────────────────────────────────────────────────────────────────

def charge_covt():
    _header("Electric Charge Converter")
    value = get_float_input("  Enter charge : ")
    print("""
  1. Coulomb    2. Milliampere-hour (mAh)    3. Ampere-hour (Ah)""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.charge(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  18. CAPACITANCE
# ─────────────────────────────────────────────────────────────────────────────

def capacitance_covt():
    _header("Capacitance Converter")
    value = get_float_input("  Enter capacitance : ")
    print("""
  1. Farad    2. Microfarad    3. Nanofarad    4. Picofarad""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.capacitance(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  19. MAGNETIC FIELD
# ─────────────────────────────────────────────────────────────────────────────

def magnetic_covt():
    _header("Magnetic Field Converter")
    value = get_float_input("  Enter magnetic field strength : ")
    print("""
  1. Tesla    2. Gauss    3. Millitesla""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.magnetic_field(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  20. LUMINANCE / LIGHT
# ─────────────────────────────────────────────────────────────────────────────

def luminance_covt():
    _header("Luminance / Light Converter")
    value = get_float_input("  Enter value : ")
    print("""
  1. Candela (cd)    2. Lumen (lm)    3. Lux (lx)    4. Foot-candle (fc)
  Note: Practical approximation at 1 sr / 1 m² baseline.""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.luminance(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  21. ANGLE
# ─────────────────────────────────────────────────────────────────────────────

def angle_covt():
    _header("Angle Converter")
    value = get_float_input("  Enter angle : ")
    print("""
  1. Degree    2. Radian    3. Gradian    4. Arcminute    5. Arcsecond
  6. Revolution / Turn""")
    in_scale  = get_int_input("  Current scale (1-6) : ", range(1, 7))
    out_scale = get_int_input("  Target  scale (1-6) : ", range(1, 7))
    result, unit = cf.angle(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  22. DIGITAL STORAGE
# ─────────────────────────────────────────────────────────────────────────────

def storage_covt():
    _header("Digital Storage Converter")
    value = get_float_input("  Enter storage size : ")
    print("""
  — SI (powers of 10) ——————————————————————————
   1. bit       2. Byte      3. Kilobyte (KB)
   4. Megabyte (MB)          5. Gigabyte (GB)
   6. Terabyte (TB)          7. Petabyte (PB)
  — Binary (powers of 2) ———————————————————————
   8. Kibibyte (KiB)         9. Mebibyte (MiB)
  10. Gibibyte (GiB)        11. Tebibyte (TiB)
  12. Pebibyte (PiB)""")
    in_scale  = get_int_input("  Current scale (1-12) : ", range(1, 13))
    out_scale = get_int_input("  Target  scale (1-12) : ", range(1, 13))
    result, unit = cf.digital_storage(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  23. DATA TRANSFER RATE
# ─────────────────────────────────────────────────────────────────────────────

def datarate_covt():
    _header("Data Transfer Rate Converter")
    value = get_float_input("  Enter data rate : ")
    print("""
  1. bps    2. Kbps    3. Mbps    4. Gbps""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.data_rate(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  24. FUEL EFFICIENCY
# ─────────────────────────────────────────────────────────────────────────────

def fuel_covt():
    _header("Fuel Efficiency Converter")
    value = get_float_input("  Enter fuel efficiency : ")
    print("""
  1. mpg (US)    2. mpg (UK)    3. L/100km    4. km/L""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.fuel_efficiency(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  25. DENSITY
# ─────────────────────────────────────────────────────────────────────────────

def density_covt():
    _header("Density Converter")
    value = get_float_input("  Enter density : ")
    print("""
  1. kg/m³    2. g/cm³    3. lb/ft³    4. lb/in³""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.density(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  26. TORQUE
# ─────────────────────────────────────────────────────────────────────────────

def torque_covt():
    _header("Torque Converter")
    value = get_float_input("  Enter torque : ")
    print("""
  1. Newton-meter    2. Pound-foot    3. Pound-inch    4. Kilogram-meter""")
    in_scale  = get_int_input("  Current scale (1-4) : ", range(1, 5))
    out_scale = get_int_input("  Target  scale (1-4) : ", range(1, 5))
    result, unit = cf.torque(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  27. DYNAMIC VISCOSITY
# ─────────────────────────────────────────────────────────────────────────────

def visc_dyn_covt():
    _header("Dynamic Viscosity Converter")
    value = get_float_input("  Enter dynamic viscosity : ")
    print("""
  1. Pascal-second (Pa·s)    2. Poise (P)    3. Centipoise (cP)""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.viscosity_dynamic(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  28. KINEMATIC VISCOSITY
# ─────────────────────────────────────────────────────────────────────────────

def visc_kin_covt():
    _header("Kinematic Viscosity Converter")
    value = get_float_input("  Enter kinematic viscosity : ")
    print("""
  1. m²/s    2. Stokes (St)    3. Centistokes (cSt)""")
    in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
    out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
    result, unit = cf.viscosity_kinematic(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  29. RADIOACTIVITY / RADIATION  (3 sub-converters)
# ─────────────────────────────────────────────────────────────────────────────

def radiation_covt():
    _header("Radioactivity / Radiation Converter")
    print("""
  Sub-category:
  1. Activity           (Becquerel ↔ Curie)
  2. Absorbed dose      (Gray ↔ Rad)
  3. Dose equivalent    (Sievert ↔ Rem ↔ Roentgen)""")
    sub = get_int_input("  Choose sub-category (1-3) : ", range(1, 4))

    if sub == 1:
        value = get_float_input("  Enter activity : ")
        print("""
  1. Becquerel (Bq)    2. Curie (Ci)""")
        in_scale  = get_int_input("  Current scale (1-2) : ", range(1, 3))
        out_scale = get_int_input("  Target  scale (1-2) : ", range(1, 3))
        result, unit = cf.radiation_activity(value, in_scale, out_scale)

    elif sub == 2:
        value = get_float_input("  Enter absorbed dose : ")
        print("""
  1. Gray (Gy)    2. Rad""")
        in_scale  = get_int_input("  Current scale (1-2) : ", range(1, 3))
        out_scale = get_int_input("  Target  scale (1-2) : ", range(1, 3))
        result, unit = cf.radiation_dose_absorbed(value, in_scale, out_scale)

    else:
        value = get_float_input("  Enter dose equivalent : ")
        print("""
  1. Sievert (Sv)    2. Rem    3. Roentgen (R)""")
        in_scale  = get_int_input("  Current scale (1-3) : ", range(1, 4))
        out_scale = get_int_input("  Target  scale (1-3) : ", range(1, 4))
        result, unit = cf.radiation_dose_equivalent(value, in_scale, out_scale)

    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  30. CONCENTRATION
# ─────────────────────────────────────────────────────────────────────────────

def concentration_covt():
    _header("Concentration Converter")
    value = get_float_input("  Enter concentration : ")
    print("""
  1. mol/L  (Molarity)    2. mol/kg (Molality)
  3. ppm                  4. ppb                5. %
  Note: Molar ↔ ppm/ppb/% requires molar mass and is not directly supported.""")
    in_scale  = get_int_input("  Current scale (1-5) : ", range(1, 6))
    out_scale = get_int_input("  Target  scale (1-5) : ", range(1, 6))
    result, unit = cf.concentration(value, in_scale, out_scale)
    _show_result(result, unit)


# ─────────────────────────────────────────────────────────────────────────────
#  31. FLOW RATE
# ─────────────────────────────────────────────────────────────────────────────

def flowrate_covt():
    _header("Flow Rate Converter")
    value = get_float_input("  Enter flow rate : ")
    print("""
  1. L/s    2. L/min    3. L/hr    4. m³/s    5. gal/min (US)""")
    in_scale  = get_int_input("  Current scale (1-5) : ", range(1, 6))
    out_scale = get_int_input("  Target  scale (1-5) : ", range(1, 6))
    result, unit = cf.flow_rate(value, in_scale, out_scale)
    _show_result(result, unit)