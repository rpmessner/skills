"""pi-wait against a fake tmux whose pane text is a file the test appends to."""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name("pi-wait")
CODEX = "Error: Codex error: The usage limit has been reached"


class PiWaitTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        bin_dir = root / "bin"
        bin_dir.mkdir()
        self.pane = root / "pane"
        self.pane.write_text("")
        tmux = bin_dir / "tmux"
        tmux.write_text(f'''#!/usr/bin/env python3
import sys
if sys.argv[1] == "list-windows":
    print("build")
elif sys.argv[1] == "capture-pane":
    sys.stdout.write(open({str(self.pane)!r}).read())
''')
        tmux.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{bin_dir}:/usr/bin:/bin", PI_WAIT_INTERVAL="0.1",
                        PI_WAIT_IDLE="600")

    def wait(self, *lines, before=()):
        self.write(*before)
        proc = subprocess.Popen(["bash", str(SCRIPT), "build", "BUILD DONE", "10"], env=self.env,
                                stdout=subprocess.PIPE, text=True)
        time.sleep(0.4)  # let pi-wait take its baseline before the session prints
        self.write(*lines)
        out, _ = proc.communicate(timeout=10)
        return proc.returncode, out.strip().splitlines()

    def write(self, *lines):
        with self.pane.open("a") as pane:
            for line in lines:
                pane.write(line + "\n")

    def test_provider_limit_after_start_exits_limited_with_the_line(self):
        code, out = self.wait("working", "  " + CODEX + "  ")
        self.assertEqual(code, 5)
        self.assertEqual(out, ["LIMITED", CODEX])

    def test_anthropic_extra_usage_refusal_is_a_limit(self):
        line = "Error: Third-party apps now draw from your extra usage"
        self.assertEqual(self.wait(line), (5, ["LIMITED", line]))

    def test_rate_limit_429_is_a_limit(self):
        line = "Error: 429 rate limit exceeded, retry later"
        self.assertEqual(self.wait(line), (5, ["LIMITED", line]))

    def test_limit_printed_before_the_wait_started_does_not_count(self):
        code, out = self.wait("BUILD DONE", before=[CODEX, "continue"])
        self.assertEqual((code, out), (0, ["DONE"]))

    def test_limit_words_outside_an_error_line_are_ignored(self):
        code, out = self.wait('  assert msg =~ "usage limit has been reached"', "BUILD DONE")
        self.assertEqual((code, out), (0, ["DONE"]))

    def test_done_beats_limited(self):
        self.assertEqual(self.wait(CODEX, "BUILD DONE"), (0, ["DONE"]))

    def test_trust_prompt_exits_blocked(self):
        code, out = self.wait(" Trust project folder?", " /home/me/dev/new-worktree", " → Trust")
        self.assertEqual(code, 6)
        self.assertEqual(out[0], "BLOCKED")
        self.assertIn("Trust project folder?", out[1])

    def test_screen_unchanged_for_the_idle_limit_exits_idle_with_last_lines(self):
        self.env["PI_WAIT_IDLE"] = "1"
        code, out = self.wait("working", "One gate remains: may I create a fixture commit?")
        self.assertEqual(code, 7)
        self.assertEqual(out[0], "IDLE")
        self.assertIn("One gate remains: may I create a fixture commit?", out)

    def test_a_changing_screen_is_not_idle(self):
        self.env["PI_WAIT_IDLE"] = "1"
        self.write("start")
        proc = subprocess.Popen(["bash", str(SCRIPT), "build", "BUILD DONE", "10"], env=self.env,
                                stdout=subprocess.PIPE, text=True)
        for i in range(12):  # keep printing for about 1.2 s, longer than the idle limit
            time.sleep(0.1)
            self.write(f"step {i}")
        self.write("BUILD DONE")
        out, _ = proc.communicate(timeout=10)
        self.assertEqual((proc.returncode, out.strip().splitlines()), (0, ["DONE"]))

    def test_done_beats_idle(self):
        self.env["PI_WAIT_IDLE"] = "1"
        self.assertEqual(self.wait("BUILD DONE"), (0, ["DONE"]))


if __name__ == "__main__":
    unittest.main()
