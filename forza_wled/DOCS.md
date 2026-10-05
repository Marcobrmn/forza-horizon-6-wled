# Quick setup

The game sends one-way UDP telemetry while you drive. This app reads the engine RPM and sends a rate-limited LED bar to WLED using DDP. WLED must already be on; after driving, its own realtime timeout returns it to the previous mode.

## Set it up

- **App → Configuration:** enter the game device's IPv4 (`forza_source`), WLED's IPv4 (`wled_host`), and the LED count. Replace the blank IP defaults with your own addresses. For illustration only: `192.0.2.50` and `192.0.2.60` are *documentation addresses*, not usable device IPs.
- **App → Network:** check the UDP **host port** mapped to `20446/udp`. The internal container port stays 20446.
- **Forza Horizon 6 → Settings → HUD and Gameplay:** enable **Data Out**. Destination IP = your **Home Assistant host**, destination port = the app's **host port**. Test while actively driving; no telemetry is sent in menus or pauses.
- **WLED:** switch it on, allow DDP realtime input (normally UDP 4048), and set a suitable realtime timeout.

## Tune it

- **Colors:** `green_until` and `amber_until` mark positions *along the strip*. Defaults: green below 58%, amber from 58% to 72%, red from 72%. Keep the green boundary below the amber boundary.
- **Red flash:** `flash_at` is different: it uses a percentage of the car's maximum **RPM**, default 96%.
- **LED rate:** `fps` defaults to 12 LED frames/s (not the game's frame rate). Up to 30 is supported; a higher value may not look different. `telemetry_timeout` defaults to 0.7 s. Save configuration changes and restart the app.

## If nothing appears

- Check the app log, Forza Data Out destination IP/**host** port, and that you are driving.
- Check WLED's IP, DDP port, LED count, power and realtime settings. The app never turns WLED on or sends an off frame.
- Keep the UDP listener on a trusted LAN; source-IP filtering cannot prevent spoofed packets.

Updating from 1.0.5? Re-enter the two private device IPs in Configuration; never put them in Git. Keep a backup of the previous app for rollback. Standalone use without Supervisor requires `FORZA_SOURCE` and `WLED_HOST` environment variables; `FORZA_PORT` applies only to standalone mode.
