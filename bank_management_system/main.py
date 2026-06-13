"""
main.py — BankOS
Single entry point: first-run setup → login screen → Admin portal / Customer portal.

All data lives in SQLite databases. CSV/XLSX import is supported at first-run setup.
XLSX/CSV export is on-demand only from the Admin portal.

Admin  menu : 10 options
Customer menu: 8 options
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import NamedTuple

from utils_currency import (
    SUPPORTED,
    convert_minor,
    format_money,
    format_money_dual,
    parse_amount_input,
)
from utils_reports import generate_pdf_statement
from utils_security import check_admin_password, hash_password, VAULT_MAX_TRIES
from utils_storage import (
    FILTER_WHERE,
    authenticate_customer,
    bank_overview,
    convert_account_type,
    create_account,
    create_vault,
    delete_account,
    destroy_vault,
    export_accounts_csv,
    export_accounts_xlsx,
    first_run_setup,
    freeze_account,
    get_logs,
    get_outbound_today,
    get_pending_transfers,
    import_file_to_table,
    init_storage,
    list_accounts,
    log_account_action,
    log_freeze_action,
    log_transaction,
    payback_credit,
    recent_transactions,
    review_pending,
    seed_sample_data,
    set_daily_limit,
    transfer,
    transfer_1tomany,
    transfer_manyto1,
    vault_add,
    vault_deduct,
)
from utils_validinput import (
    prompt_positive_int,
    prompt_amount_minor,
    prompt_yes_no,
    prompt_category,
    prompt_currency,
    prompt_menu_choice,
    prompt_filter_key,
    prompt_password,
    prompt_pin,
    prompt_account_number,
)


# ── constants ─────────────────────────────────────────────────────────────────

FILTER_KEYS = list(FILTER_WHERE.keys())


# ── log-path bundle ───────────────────────────────────────────────────────────

class Logs(NamedTuple):
    """Holds the four log DB connections for the lifetime of the session."""
    acc:     sqlite3.Connection   # account_log DB
    tx:      sqlite3.Connection   # transaction_log DB
    freeze:  sqlite3.Connection   # freezing_account DB
    pending: sqlite3.Connection   # pending_transfers DB


# ─────────────────────────────────────────────────────────────────────────────
#  Input helpers (thin wrappers where prompt_* doesn't cover it directly)
# ─────────────────────────────────────────────────────────────────────────────

def _input(prompt: str = "") -> str:
    return input(prompt).strip()


def _divider(title: str = "") -> None:
    if title:
        print(f"\n{'\u2500' * 10}  {title}  {'\u2500' * 10}")
    else:
        print("\u2500" * 40)


# ─────────────────────────────────────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────────────────────────────────────

def _display_account_row(row, dual: bool = True) -> None:
    currency = row["currency"]
    fmt = format_money_dual if dual else format_money

    print(f"  Account     : {row['acc_num']}")
    print(f"  Type        : {row['acc_type'].replace('_', ' ').title()}")
    print(f"  Currency    : {currency}")
    print(f"  Balance     : {fmt(row['acc_balance'], currency)}")
    print(f"  Status      : {'FROZEN' if row['is_frozen'] else 'Active'}")
    print(f"  Daily Limit : {fmt(row['daily_transfer_limit'], currency)}")

    if row["acc_type"] == "credit_card":
        cc = row["credit_card_num"]
        masked = f"**** **** **** {cc[-4:]}" if cc else "N/A"
        print(f"  Card        : {masked}")
        print(f"  CC Limit    : {fmt(row['credit_card_limit'], currency)}")
        print(f"  Credit Used : {fmt(row['credit_used'], currency)}")
        print(f"  CC Available: {fmt(row['credit_card_limit'] - row['credit_used'], currency)}")

    if row["vault_no"]:
        print(f"  Vault No    : {row['vault_no']}")
        print(f"  Vault Bal   : {fmt(row['vault_balance'], currency)}")
    else:
        print(f"  Vault       : none")


def _display_log_row(row) -> None:
    parts = [f"{k}={v}" for k, v in dict(row).items() if k != "id"]
    print("  " + " | ".join(parts))


def _display_transaction_row(row) -> None:
    currency = row["currency"]
    print(
        f"  {row['timestamp']}  {row['type']:<22}"
        f"  {format_money(row['amount'], currency):<22}"
        f"  {row['category']:<10}  {row['status']:<8}"
        f"  bal_after={format_money(row['balance_after'], currency)}"
    )


def _display_pending_row(row) -> None:
    print(
        f"  ID={row['id']}  {row['timestamp']}"
        f"  {row['sender_acc_num']} -> {row['receiver_acc_num']}"
        f"  {format_money(row['amount'], row['currency'])}"
        f"  via_credit={'yes' if row['via_credit'] else 'no'}"
        f"  status={row['status']}"
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Session startup
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_csv(path: str, header: list) -> None:
    """Create a CSV file with a header row if it does not yet exist."""
    import csv as _csv
    p = Path(path)
    if not p.exists() or p.stat().st_size == 0:
        with p.open("w", newline="", encoding="utf-8") as f:
            _csv.writer(f).writerow(header)


def _start_session():
    """Always runs first_run_setup() on every program start."""
    conn, acc_log_conn, tx_log_conn, freeze_log_conn, pending_conn = first_run_setup()
    return conn, Logs(acc=acc_log_conn, tx=tx_log_conn, freeze=freeze_log_conn, pending=pending_conn)


# ─────────────────────────────────────────────────────────────────────────────
#  Admin portal
# ─────────────────────────────────────────────────────────────────────────────

def admin_portal(conn, logs: Logs) -> None:
    """9-option admin menu. Returns to login screen on logout."""
    while True:
        _divider("Admin Menu")
        print("  [1] Account Management")
        print("  [2] Vault Management")
        print("  [3] Show Accounts")
        print("  [4] View Logs")
        print("  [5] Bank Overview")
        print("  [6] Freeze / Unfreeze Account")
        print("  [7] Pending Transfer Approval")
        print("  [8] Generate PDF Statement")
        print("  [9] Export Accounts (XLSX / CSV)")
        print("  [0] Logout")
        _divider()

        ch = prompt_menu_choice("  Select: ", {"1","2","3","4","5","6","7","8","9","0"})

        if   ch == "1": _admin_account_crud(conn, logs)
        elif ch == "2": _admin_vault_crud(conn, logs)
        elif ch == "3": _admin_show_accounts(conn)
        elif ch == "4": _admin_logs(conn, logs)
        elif ch == "5": _admin_overview(conn, logs)
        elif ch == "6": _admin_freeze(conn, logs)
        elif ch == "7": _admin_pending(conn, logs)
        elif ch == "8": _admin_pdf(conn, logs)
        elif ch == "9": _admin_export(conn)
        elif ch == "0":
            print("  Logged out.")
            return


def _admin_account_crud(conn, logs: Logs) -> None:
    """Option 1 — Account CRUD: add, delete, convert type, set daily limit."""
    _divider("Account Management")
    print("  [1] Add account")
    print("  [2] Delete account")
    print("  [3] Convert account type (credit <-> non-credit)")
    print("  [4] Set daily transfer limit")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","3","4","0"})
    if sub == "0":
        return

    if sub == "1":
        _divider("Add Account")
        acc      = prompt_positive_int("  Account number: ")
        pwd      = prompt_password("  Password: ")
        currency = prompt_currency()
        acc_type = prompt_menu_choice(
            "  Type (credit_card / non_credit_card): ",
            {"credit_card", "non_credit_card"},
        )
        bal = prompt_amount_minor("  Opening balance (major units, e.g. 500): ")
        dtl = prompt_amount_minor("  Daily transfer limit (major units, e.g. 5000): ")

        result = create_account(conn, acc, pwd, currency, acc_type, bal, dtl)
        print(f"  {result}")
        if "successfully" in result:
            log_account_action(
                conn, logs.acc, acc, "ACCOUNT_ADDED",
                f"New {acc_type} | {currency} | opening_bal={format_money(bal, currency)}",
            )
            if prompt_yes_no("  Attach a vault now? [yes/no]: "):
                vno = _input("  Vault number (e.g. V001): ")
                vpw = _input("  Vault password: ")
                if vno and vpw:
                    vresult = create_vault(conn, acc, vno, vpw)
                    print(f"  {vresult}")
                    if "created" in vresult:
                        log_account_action(
                            conn, logs.acc, acc, "VAULT_CREATED",
                            f"Vault {vno} created at account creation",
                        )
                else:
                    print("  [SKIP] Vault number or password was empty.")

    elif sub == "2":
        _divider("Delete Account")
        acc = prompt_positive_int("  Account number to delete: ")
        row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc,)).fetchone()
        if not row:
            print("  [!] Account not found.")
            return
        _display_account_row(row)
        if not prompt_yes_no(f"\n  Permanently delete account {acc}? [yes/no]: "):
            print("  Cancelled.")
            return
        result = delete_account(conn, acc)
        print(f"  {result}")
        if "deleted" in result:
            log_account_action(conn, logs.acc, acc, "ACCOUNT_DELETED", "Deleted by admin")

    elif sub == "3":
        _divider("Convert Account Type")
        acc     = prompt_positive_int("  Account number: ")
        to_type = prompt_menu_choice(
            "  Convert to (credit_card / non_credit_card): ",
            {"credit_card", "non_credit_card"},
        )
        result = convert_account_type(conn, acc, to_type)
        print(f"  {result}")
        if "converted" in result:
            log_account_action(conn, logs.acc, acc, "CONVERT_TYPE",
                               f"Converted to {to_type}")

    elif sub == "4":
        _divider("Set Daily Transfer Limit")
        acc = prompt_positive_int("  Account number: ")
        row = conn.execute(
            "SELECT acc_num, currency, daily_transfer_limit FROM accounts WHERE acc_num=?",
            (acc,),
        ).fetchone()
        if not row:
            print("  [!] Account not found.")
            return
        print(f"  Current limit: {format_money_dual(row['daily_transfer_limit'], row['currency'])}")
        new_limit = prompt_amount_minor("  New daily transfer limit (major units): ")
        result    = set_daily_limit(conn, acc, new_limit)
        print(f"  {result}")
        log_account_action(
            conn, logs.acc, acc, "LIMIT_CHANGED",
            f"Daily limit -> {format_money(new_limit, row['currency'])}",
        )


def _admin_vault_crud(conn, logs: Logs) -> None:
    """Option 2 — Vault CRUD: create vault, destroy vault with full auth flow."""
    _divider("Vault Management")
    print("  [1] Create vault")
    print("  [2] Destroy vault")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","0"})
    if sub == "0":
        return

    acc = prompt_positive_int("  Account number: ")
    row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc,)).fetchone()
    if not row:
        print("  [!] Account not found.")
        return

    if sub == "1":
        _divider("Create Vault")
        if row["vault_no"]:
            print(f"  [!] Account {acc} already has vault '{row['vault_no']}'.")
            return
        vno = _input("  New vault number (e.g. V002): ")
        if not vno:
            print("  [!] Vault number cannot be empty.")
            return
        vpw = _input("  New vault password: ")
        if not vpw:
            print("  [!] Vault password cannot be empty.")
            return
        result = create_vault(conn, acc, vno, vpw)
        print(f"  {result}")
        if "created" in result:
            log_account_action(conn, logs.acc, acc, "VAULT_CREATED",
                               f"Vault {vno} created")

    elif sub == "2":
        _divider("Destroy Vault")
        if not row["vault_no"]:
            print(f"  [!] Account {acc} has no vault.")
            return

        currency      = row["currency"]
        vault_balance = row["vault_balance"]
        print(f"  Vault: {row['vault_no']}  |  Balance: {format_money_dual(vault_balance, currency)}")

        # vault password — 3 attempts
        vpw_ok = False
        vpw    = ""
        for attempt in range(1, VAULT_MAX_TRIES + 1):
            vpw = _input(f"  Vault password (attempt {attempt}/{VAULT_MAX_TRIES}): ")
            if row["vault_password_hash"] == hash_password(vpw):
                vpw_ok = True
                break
            remaining = VAULT_MAX_TRIES - attempt
            if remaining:
                print(f"  [!] Wrong password. {remaining} attempt(s) left.")
            else:
                print("  [!] Too many wrong attempts. Operation cancelled.")
        if not vpw_ok:
            return

        result = ""
        if vault_balance > 0:
            print(f"\n  Vault has {format_money_dual(vault_balance, currency)}.")
            print("  [1] Transfer to account balance (requires account password)")
            print("  [2] Pay back credit card (requires CC PIN — CC accounts only)")
            dest = prompt_menu_choice("  Choose destination: ", {"1", "2"})

            if dest == "1":
                acc_pwd = prompt_password("  Account password: ")
                ok, msg = _check_account_password(conn, acc, acc_pwd)
                if not ok:
                    print(f"  [!] {msg} Vault not destroyed.")
                    return
                result = destroy_vault(conn, logs.tx, acc, vpw, transfer_to_balance=True)

            elif dest == "2":
                if row["acc_type"] != "credit_card":
                    print("  [!] This account has no credit card. Use option 1.")
                    return
                cc_pin = _input("  Credit card PIN: ")
                if row["credit_card_pin_hash"] != hash_password(cc_pin):
                    print("  [!] Wrong credit card PIN. Vault not destroyed.")
                    return
                pay = min(vault_balance, row["credit_used"])
                if pay > 0:
                    conn.execute(
                        "UPDATE accounts SET vault_balance=vault_balance-?,"
                        " credit_used=credit_used-? WHERE acc_num=?",
                        (pay, pay, acc),
                    )
                    conn.commit()
                    bal_now = conn.execute(
                        "SELECT acc_balance FROM accounts WHERE acc_num=?", (acc,)
                    ).fetchone()["acc_balance"]
                    log_transaction(conn, logs.tx, acc, "cc_payback_balance",
                                    pay, currency, "other", "success", bal_now)
                leftover = vault_balance - pay
                if leftover > 0:
                    conn.execute(
                        "UPDATE accounts SET acc_balance=acc_balance+? WHERE acc_num=?",
                        (leftover, acc),
                    )
                    conn.commit()
                result = destroy_vault(conn, logs.tx, acc, vpw, transfer_to_balance=False)
        else:
            result = destroy_vault(conn, logs.tx, acc, vpw, transfer_to_balance=False)

        print(f"  {result}")
        if "destroyed" in result.lower():
            log_account_action(conn, logs.acc, acc, "VAULT_DESTROYED",
                               "Vault destroyed by admin")


def _admin_show_accounts(conn) -> None:
    """Option 3 — Show all accounts with filter + dual-currency toggle."""
    _divider("Show Accounts")
    flt  = prompt_filter_key("  Select filter: ", filter_map=FILTER_WHERE)
    dual = prompt_yes_no("  Show dual-currency display? [yes/no]: ")
    rows = list_accounts(conn, flt)
    if not rows:
        print("  No accounts match this filter.")
        return
    print(f"\n  {len(rows)} account(s) — filter: {flt}\n")
    for row in rows:
        _divider()
        _display_account_row(row, dual=dual)
    _divider()


def _admin_logs(conn, logs: Logs) -> None:
    """Option 4 — View account_log, transaction_log, or pending_transfers."""
    _divider("View Logs")
    print("  [1] Account log")
    print("  [2] Transaction log")
    print("  [3] Freeze log")
    print("  [4] Pending transfers log")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","3","4","0"})
    if sub == "0":
        return

    table = {
        "1": "account_log",
        "2": "transaction_log",
        "3": "freezing_account",
        "4": "pending_transfers",
    }[sub]
    acc_raw   = _input("  Filter by account number (Enter for all): ")
    acc_num   = int(acc_raw) if acc_raw.isdigit() else None
    limit_raw = _input("  Max rows to show (Enter for 50): ")
    limit     = int(limit_raw) if limit_raw.isdigit() else 50

    rows = get_logs(conn, table, acc_num, limit,
                    acc_log_conn=logs.acc, tx_log_conn=logs.tx,
                    freeze_log_conn=logs.freeze, pending_conn=logs.pending)
    if not rows:
        print("  No log entries found.")
        return
    label = f" for acc {acc_num}" if acc_num else ""
    print(f"\n  {len(rows)} entry(ies) — {table}{label}")
    _divider()
    for row in rows:
        if table == "transaction_log":
            _display_transaction_row(row)
        elif table == "pending_transfers":
            _display_pending_row(row)
        else:
            _display_log_row(row)
    _divider()


def _admin_overview(conn, logs: Logs) -> None:
    """Option 5 — Bank overview: pool totals, frozen count, pending count."""
    _divider("Bank Overview")
    ov = bank_overview(conn, pending_conn=logs.pending)
    print("  Total balances by currency:")
    for cur, total in ov.get("totals", {}).items():
        print(f"    {format_money_dual(total, cur)}")
    print(f"  Frozen accounts  : {ov['frozen_accounts']}")
    print(f"  Pending transfers: {ov['pending_count']}")
    _divider()


def _admin_freeze(conn, logs: Logs) -> None:
    """Option 6 — Freeze or unfreeze an account. Writes to account_log."""
    _divider("Freeze / Unfreeze Account")
    acc = prompt_positive_int("  Account number: ")
    row = conn.execute(
        "SELECT acc_num, is_frozen FROM accounts WHERE acc_num=?", (acc,)
    ).fetchone()
    if not row:
        print("  [!] Account not found.")
        return

    print(f"  Account {acc} is currently: {'FROZEN' if row['is_frozen'] else 'Active'}")
    action = prompt_menu_choice("  Action (freeze / unfreeze): ", {"freeze", "unfreeze"})
    result = freeze_account(conn, acc, freeze=(action == "freeze"))
    print(f"  {result}")

    log_key = "ACCOUNT_FROZEN" if action == "freeze" else "ACCOUNT_UNFROZEN"
    detail  = f"{action.capitalize()}d by admin"
    log_account_action(conn, logs.acc, acc, log_key, detail)
    log_freeze_action(conn, logs.freeze, acc, log_key, detail)


def _admin_pending(conn, logs: Logs) -> None:
    """Option 7 — List pending transfers, approve or reject."""
    _divider("Pending Transfers")
    rows = get_pending_transfers(logs.pending)
    if not rows:
        print("  No pending transfers.")
        return

    print(f"  {len(rows)} pending transfer(s):\n")
    for row in rows:
        _display_pending_row(row)

    _divider()
    pid = prompt_positive_int("  Enter transfer ID to review (0 not allowed): ")
    approve = prompt_yes_no(f"  Approve transfer ID {pid}? [yes/no]: ")
    print(f"  {review_pending(conn, logs.tx, pid, approve, pending_conn=logs.pending)}")


def _admin_pdf(conn, logs: Logs) -> None:
    """Option 8 — Generate PDF statement for any account."""
    _divider("Generate PDF Statement")
    acc = prompt_positive_int("  Account number: ")
    if not conn.execute("SELECT acc_num FROM accounts WHERE acc_num=?", (acc,)).fetchone():
        print("  [!] Account not found.")
        return
    print(f"  {generate_pdf_statement(conn, acc, tx_log_conn=logs.tx)}")


def _admin_export(conn) -> None:
    """Option 9 — Export accounts snapshot to XLSX or CSV with filter."""
    _divider("Export Accounts")
    print("  [1] XLSX")
    print("  [2] CSV")
    print("  [0] Back")
    fmt = prompt_menu_choice("  Format: ", {"1","2","0"})
    if fmt == "0":
        return

    flt      = prompt_filter_key("  Select filter: ", filter_map=FILTER_WHERE)
    filename = _input("  Output filename (Enter for auto-generated name): ")
    ext      = "xlsx" if fmt == "1" else "csv"
    if not filename:
        from datetime import datetime as _dt
        filename = f"accounts_{flt}_{_dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.{ext}"

    if fmt == "1":
        print(f"  {export_accounts_xlsx(conn, filename, flt)}")
    else:
        print(f"  {export_accounts_csv(conn, filename, flt)}")


# ─────────────────────────────────────────────────────────────────────────────
#  Customer portal
# ─────────────────────────────────────────────────────────────────────────────

def customer_portal(conn, acc_num: int, logs: Logs) -> None:
    """8-option customer menu. Returns to login screen on logout."""
    while True:
        row = conn.execute(
            "SELECT * FROM accounts WHERE acc_num=?", (acc_num,)
        ).fetchone()
        if not row:
            print("  [!] Session error: account not found.")
            return

        _divider(f"Customer Menu — Acc {acc_num}")
        print(f"  Balance: {format_money_dual(row['acc_balance'], row['currency'])}")
        if row["is_frozen"]:
            print("  [WARNING] Account is FROZEN — most operations unavailable.")
        print()
        print("  [1] View account details")
        print("  [2] Add / Deduct balance")
        print("  [3] Transfer")
        print("  [4] Manage vault")
        print("  [5] Payback credit card")
        print("  [6] Last 10 transactions")
        print("  [7] Generate PDF statement")
        print("  [8] Logout")
        _divider()

        ch = prompt_menu_choice("  Select: ", {"1","2","3","4","5","6","7","8"})

        if   ch == "1": _cust_view(conn, acc_num)
        elif ch == "2": _cust_add_deduct(conn, acc_num, logs)
        elif ch == "3": _cust_transfer(conn, acc_num, logs)
        elif ch == "4": _cust_vault(conn, acc_num, logs)
        elif ch == "5": _cust_payback(conn, acc_num, logs)
        elif ch == "6": _cust_transactions(conn, acc_num, logs)
        elif ch == "7": _cust_pdf(conn, acc_num, logs)
        elif ch == "8":
            print("  Logged out.")
            return


# ── Customer sub-menus ────────────────────────────────────────────────────────

def _cust_view(conn, acc_num: int) -> None:
    """Option 1 — Display full account info with dual-currency balances."""
    row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,)).fetchone()
    _divider("Account Details")
    _display_account_row(row, dual=True)
    _divider()


def _cust_add_deduct(conn, acc_num: int, logs: Logs) -> None:
    """Option 2 — Add or deduct balance with optional currency conversion."""
    row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,)).fetchone()
    if row["is_frozen"]:
        print("  [!] Account is frozen. Operation not allowed.")
        return

    _divider("Add / Deduct Balance")
    print("  [1] Add balance")
    print("  [2] Deduct balance")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","0"})
    if sub == "0":
        return

    native_currency = row["currency"]
    print(f"  Account currency: {native_currency}")
    input_currency  = prompt_currency("  Enter amount in currency (BDT/USD): ")
    raw_amt         = prompt_amount_minor(f"  Amount ({input_currency}): ")
    amount_native   = convert_minor(raw_amt, input_currency, native_currency)

    if sub == "1":
        conn.execute(
            "UPDATE accounts SET acc_balance=acc_balance+? WHERE acc_num=?",
            (amount_native, acc_num),
        )
        conn.commit()
        new_bal = conn.execute(
            "SELECT acc_balance FROM accounts WHERE acc_num=?", (acc_num,)
        ).fetchone()["acc_balance"]
        log_transaction(conn, logs.tx, acc_num, "add", amount_native,
                        native_currency, "other", "success", new_bal)
        print(f"  [OK] Deposited {format_money(amount_native, native_currency)}. "
              f"New balance: {format_money_dual(new_bal, native_currency)}")

    elif sub == "2":
        cat = prompt_category()
        if row["acc_balance"] < amount_native:
            log_transaction(conn, logs.tx, acc_num, "deduct", amount_native,
                            native_currency, cat, "failed", row["acc_balance"])
            print(f"  [!] Insufficient balance. "
                  f"Available: {format_money_dual(row['acc_balance'], native_currency)}")
            return
        conn.execute(
            "UPDATE accounts SET acc_balance=acc_balance-? WHERE acc_num=?",
            (amount_native, acc_num),
        )
        conn.commit()
        new_bal = conn.execute(
            "SELECT acc_balance FROM accounts WHERE acc_num=?", (acc_num,)
        ).fetchone()["acc_balance"]
        log_transaction(conn, logs.tx, acc_num, "deduct", amount_native,
                        native_currency, cat, "success", new_bal)
        print(f"  [OK] Deducted {format_money(amount_native, native_currency)}. "
              f"New balance: {format_money_dual(new_bal, native_currency)}")
        if new_bal <= 50_000:
            print(f"  [WARNING] Low balance: {format_money_dual(new_bal, native_currency)}")


def _cust_transfer(conn, acc_num: int, logs: Logs) -> None:
    """Option 3 — Transfer: 1-to-1, 1-to-many, many-to-1."""
    row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,)).fetchone()
    if row["is_frozen"]:
        print("  [!] Account is frozen.")
        return

    _divider("Transfer")
    print("  [1] Transfer 1 to 1")
    print("  [2] Transfer 1 to many")
    print("  [3] Transfer many to 1  (you are one of the senders)")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","3","0"})
    if sub == "0":
        return

    native_currency = row["currency"]
    spent_today     = get_outbound_today(conn, acc_num, logs.tx)
    limit           = row["daily_transfer_limit"]
    remaining_limit = max(0, limit - spent_today)
    print(
        f"  Daily limit: {format_money_dual(limit, native_currency)}"
        f"  |  Used today: {format_money(spent_today, native_currency)}"
        f"  |  Remaining: {format_money_dual(remaining_limit, native_currency)}"
    )

    if sub == "1":
        receiver   = prompt_positive_int("  Receiver account number: ")
        amount     = prompt_amount_minor("  Amount (major units): ")
        via_credit = _ask_via_credit(row)
        cat        = prompt_category()
        print(f"  {transfer(conn, logs.tx, acc_num, receiver, amount, cat, via_credit, pending_conn=logs.pending)}")

    elif sub == "2":
        n          = prompt_positive_int("  Number of receivers: ")
        receivers  = [prompt_positive_int(f"  Receiver {i} account number: ")
                      for i in range(1, n + 1)]
        amount     = prompt_amount_minor("  Amount per receiver (major units): ")
        via_credit = _ask_via_credit(row)
        cat        = prompt_category()
        for r in transfer_1tomany(conn, logs.tx, acc_num, receivers,
                                   amount, cat, via_credit,
                                   pending_conn=logs.pending):
            print(f"  {r}")

    elif sub == "3":
        print(f"  You (Acc {acc_num}) are one of the senders.")
        n       = prompt_positive_int("  How many total senders (including you)? ")
        senders = [acc_num] + [
            prompt_positive_int(f"  Sender {i} account number: ")
            for i in range(2, n + 1)
        ]
        receiver   = prompt_positive_int("  Receiver account number: ")
        amount     = prompt_amount_minor("  Amount per sender (major units): ")
        via_credit = _ask_via_credit(row)
        cat        = prompt_category()
        for r in transfer_manyto1(conn, logs.tx, senders, receiver,
                                   amount, cat, via_credit,
                                   pending_conn=logs.pending):
            print(f"  {r}")


def _ask_via_credit(row) -> bool:
    """Ask if sender wants to pay via credit card (CC accounts only)."""
    if row["acc_type"] == "credit_card":
        return prompt_yes_no("  Pay via credit card? [yes/no]: ")
    return False


def _cust_vault(conn, acc_num: int, logs: Logs) -> None:
    """Option 4 — Vault: add / withdraw with 3-attempt password gate."""
    row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,)).fetchone()
    if row["is_frozen"]:
        print("  [!] Account is frozen.")
        return
    if not row["vault_no"]:
        print("  [!] No vault attached to this account.")
        return

    currency      = row["currency"]
    vault_balance = row["vault_balance"]
    _divider("Vault Management")
    print(f"  Vault: {row['vault_no']}  |  Balance: {format_money_dual(vault_balance, currency)}")
    print()
    print("  [1] Add money to vault")
    print("  [2] Withdraw from vault")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","0"})
    if sub == "0":
        return

    # vault password — 3 attempts
    vpw_ok = False
    vpw    = ""
    for attempt in range(1, VAULT_MAX_TRIES + 1):
        vpw = _input(f"  Vault password (attempt {attempt}/{VAULT_MAX_TRIES}): ")
        if row["vault_password_hash"] == hash_password(vpw):
            vpw_ok = True
            break
        remaining = VAULT_MAX_TRIES - attempt
        if remaining:
            print(f"  [!] Wrong password. {remaining} attempt(s) left.")
        else:
            print("  [!] Too many wrong attempts. Operation cancelled.")
    if not vpw_ok:
        return

    if sub == "1":
        _divider("Add to Vault")
        print("  [1] From account balance")
        if row["acc_type"] == "credit_card":
            print("  [2] From credit card")
        source      = prompt_menu_choice(
            "  Source: ",
            {"1","2"} if row["acc_type"] == "credit_card" else {"1"},
        )
        amount      = prompt_amount_minor("  Amount (major units): ")
        from_credit = (source == "2")
        print(f"  {vault_add(conn, logs.tx, acc_num, amount, vpw, from_credit=from_credit)}")

    elif sub == "2":
        _divider("Withdraw from Vault")
        print("  [1] To account balance")
        if row["acc_type"] == "credit_card":
            print("  [2] Pay back credit card")
        dest      = prompt_menu_choice(
            "  Destination: ",
            {"1","2"} if row["acc_type"] == "credit_card" else {"1"},
        )
        amount    = prompt_amount_minor("  Amount (major units): ")
        to_credit = (dest == "2")
        print(f"  {vault_deduct(conn, logs.tx, acc_num, amount, vpw, to_credit_payback=to_credit)}")


def _cust_payback(conn, acc_num: int, logs: Logs) -> None:
    """Option 5 — Pay back credit card via account balance or instant cash."""
    row = conn.execute("SELECT * FROM accounts WHERE acc_num=?", (acc_num,)).fetchone()
    if row["acc_type"] != "credit_card":
        print("  [!] This account has no credit card.")
        return
    if row["is_frozen"]:
        print("  [!] Account is frozen.")
        return

    currency = row["currency"]
    _divider("Credit Card Payback")
    print(f"  Credit used     : {format_money_dual(row['credit_used'], currency)}")
    print(f"  Credit limit    : {format_money_dual(row['credit_card_limit'], currency)}")
    print(f"  Credit available: {format_money_dual(row['credit_card_limit'] - row['credit_used'], currency)}")
    if row["credit_used"] == 0:
        print("  [!] No outstanding credit balance.")
        return

    print()
    print("  [1] Pay via account balance")
    print("  [2] Pay via instant cash (external payment)")
    print("  [0] Back")
    sub = prompt_menu_choice("  Choose: ", {"1","2","0"})
    if sub == "0":
        return

    amount = prompt_amount_minor("  Payback amount (major units): ")
    cc_pin = prompt_pin("  Credit card PIN: ")
    print(f"  {payback_credit(conn, logs.tx, acc_num, amount, from_balance=(sub == '1'), cc_pin=cc_pin)}")


def _cust_transactions(conn, acc_num: int, logs: Logs) -> None:
    """Option 6 — Last 10 transactions."""
    _divider("Last 10 Transactions")
    rows = recent_transactions(conn, acc_num, 10, tx_log_conn=logs.tx)
    if not rows:
        print("  No transactions yet.")
        return
    for row in rows:
        _display_transaction_row(row)
    _divider()


def _cust_pdf(conn, acc_num: int, logs: Logs) -> None:
    """Option 7 — Generate PDF statement."""
    _divider("Generate PDF Statement")
    print(f"  {generate_pdf_statement(conn, acc_num, tx_log_conn=logs.tx)}")


# ─────────────────────────────────────────────────────────────────────────────
#  Auth helper
# ─────────────────────────────────────────────────────────────────────────────

def _check_account_password(conn, acc_num: int, password: str) -> tuple:
    """Verify account password without touching the failed-login counter."""
    row = conn.execute(
        "SELECT acc_password_hash FROM accounts WHERE acc_num=?", (acc_num,)
    ).fetchone()
    if not row:
        return False, "Account not found."
    if row["acc_password_hash"] == hash_password(password):
        return True, "OK"
    return False, "Wrong password."


# ─────────────────────────────────────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    conn, logs = _start_session()
    seed_sample_data(conn)

    while True:
        _divider("BankOS — Login")
        print("  [1] Admin login")
        print("  [2] Customer login")
        print("  [3] Exit")
        _divider()
        ch = prompt_menu_choice("  Select: ", {"1","2","3"})

        if ch == "3":
            conn.close()
            logs.acc.close()
            logs.tx.close()
            logs.freeze.close()
            logs.pending.close()
            print("  Goodbye.")
            return
        elif ch == "1":
            pwd = _input("  Admin password: ")
            if check_admin_password(pwd):
                admin_portal(conn, logs)
            else:
                print("  [!] Invalid admin password.")
        elif ch == "2":
            acc = prompt_positive_int("  Account number: ")
            pwd = _input("  Password: ")
            ok, msg = authenticate_customer(conn, acc, pwd)
            print(f"  {msg}")
            if ok:
                customer_portal(conn, acc, logs)


if __name__ == "__main__":
    main()