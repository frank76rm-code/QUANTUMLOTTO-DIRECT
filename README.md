# QUANTUMLOTTO DIRECT

Repository privata dedicata alla linea QUANTUM LOTTO DIRECT distribuita fuori Google Play.

Base sorgente obbligatoria: QUANTUM LOTTO 3.4.2 stabile, branch sorgente `release/quantum-lotto-3.4.2`, commit `dc0bfdb81f6c6ec4a1f345b976e0134e01a3df3f`.

La linea DIRECT mantiene package `com.frankpetra.quantumlotto` e la stessa identità di firma Android della 3.4.2 per garantire la continuità degli aggiornamenti compatibili.

Il sistema di licenza DIRECT usa una coppia Ed25519 separata dalla firma Android. La chiave privata Ed25519 non deve essere mai inserita nel repository o nell'APK; nell'app può essere presente esclusivamente la chiave pubblica di verifica.

Algoritmi, archivi, analisi matematiche e motore statistico della 3.4.2 sono protetti e non devono essere modificati.
