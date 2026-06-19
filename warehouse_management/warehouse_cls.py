class Product:

    def __init__(self, sku, name, category, quantity, min_threshold):
        self.sku = sku
        self.name = name
        self.category = category
        self.quantity = quantity
        self.min_threshold = min_threshold

    def is_low_stock(self):

        if self.quantity < self.min_threshold:
            return True
        else:
            return False


class Warehouse:

    def __init__(self):
        self.products = {}       # dict : sku → Product
        self.zones = {           # dict : zone_name → [sku, sku, ...]
            "Cold Storage" : [],
            "General" : [],
            "Hazardous" : []
        }

    def add_product(self, new_product, zone):

        # Makes sure proper zone is in the list
        if zone not in self.zones:
            raise ValueError(f"Unknown zone: {zone}. Allowed zones are: {list(self.zones.keys())}")

        # Add to the main registry (dictionary)
        self.products[new_product.sku] = new_product

        self.zones[zone].append(new_product.sku)

    def move_stock(self, sku, to_zone):

        if sku not in self.products:
            print(f"Error: SKU {sku} not found in warehouse")
            return

        if to_zone not in self.zones:
            print(f"Error: Zone '{to_zone}' does not exist. Allowed zones are: {list(self.zones.keys())}")
            return

        current_zone = None
        for zone_name, sku_list in self.zones.items():
            if sku in sku_list:
                current_zone = zone_name
                break

        if current_zone is None:
            print(f"Error: SKU {sku} is not assigned to any zone")
            return

        if current_zone == to_zone:
            print(f"SKU {sku} is already in '{to_zone}' zone")
            return

        self.zones[current_zone].remove(sku)
        self.zones[to_zone].append(sku)
        print(f"Moved SKU {sku} from '{current_zone}' to '{to_zone}'")

    def get_zone_value(self, zone_name):

        if zone_name not in self.zones:
            print(f"Error: Zone '{zone_name}' does not exist. Allowed zones are: {list(self.zones.keys())}")
            return 0

        total = 0
        for sku in self.zones[zone_name]:
            if sku in self.products:
                total += self.products[sku].quantity

        return total


class LogisticsManager:

    def __init__(self, warehouse):
        self.warehouse = warehouse

    def audit_warehouse(self):
        low_stock = []
        for sku, product in self.warehouse.products.items():
            if product.is_low_stock():
                low_stock.append(sku)
        return low_stock

    def category_breakdown(self):
        cat_breakdown = {}
        for product in self.warehouse.products.values():
            cat = product.category
            if cat not in cat_breakdown:
                cat_breakdown[cat] = 0
            cat_breakdown[cat] += 1
        return cat_breakdown
