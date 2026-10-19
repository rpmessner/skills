#!/usr/bin/env python3
"""Real tmux acceptance probe; isolated server, stub pi, no user shell config."""
import os
from pathlib import Path
import subprocess
import tempfile
import time

D = Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix="pane-check-", dir=D) as tmp:
        root = Path(tmp)
        socket = root.name
        env = dict(os.environ, PATH=f"{root}:/usr/bin:/bin", PI_WAIT_INTERVAL="0.1",
                   PI_WAIT_IDLE="30", CHECK_ROOT=str(root))
        for name, text in {
            "zsh": '#!/bin/bash\nexec /usr/bin/zsh -f -c "$2"\n',
            "pi": '''#!/usr/bin/python3
import os, pathlib, time
name = os.environ["FOREMAN_SESSION"]
print("READY " + name, flush=True)
while not (pathlib.Path(os.environ["CHECK_ROOT"]) / name).exists(): time.sleep(.05)
print(name.upper() + " DONE", flush=True)
''',
        }.items():
            path = root / name
            path.write_text(text)
            path.chmod(0o755)

        def tmux(*args):
            return subprocess.check_output(["tmux", "-L", socket, *args], env=env, text=True).strip()

        def script(name, *args):
            return subprocess.check_output(["bash", str(D / name), *args], env=env, text=True).strip()

        try:
            tmux("-f", "/dev/null", "new-session", "-d", "-s", "scratch", "-n", "epic",
                 "-x", "160", "-y", "60", "sleep 300")
            env["TMUX"] = tmux("display-message", "-p", "#{socket_path},#{pid},0")
            caller = tmux("display-message", "-p", "#{pane_id}")
            env["TMUX_PANE"] = caller
            brief = root / "brief"
            brief.write_text("Scratch acceptance only.")
            panes = {}
            for name in ("build-one", "build-two"):
                print(script("pi-window", "--pane", name, str(root), str(brief)), flush=True)
                panes[name] = script("pi-pane", name)
                assert tmux("show-options", "-p", "-v", "-t", panes[name], "@build") == name
                assert tmux("display-message", "-p", "-t", panes[name], "#{pane_title}") == name
                assert tmux("display-message", "-p", "-t", panes[name], "#{window_id}") == tmux("display-message", "-p", "-t", caller, "#{window_id}")
                proc = subprocess.Popen(["bash", str(D / "pi-wait"), "--pane", name,
                                         name.upper() + " DONE", "10"], env=env,
                                        stdout=subprocess.PIPE, text=True)
                try:
                    time.sleep(.5)
                    (root / name).touch()
                    out, _ = proc.communicate(timeout=15)
                    assert (proc.returncode, out.strip()) == (0, "DONE"), out
                finally:
                    if proc.poll() is None:
                        proc.kill()
                        proc.wait()
                print(f"{name}: found {panes[name]}, wait DONE", flush=True)
            duplicate = subprocess.run(["bash", str(D / "pi-window"), "--pane", "build-one",
                                        str(root), str(brief)], env=env, capture_output=True, text=True)
            assert duplicate.returncode == 1, duplicate
            print("duplicate build-one refused", flush=True)
            assert len(tmux("list-windows", "-F", "#{window_id}").splitlines()) == 1
            assert tmux("display-message", "-p", "#{pane_id}") == caller
            tmux("kill-pane", "-t", script("pi-pane", "build-one"))
            remaining = tmux("list-panes", "-F", "#{pane_id}").splitlines()
            assert set(remaining) == {caller, panes["build-two"]}, remaining
            assert script("pi-pane", "build-two") == panes["build-two"]
            gone = subprocess.run(["bash", str(D / "pi-wait"), "--pane", "build-one", "DONE", "1"],
                                  env=env, text=True, capture_output=True)
            assert (gone.returncode, gone.stdout.strip()) == (2, "GONE")
            print("build-one killed: GONE; build-two and coordinator intact; one window", flush=True)
        finally:
            subprocess.run(["tmux", "-L", socket, "kill-server"], env=env, capture_output=True)
    print("scratch acceptance PASS")


if __name__ == "__main__":
    main()
