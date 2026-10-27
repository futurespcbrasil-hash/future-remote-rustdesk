#!/usr/bin/env python3
"""Apply Future Remote identity and rendezvous settings to the pinned hbb_common source.

Strict replacements intentionally fail if upstream changes the expected declarations.
"""
from pathlib import Path
import re
import sys

CONFIG = Path("libs/hbb_common/src/config.rs")
APP_NAME = "Future Remote"
HOST = "future-remote.duckdns.org"
PUBLIC_KEY = "NgQBktnunnDC45ZaFZX9w1fixGsGD8Wb9J0WB94niB8="

def replace_one(pattern: str, replacement: str, source: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, source, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Expected exactly one declaration for {label}; found {count}. No file written.")
    return updated

def main() -> int:
    if not CONFIG.is_file():
        print(f"ERROR: {CONFIG} not found. Initialize submodules first.", file=sys.stderr)
        return 2
    original = CONFIG.read_text(encoding="utf-8")
    updated = replace_one(
        r'^\s*pub static ref APP_NAME: RwLock<String> = RwLock::new\("[^"]*"\.to_owned\(\)\);',
        f'    pub static ref APP_NAME: RwLock<String> = RwLock::new("{APP_NAME}".to_owned());',
        original, "APP_NAME",
    )
    updated = replace_one(
        r'^pub const RENDEZVOUS_SERVERS:\s*&\[&str\]\s*=\s*&\[[^\n]*\];',
        f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{HOST}"];',
        updated, "RENDEZVOUS_SERVERS",
    )
    updated = replace_one(
        r'^pub const RS_PUB_KEY:\s*&str\s*=\s*"[^"]*";',
        f'pub const RS_PUB_KEY: &str = "{PUBLIC_KEY}";',
        updated, "RS_PUB_KEY",
    )
    if updated == original:
        print("Future Remote app name and server configuration are already applied.")
    else:
        CONFIG.write_text(updated, encoding="utf-8")
        print("Applied Future Remote app name, rendezvous hostname and public key.")
    check = CONFIG.read_text(encoding="utf-8")
    required = [
        f'RwLock::new("{APP_NAME}".to_owned())',
        f'&["{HOST}"]',
        f'= "{PUBLIC_KEY}";',
    ]
    if not all(item in check for item in required):
        print("ERROR: post-write validation failed.", file=sys.stderr)
        return 3
    if "id_ed25519" in check or "PRIVATE KEY" in check:
        print("ERROR: private-key-like content detected; refusing to continue.", file=sys.stderr)
        return 4
    print(f"Validated app name: {APP_NAME}")
    print(f"Validated rendezvous host: {HOST}")
    print("Validated public key: present (public key only)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
