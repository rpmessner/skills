import importlib.machinery
import importlib.util
from pathlib import Path
import socket
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('devserve')
loader = importlib.machinery.SourceFileLoader('devserve', str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
d = importlib.util.module_from_spec(spec)
loader.exec_module(d)


class ConfigTest(unittest.TestCase):
    def config(self, text):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'apps.toml'
            path.write_text(text)
            return d.load_config(path)

    def test_valid_copy_and_overlap_rejected_with_both_names(self):
        app = '''[[apps]]
name = "stub"
path = "/tmp/main"
ports = [43000, 43010]
start = ["python3", "app.py"]
data = "copy"
source_database = "devserve_test_source"
migrate = ["true"]
'''
        self.assertEqual(self.config(app)[0]['name'], 'stub')
        for field in ('name', 'path', 'ports', 'start', 'data', 'source_database', 'migrate'):
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.config('\n'.join(line for line in app.splitlines() if not line.startswith(field + ' =')))
        with self.assertRaises(ValueError):
            self.config(app.replace('source_database = "devserve_test_source"', 'source_database = 12'))
        with self.assertRaisesRegex(ValueError, 'stub.*other'):
            self.config(app + app.replace('"stub"', '"other"'))
        with self.assertRaisesRegex(ValueError, 'stub.*other'):
            self.config(app + app.replace('"stub"', '"other"').replace('[43000, 43010]', '[43010, 43020]'))

    def test_required_fields_absolute_paths_and_types(self):
        app = '''[[apps]]
name = "stub"
path = "/tmp/main"
ports = [43000, 43010]
start = ["true"]
data = "fresh"
migrate = ["true"]
seed = ["true"]
'''
        for old, new in [('path = "/tmp/main"', 'path = "relative"'),
                         ('seed = ["true"]', ''), ('ports = [43000, 43010]', 'ports = [true, 43010]'),
                         ('start = ["true"]', 'start = "true"'),
                         ('name = "stub"', 'name = "../bad"')]:
            with self.subTest(new=new), self.assertRaises(ValueError):
                self.config(app.replace(old, new))
        with self.assertRaises(ValueError):
            self.config(app + 'env_file = "relative"\n')


class PureTest(unittest.TestCase):
    def test_lifecycle_golden_and_reachability(self):
        import random
        from render_lifecycle import render
        self.assertEqual((SCRIPT.parent.parent / 'lifecycle.md').read_text(), render())
        states = {'absent'}
        for _ in range(5):
            states |= {target for (source, _), (target, _) in d.TRANSITIONS.items() if source in states}
        self.assertEqual(states, {'absent', 'starting', 'running', 'failed', 'stopped'})
        rng = random.Random(17)
        state = 'absent'
        for _ in range(500):
            event = rng.choice(['up', 'ready', 'error', 'down', 'drop'])
            before = dict(d.TRANSITIONS)
            try:
                target, effects = d.step(state, event)
                self.assertIn(target, states)
                self.assertIsInstance(effects, tuple)
                if 'drop' in effects:
                    self.assertIn(state, ('stopped', 'failed'))
                state = target
            except ValueError:
                self.assertNotIn((state, event), d.TRANSITIONS)
            self.assertEqual(before, d.TRANSITIONS)

    def test_names_are_bounded_safe_and_distinguish_same_basename(self):
        unit, db = d.names('stub', Path('/tmp/a/feature'))
        self.assertRegex(unit, r'^devserve-stub-feature-[a-f0-9]{12}\.service$')
        self.assertRegex(db, r'^stub_preview_feature_[a-f0-9]{12}$')
        self.assertNotEqual(d.names('stub', Path('/tmp/b/feature')), (unit, db))
        self.assertLessEqual(len(d.names('a'*20, Path('/tmp/' + 'b'*200))[1]), 63)

    def test_port_choice_takes_first_available(self):
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            port = sock.getsockname()[1]
        self.assertEqual(d.choose_port([port, port + 1], set()), port)

    def test_port_choice_skips_claims_and_real_listener(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
            self.assertEqual(d.choose_port([port, port + 2], {port + 1}), port + 2)
            with self.assertRaisesRegex(ValueError, 'port'):
                d.choose_port([port, port + 1], {port + 1})

    def test_lifecycle_returns_effects_and_rejects_invalid_events(self):
        self.assertEqual(d.step('absent', 'up'), ('starting', ('prepare', 'launch')))
        self.assertEqual(d.step('starting', 'ready'), ('running', ()))
        self.assertEqual(d.step('starting', 'error'), ('failed', ('rollback',)))
        self.assertEqual(d.step('running', 'down'), ('stopped', ('terminate',)))
        self.assertEqual(d.step('stopped', 'drop'), ('absent', ('drop',)))
        with self.assertRaises(ValueError):
            d.step('absent', 'ready')


if __name__ == '__main__':
    unittest.main()
