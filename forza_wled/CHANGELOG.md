# Änderungen

## 1.1.0

- Home-Assistant-Repository-Struktur mit `repository.yaml` und App-Verzeichnis.
- Quelle, WLED-Ziel, DDP-Port, LEDs, FPS, Telemetrie-Timeout und physische Farb-/Blinkgrenzen als validierte App-Optionen; ohne gültige Quelle/Ziel kein Start.
- HA-Container lauscht weiterhin intern auf UDP 20446; Host-Port über Netzwerk frei zuordenbar.
- Keine Änderungen an WLED-Einschaltung, HA-Automationen oder bestehender DDP-Farbgeometrie bei Standardwerten.
- Tests für Optionen, Fehlwerte und synthetisches UDP→DDP auf localhost.

## 1.0.5

- Vorherige flache lokale Version ohne App-Konfigurationsschema.
