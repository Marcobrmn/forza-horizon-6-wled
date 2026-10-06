# Forza Horizon 6 → WLED RPM bar

Imagine the rev counter extending beyond the screen: as the engine revs rise, a WLED strip fills from green through amber to red. This unofficial Home Assistant app listens to Forza Horizon 6 **Data Out** over the local network and sends LED frames straight to WLED. It does not switch the strip on or change your Home Assistant lights.

<img width="568" height="242" alt="image" src="https://github.com/user-attachments/assets/f161f3b1-0681-476f-a587-b70611df3600" />

> **Experimental beta, 1.1.3:** Not affiliated with Forza, Microsoft, Playground Games, WLED, or Home Assistant. Tested locally on Home Assistant OS; independent installation and driving behavior have not yet been verified.

## Quick start

- Home Assistant OS / Supervised: add `https://github.com/Marcobrmn/forza-horizon-6-wled` under **Settings → Apps → Install app → ⋮ → Repositories**, then install **Forza Horizon 6 WLED tachometer**. This is a third-party app repository, not an official Home Assistant app.
- In the app's **Configuration**, enter your game device's IPv4 as `forza_source`, WLED's IPv4 as `wled_host`, and the correct `led_count`. The IP defaults are blank on purpose.
<img width="1042" height="858" alt="image" src="https://github.com/user-attachments/assets/1735f142-2c2f-45a7-b0d5-1eed97e353ab" />

- Reserve the game device's, Home Assistant host's, and WLED's IPs in your router's DHCP settings to help keep their addresses stable while they use automatic IP assignment.
- In **Network**, note the UDP **host port** mapped to `20446/udp` (default 20446).
- In Forza: **Settings → HUD and Gameplay → Data Out** on; destination IP = your Home Assistant host, destination port = that **host port**. Switch WLED on separately and test while driving.

The app shows English explanations beside the settings. The LED update rate defaults to 12 FPS; 30 FPS is available but not guaranteed to look different. For troubleshooting and color zones, see the [short setup guide](forza_wled/DOCS.md).

## Notes for developers

- [App source](forza_wled/) · [codebase map](docs/CODEBASE.md) · [telemetry and possible future features](docs/TELEMETRY.md) · [changelog](forza_wled/CHANGELOG.md)
- Tests: `PYTHONPATH=. python3 -m unittest discover -s forza_wled/tests -v` (localhost only).
- The source-IP filter is not authentication. Keep the UDP port on a trusted LAN; do not expose it to the internet.
- License: [MIT](LICENSE).
