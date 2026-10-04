# Einrichtung und Betrieb

## Vor der ersten Nutzung

In der App unter Konfiguration `forza_source` auf die einzelne IPv4-Adresse des Spielgeräts und `wled_host` auf die IPv4-Adresse des WLED-Geräts setzen. Die leeren Standardwerte sind absichtlich nicht lauffähig. Eine falsche oder fehlende Adresse führt zu einem klaren Startfehler im App-Protokoll; es wird dann kein DDP gesendet. Die Quelle wird pro UDP-Paket exakt geprüft (kein offener beliebiger Absender). UDP-Quelladressen sind grundsätzlich spoofbar; das ersetzt keine Netzwerksegmentierung oder Firewall.

Unter Netzwerk wird die Host-Port-Zuordnung für `20446/udp` frei gewählt. Der Container lauscht immer intern auf UDP 20446. Die dort angezeigte Host-Portnummer im Spiel als Zielport eintragen; sie ist keine Option unter Konfiguration. In Forza Horizon 6: Einstellungen → HUD und Gameplay → Data Out einschalten, Ziel-IP = IPv4 des Home-Assistant-Hosts, Zielport = gewählter Host-Port. Das Spiel sendet nur beim Fahren. Keine zusätzliche `FORZA_PORT`-Option der HA-App.

WLED muss erreichbar und für DDP-Realtime-Empfang eingerichtet sein (üblicher DDP-Port 4048). `led_count` entspricht der tatsächlich für die Anzeige vorgesehenen LED-Anzahl; in WLED LED-Konfiguration und Realtime-Einstellungen prüfen, ob DDP angenommen wird. WLED-Realtime-Timeout passend setzen, damit nach Spielende der vorherige Modus zurückkehrt. Diese App sendet kein Schwarz/Off, schaltet WLED nicht ein und ruft keine HA-Services auf. Ist WLED aus, bleibt es aus; das Einschalten geschieht bewusst separat.

## Optionen

- `forza_source`: genau eine IPv4 des Spielgeräts; keine DNS-Namen, Netze oder Platzhalter.
- `wled_host`: genau eine IPv4 des WLED-Geräts.
- `wled_port`: DDP-Zielport, Standard 4048 (1–65535).
- `led_count`: LEDs im DDP-Balken, Standard 300 (1–480; DDP-Einzelpaketgrenze).
- `fps`: Ausgaberate in Bildern/s, Standard 12 (1–30).
- `telemetry_timeout`: Sekunden bis zum Ende der Realtime-Ausgabe ohne frische Pakete, Standard 0,7 (0,1–10).
- `green_until`, `amber_until`: physische Farbgrenzen in Prozent der Leiste, Standard 58 und 72; grün <58 %, orange 58–72 %, rot ab 72 %. `green_until` muss kleiner als `amber_until` sein. Keine Aussage zum Motorbegrenzer.
- `flash_at`: Drehzahlanteil am tatsächlichen Höchstwert für rotes Blinken, Standard 96 % (1–100).

Änderungen an Optionen erfordern einen App-Neustart. `/data/options.json` wird beim Start validiert; unbekannte, ungültige oder fehlende Werte verhindern den Start. Standalone ohne Supervisor: `FORZA_SOURCE` und `WLED_HOST` ausdrücklich als IPv4 setzen und `python3 forza_wled/receiver.py` mit `PYTHONPATH=.` ausführen; dafür kann `FORZA_PORT` als Umgebungsvariable verwendet werden. In der HA-App zählt ausschließlich `/data/options.json` und intern Port 20446.

## Migration und Rückweg

Version 1.1.0 benötigt die beiden expliziten IP-Optionen. Bei einem Update von 1.0.5 die bisherigen privaten IP-Adressen vor dem Neustart in der App-Konfiguration eintragen; nicht in Git speichern. Vorher die App-Quellversion sichern. Bei Problemen die gesicherte Version erneut installieren und die Netzwerkeinstellungen wiederherstellen; keine Automationsdateien oder HA-Services werden dabei verändert.

## Fehlersuche

- Startfehler `forza_source`/`wled_host`: korrekte einzelne IPv4 in Optionen eintragen und App neu starten. Keine Wildcard-Quelle möglich.
- Keine Telemetrie: Im Spiel Data Out aktivieren, Host-IP und den unter Netzwerk gewählten UDP-Host-Port prüfen, Firewall/Netz prüfen und erst während der Fahrt testen. Der interne Port ist immer 20446.
- Telemetrie da, keine LEDs: WLED-Adresse/Port, DDP-Realtime-Empfang, LED-Anzahl, Stromversorgung und WLED-Zustand prüfen. Die App schaltet WLED nicht ein.
- Anzeige endet zu früh/zu spät: `telemetry_timeout` und WLED-eigenen Realtime-Timeout unterscheiden. Keine schwarzen Frames werden gesendet.
- Bei ungültigen Zahlen/Schwellen zeigt das Protokoll den jeweiligen Optionsnamen; Werte korrigieren und neu starten.

Ein reales Aufbau-Foto ist als künftig hochzuladende Datei `docs/images/real-setup.jpg` vorgesehen. Es gibt aktuell weder Foto noch Screenshot in diesem Repository.
