# Codebasis

- `repository.yaml`: Metadaten des späteren HA-App-Repositories; keine URL hinterlegt.
- `forza_wled/config.yaml`: App-Manifest, Optionen, Schema und UDP-Host-Port-Mapping auf internen 20446.
- `forza_wled/Dockerfile`: HA-Basisimage, Python-Laufzeit, Architektur-/Versionslabels, Startprozess.
- `forza_wled/receiver.py`: strikte Startvalidierung von `/data/options.json`, UDP-Quellprüfung, Forza-Paketparser, RPM-Mapping, DDP-Frames und Timeout. Standalone: explizite Env-Endpunkte und optionaler Env-Port.
- `forza_wled/tests/`: Parser-/Frame-Regression, Optionen einschließlich ungültiger IPs/Ports/Schwellen sowie UDP→DDP-Loopback ohne echtes WLED.
- `forza_wled/DOCS.md`, `forza_wled/CHANGELOG.md`, root `README.md`: Einrichtung, Migration und Änderungsverlauf.

Tests: `PYTHONPATH=. python3 -m unittest discover -s forza_wled/tests -v`. Kein externer Schreibzugriff beim Test; Integration verwendet ausschließlich localhost. Das Repository enthält keine persönlichen IP-Adressen. Optionen und private JSON-Dateien gehören nicht in Git. Die Quellenprüfung begrenzt akzeptierte Sender, ist aber keine kryptographische Authentisierung gegen UDP-Spoofing. Kein HA-API-Zugriff, kein WLED-On/Off; nur DDP-Telemetrie. Änderungskarte: Optionen/schema → `config.yaml`; Validierung/Frame → `receiver.py` + Tests; Installation/Fehlersuche → `DOCS.md`; neue Funktionen zuerst mit Tests absichern. Die lokale HA-App wurde auf Version 1.1.0 mit ihren bisherigen Werten aktualisiert; Supervisor meldet gestartet und 20446/udp zugeordnet. Ein echter Fahrtest der neuen Version steht noch aus.
