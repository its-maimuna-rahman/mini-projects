# 🏦 BankOS v2 — Upgraded Bank Management System

A Python console application for managing bank accounts, credit cards, vaults, and transactions.  
Upgraded from basic CSV to **SQLite (primary) + CSV logs + on-demand XLSX export**, with multi-currency (BDT/USD), split Admin/Customer portals, SHA-256 password hashing, login lockout, daily transfer limits, spending categories, simulation, PDF statements, and pending-transfer approval workflow.

---

## 📁 Project Structure

```
bank_system/
├── oop_account_cls.py      # All OOP class definitions (~3-line change from original)
├── utils.py                # All helpers — SQLite load/save, hashing, lockout, PDF, currency, export
├── main.py                 # Single entry point — login screen + Admin & Customer portals
├── bank.db                 # Auto-created SQLite database (main storage)
├── account_log.csv         # Live append-only log — easy Excel viewing
├── transaction_log.csv     # Live append-only log — easy Excel viewing
└── statements/             # Generated PDF statements
```

> **Note:** `accounts.xlsx` is not kept live. XLSX is generated on-demand via the Export menu only.

---

**Why not live XLSX mirroring?**  
XLSX is a complex binary format. Every write requires loading, modifying, and rewriting the entire file via `openpyxl`. For frequent transaction writes this is slow and risks corruption on interrupted writes. XLSX is best treated as a presentation layer — generated once when you need it, not maintained alongside the DB.

---

## 🛠️ Requirements

| Requirement | Notes |
|---|---|
| Python | 3.10 or higher |
| `tabulate` | `pip install tabulate` — pretty CLI tables |
| `fpdf2` | `pip install fpdf2` — PDF statement generation |
| `openpyxl` | `pip install openpyxl` — XLSX export (on-demand only) |
| `sqlite3` | Built into Python standard library |
| `hashlib` | Built into Python standard library — SHA-256 hashing |

```bash
pip install tabulate fpdf2 openpyxl
```

---

## 🚀 How to Run

```bash
python3 main.py
```
## VALID INPUT
utils_validinput.py
Centralised, reusable input-validation helpers for BankOS v2.

Design principles
─────────────────
• Every public function either *returns* a clean value or *raises* ValueError
  with a human-readable message — callers decide whether to loop or abort.
• Functions that prompt the user in a loop are prefixed `prompt_`.
• Pure validators (no I/O) are prefixed `validate_`.
• All prompting helpers accept an optional `prompt` kwarg so callers can
  customise the displayed text without duplicating validation logic.

Covered domains
───────────────
  Amounts        – positive monetary amounts (major → minor units)
  Integers       – generic whole numbers, positive integers
  Yes / No       – boolean confirmations
  Currency       – BDT / USD selection
  Account type   – credit_card / non_credit_card
  Category       – transaction category enum
  Menu choice    – arbitrary sets of valid string options
  Filter key     – account-list filter names (from FILTER_WHERE)
  Account number – positive integer with optional DB existence check
  Passwords      – non-empty, with optional minimum-length rule
  Vault number   – non-empty string, format hint (e.g. "001")
  Filenames      – non-empty, optional suffix enforcement
  PIN            – numeric string of exact length


### First-Run Setup

On first run (or if files are missing), the program asks for storage setup:
| option | description |
|---|---|
|[1] Import database | asks for filename, db will be imported and will work directly
|[3] Start fresh database | empty db created, will ask for the db name |
|[4] Exit program |

then the progam will ask : do you want to import any csv/xlsx file in the database?

if no, then continue.
if yes, how many files you want to import? -> gives integer number
enter name and import csv/xlsx file in the existing db -> insert all the data in the db
if csv/xlsx input fails -> csv file upload failed-> do you want to retry (the csv/xlsx file count will stuck)? (if yes : again ask for csv name, if no : continue, (the count will increase)).
CSV import → add one sentence: "Duplicates / invalid rows skipped with warning"
```
SAME PROCESS WILL REPEAT FOR `account_log` `transaction_log` AND `freezing_account`. (first ask for db, then import csv/xlsx if needed)
```
** n.b. : db files will not sync with csv and xlsx, all edits will be shown in db, it is not changeable outside if the program.


> This is asked **once only** on first run. After setup, storage behaviour is fixed: SQLite for all databases , CSV for csv files, XLSX report on-demand.

