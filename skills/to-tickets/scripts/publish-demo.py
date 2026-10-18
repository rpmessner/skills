#!/usr/bin/env python3
"""Rehearse the documented publish recipe with a real CLI and no bd on PATH."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--foreman", required=True, type=Path)
parser.add_argument("--erlang-bin", required=True, type=Path)
args = parser.parse_args()
recipe = (Path(__file__).parents[1] / "references/files.md").read_text().split("```bash\n", 1)[1].split("```", 1)[0]

with tempfile.TemporaryDirectory(prefix="publish-files-") as scratch:
    root = Path(scratch)
    repo = root / "repo"
    config = root / "config"
    bin_dir = root / "bin"
    for directory in [repo, config, bin_dir, repo / "tickets"]:
        directory.mkdir()
    for tool in ["bash", "git", "jq", "dirname", "basename"]:
        (bin_dir / tool).symlink_to(shutil.which(tool))
    (bin_dir / "foreman").symlink_to(args.foreman.resolve())
    spec = "## Goal\nPublish offline.\n\n## Acceptance checks\n- [ ] Dependencies determine readiness.\n"
    first = "## What to build\nFoundation.\n\n## Acceptance\n- [ ] Foundation verified.\n"
    next_body = "## What to build\nConsumer.\n\n## Acceptance\n- [ ] Consumer verified.\n"
    for name, body in [("spec.md", spec), ("first.md", first), ("next.md", next_body)]:
        (root / name).write_text(body)
    (config / "foreman.toml").write_text(
        f'[[repos]]\nkey = "demo"\npath = {json.dumps(str(repo))}\nprefix = "demo"\ntickets = "files"\n'
    )
    env = {**os.environ, "PATH": f"{bin_dir}:{args.erlang_bin.resolve()}",
           "FOREMAN_CONFIG_DIR": str(config), "FOREMAN_URL": "http://127.0.0.1:1",
           "SPEC": str(root / "spec.md"), "FIRST_BODY": str(root / "first.md"),
           "NEXT_BODY": str(root / "next.md")}
    assert shutil.which("bd", path=env["PATH"]) is None
    for key in list(env):
        if key.startswith("GIT_"):
            del env[key]

    def run(*command):
        result = subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True, check=True)
        assert not result.stderr, result.stderr
        return result.stdout

    run("git", "init", "--quiet")
    print("bd on PATH: absent; service destination: closed port")
    print(run("bash", "-c", recipe), end="")
    tickets = json.loads(run("foreman", "ls", "--json"))
    epic = next(ticket for ticket in tickets if ticket["type"] == "epic")
    children = sorted((t for t in tickets if t["parent"] == epic["id"]), key=lambda t: t["id"])
    assert len(tickets) == 3 and len(children) == 2
    assert epic["body"].rstrip() == spec.rstrip()
    assert children[0]["body"].rstrip() == first.rstrip()
    assert children[1]["body"].rstrip() == next_body.rstrip()
    assert children[0]["blocked_by"] == []
    assert children[1]["blocked_by"] == [children[0]["id"]]
    assert [t["id"] for t in json.loads(run("foreman", "ready", "--json"))] == [children[0]["id"]]
    print("PASS: exact approved bodies, parent and blocker edges, foundation-only frontier")
    run("foreman", "close", children[0]["id"], "--reason", "Rehearsal verified", "--json")
    assert [t["id"] for t in json.loads(run("foreman", "ready", "--json"))] == [children[1]["id"]]
    print("PASS: closing foundation makes consumer ready")
    print(run("foreman", "check", "--json"), end="")
