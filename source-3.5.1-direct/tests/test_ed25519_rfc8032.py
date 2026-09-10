"""Regression tests for the embedded Ed25519 verifier.

The vectors are from RFC 8032 section 7.1 and contain public test material only.
No QUANTUM LOTTO private licensing key is present here.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "runtime" / "direct_entitlement.py"
spec = importlib.util.spec_from_file_location("direct_entitlement", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _verify_with_public_key(public_key_hex: str, message_hex: str, signature_hex: str) -> bool:
    old_key = mod.PUBLIC_KEY
    try:
        mod.PUBLIC_KEY = bytes.fromhex(public_key_hex)
        return mod._verify(bytes.fromhex(message_hex), bytes.fromhex(signature_hex))
    finally:
        mod.PUBLIC_KEY = old_key


def test_rfc8032_vector_1_empty_message():
    assert _verify_with_public_key(
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "",
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b",
    )


def test_rfc8032_vector_2_one_byte_message():
    assert _verify_with_public_key(
        "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "72",
        "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
        "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00",
    )


def test_modified_message_is_rejected():
    assert not _verify_with_public_key(
        "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c",
        "73",
        "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
        "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00",
    )


def test_modified_signature_is_rejected():
    sig = bytearray.fromhex(
        "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
        "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    )
    sig[0] ^= 1
    assert not _verify_with_public_key(
        "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a",
        "",
        sig.hex(),
    )