```
so basically you input a db or start a fresh db (automatically created), then if you have existing data in csv/xlsx, you import those files and enter all the data into the db
```

```
=== BANK MANAGEMENT SYSTEM ===
 [1] Import existing database
 [2] Start fresh database 
[3] Exit 

Import CSV/XLSX files into DB? [yes/no]: 

--- Log Table Setup --- 
Account log setup:
 [1] Import existing database 
 [2] Start fresh (no import)
 [3] Exit

Import CSV/XLSX files into DB? [yes/no]:

 
Transaction log setup:
 [1] Import existing database 
 [2] Start fresh (no import)
 [3] Exit

Import CSV/XLSX files into DB? [yes/no]:

Account Freeze data setup:
 [1] Import existing database 
 [2] Start fresh (no import)
 [3] Exit

Import CSV/XLSX files into DB? [yes/no]:


every time "Import CSV/XLSX files into DB? [yes/no]:" is yes then 
# above part as many times as many files to import and will take valid imput for file type
How many files to import? :
File format:    
    [1] CSV  (.csv)
    [2] XLSX (.xlsx)
    Choose [1/2]: 

# if csv file
Enter .csv file name :
# if xlsx file
Enter .xlsx file name:

# then the csv or xlsx or both type files' data will be input in the databases according to their respective databases.

```

### Login Screen

| Login Type | What to Enter | Result |
|---|---|---|
| Admin | Admin password (default: `bankadmin123`) | Admin Menu (9 options) |
| Customer | Account number → then account password | Customer Menu (9 options) or lockout message |

---

## ✨ Features

| Feature | Details |
|---|---|
| Storage | SQLite (`bank.db`) — faster, atomic, no corruption risk |
| Logs | CSV append-only — `account_log.csv`, `transaction_log.csv` |
| XLSX Export | On-demand from Admin menu — full accounts snapshot |
| Auth Security | `hashlib` SHA-256 hashing — passwords, PINs, vault passwords |
| Login Safety | 3-strike lockout for 2 minutes, stored in DB |
| Currency | BDT + USD, auto-conversion at `1 USD = 120 BDT` |
| Interface | Separate Admin portal + Customer portal |
| Transfers | 1-to-1 / 1-to-many / many-to-1 + daily limits + pending approval flow |
| Spending Tracking | Category tag on every deduction |
| Reports | PDF account statement per account (saved to `/statements/`) |
| `credit_used` Persistence | Saved correctly in DB on every transaction |

---

## 🔐 Security & Hashing

### How `hashlib` is used

All passwords, PINs, and vault passwords are hashed before storage using Python's built-in `hashlib` — no extra library needed.

```python
import hashlib

def hash_password(plaintext: str) -> str:
    return hashlib.sha256(plaintext.encode()).hexdigest()
```

This function is called in `utils.py` whenever a new password/PIN/vault password is set. The returned hex string (64 characters) is what gets written to the DB — the original plaintext is never stored.

**Verification at login:**

```python
def check_password(self, input_pwd: str) -> bool:
    return self._acc_password_hash == hash_password(input_pwd)
```

The input is hashed on the fly and compared to the stored hash. The plaintext never leaves memory.

### Development Mode (plain-text debug columns)

During development, secrets are also stored in `_plain_debug` columns alongside the hash columns. These exist **only for developer convenience** — to recover forgotten test passwords without resetting the DB.

| Column | Used for |
|---|---|
| `acc_password_hash` | All authentication — always used |
| `acc_password_plain_debug` | Developer reference only — never used for auth |

> **Before publishing or handing in:** delete all `_plain_debug` columns (or set them to `NULL`) to achieve production-like behaviour.

### Other Security Protections

- `__str__` methods never expose passwords or PINs in any output
- Vault destruction and all fund transfers require re-authentication every time
- 3 failed login attempts → 2-minute lockout (`locked_until` timestamp stored in DB)
- Account freeze by admin blocks login and all inbound/outbound transactions
- Daily outbound transfer limit enforced per account per calendar day
- Large transfers above threshold are routed to `pending_transfers` for admin approval

> Suitable for educational use.

---

## 🗄️ Database Schema (`bank.db`)


### `accounts`

