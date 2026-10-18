"""Opt-in real services: DEVSERVE_INTEGRATION=1 python3 -m unittest discover ..."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.request

SCRIPT = Path(__file__).with_name('devserve').resolve()


@unittest.skipUnless(os.environ.get('DEVSERVE_INTEGRATION') == '1', 'requires real user systemd and Postgres')
class IntegrationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='devserve test-')
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, DEVSERVE_CONFIG_DIR=str(self.root), FOREMAN_SESSION='stub-session')
        self.pg = dict(os.environ, PGHOST='localhost', PGUSER='postgres', PGPASSWORD='postgres', PGDATABASE='postgres', PSQLRC='/dev/null')
        self.app = 'devserve_test' + str(os.getpid())
        self.source = 'devserve_test_source_' + str(os.getpid())
        self.main_unit = 'devserve-' + self.app + '-main.service'
        self.addCleanup(self.cleanup)
        self.sql(f'CREATE DATABASE {self.source}')
        self.sql('CREATE TABLE evidence (value text); INSERT INTO evidence VALUES (\'copied-data\')', self.source)
        self.main = self.root / 'main'
        self.main.mkdir()
        self.run_cmd('git', 'init', '-q', '-b', 'main', cwd=self.main)
        (self.main / 'app.py').write_text('''import http.server, json, os, subprocess
from urllib.parse import urlsplit, unquote
u = urlsplit(os.environ['DATABASE_URL'])
assert os.environ['STUB_SECRET'] == 'devserve-unique-secret-canary'
env = dict(os.environ, PGHOST=u.hostname, PGPORT=str(u.port), PGUSER=unquote(u.username), PGPASSWORD=unquote(u.password or ''))
value = subprocess.check_output(['psql', '-XAt', '-d', u.path[1:], '-c', 'SELECT value FROM evidence'], env=env, text=True).strip()
class Handler(http.server.BaseHTTPRequestHandler):
 def do_GET(self):
  body = json.dumps(dict(value=value, database=u.path[1:], preview=os.environ['PREVIEW'])).encode()
  self.send_response(200); self.end_headers(); self.wfile.write(body)
print('stub-ready', flush=True)
http.server.HTTPServer(('127.0.0.1', int(os.environ['PORT'])), Handler).serve_forever()
''')
        self.run_cmd('git', 'add', '.', cwd=self.main)
        self.run_cmd('git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'stub', cwd=self.main)
        self.trees = [self.root / 'one', self.root / 'two']
        for tree in self.trees:
            self.run_cmd('git', 'worktree', 'add', '-qb', tree.name, str(tree), cwd=self.main)
        (self.root / 'secrets').write_text('PGHOST=localhost\nPGUSER=postgres\nPGPASSWORD=postgres\nSTUB_SECRET=devserve-unique-secret-canary\n')
        (self.root / 'secrets').chmod(0o600)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            self.port = sock.getsockname()[1]
        self.config = f'''[[apps]]
name = "{self.app}"
path = "{self.main}"
ports = [{self.port}, {self.port + 9}]
start = ["/usr/bin/python3", "app.py"]
data = "copy"
source_database = "{self.source}"
migrate = ["/usr/bin/true"]
env_file = "{self.root / 'secrets'}"
main_units = ["{self.main_unit}"]
'''
        (self.root / 'apps.toml').write_text(self.config)
        self.transcript = []

    def run_cmd(self, *args, **kwargs):
        return subprocess.run(args, text=True, capture_output=True, check=True, timeout=120, **kwargs).stdout.strip()

    def sql(self, sql, db='postgres'):
        return self.run_cmd('psql', '-XAt', '-v', 'ON_ERROR_STOP=1', '-d', db, '-c', sql, env=self.pg)

    def cli(self, *args, ok=True):
        result = subprocess.run(['python3', str(SCRIPT), *map(str, args)], env=self.env,
                                text=True, capture_output=True, timeout=150)
        self.transcript.append('$ devserve ' + ' '.join(map(str, args)) + '\n' + result.stdout + result.stderr)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result.stdout.strip()

    def rows(self):
        return json.loads(self.cli('ls', '--json'))['previews']

    def preview_argv(self, unit):
        group = self.run_cmd('systemctl', '--user', 'show', unit, '--property=ControlGroup', '--value')
        self.assertTrue(group.startswith('/'), 'preview must have a cgroup')
        root = Path('/sys/fs/cgroup') / group.lstrip('/')
        pids = {int(pid) for file in root.rglob('cgroup.procs') for pid in file.read_text().split()}
        commands = {}
        for pid in pids:
            try:
                commands[pid] = Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0', b' ').decode()
            except FileNotFoundError:
                pass  # A short-lived child may exit between the cgroup and /proc reads.
        main = int(self.run_cmd('systemctl', '--user', 'show', unit, '--property=MainPID', '--value'))
        self.assertIn(main, commands, 'argv inspection must include the live preview worker')
        return commands

    def assert_no_secrets(self, output, boundary):
        for secret in ('devserve-unique-secret-canary', 'postgres:postgres', 'PGPASSWORD=postgres'):
            self.assertFalse(secret in output, f'secret in {boundary}')

    def cleanup(self):
        units = self.run_cmd('systemctl', '--user', 'list-units', '--all', '--plain', '--no-legend', 'devserve-' + self.app + '-*')
        for line in units.splitlines():
            unit = line.split()[0]
            subprocess.run(['systemctl', '--user', 'stop', unit], capture_output=True)
            subprocess.run(['systemctl', '--user', 'reset-failed', unit], capture_output=True)
        dbs = self.sql(f"SELECT datname FROM pg_database WHERE datname LIKE '{self.app}_preview_%' OR datname = '{self.source}'")
        for db in dbs.splitlines():
            self.sql(f'DROP DATABASE "{db}" WITH (FORCE)')
        self.temp.cleanup()

    def test_copied_preview_lifecycle_and_secret_boundary(self):
        url = self.cli('up', self.trees[0])
        self.assertTrue(url.startswith('http://127.0.0.1:'), url)
        with urllib.request.urlopen(url, timeout=5) as response:
            page = json.load(response)
        self.assertEqual(page['value'], 'copied-data')
        self.assertEqual(page['preview'], '1')
        self.cli('up', self.trees[1])
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual(len({r['port'] for r in rows}), 2)
        self.assertEqual(len({r['database'] for r in rows}), 2)
        first = next(r for r in rows if r['worktree'] == str(self.trees[0]))
        self.assertEqual(first['owner'], 'stub-session')
        self.assertEqual(first['branch'], 'one')
        self.assertEqual(first['state'], 'running')
        self.assertIn(self.main_unit, self.cli('ls'))
        show = self.run_cmd('systemctl', '--user', 'show', first['unit'])
        unrelated = subprocess.Popen(['/usr/bin/python3', '-c', 'import sys; sys.stdin.read()',
                                      'devserve-unique-secret-canary'], stdin=subprocess.PIPE)
        self.addCleanup(lambda: unrelated.communicate(timeout=5))
        for row in rows:
            for argv in self.preview_argv(row['unit']).values():
                self.assert_no_secrets(argv, 'preview argv')
        for output in (show, json.dumps(rows)):
            self.assert_no_secrets(output, 'unit metadata')
        self.assertIn('stub-ready', self.cli('logs', first['unit']))
        self.cli('down', first['unit'])
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{first['database']}'"), '1')
        self.assertEqual(next(r for r in self.rows() if r['unit'] == first['unit'])['state'], 'stopped')
        self.cli('down', first['unit'], '--drop-db')
        shutil.rmtree(self.trees[1])
        self.assertTrue(self.rows()[0]['missing'])
        self.cli('gc')
        self.assertEqual(self.rows(), [])
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname LIKE '{self.app}_preview_%'"), '0')
        print('\n'.join(self.transcript))

    def test_argv_inspection_detects_secret_in_preview_child(self):
        start = ['/usr/bin/python3', 'app.py', 'devserve-unique-secret-canary']
        (self.root / 'apps.toml').write_text(self.config.replace(
            'start = ["/usr/bin/python3", "app.py"]', 'start = ' + json.dumps(start)))
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        commands = self.preview_argv(row['unit'])
        with self.assertRaisesRegex(AssertionError, 'secret in preview argv'):
            for argv in commands.values():
                self.assert_no_secrets(argv, 'preview argv')
        self.cli('down', row['unit'], '--drop-db')

    def test_restart_keeps_data_but_runs_migrations(self):
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        self.sql("INSERT INTO evidence VALUES ('preview-only')", row['database'])
        self.cli('down', row['unit'])
        config = self.config.replace('migrate = ["/usr/bin/true"]',
            'migrate = ["/usr/bin/python3", "-c", "import os, pathlib; pathlib.Path(\'migrated\').write_text(os.environ[\'PREVIEW\'])"]')
        (self.root / 'apps.toml').write_text(config)
        self.cli('up', self.trees[0])
        self.assertTrue((self.trees[0] / 'migrated').exists(), 'restart must run migrate')
        self.assertEqual((self.trees[0] / 'migrated').read_text(), '1')
        self.assertEqual(self.sql('SELECT count(*) FROM evidence', row['database']), '2')
        self.assertEqual(self.sql('SELECT count(*) FROM evidence', self.source), '1')
        self.cli('down', row['unit'], '--drop-db')

    def test_failed_start_rolls_back_owned_database(self):
        (self.root / 'apps.toml').write_text(self.config.replace('start = ["/usr/bin/python3", "app.py"]', 'start = ["/usr/bin/false"]'))
        self.cli('up', self.trees[0], ok=False)
        row = self.rows()[0]
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname LIKE '{self.app}_preview_%'"), '0')
        self.cli('down', row['unit'], '--drop-db')
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname LIKE '{self.app}_preview_%'"), '0')
        self.assertEqual(self.sql('SELECT value FROM evidence', self.source), 'copied-data')

    def test_rollback_refusal_still_records_failed_state(self):
        code = ('import os, pathlib, subprocess, urllib.parse; '
                'db = urllib.parse.urlsplit(os.environ["DATABASE_URL"]).path[1:]; '
                'subprocess.run(["psql", "-X", "-d", "postgres", "-c", '
                '\'COMMENT ON DATABASE "\' + db + \'" IS \\\'manual-owner\\\'\'], check=True); '
                'pathlib.Path("ownership-changed").touch()')
        config = self.config.replace('start = ["/usr/bin/python3", "app.py"]',
                                     'start = ' + json.dumps(['/usr/bin/python3', '-c', code]))
        (self.root / 'apps.toml').write_text(config)
        process = subprocess.Popen(['python3', str(SCRIPT), 'up', str(self.trees[0])], env=self.env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 10
            while not (self.trees[0] / 'ownership-changed').exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue((self.trees[0] / 'ownership-changed').exists())
            row = self.rows()[0]
            while self.run_cmd('systemctl', '--user', 'show', row['unit'], '--property=MainPID', '--value') != '0' and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertEqual(self.rows()[0]['state'], 'failed')
            process.communicate(timeout=5)
            self.assertNotEqual(process.returncode, 0)
            self.cli('down', row['unit'], '--drop-db', ok=False)
            self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '1')
        finally:
            if process.poll() is None:
                import signal
                process.send_signal(signal.SIGINT)
            process.communicate(timeout=10)

    def test_down_failed_preview_records_stopped(self):
        (self.root / 'apps.toml').write_text(self.config.replace('start = ["/usr/bin/python3", "app.py"]', 'start = ["/usr/bin/false"]'))
        self.cli('up', self.trees[0], ok=False)
        row = self.rows()[0]
        self.cli('down', row['unit'])
        self.assertEqual(self.rows()[0]['state'], 'stopped')
        self.cli('down', row['unit'], '--drop-db')

    def test_migration_failure_removes_new_database(self):
        (self.root / 'apps.toml').write_text(self.config.replace('migrate = ["/usr/bin/true"]', 'migrate = ["/usr/bin/false"]'))
        self.cli('up', self.trees[0], ok=False)
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname LIKE '{self.app}_preview_%'"), '0')
        self.cli('down', self.rows()[0]['unit'], '--drop-db')

    def test_failed_start_kills_child_process_group(self):
        code = "import subprocess; subprocess.Popen(['/usr/bin/sleep', '97'])"
        (self.root / 'apps.toml').write_text(self.config.replace(
            'start = ["/usr/bin/python3", "app.py"]', 'start = ' + json.dumps(['/usr/bin/python3', '-c', code])))
        self.cli('up', self.trees[0], ok=False)
        row = self.rows()[0]
        group = self.run_cmd('systemctl', '--user', 'show', row['unit'], '--property=ControlGroup', '--value')
        pids = Path('/sys/fs/cgroup' + group + '/cgroup.procs')
        self.assertTrue(not group or not pids.exists() or not pids.read_text().strip(), 'failed start left a process')
        self.cli('down', row['unit'], '--drop-db')

    def test_unowned_collision_is_neither_started_nor_dropped(self):
        import test_devserve
        unit, database = test_devserve.d.names(self.app, self.trees[0])
        self.sql(f'CREATE DATABASE "{database}"')
        self.sql('CREATE TABLE precious (value text)', database)
        self.cli('up', self.trees[0], ok=False)
        self.cli('down', unit, '--drop-db', ok=False)
        self.assertEqual(self.sql("SELECT count(*) FROM pg_tables WHERE tablename = 'precious'", database), '1')

    def test_interrupt_during_migration_rolls_back(self):
        code = 'import pathlib, time; pathlib.Path("migrating").touch(); time.sleep(90)'
        config = self.config.replace('migrate = ["/usr/bin/true"]', 'migrate = ' + json.dumps(['/usr/bin/python3', '-c', code]))
        (self.root / 'apps.toml').write_text(config)
        process = subprocess.Popen(['python3', str(SCRIPT), 'up', str(self.trees[0])], env=self.env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 10
            while not (self.trees[0] / 'migrating').exists() and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue((self.trees[0] / 'migrating').exists())
            import signal
            process.send_signal(signal.SIGINT)
            process.communicate(timeout=15)
            self.assertNotEqual(process.returncode, 0)
            self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname LIKE '{self.app}_preview_%'"), '0')
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate(timeout=5)
        self.cli('down', self.rows()[0]['unit'], '--drop-db')

    def test_worktree_path_is_literal_not_systemd_specifier(self):
        tree = self.root / 'percent%h'
        self.run_cmd('git', 'worktree', 'add', '-qb', 'literal', str(tree), cwd=self.main)
        self.cli('up', tree)
        row = self.rows()[0]
        self.assertEqual(row['worktree'], str(tree))
        self.cli('down', row['unit'], '--drop-db')

    def test_port_range_exhaustion_never_spills_into_other_app(self):
        other = self.root / 'other'
        other.mkdir()
        self.run_cmd('git', 'init', '-q', cwd=other)
        config = self.config.replace(f'ports = [{self.port}, {self.port + 9}]', f'ports = [{self.port}, {self.port}]')
        config += self.config.replace(f'name = "{self.app}"', 'name = "other"').replace(
            f'path = "{self.main}"', f'path = "{other}"').replace(
            f'ports = [{self.port}, {self.port + 9}]', f'ports = [{self.port + 10}, {self.port + 19}]')
        (self.root / 'apps.toml').write_text(config)
        self.cli('up', self.trees[0])
        self.cli('down', self.rows()[0]['unit'])
        self.cli('up', self.trees[1], ok=False)
        self.assertEqual([r['port'] for r in self.rows()], [self.port])
        self.cli('down', self.rows()[0]['unit'], '--drop-db')

    def test_main_units_are_listed_and_tailed_without_mutation(self):
        self.run_cmd('systemd-run', '--user', '--quiet', '--remain-after-exit',
                     '--unit=' + self.main_unit, '/usr/bin/echo', 'stub-main-log')
        listing = json.loads(self.cli('ls', '--json'))
        self.assertEqual(listing['main_units'], [dict(app=self.app, unit=self.main_unit, state='active')])
        self.assertIn('stub-main-log', self.cli('logs', self.app))
        self.cli('gc')
        self.assertEqual(self.run_cmd('systemctl', '--user', 'is-active', self.main_unit), 'active')

    def test_logs_follow_receives_new_http_request(self):
        import selectors
        url = self.cli('up', self.trees[0])
        row = self.rows()[0]
        process = subprocess.Popen(['python3', str(SCRIPT), 'logs', row['unit'], '-f'],
                                   env=self.env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        try:
            with urllib.request.urlopen(url + '/follow-canary', timeout=5) as response:
                response.read()
            output = b''
            deadline = time.monotonic() + 10
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                while b'follow-canary' not in output and time.monotonic() < deadline:
                    if selector.select(timeout=0.2):
                        output += os.read(process.stdout.fileno(), 65536)
            self.assertIn(b'follow-canary', output)
        finally:
            process.terminate()
            process.communicate(timeout=5)
        self.cli('down', row['unit'], '--drop-db')

    def test_fresh_migrates_then_seeds(self):
        def command(sql):
            code = ('import os, subprocess, urllib.parse; '
                    'os.environ["PGDATABASE"] = urllib.parse.urlsplit(os.environ["DATABASE_URL"]).path[1:]; '
                    f'subprocess.run(["psql", "-X", "-c", {sql!r}], check=True)')
            return json.dumps(['/usr/bin/python3', '-c', code])
        config = self.config.replace('data = "copy"', 'data = "fresh"').replace(
            'migrate = ["/usr/bin/true"]',
            'migrate = ' + command('CREATE TABLE evidence (value text)') + '\nseed = ' +
            command("INSERT INTO evidence VALUES ('seeded')"))
        (self.root / 'apps.toml').write_text(config)
        url = self.cli('up', self.trees[0])
        with urllib.request.urlopen(url, timeout=5) as response:
            self.assertEqual(json.load(response)['value'], 'seeded')
        self.cli('down', self.rows()[0]['unit'], '--drop-db')


if __name__ == '__main__':
    unittest.main()
