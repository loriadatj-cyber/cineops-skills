# CineOps Skills

[![CI](https://github.com/loriadatj-cyber/cineops-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/loriadatj-cyber/cineops-skills/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![External pilots wanted](https://img.shields.io/badge/external_pilots-wanted-2ea44f.svg)](https://github.com/loriadatj-cyber/cineops-skills/issues/2)

CineOps is an open, provider-agnostic production-control toolkit for AI filmmaking. It combines five Codex Skills with a deterministic CLI that validates the artifacts passed between story, shot planning, continuity, and generation review.

It is deliberately not a prompt collection. Creative output remains flexible; IDs, references, state transitions, review coverage, and release gates are inspectable and testable.

## Why CineOps

AI film workflows often lose information between stages. A renamed character breaks prompts, a prop changes hands between shots, an approved revision never reaches the storyboard, or an attractive shot cannot edit into the sequence. CineOps treats those handoffs as production contracts.

## Included Skills

| Skill | Responsibility |
| --- | --- |
| `cineops-router` | Route work and enforce stage gates |
| `cineops-screenplay-diagnostics` | Diagnose causality, intention, visual action, and producibility |
| `cineops-shot-planning` | Build timed, blocked, state-aware shot plans |
| `cineops-continuity-ledger` | Maintain canon and trace revision impact |
| `cineops-generation-readiness-review` | Decide ready, revise, or blocked before generation |

## Quick Start

Install the CLI locally:

```bash
python -m pip install https://github.com/loriadatj-cyber/cineops-skills/releases/download/v0.1.1/cineops-0.1.1-py3-none-any.whl
cineops init my-production
cineops validate my-production
cineops gate my-production
cineops evidence my-production --output cineops-evidence.json
```

Clone the repository instead when you want the bundled Codex Skills, schemas, examples, and benchmark corpus.

Validate the included reproducible example:

```bash
cineops validate examples/glass-elevator
cineops gate examples/glass-elevator
```

Compare continuity revisions:

```bash
cineops impact old-continuity-ledger.json new-continuity-ledger.json
```

Run the versioned continuity-failure corpus:

```bash
python -m unittest discover -s tests -v
```

The corpus contains 12 original synthetic handoff failures covering broken references, duplicate IDs, prop possession, wardrobe, visible damage, knowledge state, screen direction, timing, review gates, and stale source revisions. See [benchmarks/continuity-failures](benchmarks/continuity-failures) for its version, expected findings, and limitations.

Install the repository as a Codex Plugin from its GitHub URL or local path. The plugin manifest is at `.codex-plugin/plugin.json`; each skill can also be inspected independently under `skills/`.

## Artifact Contract

A project directory contains four JSON artifacts:

- `project.json`: episodes and scenes.
- `continuity-ledger.json`: canonical entities and scene boundary states.
- `shot-plan.json`: ordered shots with observable action and entry/exit state.
- `readiness-report.json`: one review decision per shot.

Stable IDs use `EP001`, `SC001`, `SH001`, `CHAR-*`, `LOC-*`, and `PROP-*`. The CLI rejects malformed IDs, duplicate IDs, broken references, invalid shot timing, contradictory readiness decisions, stale source revisions, and state mismatches between adjacent shots. It warns when scenes lack state records or shots lack readiness review.

`cineops validate` checks whether the artifact handoff is structurally coherent. `cineops gate` additionally fails when any shot is marked `revise` or `blocked`, or has no review. Keeping the commands separate lets teams inspect incomplete work without accidentally treating it as release-ready.

## Design Principles

- Human approval owns canon, publishing, and paid generation.
- Unknown information remains explicit instead of being guessed.
- Skills diagnose within their stage and hand off cleanly.
- Core workflows do not depend on a specific model, editor, or generation platform.
- Runtime validation uses only the Python standard library.

## Development

```bash
python -m unittest discover -s tests -v
python -m cineops.cli validate examples/glass-elevator
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [ROADMAP.md](ROADMAP.md), and [SECURITY.md](SECURITY.md). The example story and all workflow text in this repository are original project materials.

## Share A Production Case

Real use, failed use, and abandoned use are all valuable. Read the [adoption evidence policy](docs/ADOPTION.md), then open a Production adoption report or use the [case template](docs/adoption-case.template.md). Reports must separate observed evidence from interpretation and must not expose private production material.

Independent participants can complete the [15-minute external pilot](docs/EXTERNAL-PILOT-QUICKSTART.md). `cineops evidence` creates an aggregate technical summary that omits creative content, identifiers, messages, and filesystem paths.

The [adoption evidence index](adoption/README.md) reports external cases separately from maintainer pilots.

## Status

Version `0.1.1` is an alpha evidence release. We welcome real production cases, anonymized failure reports, and adapters that keep the core provider-agnostic.

## License

Apache License 2.0. See [LICENSE](LICENSE).
