from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "runtime" / "direct_entitlement.py"
spec = importlib.util.spec_from_file_location("direct_entitlement", MODULE)
ent = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(ent)


def test_release_identity():
    assert ent.PACKAGE_ID == "com.frankpetra.quantumlotto"
    assert ent.LICENSE_PREFIX == "QLD2"
    assert len(ent.PUBLIC_KEY) == 32


def test_free_without_license(tmp_path):
    status = ent.EntitlementManager(tmp_path).status()
    assert not status.valid
    assert not status.full_access
    assert status.reason == "NO_LICENSE"


def test_normal_archive_is_not_consumed_as_license(tmp_path):
    p = tmp_path / "archive.json"
    p.write_text('{"archive":"ordinary-3.4.2-data"}', encoding="utf-8")
    status = ent.EntitlementManager(tmp_path / "state").try_import_file(p)
    assert not status.recognized
    assert status.reason == "NOT_LICENSE"


def test_malformed_direct_file_fails_closed(tmp_path):
    p = tmp_path / "bad.ql"
    p.write_text("QLD2.not-base64.not-a-signature", encoding="utf-8")
    status = ent.EntitlementManager(tmp_path / "state").try_import_file(p)
    assert status.recognized
    assert not status.valid
    assert not status.full_access


def test_restricted_screen_contract():
    assert ent.restricted_screen("UNIVERSALE")
    assert ent.restricted_screen("BACKTEST")
    assert not ent.restricted_screen("HOME")
    assert not ent.restricted_screen("ARCHIVI")
