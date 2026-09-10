# QUANTUM LOTTO 3.5.1 DIRECT - Security contract

## Key separation

The Android application signing identity and the DIRECT license-signing identity are independent.

- Android updates must retain package `com.frankpetra.quantumlotto` and the historical Android signing identity used by stable 3.4.2.
- DIRECT licenses are verified with Ed25519.
- The application contains only the Ed25519 public verification key.
- The Ed25519 private key must never be committed, packaged in the APK, written to BuildConfig/resources/assets, or printed in CI logs.

## Source contract

The DIRECT patch is applied only over the certified 3.4.2 source. Mathematical/statistical engines, historical archives and their parsers are not DIRECT implementation targets.

## Release gates

Before any release build is accepted:

1. run the inherited 3.4.2 preflight after applying the DIRECT patch;
2. run `source-3.5.1-direct/scripts/security_preflight.py` against the patched project;
3. verify `versionName=3.5.1`, `versionCode=30501`, package `com.frankpetra.quantumlotto`;
4. verify the produced APK certificate SHA-256 equals the historical 3.4.2 certificate;
5. verify an in-place update from the signed 3.4.2 APK without data loss;
6. verify FREE, valid FULL, wrong-device, expired, malformed and modified-signature license cases;
7. verify ordinary archive import remains the original 3.4.2 path.

No release artifact is approved merely because it compiles.
