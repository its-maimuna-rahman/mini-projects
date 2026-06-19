# Dynamic Warehouse & Stock Flow Manager

A Python project that simulates a real warehouse management system. It handles product registration, zone-based storage, stock movement between zones, and automatic low-stock reporting — all through an interactive command-line interface.

---

## Project Structure

```
warehouse_cls.py   # Product, Warehouse, and LogisticsManager classes
main.py            # Interactive CLI — run this to use the app
```

---

## How to Run

```bash
python main.py
```

No external libraries needed. Works with Python 3.6+.

---

## Features

- **Add products** — register a product with a SKU, name, category, quantity, and minimum stock threshold, then assign it to a zone
- **View all products** — see every product in a formatted table with its current zone and whether it is running low
- **Move stock between zones** — reassign any product from one zone to another with full validation
- **Zone summary** — see how many products and total units are sitting in each zone
- **Low stock audit** — instantly get a list of every product that has fallen below its minimum threshold
- **Category breakdown** — see how many distinct products exist per category

---

## How It Works

The app is built around three classes that work together.

### `Product`
Represents a single item. Each product has a SKU (unique ID), name, category, quantity on hand, and a minimum threshold. It knows how to check whether its own stock is low.

| Attribute       | Type | Description                                       |
|-----------------|------|---------------------------------------------------|
| `sku`           | str  | Unique identifier for the product                 |
| `name`          | str  | Human-readable product name                       |
| `category`      | str  | The group this product belongs to                 |
| `quantity`      | int  | Current units in stock                            |
| `min_threshold` | int  | Units below this count triggers a low-stock alert |

### `Warehouse`
The central storage hub. It keeps two data structures in sync at all times — a dictionary of all products (keyed by SKU for fast lookup), and a dictionary of zones where each zone holds a list of SKUs currently assigned to it.

**Zones:** `Cold Storage`, `General`, `Hazardous`

| Method                       | What it does                                          |
|------------------------------|-------------------------------------------------------|
| `add_product(product, zone)` | Registers the product and places it in the given zone |
| `move_stock(sku, to_zone)`   | Moves a product from its current zone to another      |
| `get_zone_value(zone_name)`  | Returns the total unit count for an entire zone       |

### `LogisticsManager`
The reporting layer. It takes a `Warehouse` object and runs analysis across all of its data.

| Method                 | What it does                                              |
|------------------------|-----------------------------------------------------------|
| `audit_warehouse()`    | Returns a list of SKUs that are below their min threshold |
| `category_breakdown()` | Returns a count of products per category                  |

---

## Input Validation

Every action in the app checks for bad input before doing anything:

- Empty or blank SKU and name are rejected
- Adding a product with a duplicate SKU is blocked
- Quantity and threshold fields only accept whole numbers
- Zone selection is always done via a numbered menu so invalid zones are impossible to enter
- Moving a SKU that does not exist, or that is already in the destination zone, gives a clear error message instead of crashing

---

## Sample Data

When you launch the app, five products are pre-loaded across all three zones so you can immediately try every feature without adding data manually.
