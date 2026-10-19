"""Real pi/model, fake foreman. Writes only beneath the supplied worktree evidence dir."""
import atexit
import base64
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time

extension = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
agent = out / "agent"
agent.mkdir(exist_ok=True)
scratch = out / "scratch"
scratch.mkdir(exist_ok=True)
bin_dir = out / "bin"
bin_dir.mkdir(exist_ok=True)
log = out / "foreman.jsonl"
log.write_text("")
fake = bin_dir / "foreman"
fake.write_text('#!/usr/bin/python3\nimport json,sys\nwith open(' + repr(str(log)) + ', "a") as f: f.write(json.dumps(sys.argv[1:])+"\\n")\n')
fake.chmod(0o755)
(agent / "settings.json").write_text(json.dumps({"retry": {"enabled": False}, "enableInstallTelemetry": False}))
settings = Path.home() / ".pi/agent/settings.json"
before = hashlib.sha256(settings.read_bytes()).hexdigest()
# --no-refresh reads existing credentials without updating the real agent directory.
credential = subprocess.check_output(["pi", "auth", "check", "--provider", "openai-codex", "--no-refresh", "--credentials"], text=True).strip()
# Codex requires an OAuth credential, not an --api-key override. Keep this temporary
# file owner-only and remove it before the check returns; never retain it as evidence.
credential_file = agent / "auth.json"
claims = json.loads(base64.urlsafe_b64decode(credential.split(".")[1] + "=="))
credential_file.touch(mode=0o600)
atexit.register(lambda: credential_file.unlink(missing_ok=True))
credential_file.write_text(json.dumps({"openai-codex": {"type": "oauth", "access": credential, "refresh": "", "expires": claims["exp"] * 1000}}))
env = dict(os.environ, PI_CODING_AGENT_DIR=str(agent), PI_OFFLINE="1", PATH=f"{bin_dir}:{os.environ['PATH']}",
           FOREMAN_TICKETS="fm-live", FOREMAN_SESSION="sk-piwait-live", FOREMAN_ACTOR="pi")
args = ["pi", "--mode", "rpc", "--no-session", "--offline", "-ne", "-ns", "-np", "-nc", "--no-themes", "--no-tools",
        "-e", str(extension), "-e", str(extension / "fixtures/prompts.ts"), "--model", "openai-codex/gpt-6-astra", "--thinking", "minimal"]
events = queue.Queue()
with (out / "stderr.txt").open("w") as stderr:
    child = subprocess.Popen(args, cwd=scratch, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
    def reader():
        with (out / "events.jsonl").open("wb") as evidence:
            for line in child.stdout:
                evidence.write(line)
                evidence.flush()
                events.put(json.loads(line))
    threading.Thread(target=reader, daemon=True).start()
    def send(message):
        child.stdin.write((json.dumps({"type": "prompt", "message": message}) + "\n").encode())
        child.stdin.flush()
    def settled():
        deadline = time.monotonic() + 90
        texts = []
        while time.monotonic() < deadline:
            event = events.get(timeout=max(0.1, deadline - time.monotonic()))
            if event["type"] == "response" and not event.get("success", True):
                raise AssertionError(event)
            if event["type"] == "extension_error":
                raise AssertionError(event)
            if event["type"] == "message_end" and event["message"]["role"] == "assistant":
                message = event["message"]
                assert message["stopReason"] == "stop", message.get("errorMessage", message["stopReason"])
                texts.extend(c["text"] for c in message["content"] if c["type"] == "text")
            if event["type"] == "agent_settled":
                return texts
        raise AssertionError("pi did not settle")
    def calls(count):
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            rows = [json.loads(line) for line in log.read_text().splitlines()]
            if len(rows) >= count:
                assert len(rows) == count, rows
                return rows
            time.sleep(0.02)
        raise AssertionError(f"expected {count} foreman calls")
    try:
        send("Ask me exactly this question and then stop: Which color should I use?")
        question = settled()
        first = calls(1)
        assert first[0][:5] == ["ask", "session_waiting", "fm-live", "--reason", "input"], first
        send("Blue. Reply only with the word Acknowledged and a period. Do not ask another question.")
        answer = settled()
        final = calls(2)
        assert final[1][:3] == ["session-hook", "UserPromptSubmit", "fm-live"], final
        for method, command, reason, count in [("confirm", "/wait-confirm", "permission", 3), ("input", "/wait-input", "input", 5)]:
            send(command)
            deadline = time.monotonic() + 10
            while True:
                event = events.get(timeout=max(0.1, deadline - time.monotonic()))
                if event["type"] == "extension_ui_request" and event.get("method") == method:
                    break
                assert time.monotonic() < deadline, "missing UI prompt"
            waiting = calls(count)
            assert waiting[-1][:5] == ["ask", "session_waiting", "fm-live", "--reason", reason]
            response = {"type": "extension_ui_response", "id": event["id"], "confirmed": True, "value": "blue"}
            child.stdin.write((json.dumps(response) + "\n").encode())
            child.stdin.flush()
            final = calls(count + 1)
            assert final[-1][:3] == ["session-hook", "UserPromptSubmit", "fm-live"]
        after = hashlib.sha256(settings.read_bytes()).hexdigest()
        assert before == after
        result = {"question": question, "answer": answer, "foreman_calls": final, "settings_unchanged": before == after}
        (out / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
    finally:
        credential_file.unlink(missing_ok=True)
        child.stdin.close()
        try:
            child.wait(timeout=8)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait()
