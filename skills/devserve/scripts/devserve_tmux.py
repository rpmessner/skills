"""tmux process adapter and private, atomic registry. No shell commands from config."""
import contextlib
import fcntl
import json
import os
from pathlib import Path
import re
import signal
import sys
import tempfile
import time
import uuid


def state_dir():
    return Path(os.environ.get('DEVSERVE_STATE_DIR') or
                str(Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'devserve'))


def read_env(path):
    """Literal dotenv subset; never execute shell substitutions or expose values in errors."""
    status = Path(path).stat()
    if status.st_uid != os.getuid() or status.st_mode & 0o077:
        raise ValueError('env_file must be owned by you and mode 0600')
    values = {}
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'(?:export\s+)?([A-Z_][A-Z0-9_]*)=(.*)', line)
        if not match:
            raise ValueError(f'env_file line {number}: expected KEY=VALUE')
        key, value = match.groups()
        if key.startswith('DEVSERVE_') or key == 'NOTIFY_SOCKET':
            raise ValueError(f'env_file line {number}: reserved variable')
        if value.startswith(("'", '"')):
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f'env_file line {number}: unmatched quote')
            literal = value[0] == "'"
            value = value[1:-1]
        else:
            literal = False
        if not literal and any(c in value for c in '$`\\'):
            raise ValueError(f'env_file line {number}: use literal values, not substitutions or escapes')
        values[key] = value
    return values


