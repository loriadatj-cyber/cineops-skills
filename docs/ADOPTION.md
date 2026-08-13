# Adoption Evidence

CineOps values inspectable production evidence over vanity metrics. A star, page view, automated download, or maintainer-authored demo is useful context but does not by itself demonstrate adoption.

## Evidence Levels

| Level | Evidence | How it may be described |
| --- | --- | --- |
| 0 | Maintainer fixture or internal experiment | Reproducible example, not external adoption |
| 1 | Independent user confirms use in a real workflow | Self-reported adoption |
| 2 | Anonymized artifacts or validator output support the report | Verified production case |
| 3 | Public project, repeat usage, or independent integration is reproducible | Public adoption |

Negative results count. A case that finds no improvement, exposes false positives, or abandons a workflow can improve the contracts more than an unsupported success claim.

## Minimum Case Record

Every accepted case should record:

- production scope and participant relationship;
- exact CineOps version, skills, commands, and stages used;
- baseline workflow or previous failure mode;
- observed result with uncertainty clearly stated;
- friction, missed defects, and workarounds;
- public evidence or an anonymized reproducible fixture;
- permission and privacy status;
- follow-up changes linked to issues or pull requests.

Use `adoption-case.template.md` for repository-based cases or open a Production adoption report through GitHub Issues.

For a minimal real-workflow test, follow the [15-minute external pilot](EXTERNAL-PILOT-QUICKSTART.md). The `cineops evidence` command exports aggregate technical results without creative content or identifiers; participants must still inspect the file before sharing it.

## Privacy Rules

Never request or publish credentials, client identities, private scripts, unreleased frames, contractual data, or copyrighted media without explicit permission. Synthetic fixtures should preserve the failure mechanism while replacing creative content and identifying details.

## Maintainer Reporting

Aggregate summaries must distinguish external users from maintainers, self-reported cases from verified cases, and unique cases from repeated runs. Do not infer adoption from download counts alone.
