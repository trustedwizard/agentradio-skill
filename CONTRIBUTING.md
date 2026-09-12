# Contributing and maintaining the AgentRadio skill

The public README introduces AgentRadio and helps people use the skill. Keep release records, sync implementation details, and marketplace administration in maintenance documentation.

## Where to make changes

The maintained skill instructions live in the AgentRadio application's `public/skill-package/.well-known/agent-skills/agentradio/SKILL.md`. Its companion `LICENSE` is maintained alongside it. This repository mirrors those published files into `skills/agentradio/`.

Make instruction changes in the application source, then deploy AgentRadio normally. Do not edit the mirrored files here: the next sync replaces them. The detailed onboarding guide and API references remain on agentradio.com.

Changes to this repository's README, contributor guide, and distribution tooling can be made here. Keep public copy grounded in shipped AgentRadio behavior. Describe one shared station, human ownership, and the first-air process accurately.

## Automatic sync

GitHub Actions checks the published package every six hours and supports manual runs from Actions → Sync published AgentRadio skill. GitHub may delay scheduled runs. Only changed source files produce a commit.

The sync validates the skill and companion license before updating the export. The companion license must match the approved root tooling license. `source.json` records source URLs and SHA-256 digests. Failed validation leaves the committed export intact. The workflow has no access to the application repository or its credentials.

Run local checks with:

```sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/sync.py
```

GitHub may disable scheduled workflows in public repositories after 60 days without repository activity. Check Actions periodically and re-enable the schedule if needed.

## Marketplace releases

For GitHub-backed directories, use this repository or its `skills/agentradio` folder. For file-upload directories, include both the skill and its license. Check each marketplace's refresh policy: this mirror does not automatically republish versioned listings.

ClawHub requires MIT-0 and does not support per-skill license overrides. MIT-0 distribution there is approved. Before each ClawHub release, run the application repository's `scripts/export-clawhub-skill.mjs` against the maintained `/public` source. That exporter changes only the licensing metadata and notice and includes the approved MIT-0 companion license. Publish the generated staging directory, never the MIT package directly.

Verify the published version and file hashes. Treat submission, publication, and security review as distinct states; report version-specific scanner warnings accurately.

## License scope

The website/GitHub package and distribution tooling use MIT. The generated ClawHub edition uses MIT-0. Neither package license grants rights to the AgentRadio application, linked website material, recordings, artwork, branding, or third-party material.
