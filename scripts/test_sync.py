import unittest
from sync import validate


class ValidationTests(unittest.TestCase):
    def test_contract_and_rejections(self):
        valid = b'---\nname: agentradio\n---\nhttps://agentradio.com/skill.md human claim first-air review'
        self.assertEqual(validate(valid), valid)
        for data in [b'<html>error</html>', valid.replace(b'human claim', b'claim'),
                     valid + b' ar_agent_secret', valid + b'x' * 65536]:
            with self.subTest(data=data[:40]), self.assertRaises(ValueError):
                validate(data)


if __name__ == '__main__':
    unittest.main()
