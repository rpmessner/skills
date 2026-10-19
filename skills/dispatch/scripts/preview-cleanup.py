#!/usr/bin/env python3
"""Remove devserve previews owned by one dispatched session."""

import argparse
import json
import subprocess
import sys


def previews():
    result = subprocess.run(["devserve", "ls", "--json"], check=True,
                            capture_output=True, text=True, timeout=30)
    rows = json.loads(result.stdout)["previews"]
    if not isinstance(rows, list) or any(
        not isinstance(row, dict)
        or not isinstance(row.get("owner"), str) or not row["owner"]
        or not isinstance(row.get("unit"), str)
        or not row["unit"].startswith("devserve-")
        or not row["unit"].endswith(".service")
        for row in rows
    ):
        raise ValueError("invalid devserve preview listing")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("owner", help="Exact dispatch session/window name")
    args = parser.parse_args()
    if not args.owner.strip():
        parser.error("owner must not be empty")
    try:
        for preview in previews():
            if preview["owner"] == args.owner:
                subprocess.run(["devserve", "down", preview["unit"], "--drop-db"],
                               check=True, timeout=180)
        if any(preview["owner"] == args.owner for preview in previews()):
            raise ValueError(f"previews still registered for {args.owner}")
        print(f"Cleaned previews for {args.owner}")
        return 0
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(f"Preview cleanup failed; keep the session window: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
