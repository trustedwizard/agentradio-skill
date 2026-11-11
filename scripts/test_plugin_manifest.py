"""Validate the marketplace plugin manifests without touching the synced skill."""
import json
import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = re.compile(r'^(?!.*(?:--|\\.\\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$')
CURSOR_FIELDS = {
    'name', 'description', 'version', 'author', 'homepage', 'repository',
    'license', 'keywords', 'logo', 'rules', 'agents', 'skills', 'commands',
    'hooks', 'mcpServers', 'variables',
}
AGENT_FIELDS = {
    '$schema', 'name', 'version', 'description', 'author', 'homepage',
    'repository', 'license', 'keywords', 'extensions',
}
SECRET_MARKERS = ('ar_agent_', 'ar_rehearse_', 'Bearer ', 'BEGIN ')


def load(path):
    text = (ROOT / path).read_text(encoding='utf-8')
    for marker in SECRET_MARKERS:
        if marker in text:
            raise AssertionError(path + ' contains ' + marker)
    return json.loads(text)


class PluginManifestTests(unittest.TestCase):
    def test_cursor_manifest_matches_documented_fields(self):
        manifest = load('.cursor-plugin/plugin.json')
        self.assertEqual(set(manifest), {
            'name', 'version', 'description', 'author', 'homepage',
            'repository', 'license', 'keywords', 'logo', 'mcpServers',
        })
        unknown = set(manifest) - CURSOR_FIELDS
        self.assertEqual(unknown, set())
        self.assertTrue(NAME.fullmatch(manifest['name']))
        self.assertEqual(manifest['name'], 'agentradio')
        self.assertEqual(manifest['license'], 'MIT')
        self.assertEqual(manifest['version'], '1.0.0')
        self.assertEqual(manifest['author'], {'name': 'AgentRadio'})
        self.assertEqual(manifest['logo'], 'assets/logo.png')
        cursor_server = manifest['mcpServers']['agentradio']
        self.assertEqual(cursor_server['type'], 'http')
        self.assertEqual(cursor_server['url'], 'https://agentradio.com/api/mcp')
        self.assertNotIn('headers', cursor_server)
        self.assertNotIn('email', manifest['author'])
        logo = (ROOT / manifest['logo']).read_bytes()
        self.assertEqual(logo[:8], b'\x89PNG\r\n\x1a\n')
        width, height = struct.unpack('>II', logo[16:24])
        self.assertEqual((width, height), (512, 512))
        # color type 2 is RGB, so the plate is opaque rather than transparent
        self.assertEqual(logo[25], 2)

    def test_agent_plugins_manifest_is_closed(self):
        manifest = load('plugin.json')
        self.assertEqual(set(manifest) - AGENT_FIELDS, set())
        self.assertEqual(
            manifest['$schema'],
            'https://agent-plugins.org/schemas/1.0.0/plugin.schema.json',
        )
        self.assertTrue(NAME.fullmatch(manifest['name']))
        self.assertEqual(set(manifest['author']), {'name', 'url'})
        self.assertNotIn('logo', manifest)

    def test_mcp_json_is_remote_oauth_without_a_secret(self):
        config = load('mcp.json')
        self.assertEqual(
            config['$schema'],
            'https://agent-plugins.org/schemas/1.0.0/mcp.schema.json',
        )
        self.assertEqual(set(config), {'$schema', 'mcpServers'})
        server = config['mcpServers']['agentradio']
        self.assertEqual(set(server), {'type', 'url'})
        self.assertEqual(server['type'], 'streamable-http')
        self.assertEqual(server['url'], 'https://agentradio.com/api/mcp')
        self.assertNotIn('headers', server)
        self.assertNotIn('auth', server)

    def test_connector_skill_stays_beside_the_synced_skill(self):
        skill = (ROOT / 'skills/agentradio-mcp/SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(skill.startswith('---\nname: agentradio-mcp\n'))
        for marker in (
            'https://agentradio.com/skill.md',
            'actingAgentId',
            'agentradio_home',
            'station://now-playing',
            'human claim',
            'first-air',
            'Do not say something aired',
        ):
            self.assertIn(marker, skill)
        mirrored = (ROOT / 'skills/agentradio/SKILL.md').read_text(encoding='utf-8')
        self.assertTrue(mirrored.startswith('---\nname: agentradio\n'))
        self.assertIn('https://agentradio.com/skill.md', mirrored)


if __name__ == '__main__':
    unittest.main()
