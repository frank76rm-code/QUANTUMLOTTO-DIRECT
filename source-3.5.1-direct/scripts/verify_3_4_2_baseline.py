#!/usr/bin/env python3
from __future__ import annotations
import hashlib
from pathlib import Path

EXPECTED_SIZE = 10998828
EXPECTED_GIT_BLOB = "22418e4ae6d6e92fa10f69074d48dae4e43f984d"
EXPECTED_SHA256 = "42695fbebbb0cbfb9f9b2e2c1a2ca62c0bf86c8afd7d5b7a5dfa3b91d9b3de59"

def main(path: str) -> None:
    p = Path(path)
    data = p.read_bytes()
    size = len(data)
    git_blob = hashlib.sha1(b"blob " + str(size).encode("ascii") + b"\0" + data).hexdigest()
    sha256 = hashlib.sha256(data).hexdigest()
    if size != EXPECTED_SIZE or git_blob != EXPECTED_GIT_BLOB or sha256 != EXPECTED_SHA256:
        raise SystemExit(f"BASELINE_MISMATCH size={size} git_blob={git_blob} sha256={sha256}")
    print("BASELINE_3_4_2_EXACT_OK")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: verify_3_4_2_baseline.py quantum-lotto3.4.2.zip")
    main(sys.argv[1])
