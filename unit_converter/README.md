# Unit Converter

A comprehensive command-line unit converter built in Python, supporting **31 physical and scientific categories** with high-precision arithmetic for astronomical and quantum-scale values.

## Features

- 31 conversion categories covering everyday and scientific units
- High-precision calculations using Python's `Decimal` module (50 significant digits)
- Smart output formatting — plain floats for everyday numbers, scientific notation for extreme values
- Input validation with informative error messages (e.g., below absolute zero, negative lengths)

## Project Structure

```
unit-converter/
├── main_converter.py    # Entry point — displays menu and dispatches to converters
├── scale_converter.py   # Interactive prompts for each category
└── converter_func.py    # Core conversion logic and unit definitions
```

- **`converter_func.py`** — Contains all conversion functions. Each category is self-contained with its own unit labels, conversion factors (or formulas), and input validation.
- **`scale_converter.py`** — Handles user interaction for each category: prompts for unit selection and value input, then calls the appropriate function from `converter_func.py`.
- **`main_converter.py`** — The entry point. Displays the category menu, validates the user's choice, and dispatches to the correct converter via a lookup table.


## Supported Categories

| # | Category | # | Category |
|---|----------|---|----------|
| 1 | Temperature | 17 | Electric Charge |
| 2 | Length | 18 | Capacitance |
| 3 | Mass / Weight | 19 | Magnetic Field |
| 4 | Area | 20 | Luminance / Light |
| 5 | Volume | 21 | Angle |
| 6 | Speed / Velocity | 22 | Digital Storage |
| 7 | Acceleration | 23 | Data Transfer Rate |
| 8 | Time | 24 | Fuel Efficiency |
| 9 | Force | 25 | Density |
| 10 | Pressure | 26 | Torque |
| 11 | Energy / Work | 27 | Dynamic Viscosity |
| 12 | Power | 28 | Kinematic Viscosity |
| 13 | Frequency | 29 | Radiation |
| 14 | Electric Current | 30 | Concentration |
| 15 | Voltage | 31 | Flow Rate |
| 16 | Resistance | | |

## Requirements

- Python 3.6+
- No external dependencies — uses only the Python standard library


## Usage

Download the whole folder and run the main script from your terminal:

```bash
python main_converter.py
```

You will be presented with a numbered list of conversion categories. Enter the number corresponding to the category you want, then follow the prompts to select your input unit, output unit, and value.

**Example session:**

```
List of variables for unit conversion:

   1. Temperature
   2. Length
   ...

Enter a variable you want to convert (1-31): 1

  1: Celsius
  2: Fahrenheit
  3: Kelvin
  4: Rankine

Convert from: 1
Convert to: 2
Enter value: 100

Result: 100 °C = 212.0 °F
```


## Notes

- **Temperature** is the only category that uses direct formulas rather than a base-unit factor table, since Celsius/Fahrenheit/Kelvin/Rankine are offset scales.
- **Fuel efficiency** (mpg ↔ L/100km) uses an intermediate L/100km conversion step because the units are inversely related.
- **Concentration** conversions between molar units (mol/L, mol/kg) and mass-fraction units (ppm, ppb, %) require solute molar mass and are intentionally not supported directly.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
