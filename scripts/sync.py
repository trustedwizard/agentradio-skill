"""Mirror only the deployed public skill; never crawl or export the app repository."""
import hashlib
import json
from pathlib import Path
import urllib.request

SOURCE = 'https://agentradio.com/skill-package/.well-known/agent-skills/agentradio/SKILL.md'
ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    text = data.decode('utf-8')
    if len(data) > 65536 or not text.startswith('---\nname: agentradio\n'):
        raise ValueError('Unexpected skill size or frontmatter')
    for marker in ['https://agentradio.com/skill.md', 'human claim', 'first-air review']:
        if marker not in text:
            raise ValueError('Missing required public contract marker: ' + marker)
    for marker in ['ar_agent_', '-----BEGIN ', '<html', '<!DOCTYPE']:
        if marker in text:
            raise ValueError('Unexpected credential or non-skill content')
    return data


def main():
    request = urllib.request.Request(SOURCE, headers={'User-Agent': 'AgentRadio-public-skill-sync/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.url != SOURCE:
            raise ValueError('Unexpected source status or redirect')
        data = validate(response.read(65537))
    target = ROOT / 'skills/agentradio/SKILL.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    manifest = {'source': SOURCE, 'sha256': hashlib.sha256(data).hexdigest()}
    (ROOT / 'source.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Verified public skill:', manifest['sha256'])


if __name__ == '__main__':
    main()
