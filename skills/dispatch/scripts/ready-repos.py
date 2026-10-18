#!/usr/bin/env python3
"""List ready tickets across main checkouts; stdout is JSON, failures go to stderr."""
import json
import os
from pathlib import Path
import subprocess
import sys


def repositories(root):
    for directory, dirs, files in os.walk(root):
        path = Path(directory)
        if ".git" in files:
            dirs.clear()
            continue
        if ".git" in dirs:
            if "tickets" in dirs:
                yield path, "files", "foreman"
            elif ".beads" in dirs:
                yield path, "beads", "bd"
        dirs[:] = sorted(set(dirs) - {".git", ".beads", "tickets", "node_modules", "deps", "_build"})
        if len(path.relative_to(root).parts) >= 4:
            dirs.clear()


def main():
    root = Path(sys.argv[1]).expanduser().resolve() if len(sys.argv) > 1 else Path.home() / "dev"
    results = []
    failed = False
    if not root.is_dir():
        print(f"{root}: not a directory", file=sys.stderr)
        return 1
    for repo, tracker, cli in repositories(root):
        try:
            command = [cli, "ready", "--json"]
            if tracker == "beads":
                command.extend(["--limit", "0"])
            result = subprocess.run(
                command, cwd=repo, text=True, capture_output=True, timeout=30,
            )
            if result.stderr.strip():
                print(f"{repo}: {result.stderr.strip()}", file=sys.stderr)
            if result.returncode:
                raise ValueError(f"{cli} ready exited {result.returncode}: {result.stdout.strip()}")
            tickets = json.loads(result.stdout)
            if not isinstance(tickets, list) or any(
                not isinstance(ticket, dict) or not isinstance(ticket.get("id"), str)
                for ticket in tickets
            ):
                raise ValueError(f"{cli} ready did not return a ticket list")
            results.append({"repo": str(repo), "tracker": tracker, "tickets": tickets})
        except (OSError, ValueError, subprocess.TimeoutExpired) as error:
            print(f"{repo}: {error}", file=sys.stderr)
            failed = True
    print(json.dumps(results, indent=2))
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
