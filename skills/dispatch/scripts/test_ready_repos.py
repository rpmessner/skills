import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("ready-repos.py")


class ReadyReposTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.dev = self.root / "dev"
        self.dev.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.env = {**os.environ, "PATH": str(self.bin)}

    def repo(self, name, tracker, *, worktree=False):
        repo = self.dev / name
        repo.mkdir(parents=True)
        if worktree:
            (repo / ".git").write_text("gitdir: fake-worktree\n")
        else:
            (repo / ".git").mkdir()
        (repo / tracker).mkdir()
        return repo

    def cli(self, name):
        script = self.bin / name
        script.write_text(
            f"#!{sys.executable}\n"
            "import json, pathlib, sys\n"
            f"assert sys.argv[1:] in ([['ready', '--json'], ['ready', '--json', '--limit', '0']] if {name!r} == 'bd' else [['ready', '--json']])\n"
            "repo = pathlib.Path.cwd()\n"
            f"assert ('foreman' if (repo / 'tickets').is_dir() else 'bd') == {name!r}\n"
            "response = (repo / 'ready.json').read_text()\n"
            f"if {name!r} == 'bd' and '--limit' not in sys.argv and (repo / 'capped').exists():\n"
            "    response = json.dumps(json.loads(response)[:100])\n"
            "    print('Showing 100 ready issues; use --limit 0', file=sys.stderr)\n"
            "print(response)\n"
        )
        script.chmod(0o755)

    def run_listing(self):
        return subprocess.run(
            [sys.executable, str(SCRIPT), str(self.dev)],
            env=self.env, text=True, capture_output=True, check=False,
        )

    def test_mixed_repos_preserve_ready_tickets_and_prefer_files(self):
        files = self.repo("utils/files repo", "tickets")
        (files / ".beads").mkdir()
        beads = self.repo("games/beads", ".beads")
        ready = [{"id": "demo-abc.1", "title": "Foundation", "priority": 2}]
        for repo in [files, beads]:
            (repo / "ready.json").write_text(json.dumps(ready))
        self.cli("foreman")
        self.cli("bd")
        result = self.run_listing()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [
            {"repo": str(beads), "tracker": "beads", "tickets": ready},
            {"repo": str(files), "tracker": "files", "tickets": ready},
        ])
        self.assertEqual(result.stderr, "")

    def test_files_only_needs_no_bd_and_ignores_dependency_trees(self):
        repo = self.repo("files", "tickets")
        (repo / "ready.json").write_text("[]")
        self.repo("node_modules/ignored", ".beads")
        self.repo("deps/ignored", ".beads")
        self.repo("_build/ignored", ".beads")
        self.repo("a/b/c/d/too-deep", ".beads")
        (self.dev / "not-a-repo/tickets").mkdir(parents=True)
        self.cli("foreman")
        result = self.run_listing()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [
            {"repo": str(repo), "tracker": "files", "tickets": []},
        ])

    def test_beads_frontier_is_not_truncated_at_default_limit(self):
        repo = self.repo("large", ".beads")
        ready = [{"id": f"demo-{number}"} for number in range(188)]
        (repo / "ready.json").write_text(json.dumps(ready))
        (repo / "capped").touch()
        self.cli("bd")
        result = self.run_listing()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)[0]["tickets"], ready)
        self.assertEqual(result.stderr, "")

    def test_worktrees_do_not_duplicate_main_checkout_frontiers(self):
        expected = []
        for name, tracker, cli in [("beads", ".beads", "bd"), ("files", "tickets", "foreman")]:
            ready = [{"id": f"{name}-abc"}]
            main = self.repo(f"{name}-main", tracker)
            linked = self.repo(f"{name}-worktree", tracker, worktree=True)
            for repo in [main, linked]:
                (repo / "ready.json").write_text(json.dumps(ready))
            self.cli(cli)
            expected.append({"repo": str(main), "tracker": name, "tickets": ready})
        result = self.run_listing()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), expected)
        self.assertEqual(result.stderr, "")

    def test_failed_repo_is_reported_without_hiding_healthy_repo(self):
        broken = self.repo("a-broken", ".beads")
        healthy = self.repo("z-healthy", "tickets")
        (healthy / "ready.json").write_text('[{"id":"ok-abc"}]')
        self.cli("foreman")
        for response in [None, "warning: unavailable", '{"unexpected":true}']:
            with self.subTest(response=response):
                if response is not None:
                    self.cli("bd")
                    (broken / "ready.json").write_text(response)
                result = self.run_listing()
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertIn(str(broken), result.stderr)
                self.assertEqual(json.loads(result.stdout), [
                    {"repo": str(healthy), "tracker": "files", "tickets": [{"id": "ok-abc"}]},
                ])


if __name__ == "__main__":
    unittest.main()
