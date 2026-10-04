# Forza Horizon 6 → WLED Drehzahlbalken

Kostenlose, inoffizielle **Home-Assistant-App**: Sie empfängt Forza-Horizon-6-Data-Out-Telemetrie per UDP und zeichnet die Motordrehzahl als LED-Balken über WLED DDP. Kein HACS-Plugin, keine Home-Assistant-Automation. Die App schaltet einen ausgeschalteten LED-Streifen **nicht** ein und gibt den WLED-Realtime-Modus nach dem Spiel wieder frei.

> **Privater Teststand 1.1.0:** Dieses Repository ist noch nicht veröffentlicht. Installation durch Dritte und Verhalten während einer echten Fahrt sind noch nicht unabhängig bestätigt. Keine Verbindung zu Microsoft, Playground Games, Forza, WLED oder Home Assistant.

## Installation (nach Veröffentlichung)

1. Home Assistant OS oder Supervised: **Einstellungen → Apps → ⋮ → Repositories** öffnen und die URL dieses künftig öffentlichen GitHub-Repositories hinzufügen. Solange das Repository privat ist, ist dieser Installationsweg für andere Nutzer nicht verfügbar.
2. **Forza Horizon 6 WLED tachometer** installieren. In **Konfiguration** die beiden Pflichtfelder `forza_source` (IPv4 des Spielgeräts) und `wled_host` (IPv4 von WLED) eintragen und `led_count` passend zum verwendeten Streifen setzen. Standard: 300 LEDs, DDP-Port 4048, 12 Bilder/s.
3. In **Netzwerk** den freigegebenen **UDP-Host-Port** für `20446/udp` kontrollieren oder ändern. Im Container bleibt Port 20446 fest; eine geänderte Host-Portnummer muss auch im Spiel eingetragen werden.
4. In Forza Horizon 6 **Data Out** einschalten. Ziel-IP ist die IPv4 des Home-Assistant-Rechners; Zielport ist der unter Netzwerk angezeigte UDP-Host-Port. Die App starten und **während der Fahrt** testen. WLED dafür zuvor separat einschalten.

Ohne die beiden IP-Adressen startet die App absichtlich nicht. Falls die Anzeige ausbleibt, App-Protokoll, Forza-Zielport, WLED-DDP-Realtime-Einstellungen und LED-Anzahl prüfen. Alle Optionen und Fehlersuche: **[Einrichtung und Betrieb](forza_wled/DOCS.md)**.

## So sieht es aus

Hier kann später ein **echtes Foto** des Aufbaus eingefügt werden: `docs/images/real-setup.jpg`. Bis dahin kein Beispielbild und kein behaupteter Screenshot.

## Entwicklung

- App: [`forza_wled/`](forza_wled/) · [technische Karte](docs/CODEBASE.md) · [Änderungen](forza_wled/CHANGELOG.md)
- Tests ohne Hardware: `PYTHONPATH=. python3 -m unittest discover -s forza_wled/tests -v`. Synthetische UDP/DDP-Tests laufen nur auf localhost.
- Der Source-IP-Filter schützt vor versehentlichen anderen LAN-Sendern, ist aber keine kryptografische Authentisierung. Port 20446/UDP nur im eigenen LAN verwenden; nicht ins Internet freigeben.

Lizenz: [MIT](LICENSE).