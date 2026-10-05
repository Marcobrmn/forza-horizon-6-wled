# Forza Horizon 6 → WLED RPM bar

A free, unofficial **Home Assistant app** that receives Forza Horizon 6 Data Out telemetry over UDP and draws an RPM bar via WLED DDP. No HACS integration or Home Assistant automation is required. The app does **not** turn on an off LED strip; after telemetry stops, it stops sending frames so WLED can leave realtime mode according to WLED's own timeout.

> **Private pre-release, 1.1.1 candidate:** This repository is not public. Third-party installation and an actual driving test of this version have not been independently confirmed. Not affiliated with Microsoft, Playground Games, Forza, WLED, or Home Assistant.

## Installation (once the repository is public)

1. On Home Assistant OS or Supervised, open **Settings → Apps → ⋮ → Repositories** and add this repository's future public GitHub URL. Other users cannot install from this repository while it is private.
2. Install **Forza Horizon 6 WLED tachometer**. Under **Configuration**, set `forza_source` to the game device's IPv4 address and `wled_host` to the WLED controller's IPv4 address. Set `led_count` to match your strip. The defaults are 300 LEDs, DDP port 4048, and a **12 FPS baseline**, not a proven optimum. Leave the IP fields empty only until you have your own addresses: the app cannot start with empty endpoints.
3. Under **Network**, check or change the exposed UDP **host port** mapped to `20446/udp`. The container always listens on 20446; if you change the host port, set that same port in the game.
4. In Forza Horizon 6, enable **Data Out**. Set the destination IPv4 to your Home Assistant host and the destination port to the host UDP port shown under Network. Turn WLED on separately, start the app, and test **while driving**.

If nothing appears, check the app logs, Forza destination port, WLED DDP/realtime settings, and LED count. See the [setup, option reference, and troubleshooting guide](forza_wled/DOCS.md).

## Setup photo

A real setup photo may be added later at `docs/images/real-setup.jpg`. There is no placeholder photo or claimed screenshot.

## Development

- App source: [`forza_wled/`](forza_wled/) · [codebase map](docs/CODEBASE.md) · [changelog](forza_wled/CHANGELOG.md)
- Hardware-free tests: `PYTHONPATH=. python3 -m unittest discover -s forza_wled/tests -v`. Synthetic UDP/DDP tests use localhost only.
- The source-IP filter rejects unintended LAN senders but is not cryptographic authentication. Keep UDP 20446 on your own LAN; do not expose it to the internet.

License: [MIT](LICENSE).
