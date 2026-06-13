import scale_converter as sc

print("\nList of variables for unit conversion:\n")

full_list = {
    1  : "Temperature",
    2  : "Length",
    3  : "Mass / Weight",
    4  : "Area",
    5  : "Volume",
    6  : "Speed / Velocity",
    7  : "Acceleration",
    8  : "Time",
    9  : "Force",
    10 : "Pressure",
    11 : "Energy / Work",
    12 : "Power",
    13 : "Frequency",
    14 : "Electric Current",
    15 : "Voltage",
    16 : "Resistance",
    17 : "Electric Charge",
    18 : "Capacitance",
    19 : "Magnetic Field",
    20 : "Luminance / Light",
    21 : "Angle",
    22 : "Digital Storage",
    23 : "Data Transfer Rate",
    24 : "Fuel Efficiency",
    25 : "Density",
    26 : "Torque",
    27 : "Dynamic Viscosity",
    28 : "Kinematic Viscosity",
    29 : "Radiation",
    30 : "Concentration",
    31 : "Flow Rate"
}

# dispatch table — maps choice directly to function
dispatch = {
    1  : sc.temp_covt,
    2  : sc.len_covt,
    3  : sc.mass_covt,
    4  : sc.area_covt,
    5  : sc.vol_covt,
    6  : sc.speed_covt,
    7  : sc.accel_covt,
    8  : sc.time_covt,
    9  : sc.force_covt,
    10 : sc.pressure_covt,
    11 : sc.energy_covt,
    12 : sc.power_covt,
    13 : sc.freq_covt,
    14 : sc.current_covt,
    15 : sc.voltage_covt,
    16 : sc.resistance_covt,
    17 : sc.charge_covt,
    18 : sc.capacitance_covt,
    19 : sc.magnetic_covt,
    20 : sc.luminance_covt,
    21 : sc.angle_covt,
    22 : sc.storage_covt,
    23 : sc.datarate_covt,
    24 : sc.fuel_covt,
    25 : sc.density_covt,
    26 : sc.torque_covt,
    27 : sc.visc_dyn_covt,
    28 : sc.visc_kin_covt,
    29 : sc.radiation_covt,
    30 : sc.concentration_covt,
    31 : sc.flowrate_covt
}

for key, value in full_list.items():
    print(f"  {key:>2}. {value}")

while True:
    try:
        choice = int(input("\nEnter a variable you want to convert (1-31): "))
        if 1 <= choice <= 31:
            break
        else:
            print("  ✗ Invalid choice. Choose between 1 and 31.")
    except ValueError:
        print("  ✗ Please enter a whole number.")

dispatch[choice]()