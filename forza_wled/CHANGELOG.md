# Changelog

## 1.1.1 (unreleased)

- Add English Home Assistant option names, descriptions, and UDP port help using `translations/en.yaml`.
- Translate the manifest, setup documentation, changelog, codebase map, and startup validation errors into English.
- Keep all option keys/defaults, packet processing, source filtering, LED color geometry, and WLED on/off behavior unchanged. Installed and started on one local HA OS host with options preserved; a real drive and third-party installation remain unverified.

## 1.1.0

- Add Home Assistant repository structure with `repository.yaml` and an app subdirectory.
- Validate source IP, WLED target, DDP port, LED count, FPS, telemetry timeout, and physical color/flash boundaries as app options. Refuse to start without valid source and destination IPs.
- Keep the container listener on UDP 20446, with a selectable host port under Network.
- Preserve WLED power behavior, Home Assistant automations, and default DDP color geometry.
- Add options, invalid-value, and synthetic localhost UDP→DDP tests.

## 1.0.5

- Previous flat local version without an app configuration schema.
