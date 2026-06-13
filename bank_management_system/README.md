# 🏦 BankOS — Bank Management System

A Python console application for managing bank accounts, credit cards, vaults, and transactions. Upgraded from basic CSV to **SQLite + CSV logs + on-demand XLSX export**, with multi-currency (BDT/USD), split Admin/Customer portals, SHA-256 password hashing, login lockout, daily transfer limits, spending categories, PDF statements, and a pending-transfer approval workflow.

---

## 📁 Project Structure

```
bank_system/
├── main.py                 # Entry point — login screen + Admin & Customer portals
├── account_cls.py          # OOP class definitions (Account, CreditCard, Vault, Lock)
├── utils.py                # Helpers — SQLite, hashing, lockout, PDF, currency, export
├── utils_validinput.py     # Centralised input-validation helpers
├── bank.db                 # Auto-created SQLite database (primary storage)
├── account_log.csv         # Append-only account action log
├── transaction_log.csv     # Append-only transaction log
└── statements/             # Generated PDF statements
```

---

## 🛠️ Requirements

| Package | Purpose | Install |
|---|---|---|
| Python 3.10+ | Runtime | — |
| `tabulate` | Pretty CLI tables | `pip install tabulate` |
| `fpdf2` | PDF statement generation | `pip install fpdf2` |
| `openpyxl` | On-demand XLSX export | `pip install openpyxl` |
| `sqlite3` | Primary database | Built-in |
| `hashlib` | SHA-256 hashing | Built-in |

```bash
pip install tabulate fpdf2 openpyxl
```
For Ubuntu/Debian :
```
sudo apt update && sudo apt install -y python3-tabulate python3-fpdf python3-openpyxl
```
or
```
sudo apt install python3-tabulate
sudo apt install python3-fpdf
sudo apt install python3-openpyxl
```

---

## 🚀 Running the Program

```bash
python3 main.py
```

### First-Run Setup

On first run (or if DB is missing), a setup wizard runs for each storage component (`bank.db`, `account_log`, `transaction_log`, `pending_transfers`, `freezing_accounts`):

```
=== BANK MANAGEMENT SYSTEM ===
 [1] Import existing database
 [2] Start fresh database
 [3] Exit

Import CSV/XLSX files into DB? [yes/no]:
  How many files to import?: 
  File format:
    [1] CSV  (.csv)
    [2] XLSX (.xlsx)
    Choose [1/2]:
  Enter filename:
```

- Each component goes through the same flow: `import existing DB **or** start fresh DB`, then optionally import `CSV/XLSX` data into it.
- If a file import fails, the program asks to retry (the file counter holds until confirmed or skipped).
- Duplicates and invalid rows are skipped with a warning.
- **Setup runs once.** After that, SQLite handles all data; CSV/XLSX files are not synced back — edits must go through the program.

### Login Screen

| Login Type | Input | Result |
|---|---|---|
| Admin | Admin password (default: `bankadmin123`) | Admin Menu (9 options) |
| Customer | Account number → account password | Customer Menu or lockout message |

---

## ✨ Features

| Feature | Details |
|---|---|
| **Storage** | SQLite (`bank.db`) — atomic, no corruption risk |
| **Logs** | CSV append-only — `account_log.csv`, `transaction_log.csv` |
| **XLSX/CSV Export** | On-demand snapshot with filter options (all, credit card, vault, BDT/USD, etc.) |
| **Auth** | SHA-256 hashing for all passwords, PINs, and vault passwords |
| **Lockout** | 3 failed logins → 2-minute lockout (stored in DB) |
| **Currency** | BDT (৳) + USD ($), auto-converted at `1 USD = 120 BDT`; all balances shown as native + equivalent |
| **Transfers** | 1-to-1, 1-to-many, many-to-1; daily outbound limit enforced per account per calendar day |
| **Pending Approval** | Transfers ≥ `{"USD": 1000, "BDT": 120_000}` are held for admin approval |
| **Spending Categories** | Every deduction tagged: `food`, `bills`, `shopping`, `transfer`, `other` |
| **PDF Statements** | Generated per account via `fpdf2`; saved to `/statements/` |
| **Freeze** | Admin can freeze/unfreeze accounts; frozen accounts block all login and transactions |
| **Credit Cards** | Credit limit, `credit_used` persistence, PIN-authenticated payback (balance or instant cash) |
| **Vaults** | Sub-wallet per account; password-protected; fund transfer required before destruction |

