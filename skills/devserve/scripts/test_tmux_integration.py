"""Real tmux + PostgreSQL, isolated from the operator's tmux server."""
import json
import os
import subprocess
import unittest
import test_integration as fixture

Fixture = fixture.IntegrationTest


@unittest.skipUnless(os.environ.get('DEVSERVE_INTEGRATION') == '1', 'requires tmux and Postgres')
class TmuxIntegrationTest(unittest.TestCase):
    run_cmd = Fixture.run_cmd
    sql = Fixture.sql
    cli = Fixture.cli
    rows = Fixture.rows
    assert_no_secrets = Fixture.assert_no_secrets

    def setUp(self):
        fixture.IntegrationTest.setUp(self)
        self.env.update(DEVSERVE_BACKEND='tmux', DEVSERVE_STATE_DIR=str(self.root / 'state'),
                        DEVSERVE_TMUX_SOCKET='devserve-test-' + str(os.getpid()))

    def cleanup(self):
        try:
            if hasattr(self, 'env') and 'DEVSERVE_TMUX_SOCKET' in self.env:
                try:
                    for row in self.rows():
                        if row['app'] == self.app:
                            self.cli('down', row['unit'], '--drop-db', ok=True)
                finally:
                    subprocess.run(['tmux', '-L', self.env['DEVSERVE_TMUX_SOCKET'], 'kill-server'], capture_output=True)
        finally:
            fixture.IntegrationTest.cleanup(self)

    def test_backend_override_runs_in_scratch_tmux(self):
        self.cli('up', self.trees[0])
        self.assertEqual(self.rows()[0].get('backend', 'systemd'), 'tmux')
        windows = self.run_cmd('tmux', '-L', self.env['DEVSERVE_TMUX_SOCKET'], 'list-windows', '-t', 'devserve')
        self.assertIn(self.app, windows)
        row = self.rows()[0]
        self.assertEqual(row['backend'], 'tmux')
        self.assertEqual(row['owner'], 'stub-session')
        self.assertIn('stub-ready', self.cli('logs', row['unit']))
        self.assert_no_secrets(json.dumps(row), 'registry')
        self.cli('down', row['unit'], '--drop-db')
        self.assertEqual(self.rows(), [])

    def test_restart_prints_only_url(self):
        url = self.cli('up', self.trees[0])
        self.cli('down', self.rows()[0]['unit'])
        self.assertEqual(self.cli('up', self.trees[0]), url)

    def test_systemd_template_refresh_and_clone(self):
        self.env['DEVSERVE_BACKEND'] = 'systemd'
        self.test_template_refresh_and_clone()

    def test_wrong_socket_cannot_drop_live_preview(self):
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        socket = self.env['DEVSERVE_TMUX_SOCKET']
        self.env['DEVSERVE_TMUX_SOCKET'] = socket + '-other'
        try:
            self.cli('down', row['unit'], '--drop-db', ok=False)
            self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '1')
        finally:
            self.env['DEVSERVE_TMUX_SOCKET'] = socket

    def test_foreign_window_is_not_killed(self):
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        state = json.loads((self.root / 'state' / 'previews.json').read_text())
        window = state[row['unit']]['window']
        socket = self.env['DEVSERVE_TMUX_SOCKET']
        self.run_cmd('tmux', '-L', socket, 'set-option', '-w', '-t', window, '@devserve', 'foreign')
        try:
            self.cli('down', row['unit'], '--drop-db', ok=False)
            self.assertEqual(self.run_cmd('tmux', '-L', socket, 'display-message', '-p', '-t', window, '#{pane_dead}'), '0')
            self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '1')
        finally:
            self.run_cmd('tmux', '-L', socket, 'set-option', '-w', '-t', window, '@devserve', state[row['unit']]['token'])

    def test_missing_worktree_gc_preserves_unrelated_window(self):
        self.cli('up', self.trees[0])
        socket = self.env['DEVSERVE_TMUX_SOCKET']
        window = self.run_cmd('tmux', '-L', socket, 'new-window', '-d', '-P', '-F', '#{window_id}',
                              '-t', 'devserve:', '-n', 'unrelated', 'sleep', '120')
        import shutil
        shutil.rmtree(self.trees[0])
        self.cli('gc')
        self.assertEqual(self.rows(), [])
        self.assertEqual(self.run_cmd('tmux', '-L', socket, 'display-message', '-p', '-t', window, '#{window_name}'), 'unrelated')

    def test_mixed_registry_cleanup_routes_to_owner(self):
        self.env['DEVSERVE_BACKEND'] = 'systemd'
        self.cli('up', self.trees[0])
        self.env['DEVSERVE_BACKEND'] = 'tmux'
        self.cli('up', self.trees[1])
        rows = self.rows()
        self.assertEqual(len(rows), 2)
        self.assertEqual({r.get('backend', 'systemd') for r in rows}, {'systemd', 'tmux'})
        for row in rows:
            self.cli('down', row['unit'])
        self.cli('gc', '--stopped')
        self.assertEqual(self.rows(), [])

    def test_orphan_gc_requires_matching_comment_and_missing_worktree(self):
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        self.cli('down', row['unit'])
        (self.root / 'state' / 'previews.json').write_text('{}')
        self.cli('gc')
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '1')
        import shutil
        shutil.rmtree(self.trees[0])
        self.cli('gc')
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '0')

    def test_orphan_gc_preserves_unowned_and_forged_databases(self):
        database = self.app + '_preview_tree_aaaaaaaaaaaa'
        self.sql(f'CREATE DATABASE "{database}"')
        self.cli('gc', '--stopped')
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{database}'"), '1')
        mark = 'devserve:v1:devserve-' + self.app + '-tree-aaaaaaaaaaaa.service:' + 'b' * 64
        self.sql(f"COMMENT ON DATABASE \"{database}\" IS '{mark}'")
        self.cli('gc', '--stopped')
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{database}'"), '1')

    def test_orphan_gc_preserves_live_window_without_state_entry(self):
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        path = self.root / 'state' / 'previews.json'
        original = path.read_text()
        path.write_text('{}')
        try:
            self.cli('gc', '--stopped')
            self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '1')
        finally:
            path.write_text(original)

    def test_orphan_gc_never_drops_configured_source(self):
        self.cli('up', self.trees[0])
        row = self.rows()[0]
        self.cli('down', row['unit'])
        (self.root / 'state' / 'previews.json').write_text('{}')
        (self.root / 'apps.toml').write_text(self.config.replace(self.source, row['database']))
        self.cli('gc', '--stopped')
        self.assertEqual(self.sql(f"SELECT count(*) FROM pg_database WHERE datname = '{row['database']}'"), '1')

    def test_template_refresh_and_clone(self):
        base = self.app + '_base'
        config = self.config.replace('data = "copy"', f'data = "template"\ntemplate_database = "{base}"')
        (self.root / 'apps.toml').write_text(config)
        try:
            self.cli('base', 'refresh', self.app, '--dump')
            url = self.cli('up', self.trees[0])
            import urllib.request
            with urllib.request.urlopen(url, timeout=5) as response:
                self.assertEqual(json.load(response)['value'], 'copied-data')
            self.cli('down', self.rows()[0]['unit'], '--drop-db')
            self.cli('base', 'refresh', self.app)
            self.assertEqual(self.sql(f"SELECT shobj_description(oid, 'pg_database') FROM pg_database WHERE datname = '{base}'"),
                             'devserve:base:v1:' + self.app)
        finally:
            for suffix in ('', '_next', '_prev'):
                self.sql(f'DROP DATABASE IF EXISTS "{base}{suffix}" WITH (FORCE)')

    test_restart_keeps_data_but_runs_migrations = Fixture.test_restart_keeps_data_but_runs_migrations
    test_failed_start_rolls_back_owned_database = Fixture.test_failed_start_rolls_back_owned_database
    test_down_failed_preview_records_stopped = Fixture.test_down_failed_preview_records_stopped
    test_migration_failure_removes_new_database = Fixture.test_migration_failure_removes_new_database
    test_fresh_migrates_then_seeds = Fixture.test_fresh_migrates_then_seeds
    test_logs_follow_receives_new_http_request = Fixture.test_logs_follow_receives_new_http_request


del Fixture
