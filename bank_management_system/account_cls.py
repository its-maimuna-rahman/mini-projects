"""
account_cls.py
Core OOP models for BankOS.
"""

from __future__ import annotations

from utils_security import hash_password
from utils_currency import format_money, convert_minor


# ─────────────────────────────────────────────────────────────────────────────
#  Lock
# ─────────────────────────────────────────────────────────────────────────────

class Lock:
    """Holds a hashed vault password. Plaintext never stored after init."""

    def __init__(self, password_hash: str):
        self._hash = password_hash

    def check(self, plaintext: str) -> bool:
        return self._hash == hash_password(plaintext)

    def __repr__(self) -> str:
        return "Lock(****)"


# ─────────────────────────────────────────────────────────────────────────────
#  Vault
# ─────────────────────────────────────────────────────────────────────────────

class Vault:
    """
    Secure vault attached to an account.
    All amounts are in the smallest currency unit (paise / cents).
    """

    def __init__(self, vault_no: str, password_hash: str, balance: int = 0):
        self._vault_no = vault_no
        self._balance  = int(balance)
        self.lock      = Lock(password_hash)

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def vault_no(self) -> str:
        return self._vault_no

    @property
    def balance(self) -> int:
        return self._balance

    # ── fund movement ─────────────────────────────────────────────────────────

    def add(self, amount: int) -> None:
        """Add amount (minor units) to vault."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self._balance += amount

    def deduct(self, amount: int) -> bool:
        """
        Deduct amount (minor units) from vault.
        Returns False if insufficient funds.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self._balance:
            return False
        self._balance -= amount
        return True

    # ── info ──────────────────────────────────────────────────────────────────

    @property
    def vault_info(self) -> dict:
        return {"vault_no": self._vault_no, "vault_balance_minor": self._balance}

    # ── dunder ────────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return f"Vault(no={self._vault_no}, balance_minor={self._balance})"

    def __repr__(self) -> str:
        return f"Vault({self._vault_no!r}, {self._balance})"


# ─────────────────────────────────────────────────────────────────────────────
#  Base Account
# ─────────────────────────────────────────────────────────────────────────────

class Account:
    """
    Base account class.
    All monetary amounts are integers in the smallest currency unit.
    Passwords are stored as SHA-256 hashes — plaintext never lives here.
    """

    def __init__(
        self,
        acc_num: int,
        password_hash: str,
        acc_balance: int,
        currency: str,
        is_frozen: bool = False,
        daily_transfer_limit: int = 500_000,  # default 5000.00 in minor units
    ):
        self._acc_num             = int(acc_num)
        self._password_hash       = str(password_hash)
        self._acc_balance         = int(acc_balance)
        self._currency            = str(currency).upper()
        self._is_frozen           = bool(is_frozen)
        self._daily_transfer_limit = int(daily_transfer_limit)
        self.vault: Vault | None  = None

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def acc_num(self) -> int:
        return self._acc_num

    @property
    def acc_balance(self) -> int:
        return self._acc_balance

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def is_frozen(self) -> bool:
        return self._is_frozen

    @is_frozen.setter
    def is_frozen(self, value: bool) -> None:
        self._is_frozen = bool(value)

    @property
    def daily_transfer_limit(self) -> int:
        return self._daily_transfer_limit

    @daily_transfer_limit.setter
    def daily_transfer_limit(self, value: int) -> None:
        if int(value) < 0:
            raise ValueError("Daily transfer limit cannot be negative.")
        self._daily_transfer_limit = int(value)

    # ── authentication ────────────────────────────────────────────────────────

    def check_password(self, plaintext: str) -> bool:
        """Hash plaintext and compare — never compares raw strings."""
        return self._password_hash == hash_password(plaintext)

    # ── fund movement ─────────────────────────────────────────────────────────

    def add_to_balance(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self._acc_balance += amount

    def deduct_from_balance(self, amount: int) -> bool:
        """Deduct from balance. Returns False if insufficient."""
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if amount > self._acc_balance:
            return False
        self._acc_balance -= amount
        return True

    def can_deduct_from_balance(self, amount: int) -> bool:
        return self._acc_balance >= amount

    # ── dunder ────────────────────────────────────────────────────────────────

    def __iadd__(self, amount: int) -> Account:
        self.add_to_balance(amount)
        return self

    def __isub__(self, amount: int) -> Account:
        self.deduct_from_balance(amount)
        return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Account):
            return self._acc_num == other._acc_num
        return False

    def __hash__(self) -> int:
        return hash(self._acc_num)

    def __repr__(self) -> str:
        return (
            f"Account({self._acc_num}, {self._currency}, "
            f"balance_minor={self._acc_balance}, frozen={self._is_frozen})"
        )

    def __str__(self) -> str:
        return str(self.account_info)

    # ── info ──────────────────────────────────────────────────────────────────

    @property
    def account_info(self) -> dict:
        vault_detail = (
            {"vault_no": self.vault.vault_no, "vault_balance_minor": self.vault.balance}
            if self.vault else "no vault"
        )
        return {
            "acc_num":              self._acc_num,
            "acc_type":             "account",
            "currency":             self._currency,
            "acc_balance_minor":    self._acc_balance,
            "is_frozen":            self._is_frozen,
            "daily_limit_minor":    self._daily_transfer_limit,
            "vault":                vault_detail,
        }


