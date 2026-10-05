#!/usr/bin/env python3
"""Forza Horizon 6 UDP Data Out -> WLED DDP tachometer. No HA light calls."""
import logging
import ipaddress
import json
import math
import os
import select
import socket
import struct
import time
from dataclasses import dataclass
from pathlib import Path

LOG = logging.getLogger("forza_wled")
FORZA_PACKET_BYTES = 324
FORZA_HEADER = struct.Struct("<iIfff")  # race on, timestamp, max/idle/current rpm
DDP_HEADER = struct.Struct("!BBBBIH")
OPTION_KEYS = frozenset({"forza_source", "wled_host", "wled_port", "led_count", "fps",
                         "telemetry_timeout", "green_until", "amber_until", "flash_at"})


@dataclass(frozen=True)
class Config:
    bind: str
    port: int
    forza_source: str
    wled_host: str
    wled_port: int
    led_count: int
    fps: float
    telemetry_timeout: float
    green_until: float
    amber_until: float
    flash_at: float


def ipv4(value, field):
    try:
        address = ipaddress.IPv4Address(value)
    except (ValueError, TypeError, ipaddress.AddressValueError) as exc:
        raise ValueError(f"{field}: a single valid IPv4 address is required") from exc
    if (address.is_unspecified or address.is_multicast or address.is_reserved
            or address.is_link_local or address == ipaddress.IPv4Address("255.255.255.255")):
        raise ValueError(f"{field}: broadcast, multicast, and placeholder addresses are not allowed")
    return str(address)


def integer(value, field, lower, upper):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{field}: an integer from {lower} to {upper} is required")
    return value


def number(value, field, lower, upper):
    if type(value) not in (float, int) or not math.isfinite(value) or not lower <= value <= upper:
        raise ValueError(f"{field}: a finite number from {lower} to {upper} is required")
    return float(value)


def validate_options(options):
    if not isinstance(options, dict):
        raise ValueError("options.json: a JSON object is required")
    for key in OPTION_KEYS:
        if key not in options:
            raise ValueError(f"{key}: missing option")
    unknown = set(options) - OPTION_KEYS
    if unknown:
        raise ValueError(f"Unknown option: {sorted(unknown)[0]}; the Forza host port is configured under Network only")
    source = ipv4(options["forza_source"], "forza_source")
    target = ipv4(options["wled_host"], "wled_host")
    wled_port = integer(options["wled_port"], "wled_port", 1, 65535)
    count = integer(options["led_count"], "led_count", 1, 480)
    fps = number(options["fps"], "fps", 1, 30)
    timeout = number(options["telemetry_timeout"], "telemetry_timeout", 0.1, 10)
    green = number(options["green_until"], "green_until", 1, 99)
    amber = number(options["amber_until"], "amber_until", 1, 99)
    flash = number(options["flash_at"], "flash_at", 1, 100)
    if green >= amber:
        raise ValueError("green_until must be less than amber_until")
    return Config("0.0.0.0", 20446, source, target, wled_port, count, fps,
                  timeout, green / 100, amber / 100, flash / 100)


def load_config(options_path=Path("/data/options.json")):
    """Supervisor options take precedence; standalone explicitly needs both endpoints."""
    if options_path is not None:
        try:
            with Path(options_path).open(encoding="utf-8") as handle:
                return validate_options(json.load(handle))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"options.json: cannot read configuration: {exc}") from exc
    env = os.environ
    for key in ("FORZA_SOURCE", "WLED_HOST"):
        if not env.get(key):
            raise ValueError(f"{key}: an IPv4 address is required for standalone use")
    def env_int(key, default):
        try:
            return int(env.get(key, default))
        except ValueError as exc:
            raise ValueError(f"{key}: an integer is required") from exc
    def env_float(key, default):
        try:
            return float(env.get(key, default))
        except ValueError as exc:
            raise ValueError(f"{key}: a number is required") from exc
    options = {
        "forza_source": env["FORZA_SOURCE"], "wled_host": env["WLED_HOST"],
        "wled_port": env_int("WLED_PORT", 4048), "led_count": env_int("LED_COUNT", 300),
        "fps": env_float("FPS", 12), "telemetry_timeout": env_float("TELEMETRY_TIMEOUT", 0.7),
        "green_until": env_float("GREEN_UNTIL", 58), "amber_until": env_float("AMBER_UNTIL", 72),
        "flash_at": env_float("FLASH_AT", 96),
    }
    config = validate_options(options)
    bind = env.get("BIND", "0.0.0.0")
    if bind != "0.0.0.0":
        bind = ipv4(bind, "BIND")
    port = env_int("FORZA_PORT", 20446)
    integer(port, "FORZA_PORT", 1, 65535)
    return Config(bind, port, config.forza_source,
                  config.wled_host, config.wled_port, config.led_count,
                  config.fps, config.telemetry_timeout, config.green_until,
                  config.amber_until, config.flash_at)


