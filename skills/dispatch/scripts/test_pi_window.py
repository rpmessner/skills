"""Process-boundary tests; no real tmux, pi session, board or user config."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("pi-window")
SENDER = SCRIPT.parents[2] / "foreman/scripts/foreman-send"


class PiWindowTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.repo = self.root / "work tree"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "build"], cwd=self.repo, check=True)
        subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                        "commit", "-qm", "base", "--allow-empty"], cwd=self.repo, check=True)
        self.base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=self.repo, text=True).strip()
        self.brief = self.root / "brief.md"
        self.brief.write_text("Build this slice.\n")
        self.report = self.repo / "report.md"
        self.log = self.root / "events"
        self.env = dict(os.environ, PATH=f"{self.bin}:/usr/bin:/bin", TMUX="fake",
                        LOG=str(self.log), FOREMAN_ACTOR="inherited", FOREMAN_SESSION="old")
        self.executable("tmux", '''import os, subprocess, sys
args = sys.argv[1:]
if args[0] == "new-window":
    subprocess.run(args[-1], shell=True, cwd=args[args.index("-c") + 1], stdin=subprocess.DEVNULL)
''')
        self.executable("zsh", '''import subprocess, sys
sys.exit(subprocess.call(["/usr/bin/zsh", "-f", "-c", sys.argv[-1]]))
''')
        self.executable("pi", '''import json, os, sys
with open(os.environ["LOG"], "a") as f:
    f.write(json.dumps(["pi", os.environ.get("FOREMAN_ACTOR"), os.environ.get("FOREMAN_SESSION"), sys.argv[1:]]) + "\\n")
''')
        self.executable("foreman", '''import json, os, sys
with open(os.environ["LOG"], "a") as f:
    f.write(json.dumps(["foreman", os.environ.get("FOREMAN_ACTOR"), os.environ.get("FOREMAN_SESSION"), sys.argv[1:], os.getcwd()]) + "\\n")
sys.exit(int(os.environ.get("FOREMAN_EXIT", "0")))
''')

    def executable(self, name, body):
        path = self.bin / name
        path.write_text("#!/usr/bin/python3\n" + body)
        path.chmod(0o755)

    def launch(self, *args):
        return subprocess.run(["bash", str(SCRIPT), "slice", str(self.repo), str(self.brief), *args],
                              env=self.env, text=True, capture_output=True, timeout=10)

    def events(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()]

    def test_exports_identity_into_pi(self):
        result = self.launch("--model", "provider/model")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.events()[0], ["pi", "pi", "slice",
                         ["--name", "slice", "--model", "provider/model", "Build this slice."]])

    def test_dispatches_each_ticket_after_launch_with_metadata(self):
        result = self.launch("--bead", "sk-1", "--bead", "sk-2", "--report", str(self.report),
                             "--", "--model", "provider/model", "-e", "/tmp/extension")
        self.assertEqual(result.returncode, 0, result.stderr)
        events = self.events()
        self.assertEqual([event[0] for event in events], ["pi", "foreman", "foreman"])
        self.assertEqual(events[0][3], ["--name", "slice", "--model", "provider/model",
                                       "-e", "/tmp/extension", "Build this slice."])
        for event, ticket in zip(events[1:], ["sk-1", "sk-2"]):
            self.assertEqual(event, ["foreman", "pi", "slice", ["dispatch", ticket,
                "--window", "slice", "--harness", "pi", "--model", "provider/model",
                "--workdir", str(self.repo), "--branch", "build", "--base", self.base,
                "--brief", str(self.brief), "--report", str(self.report)], str(self.repo)])

    def test_brief_path_is_literal_shell_data(self):
        self.brief = self.root / "brief 'with\" $dollars.md"
        self.brief.write_text("Quoted path works.\n")
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.log.exists(), result.stderr)
        self.assertEqual(self.events()[0][3][-1], "Quoted path works.")

    def tracked_launch(self):
        return self.launch("--bead", "sk-1", "--bead", "sk-2", "--report", str(self.report))

    def test_missing_board_warns_once_and_still_launches(self):
        (self.bin / "foreman").unlink()
        result = self.tracked_launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual([event[0] for event in self.events()], ["pi"])
        self.assertEqual(len(result.stderr.splitlines()), 1, result.stderr)
        self.assertIn("warning: foreman", result.stderr)

    def test_refused_or_failed_board_never_fails_launch_or_skips_next_ticket(self):
        for code in (3, 1, 127):
            with self.subTest(code=code):
                self.log.unlink(missing_ok=True)
                self.env["FOREMAN_EXIT"] = str(code)
                result = self.tracked_launch()
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual([event[0] for event in self.events()], ["pi", "foreman", "foreman"])
                self.assertIn("warning: foreman", result.stderr)

    def test_relative_report_and_pi_model_forms(self):
        for model_args in (("-m", "provider/model"), ("--model=provider/model",)):
            with self.subTest(model_args=model_args):
                self.log.unlink(missing_ok=True)
                result = self.launch("--bead", "sk-1", "--report", "reports/slice.md", "--", *model_args)
                self.assertEqual(result.returncode, 0, result.stderr)
                args = self.events()[1][3]
                self.assertEqual(args[args.index("--model") + 1], "provider/model")
                self.assertEqual(args[args.index("--report") + 1], str(self.repo / "reports/slice.md"))

    def test_non_git_workdir_still_launches_with_honest_defaults(self):
        self.repo = self.root / "not-git"
        self.repo.mkdir()
        result = self.launch("--bead", "sk-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.events()[1][3]
        for flag, expected in (("--branch", "unknown"), ("--base", "unknown"), ("--model", "default"),
                               ("--report", str(self.repo / "drafts/sessions/slice.md"))):
            self.assertEqual(args[args.index(flag) + 1], expected)

    def test_duplicate_window_never_launches_or_dispatches(self):
        self.executable("tmux", 'import sys\nif sys.argv[1] == "list-windows": print("slice")\n')
        result = self.tracked_launch()
        self.assertEqual(result.returncode, 1)
        self.assertIn("window already exists", result.stderr)
        self.assertFalse(self.log.exists())

    def test_report_refusal_cannot_prevent_done_marker_under_errexit(self):
        self.env["FOREMAN_EXIT"] = "3"
        result = subprocess.run(["bash", "-ec",
            'bash "$1" report sk-1 --path "$2"; echo "SLICE DONE"',
            "test", str(SENDER), str(self.report)], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "SLICE DONE")
        self.assertIn("warning: foreman exited 3", result.stderr)
        self.assertEqual(self.events()[0][3], ["report", "sk-1", "--path", str(self.report)])

    def test_missing_timeout_skips_board_with_warning(self):
        self.env["PATH"] = str(self.bin)
        result = subprocess.run(["/bin/bash", str(SENDER), "progress", "sk-1", "green"],
                                env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("timeout unavailable", result.stderr)
        self.assertFalse(self.log.exists())

    def test_failed_tmux_launch_does_not_claim_dispatch(self):
        self.executable("tmux", 'import sys\nif sys.argv[1] == "new-window": sys.exit(1)\n')
        result = self.tracked_launch()
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.log.exists())

    def test_hung_board_is_bounded_and_launch_survives(self):
        self.executable("foreman", "import time\ntime.sleep(60)\n")
        result = self.launch("--bead", "sk-1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.events()[0][0], "pi")
        self.assertIn("warning: foreman", result.stderr)


if __name__ == "__main__":
    unittest.main()
