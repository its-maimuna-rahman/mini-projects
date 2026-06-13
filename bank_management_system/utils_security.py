"""
utils_security.py
Security helpers for BankOS: hashing, lockout, vault auth.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta

# ── constants ─────────────────────────────────────────────────────────────────

LOCKOUT_MINUTES = 2
MAX_ATTEMPTS    = 3
VAULT_MAX_TRIES = 3  # vault password attempts before cancellation


# ── hashing ───────────────────────────────────────────────────────────────────

def hash_password(plaintext: str) -> str:
    """
    Return the SHA-256 hex digest of plaintext.
    Used for all passwords, PINs, and vault passwords.
    The plaintext is never stored — only the returned hash is written to DB.
    """
    return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()


# ── timestamps ────────────────────────────────────────────────────────────────

def now_iso() -> str:
    """Current datetime as ISO 8601 string (seconds precision)."""
    return datetime.now().isoformat(timespec="seconds")


def now_display() -> str:
    """Current datetime formatted for log display: YYYY-MM-DD HH:MM."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def compute_lockout_until() -> str:
    """
    Return an ISO timestamp LOCKOUT_MINUTES from now.
    Stored in DB `locked_until` column on the 3rd failed login.
    """
    return (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat(timespec="seconds")


# ── lockout checks ────────────────────────────────────────────────────────────

def is_locked(locked_until: str | None) -> tuple[bool, int]:
    """
    Check whether a lockout timestamp is still active.

    Returns:
        (True, seconds_remaining)  — if still locked
        (False, 0)                 — if not locked or lock has expired
    """
    if not locked_until:
        return False, 0
    try:
        lock_dt   = datetime.fromisoformat(locked_until)
        remaining = int((lock_dt - datetime.now()).total_seconds())
        if remaining > 0:
            return True, remaining
    except ValueError:
        pass  # malformed timestamp — treat as unlocked
    return False, 0


def format_lockout_message(seconds: int) -> str:
    """Human-readable lockout message for the login screen."""
    minutes, secs = divmod(seconds, 60)
    if minutes > 0:
        return f"Account locked. Try again in {minutes}m {secs}s."
    return f"Account locked. Try again in {secs}s."


# ── vault password auth ───────────────────────────────────────────────────────

def verify_vault_password(
    stored_hash: str,
    prompt_fn,          # callable() -> str  (e.g. lambda: input("Vault password: "))
) -> bool:
    """
    Give the user VAULT_MAX_TRIES attempts to enter the correct vault password.
    Returns True on success, False if all attempts exhausted.

    Args:
        stored_hash: SHA-256 hash stored in DB.
        prompt_fn:   Zero-argument callable that returns the entered plaintext.
    """
    for attempt in range(1, VAULT_MAX_TRIES + 1):
        entered = prompt_fn()
        if hash_password(entered) == stored_hash:
            return True
        remaining = VAULT_MAX_TRIES - attempt
        if remaining > 0:
            print(f"[AUTH] Wrong vault password. {remaining} attempt(s) left.")
        else:
            print("[AUTH] Too many wrong vault password attempts. Operation cancelled.")
    return False


# ── admin password ────────────────────────────────────────────────────────────

ADMIN_PASSWORD_HASH: str = hash_password("bankadmin123")
"""
Hash of the default admin password.
To change: replace "bankadmin123" with the new password here,
or store the hash in a config/env file.
"""


def check_admin_password(plaintext: str) -> bool:
    """Verify admin login password."""
    return hash_password(plaintext) == ADMIN_PASSWORD_HASH
