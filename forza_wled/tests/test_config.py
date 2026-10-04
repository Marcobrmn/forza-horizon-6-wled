import json
import socket
import struct
import tempfile
import threading
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from forza_wled import receiver


class OptionsTests(unittest.TestCase):
    def options(self):
        return {
            "forza_source": "127.0.0.1", "wled_host": "127.0.0.1", "wled_port": 4048,
            "led_count": 300, "fps": 12, "telemetry_timeout": 0.7,
            "green_until": 58, "amber_until": 72, "flash_at": 96,
        }

    def test_options_file_controls_runtime_and_keeps_internal_port(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "options.json"
            path.write_text(json.dumps(self.options()), encoding="utf-8")
            with patch.dict("os.environ", {"FORZA_PORT": "22222", "WLED_HOST": "127.0.0.2"}):
                config = receiver.load_config(path)
            self.assertEqual(("0.0.0.0", 20446, "127.0.0.1", 4048),
                             (config.bind, config.port, config.wled_host, config.wled_port))
            self.assertEqual((300, 12, 0.7, 0.58, 0.72, 0.96),
                             (config.led_count, config.fps, config.telemetry_timeout,
                              config.green_until, config.amber_until, config.flash_at))

    def test_invalid_options_fail_closed(self):
        for key, invalid in (
            ("forza_source", "0.0.0.0"), ("forza_source", "127.0.0.2.4"),
            ("forza_source", "localhost"), ("forza_source", "224.0.0.1"),
            ("wled_host", "255.255.255.255"), ("wled_host", "example.invalid"),
            ("wled_port", 0), ("wled_port", 65536), ("wled_port", True),
            ("led_count", 0), ("led_count", 481), ("fps", 0), ("fps", 31),
            ("fps", float("nan")), ("telemetry_timeout", 0),
            ("telemetry_timeout", float("inf")), ("green_until", 72),
            ("amber_until", 58), ("flash_at", 0), ("flash_at", 101),
        ):
            with self.subTest(key=key, invalid=invalid):
                options = self.options()
                options[key] = invalid
                with self.assertRaisesRegex(ValueError, key):
                    receiver.validate_options(options)
        with self.assertRaisesRegex(ValueError, "forza_source"):
            receiver.validate_options({k: v for k, v in self.options().items() if k != "forza_source"})
        with self.assertRaisesRegex(ValueError, "forza_port"):
            receiver.validate_options(dict(self.options(), forza_port=20446))
        with self.assertRaisesRegex(ValueError, "options.json"):
            receiver.load_config(Path("/data/not-existing-options.json"))

    def test_standalone_environment_requires_explicit_ipv4_endpoints(self):
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "FORZA_SOURCE"):
                receiver.load_config(None)
        with patch.dict("os.environ", {"FORZA_SOURCE": "127.0.0.1", "WLED_HOST": "127.0.0.1",
                                     "FORZA_PORT": "20447"}, clear=True):
            self.assertEqual(receiver.load_config(None).port, 20447)
        with patch.dict("os.environ", {"FORZA_SOURCE": "127.0.0.1", "WLED_HOST": "127.0.0.1",
                                     "BIND": "not-a-host"}, clear=True):
            with self.assertRaisesRegex(ValueError, "BIND"):
                receiver.load_config(None)

    def test_synthetic_udp_to_ddp_and_wrong_source_drop(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as ddp, socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as source:
            ddp.bind(("127.0.0.1", 0))
            ddp.settimeout(2)
            config = receiver.validate_options(dict(self.options(), led_count=10, fps=20,
                                                    telemetry_timeout=0.3, wled_port=ddp.getsockname()[1]))
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
                probe.bind(("127.0.0.1", 0))
                udp_port = probe.getsockname()[1]
            config = replace(config, port=udp_port)
            stop = threading.Event()
            ready = threading.Event()
            thread = threading.Thread(target=receiver.run, args=(config,),
                                      kwargs={"stop_event": stop, "ready_event": ready}, daemon=True)
            thread.start()
            self.assertTrue(ready.wait(2), "UDP receiver not ready")
            packet = struct.pack("<iIfff", 1, 1234, 8000., 900., 4000.) + bytes(324 - 20)
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as wrong_source:
                    wrong_source.bind(("127.0.0.2", 0))
                    wrong_source.sendto(packet, ("127.0.0.1", udp_port))
                ddp.settimeout(0.2)
                with self.assertRaises(socket.timeout):
                    ddp.recvfrom(2048)
                ddp.settimeout(2)
                source.sendto(packet, ("127.0.0.1", udp_port))
                frame, address = ddp.recvfrom(2048)
                self.assertEqual(frame[:10], struct.pack("!BBBBIH", 0x41, 0, 1, 1, 0, 30))
                self.assertEqual(frame[10:13], bytes((0, 170, 12)))
                self.assertEqual(frame[-3:], bytes((0, 0, 0)))
                self.assertEqual(address[0], "127.0.0.1")
                ddp.settimeout(0.5)
                while True:
                    try:
                        ddp.recvfrom(2048)
                    except socket.timeout:
                        break

            finally:
                stop.set()
                thread.join(2)
            self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()