# ─────────────────────────────────────────────────────────────────────────────
#  Non-Credit Card Account
# ─────────────────────────────────────────────────────────────────────────────

class Non_Credit_Card(Account):
    """Standard account with no credit card."""

    @property
    def account_info(self) -> dict:
        info = super().account_info
        info["acc_type"] = "non_credit_card"
        return info

    def __repr__(self) -> str:
        return (
            f"Non_Credit_Card({self._acc_num}, {self._currency}, "
            f"balance_minor={self._acc_balance})"
        )

    def __str__(self) -> str:
        return str(self.account_info)


# ─────────────────────────────────────────────────────────────────────────────
#  Credit Card Account
# ─────────────────────────────────────────────────────────────────────────────

class CreditCard(Account):
    """
    Account with an attached credit card.
    credit_used is loaded from DB on every instantiation — not reset to 0.
    PIN is stored as SHA-256 hash.
    """

    def __init__(
        self,
        acc_num: int,
        password_hash: str,
        acc_balance: int,
        currency: str,
        credit_card_num: str,
        cc_pin_hash: str,
        credit_card_limit: int,
        credit_used: int = 0,          # loaded from DB — preserves state
        is_frozen: bool = False,
        daily_transfer_limit: int = 500_000,
    ):
        super().__init__(acc_num, password_hash, acc_balance, currency, is_frozen, daily_transfer_limit)
        self._credit_card_num   = str(credit_card_num)
        self._cc_pin_hash       = str(cc_pin_hash)
        self._credit_card_limit = int(credit_card_limit)
        self._credit_used       = int(credit_used)

    # ── properties ────────────────────────────────────────────────────────────

    @property
    def credit_card_num(self) -> str:
        return self._credit_card_num

    @property
    def credit_card_limit(self) -> int:
        return self._credit_card_limit

    @credit_card_limit.setter
    def credit_card_limit(self, value: int) -> None:
        if int(value) < 0:
            raise ValueError("Credit limit cannot be negative.")
        self._credit_card_limit = int(value)

    @property
    def credit_used(self) -> int:
        return self._credit_used

    @property
    def credit_available(self) -> int:
        return self._credit_card_limit - self._credit_used

    # ── authentication ────────────────────────────────────────────────────────

    def check_cc_pin(self, plaintext: str) -> bool:
        """Hash plaintext PIN and compare to stored hash."""
        return self._cc_pin_hash == hash_password(plaintext)

    # ── credit operations ─────────────────────────────────────────────────────

    def can_charge_credit(self, amount: int) -> bool:
        return self._credit_used + amount <= self._credit_card_limit

    def charge_credit(self, amount: int) -> bool:
        """
        Charge amount to credit card.
        Returns False if limit would be exceeded.
        Prints a warning if ≤ 50000 minor units (500.00) remaining after charge.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if not self.can_charge_credit(amount):
            return False
        self._credit_used += amount
        if self.credit_available <= 50_000:
            print(
                f"[WARNING] Low credit! Only "
                f"{format_money(self.credit_available, self._currency)} remaining."
            )
        return True

    def payback_credit(self, amount: int) -> int:
        """
        Reduce credit_used by amount (or by full outstanding if amount > credit_used).
        Returns actual amount paid back.
        """
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        paid = min(self._credit_used, amount)
        self._credit_used -= paid
        return paid

    # ── info ──────────────────────────────────────────────────────────────────

    @property
    def account_info(self) -> dict:
        info = super().account_info
        info.update({
            "acc_type":             "credit_card",
            "credit_card_num":      self._credit_card_num,
            "credit_card_limit":    self._credit_card_limit,
            "credit_used":          self._credit_used,
            "credit_available":     self.credit_available,
        })
        return info

    # ── dunder ────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        masked = self._credit_card_num[-4:] if self._credit_card_num else "????"
        return (
            f"CreditCard({self._acc_num}, {self._currency}, "
            f"balance_minor={self._acc_balance}, cc_last4={masked})"
        )

    def __str__(self) -> str:
        return str(self.account_info)


# ─────────────────────────────────────────────────────────────────────────────
#  Payment Processor
# ─────────────────────────────────────────────────────────────────────────────

class Payment_Processor:
    """
    Handles in-memory fund movement between Account objects.
    All amounts are in minor units (paise/cents).
    Cross-currency transfers auto-convert using convert_minor().
    This class operates purely on OOP objects — DB persistence is handled
    separately in utils_storage.py.
    """

    # ── single-account operations ─────────────────────────────────────────────

    def add_funds(self, account: Account, amount: int) -> bool:
        """Direct deposit to account balance."""
        print(
            f"\n--- [GATEWAY] Deposit {format_money(amount, account.currency)} "
            f"→ Account {account.acc_num} ---"
        )
        account.add_to_balance(amount)
        print(
            f"[GATEWAY] Success. New Balance: "
            f"{format_money(account.acc_balance, account.currency)}"
        )
        return True

    def deduct_funds(self, account: Account, amount: int) -> bool:
        """Direct deduction from account balance. Warns if balance ≤ 50000 after."""
        print(
            f"\n--- [GATEWAY] Deduct {format_money(amount, account.currency)} "
            f"from Account {account.acc_num} ---"
        )
        ok = account.deduct_from_balance(amount)
        if ok:
            print(
                f"[GATEWAY] Success. New Balance: "
                f"{format_money(account.acc_balance, account.currency)}"
            )
            if account.acc_balance <= 50_000:
                print(
                    f"[WARNING] Low balance! Only "
                    f"{format_money(account.acc_balance, account.currency)} remaining."
                )
        else:
            print("[GATEWAY] Failed — insufficient balance.")
        return ok

    def deduct_via_credit(self, cc: CreditCard, amount: int) -> bool:
        """Charge amount to a credit card."""
        masked = cc.credit_card_num[-4:] if cc.credit_card_num else "????"
        print(
            f"\n--- [GATEWAY] Credit charge {format_money(amount, cc.currency)} "
            f"→ Card ...{masked} ---"
        )
        ok = cc.charge_credit(amount)
        if ok:
            print(
                f"[GATEWAY] Charged. Used: {format_money(cc.credit_used, cc.currency)} / "
                f"Limit: {format_money(cc.credit_card_limit, cc.currency)}"
            )
        else:
            print("[GATEWAY] Failed — credit limit exceeded.")
        return ok

    # ── transfer helpers ──────────────────────────────────────────────────────

    def _execute_send(self, sender: Account, amount: int, via_credit: bool) -> bool:
        """Deduct from sender (balance or credit). Returns success."""
        if via_credit:
            if not isinstance(sender, CreditCard):
                print("[ERROR] Sender has no credit card.")
                return False
            return self.deduct_via_credit(sender, amount)
        return self.deduct_funds(sender, amount)

    def _execute_receive(self, receiver: Account, amount: int, sender_currency: str) -> None:
        """Credit receiver, auto-converting currency if needed."""
        recv_amount = convert_minor(amount, sender_currency, receiver.currency)
        receiver.add_to_balance(recv_amount)
        print(
            f"[GATEWAY] Receiver {receiver.acc_num} credited: "
            f"{format_money(recv_amount, receiver.currency)}"
        )

    # ── 1-to-1 transfer ───────────────────────────────────────────────────────

    def transfer_1to1(
        self,
        sender: Account,
        receiver: Account,
        amount: int,
        via_credit: bool = False,
    ) -> bool:
        """Transfer a fixed amount from one account to another."""
        print(
            f"\n--- [GATEWAY] Transfer {format_money(amount, sender.currency)}: "
            f"Acc {sender.acc_num} → Acc {receiver.acc_num} ---"
        )
        if sender.is_frozen or receiver.is_frozen:
            print("[GATEWAY] Transfer blocked — frozen account.")
            return False
        ok = self._execute_send(sender, amount, via_credit)
        if ok:
            self._execute_receive(receiver, amount, sender.currency)
            print("[GATEWAY] Transfer successful.")
        return ok

    # ── 1-to-many transfer ────────────────────────────────────────────────────

    def transfer_1tomany(
        self,
        sender: Account,
        receivers: list[Account],
        amount: int,
        via_credit: bool = False,
    ) -> bool:
        """
        Transfer the same amount from one sender to multiple receivers.
        Stops on first failure.
        """
        print(
            f"\n--- [GATEWAY] 1-to-Many: {format_money(amount, sender.currency)} each "
            f"from Acc {sender.acc_num} → {len(receivers)} receivers ---"
        )
        if sender.is_frozen:
            print("[GATEWAY] Transfer blocked — sender is frozen.")
            return False
        for rec in receivers:
            ok = self.transfer_1to1(sender, rec, amount, via_credit)
            if not ok:
                print(f"[GATEWAY] Failed at receiver Acc {rec.acc_num} — stopping.")
                return False
        return True

    # ── many-to-1 transfer ────────────────────────────────────────────────────

    def transfer_manyto1(
        self,
        senders: list[Account],
        receiver: Account,
        amount: int,
        via_credit: bool = False,
    ) -> bool:
        """
        Each sender in the list sends the same amount to one receiver.
        Stops on first failure.
        """
        print(
            f"\n--- [GATEWAY] Many-to-1: {format_money(amount, receiver.currency)} each "
            f"from {len(senders)} senders → Acc {receiver.acc_num} ---"
        )
        if receiver.is_frozen:
            print("[GATEWAY] Transfer blocked — receiver is frozen.")
            return False
        for sen in senders:
            ok = self.transfer_1to1(sen, receiver, amount, via_credit)
            if not ok:
                print(f"[GATEWAY] Failed at sender Acc {sen.acc_num} — stopping.")
                return False
        return True
