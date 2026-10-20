import os
import unittest
from unittest.mock import patch
from test_devserve import d


class SelectionTest(unittest.TestCase):
    def test_platform_default_and_explicit_override(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(d.select_backend('linux'), 'systemd')
            self.assertEqual(d.select_backend('darwin'), 'tmux')
            with self.assertRaises(ValueError):
                d.select_backend('win32')
        with patch.dict(os.environ, DEVSERVE_BACKEND='tmux'):
            self.assertEqual(d.select_backend('linux'), 'tmux')
        with patch.dict(os.environ, DEVSERVE_BACKEND='systemd'):
            self.assertEqual(d.select_backend('darwin'), 'systemd')
        with patch.dict(os.environ, DEVSERVE_BACKEND='typo'):
            with self.assertRaises(ValueError):
                d.select_backend('linux')
