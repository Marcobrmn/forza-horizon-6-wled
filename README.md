# Forza Horizon 6 → WLED RPM bar

Imagine the rev counter extending beyond the screen: as the engine revs rise, a WLED strip fills from green through amber to red. This unofficial Home Assistant app listens to Forza Horizon 6 **Data Out** over the local network and sends LED frames straight to WLED. It does not switch the strip on or change your Home Assistant lights.

> **Private pre-release, 1.1.1:** Not affiliated with Forza, Microsoft, Playground Games, WLED, or Home Assistant. Local installation has been tested; third-party installation and a drive with this version are not yet independently verified.

## Quick start

- Home Assistant OS / Supervised: after this repository is made public, add its URL under **Settings → Apps → ⋮ → Repositories**, then install **Forza Horizon 6 WLED tachometer**. The private repository is not currently installable by others.
- In the app's **Configuration**, enter your game device's IPv4 as `forza_source`, WLED's IPv4 as `wled_host`, and the correct `led_count`. The IP defaults are blank on purpose.
- In **Network**, note the UDP **host port** mapped to `20446/udp` (default 20446).
- In Forza: **Settings → HUD and Gameplay → Data Out** on; destination IP = your Home Assistant host, destination port = that **host port**. Switch WLED on separately and test while driving.

The app shows English explanations beside the settings. The LED update rate defaults to 12 FPS; 30 FPS is available but not guaranteed to look different. For troubleshooting and color zones, see the [short setup guide](forza_wled/DOCS.md).

## Notes for developers

- [App source](forza_wled/) · [codebase map](docs/CODEBASE.md) · [telemetry and possible future features](docs/TELEMETRY.md) · [changelog](forza_wled/CHANGELOG.md)
- Tests: `PYTHONPATH=. python3 -m unittest discover -s forza_wled/tests -v` (localhost only).
- The source-IP filter is not authentication. Keep the UDP port on a trusted LAN; do not expose it to the internet.
- License: [MIT](LICENSE).
