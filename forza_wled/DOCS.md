# Setup and operation

## Before first use

Under the app's **Configuration** tab, set `forza_source` to the single IPv4 address of your game device and `wled_host` to your WLED controller's IPv4 address. For illustration only, imagine the game device is `192.0.2.50` and WLED is `192.0.2.60` (RFC 5737 documentation addresses, **not usable device addresses**). Replace them with your actual LAN IPs. Both default fields are intentionally empty: the app refuses to start without valid addresses and sends no DDP. Each UDP packet must match the source IPv4 exactly. UDP source addresses can be spoofed; this filter is no substitute for a firewall or network isolation.

Under **Network**, choose the exposed UDP host-port mapping for `20446/udp`. The container always listens on UDP 20446; enter the displayed **host** port as the Data Out destination port in the game. There is no `forza_port` configuration option in the HA app. Enable Data Out in Forza Horizon 6's HUD and Gameplay settings. Its destination IP is your Home Assistant host's IPv4, **not** `forza_source` or `wled_host`. Data Out is sent while driving.

WLED must be reachable, on, and configured to receive DDP realtime data (normally UDP port 4048). Set `led_count` to the number of LEDs used for the bar and check WLED's LED/realtime settings. Configure WLED's own realtime timeout to restore its previous mode after game telemetry ends. This app sends no black/off frame, does not turn WLED on, and calls no Home Assistant services.

## Configuration options

The English UI labels and concise field help appear under **Configuration** via `translations/en.yaml`. The options below are presented by task; Home Assistant does not provide custom groups for this app. Its documented app schema supports bounded numeric `float` fields, but does not specify a native slider widget. Set the zone percentages as numeric inputs; no custom UI is included.

| Option | Meaning and baseline | Allowed values |
| --- | --- | --- |
| `forza_source` | **Connection:** source IPv4 of the PC/console sending Data Out; required, no hostname, CIDR, or wildcard. | One valid device IPv4; empty default must be replaced. |
| `wled_host` | **Connection:** destination IPv4 of the WLED controller; required. | One valid device IPv4; empty default must be replaced. |
| `wled_port` | **Connection:** WLED DDP destination port; leave at 4048 unless your WLED configuration differs. | 1–65535; default 4048. |
| `led_count` | **Display:** length of the physical LED bar; match your WLED setup. | 1–480 (single DDP packet); default 300. |
| `fps` | **Display:** frame transmission rate. **12 FPS is a starting baseline, not a proven best setting**; tune to your setup if needed. | 1–30; default 12. |
| `telemetry_timeout` | **Display:** stop sending after this many seconds without fresh telemetry. Separate from WLED's own realtime timeout. | 0.1–10 seconds; default 0.7. |
| `green_until` | **Colors:** physical bar position where green becomes amber; not an engine RPM threshold. | 1–99%; default 58; must be below `amber_until`. |
| `amber_until` | **Colors:** physical bar position where amber becomes red. | 1–99%; default 72; must exceed `green_until`. |
| `flash_at` | **Colors:** fraction of the car's reported maximum RPM at which the lit LEDs flash red. | 1–100%; default 96. |

The default physical zones are green before 58% of the bar, amber from 58% to 72%, and red from 72% onward. The host UDP port belongs under **Network**, not Configuration. Option changes require an app restart. `/data/options.json` is validated on startup: missing, unknown, or invalid values prevent startup.

Standalone without Supervisor: explicitly set IPv4 values in `FORZA_SOURCE` and `WLED_HOST`, then run `PYTHONPATH=. python3 forza_wled/receiver.py`. `FORZA_PORT` is an optional environment variable **only for standalone use**. Inside the HA app, `/data/options.json` determines all configuration and the internal listener stays at UDP 20446.

## Updating and rollback

Version 1.1.1 changes UI language/help and startup messages; it retains the 1.1.0 option keys, defaults, validation, UDP behavior, and WLED behavior. If updating from 1.0.5, enter your existing private device IPs in the app configuration before restart, never in Git. Save the previous app version first. If needed, reinstall that version and restore your network settings; no automations or HA services are changed. Version 1.1.1 has started on one local HA OS host, but has **not** been driving-tested or installed by an independent user.

## Troubleshooting

- Startup error for `forza_source` or `wled_host`: enter your device's actual single IPv4 and restart. A wildcard source is not supported.
- No telemetry: enable Data Out, check the Home Assistant host IPv4 and the **host** UDP port under Network, and test while driving. Check firewall and LAN routing. Internal port 20446 never changes.
- Telemetry received, but no LEDs: check WLED address/port, DDP realtime reception, LED count, power, and WLED's on/off state. The app does not turn it on.
- Output stops too early/late: distinguish `telemetry_timeout` (this app stops sending) from WLED's realtime timeout (previous mode returns). No black frames are sent.
- Numeric/zone validation errors name the offending option in app logs; correct it and restart.

A real setup photo may later be added as `docs/images/real-setup.jpg`; none is included or claimed here.
