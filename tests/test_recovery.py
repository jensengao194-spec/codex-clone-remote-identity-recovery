import importlib.util
import json
import pathlib
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'codex_clone_identity.py'
spec = importlib.util.spec_from_file_location('recovery', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class RecoveryTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.home = self.root / 'codex-home'
        self.home.mkdir()
        self.out = self.root / 'private-backups'
        self.out.mkdir()
        self.plan = {'schema': 1, 'codex_home': str(self.home), 'app_path': '/Applications/Codex.app', 'app_build': '21828', 'installation_id': '00000000-0000-4000-8000-000000000001', 'target': ['wss://example.invalid/server', 'test-account', 'Codex Desktop', 'srv_test', 'env_test']}
        m.configure(self.plan)
        self.original = {m.KEYS[0]: m.INSTALL, m.KEYS[1]: m.ENV, 'electron-remote-control-client-enrollments': {'test': {'clientId': 'cli_test', 'keyId': 'key_test'}}, 'threads': ['history'], 'unicode': '保留'}
        for name in ('.codex-global-state.json', '.codex-global-state.json.bak'):
            (self.home / name).write_text(json.dumps(self.original))
        (self.home / 'installation_id').write_text(m.INSTALL)
        (self.home / 'config.toml').write_text('model="test"\n')
        c = sqlite3.connect(self.home / 'state_5.sqlite')
        c.execute('CREATE TABLE remote_control_enrollments(websocket_url, account_id, app_server_client_name, server_id, environment_id, server_name, updated_at, remote_control_enabled)')
        c.execute('INSERT INTO remote_control_enrollments VALUES(?,?,?,?,?,?,?,?)', m.TARGET + ('test-name', 1, 1))
        c.execute("INSERT INTO remote_control_enrollments VALUES('other','other','other','s','e','n',1,1)")
        c.execute('CREATE TABLE threads(id,title)')
        c.execute("INSERT INTO threads VALUES('thread-test','keep history')")
        c.commit()
        c.close()

    def test_scoped_reset(self):
        result = m.reset(self.home, self.out, guard=False)
        self.assertEqual(result['removed_host_registration_count'], 1)
        self.assertFalse((self.home / 'installation_id').exists())
        for name in ('.codex-global-state.json', '.codex-global-state.json.bak'):
            self.assertEqual(json.loads((self.home / name).read_text()), {k: v for k, v in self.original.items() if k not in m.KEYS})
        c = sqlite3.connect(self.home / 'state_5.sqlite')
        self.assertEqual(c.execute('SELECT count(*) FROM remote_control_enrollments').fetchone()[0], 1)
        self.assertEqual(c.execute('SELECT * FROM threads').fetchall(), [('thread-test', 'keep history')])
        c.close()
        backup = pathlib.Path(result['backup'])
        self.assertEqual((backup / 'state_5.sqlite').stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.home / 'config.toml').read_text(), 'model="test"\n')

    def test_file_failure_rolls_back(self):
        before = {p.name: p.read_bytes() for p in self.home.iterdir()}
        real = m.atomic
        count = 0
        def failing(*args):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError('injected write failure')
            return real(*args)
        with patch.object(m, 'atomic', failing):
            with self.assertRaises(OSError):
                m.reset(self.home, self.out, guard=False)
        for name, data in before.items():
            self.assertEqual((self.home / name).read_bytes(), data, name)

    def test_stale_identity_refused(self):
        (self.home / 'installation_id').write_text('changed')
        with self.assertRaises(RuntimeError):
            m.reset(self.home, self.out, guard=False)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_running_application_refused(self):
        with patch.object(m, 'blockers', return_value=['running Codex']):
            with self.assertRaises(RuntimeError):
                m.reset(self.home, self.out, guard=True)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_duplicate_target_refused(self):
        c = sqlite3.connect(self.home / 'state_5.sqlite')
        c.execute('INSERT INTO remote_control_enrollments SELECT * FROM remote_control_enrollments WHERE account_id=?', ('test-account',))
        c.commit()
        c.close()
        with self.assertRaises(RuntimeError):
            m.validate(self.home)

if __name__ == '__main__':
    unittest.main()
