import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("preview-cleanup.py")


class PreviewCleanupTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=SCRIPT.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.state = self.root / "state.json"
        self.calls = self.root / "calls.jsonl"
        self.env = {**os.environ, "PATH": str(self.root), "STATE": str(self.state),
                    "CALLS": str(self.calls)}
        cli = self.root / "devserve"
        cli.write_text(f"#!{sys.executable}\n" + '''import json, os, pathlib, sys
state = pathlib.Path(os.environ["STATE"])
args = sys.argv[1:]
with open(os.environ["CALLS"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if args == ["ls", "--json"]:
    if os.environ.get("FAIL_LIST"):
        sys.exit(4)
    print(state.read_text())
elif len(args) == 3 and args[0] == "down" and args[2] == "--drop-db":
    if os.environ.get("FAIL_DOWN"):
        sys.exit(5)
    data = json.loads(state.read_text())
    if not os.environ.get("KEEP_PREVIEW"):
        data["previews"] = [p for p in data["previews"] if p["unit"] != args[1]]
        state.write_text(json.dumps(data))
else:
    sys.exit(6)
''')
        cli.chmod(0o755)

    def seed(self, previews):
        self.state.write_text(json.dumps({"previews": previews, "main_units": [
            {"unit": "foreman-web.service", "owner": "build-one"}]}))

    def run_cleanup(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              env=self.env, capture_output=True, text=True)

    def commands(self):
        return [json.loads(line) for line in self.calls.read_text().splitlines()]

    def test_drops_all_exact_owner_previews_and_leaves_others_and_mains(self):
        other = {"unit": "devserve-other.service", "owner": "build-one-more"}
        self.seed([{"unit": "devserve-a.service", "owner": "build-one"}, other,
                   {"unit": "devserve-b.service", "owner": "build-one", "state": "failed"}])
        result = self.run_cleanup("build-one")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.state.read_text())["previews"], [other])
        self.assertEqual(self.commands(), [["ls", "--json"],
            ["down", "devserve-a.service", "--drop-db"],
            ["down", "devserve-b.service", "--drop-db"], ["ls", "--json"]])

    def test_empty_owner_is_rejected_before_listing(self):
        self.seed([])
        result = self.run_cleanup("")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.calls.exists())

    def test_malformed_listing_is_rejected_before_any_drop(self):
        for payload in ["not json", "{}", '{"previews": {}}',
                        '{"previews": [{"owner": "build-one", "unit": "devserve-a.service"}, {}]}']:
            with self.subTest(payload=payload):
                self.state.write_text(payload)
                self.calls.write_text("")
                result = self.run_cleanup("build-one")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.commands(), [["ls", "--json"]])

    def test_no_owned_previews_is_successful_and_repeatable(self):
        self.seed([])
        for _ in range(2):
            result = self.run_cleanup("build-one")
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.commands(), [["ls", "--json"]] * 4)

    def test_failed_list_or_drop_or_remaining_preview_blocks_closeout(self):
        for failure in ["FAIL_LIST", "FAIL_DOWN", "KEEP_PREVIEW"]:
            with self.subTest(failure=failure):
                self.seed([{"unit": "devserve-a.service", "owner": "build-one"}])
                self.env[failure] = "1"
                result = self.run_cleanup("build-one")
                del self.env[failure]
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("keep the session window", result.stderr)
                self.assertEqual(len(json.loads(self.state.read_text())["previews"]), 1)

    def test_missing_devserve_blocks_closeout(self):
        (self.root / "devserve").unlink()
        result = self.run_cleanup("build-one")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("keep the session window", result.stderr)


if __name__ == "__main__":
    unittest.main()