class Backend:
    FORMAT = '#{window_id}\t#{window_name}\t#{pane_pid}\t#{pane_dead}\t#{pid}\tx#{@devserve}'

    def __init__(self, core):
        self.d = core
        self.root = state_dir()
        self.path = self.root / 'previews.json'

    def ensure(self):
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        stat = self.root.stat()
        if stat.st_uid != os.getuid() or stat.st_mode & 0o077:
            raise ValueError('devserve state directory must be private and owned by you (0700)')

    @contextlib.contextmanager
    def locked(self, name='state.lock'):
        self.ensure()
        with open(self.root / name, 'a') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            yield

    def read(self):
        if not self.path.exists():
            return {}
        self.ensure()
        entries = json.loads(self.path.read_text())
        if not isinstance(entries, dict):
            raise ValueError('invalid tmux registry')
        for unit, entry in entries.items():
            if isinstance(entry, dict) and entry.get('socket', '') != os.environ.get('DEVSERVE_TMUX_SOCKET', ''):
                raise ValueError('tmux registry belongs to another socket; use its DEVSERVE_TMUX_SOCKET')
            if (not isinstance(entry, dict) or entry.get('unit') != unit or
                    not re.fullmatch(r'[a-z][a-z0-9_]{0,19}', entry.get('app', '')) or
                    not isinstance(entry.get('worktree'), str) or
                    self.d.names(entry['app'], entry['worktree']) != (unit, entry.get('database'))):
                raise ValueError('invalid tmux registry identity')
        return entries

    def update(self, unit, entry=None, **fields):
        with self.locked():
            entries = self.read()
            if entry is not None:
                entries[unit] = entry
            elif fields:
                entries[unit].update(fields)
            else:
                entries.pop(unit, None)
            fd, name = tempfile.mkstemp(dir=self.root, prefix='.previews-')
            try:
                with os.fdopen(fd, 'w') as stream:
                    json.dump(entries, stream)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(name, self.path)
            finally:
                Path(name).unlink(missing_ok=True)

    def tmux(self, *args):
        socket = os.environ.get('DEVSERVE_TMUX_SOCKET')
        base = ['tmux'] + (['-S' if '/' in socket else '-L', socket] if socket else [])
        return self.d.run(base + list(args), env={k: v for k, v in os.environ.items() if k != 'TMUX'})

    def windows(self):
        try:
            output = self.tmux('list-windows', '-t', '=devserve', '-F', self.FORMAT)
        except ValueError:
            return {}
        return {parts[0]: parts[1:] for line in output.splitlines() if (parts := line.split('\t'))}

    def owned_window(self, entry, windows):
        window = windows.get(entry.get('window'))
        if window:
            name, pid, dead, server, token = window
            expected = (entry['unit'].removesuffix('.service'), str(entry['pid']),
                        str(entry['server']), 'x' + entry['token'])
            if (name, pid, server, token) != expected:
                raise ValueError('tmux window identity changed; refusing to touch it or its database')
        return window

    def rows(self):
        entries = self.read()
        if not entries:
            return []
        windows = self.windows()
        rows = []
        for entry in entries.values():
            window = self.owned_window(entry, windows)
            alive = bool(window and window[2] == '0')
            state = entry['state']
            if not alive and state in ('starting', 'running'):
                state, _ = self.d.step(state, 'error')
            rows.append(dict(entry, state=state, pid=entry.get('pid', 0) if alive else 0,
                             missing=not Path(entry['worktree']).is_dir()))
        return rows

    def log_path(self, unit):
        return self.root / (unit + '.log')

    def launch(self, meta):
        unit = meta['unit']
        meta = dict(meta, backend='tmux', token=uuid.uuid4().hex,
                    socket=os.environ.get('DEVSERVE_TMUX_SOCKET', ''), previous=meta['state'],
                    state=self.d.step(meta['state'], 'up')[0])
        self.update(unit, entry=meta)
        argv = [sys.executable, str(Path(self.d.__file__).resolve()), '_tmux_worker', str(self.root), unit, meta['socket']]
        try:
            try:
                self.tmux('has-session', '-t', '=devserve')
                exists = True
            except ValueError:
                exists = False
            command = ['new-window', '-t', '=devserve:'] if exists else ['new-session', '-s', 'devserve']
            output = self.tmux(*command, '-d', '-P', '-F', self.FORMAT, '-n', unit.removesuffix('.service'), '--', *argv)
            window, _, pid, _, server, _ = output.split('\t')
            self.tmux('set-option', '-w', '-t', window, '@devserve', meta['token'])
            for option, value in (('remain-on-exit', 'on'), ('automatic-rename', 'off'), ('allow-rename', 'off')):
                self.tmux('set-option', '-w', '-t', window, option, value)
            self.update(unit, window=window, pid=int(pid), server=int(server))
        except BaseException:
            self.update(unit, state=self.d.step('starting', 'error')[0])
            raise

    def wait_exit(self, unit):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if not next(r for r in self.rows() if r['unit'] == unit)['pid']:
                return
            time.sleep(0.05)
        raise ValueError('tmux worker did not stop; database retained')

    def down(self, row, drop, quiet=False):
        # Re-observe before signalling: never trust a PID read by an earlier ls.
        current = self.read()[row['unit']]
        window = self.owned_window(current, self.windows())
        if window and window[2] == '0':
            os.kill(current['pid'], signal.SIGTERM)
            self.wait_exit(row['unit'])
        window = self.owned_window(current, self.windows())
        if window:
            self.tmux('kill-window', '-t', current['window'])
        state = self.read()[row['unit']]['state']
        target, _ = self.d.step(state, 'down')
        self.update(row['unit'], state=target)
        if drop:
            self.d.step(target, 'drop')
            # Load secrets only in the cleanup process, never into the tmux server.
            self.d.run([sys.executable, str(Path(self.d.__file__).resolve()), '_tmux_drop',
                        str(self.root), row['unit']])
            self.update(row['unit'])
            self.log_path(row['unit']).unlink(missing_ok=True)
        if not quiet:
            print(row['unit'] + (' removed' if drop else ' stopped (database kept)'))

    def logs(self, row, follow):
        argv = ['tail', '-n', '100'] + (['-f'] if follow else []) + [str(self.log_path(row['unit']))]
        os.execvp(argv[0], argv)

    def worker(self, unit, drop=False):
        deadline = time.monotonic() + 10
        while True:
            meta = self.read()[unit]
            if drop or 'window' in meta:
                break
            if meta['state'] == 'failed' or time.monotonic() >= deadline:
                return 1
            time.sleep(0.02)
        if meta['config'].get('env_file'):
            os.environ.update(read_env(meta['config']['env_file']))
        os.environ.update(meta['config']['env'])
        if drop:
            self.d.drop_database(meta)
            return 0
        fd = os.open(self.log_path(unit), os.O_CREAT | os.O_APPEND | os.O_WRONLY, 0o600)
        os.dup2(fd, 1)
        os.dup2(fd, 2)
        os.close(fd)
        meta['state'] = meta['previous']
        return self.d.worker(meta, publish=lambda state: self.update(unit, state=state), tmux=True)