---

## 🔐 Security

All passwords, PINs, and vault passwords are hashed with `hashlib.sha256` — plaintext never touches disk.

Additional protections:
- `__str__` never exposes passwords or PINs
- Vault destruction and all fund transfers require re-authentication every time
- Account freeze blocks login and all transactions (admin only)
- Daily transfer limit enforced per calendar day; remaining limit shown on block

> **Dev note:** `_plain_debug` columns exist alongside hash columns for developer convenience during testing. Remove or `NULL` them before production/submission.

---

## 🗄️ Database Schema (`bank.db`)

### `accounts`

| Column | Type | Notes |
|---|---|---|
| `acc_num` | INTEGER PK | Unique account number |
| `acc_password_hash` | TEXT | SHA-256 hash |
| `acc_balance` | INTEGER | Smallest unit (paise / cents) |
| `currency` | TEXT | `"BDT"` or `"USD"` |
| `acc_type` | TEXT | `"credit_card"` / `"non_credit_card"` |
| `credit_card_num` | TEXT | NULL if non-CC |
| `credit_card_pin_hash` | TEXT | SHA-256 hash; NULL if non-CC |
| `credit_card_limit` | INTEGER | NULL if non-CC |
| `credit_used` | INTEGER | Running credit charged |
| `vault_no` | TEXT | NULL if no vault |
| `vault_password_hash` | TEXT | NULL if no vault |
| `vault_balance` | INTEGER | Smallest unit |
| `is_frozen` | INTEGER | `0` = active, `1` = frozen |
| `daily_transfer_limit` | INTEGER | Max outbound per calendar day |
| `failed_login_attempts` | INTEGER | Resets on successful login |
| `locked_until` | TEXT | ISO timestamp or NULL |

### `account_log`

| Column | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM` |
| `acc_num` | Affected account |
| `action` | `ACCOUNT_ADDED`, `VAULT_CREATED`, `CONVERT_TYPE`, `VAULT_DESTROYED`, `ACCOUNT_FROZEN`, `ACCOUNT_UNFROZEN`, `ACCOUNT_DELETED`, `LIMIT_CHANGED` |
| `details` | Human-readable description |

### `transaction_log`

| Column | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM` |
| `acc_num` | Account involved |
| `type` | `add`, `deduct`, `transfer_out`, `transfer_in`, `vault_add`, `vault_deduct`, `cc_payback_balance`, `cc_payback_cash` |
| `amount` | In account's native currency |
| `currency` | `"BDT"` or `"USD"` |
| `category` | `food`, `bills`, `shopping`, `transfer`, `other` |
| `status` | `success`, `failed`, `partial`, `pending` |
| `balance_after` | Balance post-transaction |

### `pending_transfers`

| Column | Description |
|---|---|
| `id` | Auto-increment PK |
| `timestamp` | When transfer was requested |
| `sender_acc_num` | Originating account |
| `receiver_acc_num` | Destination (comma-separated for 1-to-many) |
| `amount` | Amount per receiver |
| `currency` | Transfer currency |
| `via_credit` | `1` = charged to CC, `0` = from balance |
| `status` | `pending`, `approved`, `rejected` |
| `reviewed_at` | Timestamp of admin action; NULL if pending |

---

## 🏗️ Class Architecture (`oop_account_cls.py`)