| Column | Type | Description |
|---|---|---|
| `acc_num` | INTEGER PRIMARY KEY | Unique account number |
| `acc_password_hash` | TEXT | SHA-256 hash of account password |
| `acc_password_plain_debug` | TEXT | Plain text — development only |
| `acc_balance` | INTEGER | Balance in smallest unit (paise/cents) |
| `currency` | TEXT | `"BDT"` or `"USD"` |
| `acc_type` | TEXT | `"credit_card"` or `"non_credit_card"` |
| `credit_card_num` | TEXT | NULL if non-CC |
| `credit_card_pin_hash` | TEXT | SHA-256 hash of PIN; NULL if non-CC |
| `credit_card_pin_plain_debug` | TEXT | Plain text PIN — development only |
| `credit_card_limit` | INTEGER | Max credit in smallest unit; NULL if non-CC |
| `credit_used` | INTEGER | Running credit charged (smallest unit) |
| `vault_no` | TEXT | Vault ID (e.g. `V001`); NULL if no vault |
| `vault_password_hash` | TEXT | SHA-256 hash; NULL if no vault |
| `vault_password_plain_debug` | TEXT | Plain text vault password — development only |
| `vault_balance` | INTEGER | Vault balance in smallest unit |
| `is_frozen` | INTEGER | `0` = active, `1` = frozen |
| `daily_transfer_limit` | INTEGER | Max outbound transfer per day (smallest unit) |
| `failed_login_attempts` | INTEGER | Resets to 0 on successful login |
| `locked_until` | TEXT | ISO timestamp or NULL |

### `account_log`

| Column | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM` |
| `acc_num` | Account number affected |
| `action` | `ACCOUNT_ADDED`, `VAULT_CREATED`, `CONVERT_TYPE`, `VAULT_DESTROYED`, `ACCOUNT_FROZEN`, `ACCOUNT_UNFROZEN`, `ACCOUNT_DELETED`, `LIMIT_CHANGED` |
| `details` | Human-readable description of the change |

> Also mirrored live to `account_log.csv` (if synced).

### `transaction_log`

| Column | Description |
|---|---|
| `timestamp` | `YYYY-MM-DD HH:MM` |
| `acc_num` | Account number involved |
| `type` | `add`, `deduct`, `transfer_out`, `transfer_in`, `vault_add`, `vault_deduct`, `cc_payback_balance`, `cc_payback_cash`|
| `amount` | Amount in the account's native currency |
| `currency` | `"BDT"` or `"USD"` |
| `category` | `food`, `bills`, `shopping`, `transfer`, `other`|
| `status` | `success`, `failed`, `partial`, `pending` |
| `balance_after` | Account balance after the transaction |

> Also mirrored live to `transaction_log.csv` (if synced).

### `pending_transfers`

| Column | Description |
|---|---|
| `id` | Auto-increment primary key |
| `timestamp` | When the transfer was requested |
| `sender_acc_num` | Originating account |
| `receiver_acc_num` | Destination account (comma-separated for 1-to-many) |
| `amount` | Amount per receiver |
| `currency` | Transfer currency |
| `via_credit` | `1` if charged to CC, `0` if from balance |
| `status` | `pending`, `approved`, `rejected` |
| `reviewed_at` | Timestamp when admin acted; NULL if still pending |

---

## 🏗️ Class Architecture (`oop_account_cls.py`)

Only ~3 lines changed from the original — a `currency` attribute on `Account` and a `credit_used` parameter on `CreditCard`.

### `Lock`
Holds a hashed vault password. Attached to every `Vault` instance.

### `Vault`

| Attribute / Method | Description |
|---|---|
| `_vault_no` | Unique vault identifier (e.g. `001`) |
| `_balance` | Current vault balance in parent account's currency |
| `lock` | `Lock` instance with hashed vault password |

### `Account`

| Attribute | Description |
|---|---|
| `_acc_num` | Primary key |
| `_acc_password_hash` | SHA-256 hash — never plaintext |
| `_acc_balance` | Balance in smallest unit |
| `currency` | `"BDT"` or `"USD"` *(new in v2)* |
| `_vault` | `Vault` instance or `None` |
| `is_frozen` | Boolean freeze flag |
| `daily_transfer_limit` | In smallest unit |
| `failed_login_attempts` | Counter |
| `locked_until` | Datetime or `None` |

```python
def check_password(self, input_pwd: str) -> bool:
    return self._acc_password_hash == hash_password(input_pwd)
