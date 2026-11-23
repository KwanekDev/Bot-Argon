#!/usr/bin/env python3
"""Scan tracked files for likely secrets. Exits non-zero if any are found."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {".agents", ".github", "docs", ".venv"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".woff", ".woff2", ".mp4", ".webm", ".pyc", ".lock", ".html", ".zip", ".db"}

KEY_ANY = re.compile(r'(?i)\b(token|secret|password|passwd|api[_-]?key|client[_-]?secret|private[_-]?key)\b\s*[:=]\s*([^\s]+)')
VALID_SECRET = re.compile(r'^[A-Za-z0-9_\.:\-]{16,}$')
KNOWN_PREFIX = re.compile(r'(?i)(sk-|xox[bap]-|ghp_|github_pat_|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|-----BEGIN [A-Z ]*PRIVATE KEY-----)')
PLACEHOLDER = re.compile(r'(?i)(YOUR_|CHANGE-ME|HERE|xxx|placeholder|example|dummy|^<.*>$)')


def main() -> int:
    tracked = subprocess.check_output(["git", "ls-files"], text=True, cwd=ROOT).splitlines()
    problems = []
    for f in tracked:
        p = ROOT / f
        if not p.is_file():
            continue
        if set(p.parts) & EXCLUDED_DIRS:
            continue
        if p.suffix.lower() in SKIP_EXT:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in KEY_ANY.finditer(text):
            val = m.group(2).strip().strip("'")
            if PLACEHOLDER.search(val):
                continue
            if KNOWN_PREFIX.search(val):
                problems.append(f"{f}: {val[:50]}")
                continue
            if not VALID_SECRET.fullmatch(val):
                continue
            problems.append(f"{f}: {m.group(1)}={val[:40]}")
    if problems:
        print("Potential secrets found:")
        for item in problems:
            print(" -", item)
        return 1
    print("OK: no secrets detected in tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