| Class | Key Attributes |
|---|---|
| `Lock` | `_hashed_password` — attached to every `Vault` |
| `Vault` | `_vault_no`, `_balance`, `lock: Lock` |
| `Account` | `_acc_num`, `_acc_password_hash`, `_acc_balance`, `currency`, `_vault`, `is_frozen`, `daily_transfer_limit`, `failed_login_attempts`, `locked_until` |
| `CreditCard(Account)` | + `_credit_card_num`, `_credit_card_pin_hash`, `_credit_card_limit`, `credit_used` |

---

## 💱 Multi-Currency System

Fixed rate: **`1 USD = 120 BDT`** (defined as `EXCHANGE_RATE = 120` in `utils.py`).

| Scenario | Behaviour |
|---|---|
| Account creation | Admin chooses BDT or USD; balances stored in native currency |
| Display | Always shown as native + converted equivalent |
| Same-currency transfer | No conversion |
| Cross-currency transfer | Auto-converted; both log entries record native currency |
| Vault | Always matches parent account's currency |

---

## ✅ Input Validation (`utils_validinput.py`)

Centralised reusable helpers. Functions prefixed `prompt_` loop until valid input; `validate_` are pure (no I/O). All raise `ValueError` with a human-readable message on bad input.

| Situation | Behaviour |
|---|---|
| Wrong type (str where int expected) | Reprompts with error |
| Negative amount | Reprompts with error |
| Invalid menu choice | Reprompts with error |
| `yes`/`no` (any case) | Accepted and normalised |
| Duplicate acc/card/vault number | Rejected; reprompted |
| Wrong password (customer login) | Increments `failed_login_attempts`; locks at 3 for 2 min |
| Wrong vault password | 3 attempts then cancels operation |
| Exceeds daily transfer limit | Blocked; remaining limit displayed |
| Transfer ≥ pending threshold | Routed to `pending_transfers`; customer notified |
| Invalid category | Must be: `food`, `bills`, `shopping`, `transfer`, `other` |

**Covered domains:** amounts, integers, yes/no, currency, account type, category, menu choice, filter key, account number (with optional DB existence check), passwords, vault number, filenames, PIN.

---

## 🗺️ Admin Portal (10 options)

| # | Option | Notes |
|---|---|---|
| 1 | Account CRUD | Add (currency + type + optional vault), delete, convert type |
| 2 | Vault CRUD | Create vault, destroy vault (with fund-transfer auth) |
| 3 | Show All Accounts | Filter + currency display toggle |
| 4 | Logs | Account log + transaction log with filter options |
| 5 | Bank Overview | Pool totals, frozen count, pending count |
| 6 | Freeze / Unfreeze | Toggles `is_frozen`, logs action |
| 7 | Pending Transfer Approval | List, approve, or reject pending transfers |
| 8 | Generate PDF Statement | Per account; shows native + converted balance |
| 9 | Export XLSX / CSV | Subfilters: all, credit card, non-CC, vault, non-vault, USD, BDT |
| 0 | Logout | Returns to login screen |

## 👤 Customer Portal (8 options)

| # | Option | Notes |
|---|---|---|
| 1 | View Account | All info via `display_dual()` |
| 2 | Add / Deduct Balance | Currency picker, category required, conversion applied |
| 3 | Transfer | Enforces daily limit; routes to pending if above threshold |
| 4 | Manage Vault | Add/deduct with vault password auth |
| 5 | Payback Credit Card | Via balance or instant cash; CC PIN required |
| 6 | Last 10 Transactions | `ORDER BY timestamp DESC LIMIT 10` |
| 7 | Generate PDF Statement | Native + converted balances; saved to `/statements/` |
| 8 | Logout | Returns to login screen |

---

## 🔒 Security Notes

- Plaintext passwords never touch disk — SHA-256 hash only
- Re-authentication required for every vault operation and fund transfer
- 3 failed logins → 2-minute lockout (educational project; short window intentional)
- Frozen accounts block all login and inbound/outbound transactions
- Large transfers held in `pending_transfers` until admin approves or rejects
