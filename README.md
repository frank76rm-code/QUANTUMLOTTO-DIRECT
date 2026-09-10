# QUANTUM LOTTO 3.5.1 DIRECT

Private DIRECT release line based exclusively on the verified QUANTUM LOTTO 3.4.2 stable source.

## Mandatory baseline

- source repository: `frank76rm-code/QUANTUMLOTTO`
- source branch: `release/quantum-lotto-3.4.2`
- source commit: `dc0bfdb81f6c6ec4a1f345b976e0134e01a3df3f`
- source archive Git blob: `22418e4ae6d6e92fa10f69074d48dae4e43f984d`
- source archive SHA-256: `42695fbebbb0cbfb9f9b2e2c1a2ca62c0bf86c8afd7d5b7a5dfa3b91d9b3de59`
- package: `com.frankpetra.quantumlotto`

The algorithms, historical archives, mathematical analyses and statistical engine of 3.4.2 are protected and must not be modified by the DIRECT patch.

## DIRECT licensing

3.5.1 DIRECT uses an offline Ed25519 entitlement verifier. Only the public verification key belongs in application source. The Ed25519 private signing key must never be committed, embedded in the APK or copied into build artifacts.

Android APK signing is a separate identity and must remain compatible with the historical 3.4.2 signing certificate.

See `BASELINE-3.4.2-PROVENANCE.txt`, `source-3.5.1-direct/SECURITY.md` and the preflight scripts before any release build.
