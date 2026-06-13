"""
utils_currency.py
Currency conversion and amount formatting for BankOS.

All internal amounts are stored as integers in the smallest unit
(paise for BDT, cents for USD).  Human-readable conversion happens
here, at display time only.
"""

from __future__ import annotations

# NOTE: utils_validinput imports utils_currency, so we do NOT import it here
# to avoid a circular dependency.  choose_currency() keeps its own loop.

# ── constants ─────────────────────────────────────────────────────────────────

USD_TO_BDT: int = 120          # 1 USD = 120 BDT (fixed educational rate)
SUPPORTED: set[str] = {"BDT", "USD"}

CURRENCY_SYMBOLS: dict[str, str] = {
    "BDT": "৳",
    "USD": "$",
}


# ── minor ↔ major conversion ─────────────────────────────────────────────────

def to_minor(amount: float) -> int:
    """
    Convert a human-entered major amount to the smallest unit.
    e.g.  to_minor(12.50) → 1250
    Always rounds to the nearest integer to avoid floating-point drift.
    """
    return int(round(amount * 100))


def from_minor(amount: int) -> float:
    """
    Convert an internal minor-unit amount to a human-readable major amount.
    e.g.  from_minor(1250) → 12.5
    """
    return amount / 100.0


# ── formatting ────────────────────────────────────────────────────────────────

def format_money(amount_minor: int, currency: str) -> str:
    """
    Format a minor-unit amount with currency symbol and comma separators.

    Examples:
        format_money(1250000, "BDT")  →  "৳12,500.00 BDT"
        format_money(10000,   "USD")  →  "$100.00 USD"
    """
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol}{from_minor(amount_minor):,.2f} {currency}"


def format_money_dual(amount_minor: int, currency: str) -> str:
    """
    Format a minor-unit amount showing the native value and its converted equivalent.

    Examples:
        format_money_dual(1200000, "BDT")  →  "৳12,000.00 BDT (≈ $100.00 USD)"
        format_money_dual(10000,   "USD")  →  "$100.00 USD (≈ ৳12,000.00 BDT)"
    """
    other = "USD" if currency == "BDT" else "BDT"
    converted = convert_minor(amount_minor, currency, other)
    return f"{format_money(amount_minor, currency)} (≈ {format_money(converted, other)})"


# ── conversion ────────────────────────────────────────────────────────────────

def convert_minor(amount_minor: int, from_currency: str, to_currency: str) -> int:
    """
    Convert amount_minor from one currency to another, returning minor units.

    Same-currency:  returns amount_minor unchanged.
    Cross-currency: applies the fixed USD_TO_BDT rate.

    Raises ValueError for unsupported currencies.
    """
    if from_currency not in SUPPORTED or to_currency not in SUPPORTED:
        raise ValueError(
            f"Unsupported currency pair: {from_currency!r} → {to_currency!r}. "
            f"Supported: {', '.join(sorted(SUPPORTED))}"
        )

    if from_currency == to_currency:
        return amount_minor

    amount_major = from_minor(amount_minor)

    if from_currency == "USD" and to_currency == "BDT":
        converted = amount_major * USD_TO_BDT
    else:  # BDT → USD
        converted = amount_major / USD_TO_BDT

    return to_minor(converted)


# ── input helpers ─────────────────────────────────────────────────────────────

def parse_amount_input(raw: str) -> int | None:
    """
    Parse a user-entered amount string (major units, e.g. "125.50") into minor units.
    Returns None if the input is invalid or non-positive.

    Examples:
        parse_amount_input("125.50")  →  12550
        parse_amount_input("-1")      →  None
        parse_amount_input("abc")     →  None
    """
    try:
        value = float(raw.strip())
    except ValueError:
        return None
    if value <= 0:
        return None
    return to_minor(value)


def choose_currency(prompt: str = "Choose currency [BDT/USD]: ") -> str:
    """
    Prompt the user to pick a supported currency.
    Loops until a valid choice is entered. Returns uppercased currency code.
    """
    while True:
        choice = input(prompt).strip().upper()
        if choice in SUPPORTED:
            return choice
        print(f"[ERROR] Invalid currency. Choose from: {', '.join(sorted(SUPPORTED))}")
