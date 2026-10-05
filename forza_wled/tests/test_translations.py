"""Dependency-free structural checks for the small YAML mapping subset we publish."""
import re
import unittest
from pathlib import Path

from forza_wled import receiver

ROOT = Path(__file__).resolve().parents[1]


def mapping(path):
    result = {}
    parents = [result]
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if path.name == "config.yaml" and re.fullmatch(r"  - [\w]+", line):
            continue  # Manifest architecture list is unrelated to translated mappings.
        match = re.fullmatch(r"( *)([\w/]+):(?: (.*))?", line)
        if match is None:
            raise AssertionError(f"Unexpected YAML mapping line in {path}: {line!r}")
        spaces, key, value = match.groups()
        depth = len(spaces) // 2
        if len(spaces) % 2 or depth >= len(parents) or key in parents[depth]:
            raise AssertionError(f"Unexpected nesting or duplicate key: {line!r}")
        parents = parents[:depth + 1]
        if value is None:
            node = {}
            parents[-1][key] = node
            parents.append(node)
        else:
            parents[-1][key] = value.strip('"')
    return result


class TranslationTests(unittest.TestCase):
    def test_english_options_and_network_match_manifest(self):
        manifest = mapping(ROOT / "config.yaml")
        translations = mapping(ROOT / "translations/en.yaml")
        self.assertEqual(set(manifest["schema"]), receiver.OPTION_KEYS)
        self.assertEqual(set(manifest["options"]), receiver.OPTION_KEYS)
        self.assertEqual(set(translations), {"configuration", "network"})
        self.assertEqual(set(translations["configuration"]), receiver.OPTION_KEYS)
        for key, entry in translations["configuration"].items():
            with self.subTest(key=key):
                self.assertEqual(set(entry), {"name", "description"})
                self.assertTrue(entry["name"].strip())
                self.assertTrue(entry["description"].strip())
        self.assertEqual(set(translations["network"]), set(manifest["ports"]))
        self.assertIsInstance(translations["network"]["20446/udp"], str)
        self.assertIn("host port", translations["network"]["20446/udp"])

    def test_baselines_and_color_zone_copy(self):
        manifest = mapping(ROOT / "config.yaml")
        fields = mapping(ROOT / "translations/en.yaml")["configuration"]
        self.assertEqual(manifest["options"]["forza_source"], "")
        self.assertEqual(manifest["options"]["wled_host"], "")
        self.assertEqual(manifest["options"]["fps"], "12")
        self.assertIn("baseline", fields["fps"]["description"])
        for key, bounds in {
            "wled_port": "1–65535", "led_count": "1–480", "fps": "1–30",
            "telemetry_timeout": "0.1–10", "green_until": "1–99%",
            "amber_until": "1–99%", "flash_at": "1–100%",
        }.items():
            with self.subTest(key=key):
                self.assertIn(bounds, fields[key]["description"])
        self.assertIn("192.0.2.50", fields["forza_source"]["description"])
        self.assertIn("192.0.2.60", fields["wled_host"]["description"])
        for key in ("green_until", "amber_until"):
            self.assertIn("58%", fields[key]["description"])
            self.assertIn("72%", fields[key]["description"])
            self.assertIn("LED-strip", fields[key]["description"])
        self.assertIn("maximum RPM", fields["flash_at"]["description"])

    def test_direct_build_version_matches_manifest(self):
        manifest = mapping(ROOT / "config.yaml")
        dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn(f'ARG BUILD_VERSION={manifest["version"]}', dockerfile)

    def test_runtime_validation_errors_use_english(self):
        with self.assertRaisesRegex(ValueError, "forza_source: a single valid IPv4 address"):
            receiver.validate_options(dict(
                forza_source="", wled_host="127.0.0.1", wled_port=4048,
                led_count=300, fps=12, telemetry_timeout=0.7,
                green_until=58, amber_until=72, flash_at=96,
            ))
        with self.assertRaisesRegex(ValueError, "green_until must be less than amber_until"):
            receiver.validate_options(dict(
                forza_source="127.0.0.1", wled_host="127.0.0.1", wled_port=4048,
                led_count=300, fps=12, telemetry_timeout=0.7,
                green_until=80, amber_until=72, flash_at=96,
            ))


if __name__ == "__main__":
    unittest.main()
