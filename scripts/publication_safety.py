#!/usr/bin/env python3
"""Fail closed on secrets/private locations in the committed checkout tree.

This script must itself be trusted; a PR can modify both it and its workflow.
"""
import ipaddress
import os
import pathlib
import re
import subprocess
import sys
import tempfile

PRIVATE = tuple(ipaddress.ip_network((int(ipaddress.IPv4Address(bytes(octets))), prefix))
                for octets, prefix in (((10, 0, 0, 0), 8), ((172, 16, 0, 0), 12), ((192, 168, 0, 0), 16)))
IPV4 = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])", re.ASCII)
HOME = re.compile(r"(?<![\w/])/(?:Users|home)/([^/\\\s\x00\"'<>:;]+)")
BUILD = re.compile(r"(?<![\w/])/(?:private/var/folders|var/folders|builds|build|workspace|Volumes)/[^\s\\\x00\"'<>:;]+")
PLACEHOLDERS = {"user", "users", "username", "example", "yourname", "your-username", "runner"}


def privacy_categories(data):
    """Inspect raw bytes AND UTF-16 strings, regardless of binary/text classification."""
    views = [data.decode("latin-1")]
    if b"\x00" in data:
        for encoding in ("utf-16-le", "utf-16-be"):
            views.append(data.decode(encoding, errors="ignore"))
    found = set()
    for text in views:
        for match in HOME.finditer(text):
            if match.group(1).lower() not in PLACEHOLDERS:
                found.add("absolute home path")
        if BUILD.search(text):
            found.add("absolute build path")
        for match in IPV4.finditer(text):
            try:
                address = ipaddress.IPv4Address(match.group())
            except ipaddress.AddressValueError:
                continue
            if any(address in network for network in PRIVATE):
                found.add("RFC1918 address")
    return found


def checked_out_blobs():
    tree = subprocess.run(["git", "ls-tree", "-rz", "--full-tree", "HEAD"], check=True, capture_output=True).stdout
    for record in tree.split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        mode, kind, oid = metadata.split()
        if kind != b"blob" or mode not in (b"100644", b"100755", b"120000"):
            raise RuntimeError("unsupported tracked tree entry")
        # git output is bytes; reject unsafe paths rather than risking a traversal or collision.
        path = pathlib.PurePosixPath(os.fsdecode(name))
        if path.is_absolute() or any(part in (".", "..") for part in path.parts) or not path.parts:
            raise RuntimeError("unsafe tracked path")
        blob = subprocess.run(["git", "cat-file", "blob", oid.decode("ascii")], check=True, capture_output=True).stdout
        yield path, blob


def scan(repo=".", gitleaks=None):
    os.chdir(repo)
    if not gitleaks:
        gitleaks = os.environ.get("GITLEAKS_BIN", "gitleaks")
    categories = set()
    count = 0
    with tempfile.TemporaryDirectory(prefix="publication-safety-") as temporary:
        root = pathlib.Path(temporary)
        files = root / "files"
        files.mkdir()
        config = root / "config.toml"
        config.write_text("[extend]\nuseDefault = true\n")
        ignore = root / "empty-ignore"
        ignore.write_text("")
        for path, blob in checked_out_blobs():
            count += 1
            categories.update(privacy_categories(blob))
            target = files.joinpath(*path.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            # Never instantiate a tracked symlink or execute repository code.
            target.write_bytes(blob)
        if not count:
            raise RuntimeError("empty tracked tree")
        result = subprocess.run(
            [gitleaks, "dir", "--config", str(config), "--gitleaks-ignore-path", str(ignore),
             "--ignore-gitleaks-allow", "--exit-code", "42", "--redact=100",
             "--no-banner", "--log-level", "error", str(files)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300,
            env={key: value for key, value in os.environ.items() if not key.startswith("GITLEAKS_")},
        )
        if result.returncode == 42:
            categories.add("Gitleaks secret")
        elif result.returncode != 0:
            raise RuntimeError("Gitleaks failed (output suppressed)")
        history = subprocess.run(
            [gitleaks, "git", "--config", str(config), "--gitleaks-ignore-path", str(ignore),
             "--ignore-gitleaks-allow", "--log-opts=--all", "--exit-code", "42",
             "--redact=100", "--no-banner", "--log-level", "error", "."],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300,
            env={key: value for key, value in os.environ.items() if not key.startswith("GITLEAKS_")},
        )
        if history.returncode == 42:
            categories.add("Gitleaks history secret")
        elif history.returncode != 0:
            raise RuntimeError("Gitleaks history failed (output suppressed)")
    return count, categories


def main():
    try:
        count, categories = scan()
        if categories:
            print("publication-safety: FAILED: " + ", ".join(sorted(categories)) + " (values suppressed)")
            return 1
        print(f"publication-safety: PASS ({count} tracked blobs scanned)")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"publication-safety: ERROR ({type(exc).__name__}; details suppressed)", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
