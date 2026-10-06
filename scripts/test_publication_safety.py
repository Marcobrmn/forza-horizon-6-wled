"""Local regression tests; synthetic credentials are generated and never printed."""
import os
import pathlib
import secrets
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).with_name("publication_safety.py")
GITLEAKS = os.environ.get("GITLEAKS_BIN", "gitleaks")


class GateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = pathlib.Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main", str(self.repo)], check=True)

    def check(self, files, expected=0, binary=GITLEAKS):
        for name, content in files.items():
            dest = self.repo / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content if isinstance(content, bytes) else content.encode())
        subprocess.run(["git", "add", "--all"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "commit", "-qm", "fixture"], cwd=self.repo, check=True, capture_output=True)
        env = {**os.environ, "GITLEAKS_BIN": binary}
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo, env=env,
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def test_clean_public_examples_and_loopback(self):
        self.check({"docs.md": "127.0.0.1 192.0.2.20 /home/user /Users/example /home/runner"})

    def test_private_path_text_and_utf16_binary(self):
        secret_path = "/" + "Users" + "/" + "private-owner" + "/file"
        result = self.check({"note.txt": secret_path}, expected=1)
        self.assertIn("absolute home path", result)
        self.assertNotIn("private-owner", result)
        binary = ("/" + "home" + "/" + "private-owner").encode("utf-16-le")
        self.assertIn("absolute home path", self.check({"binary.dat": b"\xff\x00" + binary}, expected=1))

    def test_private_ipv4_binary_and_bogus_octets(self):
        address = ".".join(map(str, (192, 168, 72, 19)))
        result = self.check({"image.bin": b"\x00\xff" + address.encode() + b"\x00 999.999.999.999"}, expected=1)
        self.assertIn("RFC1918 address", result)
        self.assertNotIn(address, result)

    def test_gitleaks_secret_even_with_untrusted_config(self):
        token = "ghp_" + secrets.token_hex(18)
        # A tracked config must not disable the trusted default rules.
        result = self.check({"note.txt": "token=" + token,
                             ".gitleaks.toml": "title='disabled'\n"}, expected=1)
        self.assertIn("Gitleaks secret", result)
        self.assertNotIn(token, result)

    def test_private_build_paths_in_binary(self):
        for prefix in (("private", "var", "folders", "aa", "build"), ("builds", "agent", "project")):
            with self.subTest(prefix=prefix):
                path = "/" + "/".join(prefix)
                self.assertIn("absolute build path", self.check({"binary.dat": b"\x00" + path.encode() + b"\x00"}, expected=1))

    def test_secret_removed_from_head_still_fails_history(self):
        token = "ghp_" + secrets.token_hex(18)
        self.check({"note.txt": "token=" + token}, expected=1)
        (self.repo / "note.txt").write_text("clean\n")
        subprocess.run(["git", "add", "note.txt"], cwd=self.repo, check=True, capture_output=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "commit", "-qm", "cleaned"], cwd=self.repo, check=True, capture_output=True)
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo,
                                env={**os.environ, "GITLEAKS_BIN": GITLEAKS},
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Gitleaks history secret", result.stdout)
        self.assertNotIn(token, result.stdout + result.stderr)

    def test_scanner_failure_fails_closed(self):
        self.assertIn("ERROR", self.check({"safe.txt": "safe"}, expected=1,
                                          binary=str(self.repo / "missing-scanner")))

    def test_untracked_not_in_committed_tree(self):
        self.check({"safe.txt": "safe"})
        (self.repo / "untracked.txt").write_text("/" + "Users" + "/" + "private-owner")
        result = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo,
                                env={**os.environ, "GITLEAKS_BIN": GITLEAKS},
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
