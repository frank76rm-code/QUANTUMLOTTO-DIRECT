#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
expected_package = "com.frankpetra.quantumlotto"
expected_public = "1C69F083A1A40A73F759F02DC3BD8516AF70D500BE201AF062C16A1949EF8048"

required = [
    root / "buildozer.spec",
    root / "quantum_lotto" / "config.py",
    root / "quantum_lotto" / "direct_entitlement.py",
]
for p in required:
    if not p.is_file():
        raise SystemExit(f"SECURITY_PREFLIGHT_FAIL missing:{p}")

spec = required[0].read_text(encoding="utf-8", errors="strict")
config = required[1].read_text(encoding="utf-8", errors="strict")
ent = required[2].read_text(encoding="utf-8", errors="strict")

checks = {
    "versionName": "version = 3.5.1" in spec,
    "versionCode": "android.numeric_version = 30501" in spec,
    "package": "package.name = quantumlotto" in spec and "package.domain = com.frankpetra" in spec,
    "configVersion": 'VERSION = "3.5.1"' in config and "VERSION_CODE = 30501" in config,
    "licensePrefix": 'LICENSE_PREFIX = "QLD2"' in ent,
    "publicKey": expected_public in ent,
    "noRSA": "PUBLIC_MODULUS" not in ent and "RSA_BYTES" not in ent,
}
failed = [k for k, ok in checks.items() if not ok]
if failed:
    raise SystemExit("SECURITY_PREFLIGHT_FAIL checks:" + ",".join(failed))

# Fail closed if likely private-key material is present in the patched project.
name_patterns = re.compile(r"(ed25519.*private|private.*ed25519|license.*private|private.*license)", re.I)
for p in root.rglob("*"):
    if not p.is_file():
        continue
    rel = p.relative_to(root).as_posix()
    if any(part in {".git", ".buildozer", "__pycache__"} for part in p.parts):
        continue
    low = p.name.lower()
    if low.endswith((".pem", ".p8", ".pk8", ".p12", ".pfx")) or name_patterns.search(rel):
        raise SystemExit(f"SECURITY_PREFLIGHT_FAIL private-key-file:{rel}")
    if p.stat().st_size <= 2_000_000:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if "-----BEGIN PRIVATE KEY-----" in text or "-----BEGIN ED25519 PRIVATE KEY-----" in text:
            raise SystemExit(f"SECURITY_PREFLIGHT_FAIL private-key-content:{rel}")

print("SECURITY_PREFLIGHT_OK")
print("PACKAGE=" + expected_package)
print("VERSION=3.5.1 VERSION_CODE=30501 LICENSE=ED25519 PUBLIC_KEY_ONLY=YES")
