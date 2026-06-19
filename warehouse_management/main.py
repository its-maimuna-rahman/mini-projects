from warehouse_cls import Product, Warehouse, LogisticsManager


# ── helpers ──────────────────────────────────────────────────────────────────

def print_separator():
    print("-" * 45)

def print_header(title):
    print()
    print("=" * 45)
    print(f"  {title}")
    print("=" * 45)

def get_int_input(prompt):
    """Keep asking until the user gives a valid integer."""
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("  Please enter a valid whole number.")

def get_zone_choice():
    """Show the three zones and return the one the user picks."""
    zones = ["Cold Storage", "General", "Hazardous"]
    print("  Zones:")
    for i, zone in enumerate(zones, 1):
        print(f"    {i}. {zone}")
    while True:
        choice = input("  Pick zone (1/2/3): ").strip()
        if choice in ("1", "2", "3"):
            return zones[int(choice) - 1]
        print("  Please enter 1, 2, or 3.")


# ── menu actions ─────────────────────────────────────────────────────────────

def add_product(warehouse):
    print_header("Add New Product")

    sku = input("  SKU       : ").strip().upper()
    if not sku:
        print("  SKU cannot be empty.")
        return
    if sku in warehouse.products:
        print(f"  A product with SKU '{sku}' already exists.")
        return

    name = input("  Name      : ").strip()
    if not name:
        print("  Name cannot be empty.")
        return

    category = input("  Category  : ").strip()
    if not category:
        print("  Category cannot be empty.")
        return

    quantity     = get_int_input("  Quantity  : ")
    min_threshold = get_int_input("  Min threshold : ")

    print("  Select zone:")
    zone = get_zone_choice()

    product = Product(sku, name, category, quantity, min_threshold)
    warehouse.add_product(product, zone)
    print(f"\n  ✓ Added '{name}' (SKU: {sku}) to '{zone}'.")


def view_all_products(warehouse):
    print_header("All Products")

    if not warehouse.products:
        print("  No products in warehouse yet.")
        return

    print(f"  {'SKU':<10} {'Name':<20} {'Category':<14} {'Qty':>5} {'Min':>5} {'Zone':<14} {'Low?'}")
    print_separator()

    # Build a reverse map: sku → zone_name
    sku_to_zone = {}
    for zone_name, sku_list in warehouse.zones.items():
        for sku in sku_list:
            sku_to_zone[sku] = zone_name

    for sku, p in warehouse.products.items():
        zone = sku_to_zone.get(sku, "Unknown")
        low  = "⚠ YES" if p.is_low_stock() else "no"
        print(f"  {sku:<10} {p.name:<20} {p.category:<14} {p.quantity:>5} {p.min_threshold:>5} {zone:<14} {low}")


def move_stock(warehouse):
    print_header("Move Stock to Another Zone")

    if not warehouse.products:
        print("  No products in warehouse yet.")
        return

    sku = input("  Enter SKU to move: ").strip().upper()
    if not sku:
        print("  SKU cannot be empty.")
        return

    print("  Select destination zone:")
    to_zone = get_zone_choice()

    warehouse.move_stock(sku, to_zone)


def zone_summary(warehouse):
    print_header("Zone Summary")

    for zone_name in warehouse.zones:
        total_qty  = warehouse.get_zone_value(zone_name)
        sku_count  = len(warehouse.zones[zone_name])
        print(f"  {zone_name:<16}  {sku_count} product(s)   total qty: {total_qty}")


def run_audit(manager):
    print_header("Low Stock Audit")

    low_skus = manager.audit_warehouse()

    if not low_skus:
        print("  ✓ All products are above their minimum thresholds.")
        return

    warehouse = manager.warehouse
    print(f"  {len(low_skus)} product(s) need restocking:\n")
    print(f"  {'SKU':<10} {'Name':<20} {'Qty':>5} {'Min':>5}")
    print_separator()
    for sku in low_skus:
        p = warehouse.products[sku]
        print(f"  {sku:<10} {p.name:<20} {p.quantity:>5} {p.min_threshold:>5}")


def run_category_breakdown(manager):
    print_header("Category Breakdown")

    breakdown = manager.category_breakdown()

    if not breakdown:
        print("  No products in warehouse yet.")
        return

    print(f"  {'Category':<20} {'Count':>6}")
    print_separator()
    for cat, count in sorted(breakdown.items()):
        print(f"  {cat:<20} {count:>6}")


def print_menu():
    print()
    print("  WAREHOUSE MANAGER")
    print_separator()
    print("  1. Add product")
    print("  2. View all products")
    print("  3. Move stock to another zone")
    print("  4. Zone summary")
    print("  5. Low stock audit")
    print("  6. Category breakdown")
    print("  0. Exit")
    print_separator()


# ── main loop ─────────────────────────────────────────────────────────────────

def main():

    warehouse = Warehouse()
    manager   = LogisticsManager(warehouse)

    # Pre-load a few sample products so the app isn't empty on first run
    samples = [
        (Product("SKU001", "Apple Juice",         "Food",        50, 20), "Cold Storage"),
        (Product("SKU002", "Server Rack",          "Electronics",  3,  5), "General"),
        (Product("SKU003", "Hydrochloric Acid",    "Chemical",    10,  8), "Hazardous"),
        (Product("SKU004", "Frozen Peas",          "Food",         8, 15), "Cold Storage"),
        (Product("SKU005", "Safety Gloves",        "Equipment",   40, 10), "General"),
    ]
    for product, zone in samples:
        warehouse.add_product(product, zone)

    print("\n  Welcome to the Warehouse & Stock Flow Manager!")
    print("  (5 sample products have been pre-loaded for you)")

    while True:
        print_menu()
        choice = input("  Your choice: ").strip()

        if choice == "1":
            add_product(warehouse)
        elif choice == "2":
            view_all_products(warehouse)
        elif choice == "3":
            move_stock(warehouse)
        elif choice == "4":
            zone_summary(warehouse)
        elif choice == "5":
            run_audit(manager)
        elif choice == "6":
            run_category_breakdown(manager)
        elif choice == "0":
            print("\n  Goodbye!\n")
            break
        else:
            print("  Invalid choice. Please enter a number from the menu.")


if __name__ == "__main__":
    main()
