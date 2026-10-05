# Codebase map

## Scope and source of truth

An unofficial Home Assistant app receives Forza Horizon 6 Data Out UDP packets and sends RPM-bar pixels to WLED with DDP. Source code and `config.yaml` define runtime behavior; this document maps them but does not override them. No HA light/automation calls, WLED on/off changes, external storage, or generated artifacts are involved. Version 1.1.1 has been installed and started on one local HA OS host; its behavior during an actual drive and third-party installation remain unverified.

## Files and data flow

- `repository.yaml`: Home Assistant app repository metadata; no public URL is configured.
- `forza_wled/config.yaml`: manifest, option schema/defaults, internal UDP 20446 and host port mapping. IP defaults remain empty.
- `forza_wled/translations/en.yaml`: official app translation format: `configuration.<schema_key>.name/description`, plus `network.20446/udp` as a scalar port description. Copy is English only; this file does not change schema or runtime behavior.
- `forza_wled/Dockerfile`: HA base image, Python runtime, architecture/version labels, startup command.
- `forza_wled/receiver.py`: validate `/data/options.json` on startup → listen on UDP 20446 → filter sender IPv4 → parse 324-byte Forza telemetry → map RPM to a green/amber/red bar → send WLED DDP frames. When telemetry times out, stop sending; WLED's own realtime timeout restores its prior mode. Standalone mode uses explicit environment endpoints and optionally an environment listener port.
- `forza_wled/tests/`: config/translation validation, packet and frame regression, and localhost-only UDP→DDP exercise without hardware.
- `README.md`, `forza_wled/README.md`, `forza_wled/DOCS.md`, `forza_wled/CHANGELOG.md`: entrypoint, app summary, configuration/troubleshooting, and release history.

## Invariants, privacy, and verification

The option keys/defaults and the 20446 container listener are stable. `forza_source` and `wled_host` must be explicitly set to real single IPv4 device addresses. Source filtering is not cryptographic authentication against spoofed UDP packets: keep the port on a trusted LAN, not the internet. Never commit live `/data/options.json`, personal device IPs, or private JSON configuration. Documentation uses RFC 5737 example IPs that cannot represent working devices. Runtime never turns WLED on and never sends an off/black frame when telemetry ends.

Run `PYTHONPATH=. python3 -m unittest discover -s forza_wled/tests -v` from the repository root. Tests use localhost only and make no external writes; no real driving or HA UI test is implied. For translation changes, verify `configuration` names/descriptions match *every* schema key, the `network` port is a scalar, and no option defaults or behavior changed. For release readiness, review the full Git diff and privacy scan before any separate approval to commit or publish.

## Change map and maintenance

- Options and allowed ranges → `forza_wled/config.yaml`, `receiver.validate_options`, config tests, `forza_wled/translations/en.yaml`, `forza_wled/DOCS.md`.
- UI text only → translation YAML and related docs/tests; do not add a custom configuration frontend.
- Parser, frames, timeout → `receiver.py` and receiver/UDP tests; preserve WLED state behavior.
- Installation/network/troubleshooting → root README and `forza_wled/DOCS.md`; keep container port distinct from host port.

Update this map when schema, runtime data flow, privacy boundaries, or test commands change. Keep real-driving and third-party compatibility claims explicitly labeled; the local 1.1.1 startup does not prove them.
