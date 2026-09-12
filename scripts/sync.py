"""Mirror only the deployed public skill; never crawl or export the app repository."""
import hashlib
import json
from pathlib import Path
import urllib.request

SOURCE = 'https://agentradio.com/skill-package/.well-known/agent-skills/agentradio/SKILL.md'
ROOT = Path(__file__).resolve().parents[1]
LICENSE_SOURCE = SOURCE.rsplit('/', 1)[0] + '/LICENSE'


def validate(data):
    text = data.decode('utf-8')
    if len(data) > 65536 or not text.startswith('---\nname: agentradio\n'):
        raise ValueError('Unexpected skill size or frontmatter')
    for marker in ['https://agentradio.com/skill.md', 'human claim', 'first-air review', 'license: MIT', '[LICENSE](LICENSE)']:
        if marker not in text:
            raise ValueError('Missing required public contract marker: ' + marker)
    for marker in ['ar_agent_', '-----BEGIN ', '<html', '<!DOCTYPE']:
        if marker in text:
            raise ValueError('Unexpected credential or non-skill content')
    return data


def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'AgentRadio-public-skill-sync/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200 or response.url != url:
            raise ValueError('Unexpected source status or redirect')
        return response.read(65537)


def main():
    data = validate(fetch(SOURCE))
    license_data = fetch(LICENSE_SOURCE)
    # Validate every fetched file before modifying the export. License changes
    # require explicit review of this repository's tooling license as well.
    if license_data != (ROOT / 'LICENSE').read_bytes():
        raise ValueError('Published license differs from approved MIT license')
    target = ROOT / 'skills/agentradio/SKILL.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    (target.parent / 'LICENSE').write_bytes(license_data)
    manifest = {'source': SOURCE, 'sha256': hashlib.sha256(data).hexdigest()}
    manifest['license'] = {'source': LICENSE_SOURCE, 'sha256': hashlib.sha256(license_data).hexdigest()}
    (ROOT / 'source.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print('Verified public skill:', manifest['sha256'])


if __name__ == '__main__':
    main()