def parse_forza(data):
    if len(data) != FORZA_PACKET_BYTES:
        return None
    race_on, timestamp, maximum, idle, rpm = FORZA_HEADER.unpack_from(data)
    if race_on != 1 or not all(map(math.isfinite, (maximum, idle, rpm))):
        return None
    if not 500 <= maximum <= 30000 or not 0 <= idle < maximum or not 0 <= rpm <= maximum * 1.25:
        return None
    return max(0.0, min(rpm / maximum, 1.0))


def make_frame(fraction, count, flash=False, green_until=0.58, amber_until=0.72, flash_at=0.96):
    lit = round(max(0, min(1, fraction)) * count)
    pixels = bytearray(count * 3)
    for index in range(lit):
        position = index / max(1, count - 1)
        color = (0, 170, 12) if position < green_until else ((235, 115, 0) if position < amber_until else (245, 0, 0))
        if flash and fraction >= flash_at:
            color = (245, 0, 0)
        pixels[index * 3:index * 3 + 3] = bytes(color)
    return DDP_HEADER.pack(0x41, 0, 1, 1, 0, len(pixels)) + pixels


def run(config=None, stop_event=None, ready_event=None):
    config = config or load_config()
    period = 1 / config.fps
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as incoming, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as outgoing:
        incoming.bind((config.bind, config.port))
        incoming.setblocking(False)
        if ready_event is not None:
            ready_event.set()
        LOG.info("listening on %s:%d/udp; WLED %s:%d; %d LEDs", config.bind, config.port,
                 config.wled_host, config.wled_port, config.led_count)
        last_data = 0.0
        last_frame = 0.0
        last_log = 0.0
        last_timestamp = None
        fraction = None
        while stop_event is None or not stop_event.is_set():
            readable, _, _ = select.select([incoming], [], [], 0.05)
            if readable:
                # Bound each batch so a busy socket cannot starve frame/timeout handling.
                for _ in range(256):
                    try:
                        packet, addr = incoming.recvfrom(2048)
                    except BlockingIOError:
                        break
                    if addr[0] != config.forza_source:
                        continue
                    value = parse_forza(packet)
                    if value is not None:
                        timestamp = FORZA_HEADER.unpack_from(packet)[1]
                        now = time.monotonic()
                        delta = (timestamp - last_timestamp) & 0xffffffff if last_timestamp is not None else 1
                        # Identical/replayed data is not fresh. Accept natural u32 rollover;
                        # re-sync to a reset game clock only after telemetry has timed out.
                        if last_timestamp is not None and not (0 < delta < 10000 or (now - last_data > config.telemetry_timeout and timestamp != last_timestamp)):
                            continue
                        if fraction is None:
                            LOG.info("valid Forza telemetry received from %s", addr[0])
                        fraction = value
                        last_timestamp = timestamp
                        last_data = now
            now = time.monotonic()
            if fraction is not None and now - last_data > config.telemetry_timeout:
                fraction = None  # No black/off frame: WLED's realtime timeout restores prior mode.
                LOG.info("telemetry stopped; releasing WLED realtime mode")
            if fraction is not None and now - last_frame >= period:
                try:
                    outgoing.sendto(make_frame(fraction, config.led_count, (now % 0.5) < 0.25,
                                               config.green_until, config.amber_until, config.flash_at),
                                    (config.wled_host, config.wled_port))
                except OSError as exc:
                    if now - last_log > 15:
                        LOG.warning("WLED send failed: %s", exc)
                        last_log = now
                last_frame = now


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        run()
    except (ValueError, OSError) as exc:
        LOG.error("Configuration/start failed: %s", exc)
        raise SystemExit(1) from exc