```

### `CreditCard(Account)`

| Attribute | Description |
|---|---|
| `_credit_card_num` | Card number |
| `_credit_card_pin_hash` | SHA-256 hash of PIN |
| `_credit_card_limit` | Credit limit in smallest unit |
| `credit_used` | Running credit charged *(persists in DB in v2)* |

---

## 🛠️ `utils.py` — Helper Reference

| Function | Description |
|---|---|
| `init_db()` | Creates `bank.db` and all tables if missing |
| `hash_password(pwd)` | Returns `hashlib.sha256(pwd.encode()).hexdigest()` |
| `load_accounts()` | Reads `accounts` table; returns list of `Account`/`CreditCard` objects with `Vault` attached |
| `save_account(acc)` | Upserts a single account row (`INSERT OR REPLACE`) |
| `delete_account(acc_num)` | Deletes account row by primary key |
| `log_account_action(acc_num, action, details)` | Appends to `account_log` table AND `account_log.csv` |
| `log_transaction(...)` | Appends to `transaction_log` table AND `transaction_log.csv` |
| `export_accounts_xlsx()` | Writes full accounts snapshot to `accounts.xlsx` (on-demand only) |
| `check_lockout(acc_num)` | Returns `True` if account is currently locked |
| `increment_failed_login(acc_num)` | Increments counter; sets `locked_until` at count = 3 |
| `reset_failed_login(acc_num)` | Resets counter and clears `locked_until` |
| `get_daily_transfer_total(acc_num)` | Sums today's `transfer_out` amounts for the account |
| `convert_currency(amount, from_cur, to_cur)` | Converts between BDT and USD using fixed rate |
| `display_dual(amount, currency)` | Returns `"৳12,000.00 (≈ $100.00)"` formatted string |
| `generate_pdf_statement(acc_num)` | Creates PDF with `fpdf2`; saves to `/statements/` |
| `get_pending_transfers()` | Returns all `status = pending` rows from `pending_transfers` |
| `approve_transfer(transfer_id)` | Executes transfer; sets `status = approved` |
| `reject_transfer(transfer_id)` | Cancels transfer, reverses CC charge if applicable; sets `status = rejected` |

---

## 💱 Multi-Currency System

BankOS v2 supports BDT (৳) and USD ($). The fixed rate `1 USD = 120 BDT` is defined as a constant in `utils.py`.

| Scenario | Behaviour |
|---|---|
| Account creation | Admin chooses BDT or USD; all balances stored in native currency |
| Display | Every balance shown as native amount + converted equivalent |
| Same-currency transfers | No conversion needed |
| Cross-currency transfers | Auto-converted using fixed rate; both log entries record native currency |
| Vault | Always matches parent account's currency |


---

## ✅ Input Validation

| Situation | Behaviour |
|---|---|
| String where int/float expected | Reprompts with error message |
| Negative number | Reprompts with error message |
| Invalid menu choice | Reprompts with error message |
| Uppercase yes/no | Accepted and lowercased |
| Duplicate `acc_num` / `credit_card_num` / `vault_num` | Rejected; user prompted again |
| Wrong password / PIN (customer login) | Increments `failed_login_attempts`; locks at 3 (for 2 min; short time as educational project) |
| Wrong vault password | gives 3 attempts, then cancels the transfer |
| Transfer exceeding daily limit | Blocked; remaining limit shown |
| Transfer above pending threshold | Routed to `pending_transfers`; customer notified |
| Category input | Must be one of: `food`, `bills`, `shopping`, `transfer`, `other` |

---

## 🗺️ Project Build Outline

### Phase 1 — Foundation (`utils.py` + DB)
- Create `utils.py` with `init_db()` — all four `CREATE TABLE IF NOT EXISTS` statements
- Implement `hash_password(pwd)` using `hashlib.sha256`
- Implement `load_accounts()` — query DB, reconstruct OOP objects with `Vault` attached
- Implement `save_account()` and `delete_account()`
- Implement `log_account_action()` and `log_transaction()` — write to DB and mirror to CSV
- Smoke-test: verify DB creation and round-trip save/load

### Phase 2 — OOP Layer Update (`oop_account_cls.py`)
- Add `currency` parameter to `Account.__init__` (default `"BDT"`)
- Add `credit_used` parameter to `CreditCard.__init__` — load from DB instead of defaulting to 0
- Update `check_password()` and `check_cc_pin()` to compare hashed values using `hash_password()`
- Verify `Payment_Processor` methods still work — no logic change needed

### Phase 3 — Security Layer (`utils.py`)
- Implement `check_lockout()` — compare `locked_until` against `datetime.now()`
- Implement `increment_failed_login()` — update counter, set `locked_until` at count = 3
- Implement `reset_failed_login()`
- Implement `get_daily_transfer_total()` — `SUM` today's `transfer_out` from `transaction_log`
- Add `PENDING_THRESHOLD` a dict; implement `create_pending_transfer()`, `get_pending_transfers()`, `approve_transfer()`, `reject_transfer()` (a transfer will be pending for admin's approval if the amount of money is greater than or equal to 1000 USD / 120000 bdt)
- make PENDING_THRESHOLD a dict:
PENDING_THRESHOLD = {"USD": 1000, "BDT": 120000}
and compare against transfer amount after converting to sender's currency.

### Phase 4 — Currency System (`utils.py`)
- Define `EXCHANGE_RATE = 120` as a module-level constant
- Implement `convert_currency(amount, from_cur, to_cur)`
- Implement `display_dual(amount, currency)`
- Update `Payment_Processor` transfer methods to call `convert_currency` when currencies differ

### Phase 5 — Admin Portal (`main.py`)
- Build login screen: read input, branch to admin or customer
- Option 1 — Account CRUD: add (currency, type, optional vault), delete, convert type (like previous version of the projejct)
- Option 2 — Vault CRUD: create vault, destroy vault with fund transfer auth flow (like previous version of the projejct)
- Option 3 — Show All Accounts: filter + currency display toggle (like previous version of the projejct + currency display toggle)
- Option 4 — Logs: account log and transaction log with filter options  (like previous version of the projejct)
- Option 5 — Bank Overview: pool totals, frozen count, pending count
- Option 6 — Freeze / Unfreeze: toggle `is_frozen`, log action
- Option 7 — Pending Transfer Approval: list, approve, or reject
- Option 8 — Generate PDF: call `generate_pdf_statement(acc_num)` (will show both currency)
- Option 9 — Export to XLSX/csv -> then asks whether xlsx or csv -> call `export_accounts_xlsx()` / call `export_accounts_csv()` — on-demand snapshot (have options in the submenu for `all_account`, `credit_card_account`, `non_credit_card_account`, `vault_account`, `non_vault_account`, `usd_accounts`, `bdt_accounts`) 

### Phase 6 — Customer Portal (`main.py`)
- Customer login: check freeze → check lockout → verify password → reset or increment counter
- Option 1 — View Account: display all info using `display_dual()`
- Option 2 — Add / Deduct Balance: currency picker, category required, conversion applied
- Option 3 — Transfer: enforce daily limit; route to pending if above threshold
- Option 4 — Manage Vault: add/deduct with vault password auth
- Option 5 — Payback Credit Card: via balance or instant cash; CC PIN required
- Option 6 — Last 10 Transactions: `SELECT ... ORDER BY timestamp DESC LIMIT 10`
- Option 7 — Generate PDF Statement: call `generate_pdf_statement(acc_num)` (will specify currency, will show native + converted balance)
- Option 8 — Logout: clear session, return to login screen

### Phase 7 — PDF Generation (`utils.py`)
- Implement `generate_pdf_statement(acc_num)` using `fpdf2`
- Build PDF: header (bank name, account number, date), account summary table, full transaction table
- PDF save → add default path + "use default? [yes/no]" prompt
- if user chooses default,
`default_path = f"statements/statement_{acc.acc_num}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"`
- Test with a CC account and a non-CC account

### Phase 8 — Testing & Hardening
- End-to-end: create BDT and USD accounts, cross-currency transfers, verify log entries
- Test lockout: fail 3 times, verify lock, verify unlock after timeout
- Test daily transfer limit: exhaust limit, verify block, verify next-day reset
- Test pending transfer: exceed threshold, approve as admin, verify funds moved
- Test freeze: freeze account, verify customer login rejected
- Test vault destruction with funds: verify auth flow before deletion
- Verify `account_log.csv` and `transaction_log.csv` stay in sync with DB
- Test XLSX export: verify snapshot matches current DB state
- Fresh-machine test: only Python 3.10+, `tabulate`, `fpdf2`, `openpyxl` — verify first-run DB creation

---

## 🔒 Security Notes

- All passwords, PINs, and vault passwords are stored as SHA-256 hashes via `hashlib` — plaintext never touches disk
- `__str__` methods never expose passwords or PINs in any output
- Vault destruction and all fund transfers require re-authentication every time
