import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sync
from sync import validate


class ValidationTests(unittest.TestCase):
    def test_contract_and_rejections(self):
        valid = b'---\nname: agentradio\nlicense: MIT\n---\nhttps://agentradio.com/skill.md human claim first-air review [LICENSE](LICENSE)'
        self.assertEqual(validate(valid), valid)
        for data in [b'<html>error</html>', valid.replace(b'human claim', b'claim'),
                     valid.replace(b'license: MIT', b'license: unknown'),
                     valid + b' ar_agent_secret', valid + b'x' * 65536]:
            with self.subTest(data=data[:40]), self.assertRaises(ValueError):
                validate(data)

    def test_license_failure_preserves_export_and_valid_pair_syncs(self):
        skill = b'---\nname: agentradio\nlicense: MIT\n---\nhttps://agentradio.com/skill.md human claim first-air review [LICENSE](LICENSE)'
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = root / 'skills/agentradio/SKILL.md'
            target.parent.mkdir(parents=True)
            target.write_bytes(b'previous skill')
            (root / 'LICENSE').write_bytes(b'approved license')
            with patch.object(sync, 'ROOT', root), patch.object(sync, 'fetch', side_effect=[skill, b'wrong license']):
                with self.assertRaises(ValueError):
                    sync.main()
            self.assertEqual(target.read_bytes(), b'previous skill')
            self.assertFalse((root / 'source.json').exists())
            with patch.object(sync, 'ROOT', root), patch.object(sync, 'fetch', side_effect=[skill, b'approved license']):
                sync.main()
            self.assertEqual(target.read_bytes(), skill)
            self.assertEqual((target.parent / 'LICENSE').read_bytes(), b'approved license')


if __name__ == '__main__':
    unittest.main()
