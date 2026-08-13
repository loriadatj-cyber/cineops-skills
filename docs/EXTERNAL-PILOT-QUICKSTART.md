# 15-Minute External Pilot

This pilot tests CineOps on a real production handoff without asking you to publish scripts, frames, prompts, client identities, or project names. Failed and abandoned trials are welcome.

## Who Counts As External

You may submit a case when you are authorized to use the workflow and are independent of the CineOps maintainers. A maintainer testing their own production is useful Level 0 evidence, but it is not external adoption.

## Before You Start (1 Minute)

- Choose one real scene and one to three planned shots.
- Confirm that you are allowed to evaluate the workflow.
- Keep credentials, client data, private media, and unreleased creative material out of GitHub.
- Record your normal process or known failure mode as the baseline.

## Install (3 Minutes)

Python 3.10 or newer is required.

```bash
git clone https://github.com/loriadatj-cyber/cineops-skills.git
cd cineops-skills
python -m pip install -e .
cineops --version
git rev-parse --short HEAD
```

## Model One Real Handoff (6 Minutes)

```bash
cineops init pilot
```

Edit the four files under `pilot/` locally:

- `project.json`: describe one real scene using an anonymous title and summary.
- `continuity-ledger.json`: record only the characters, locations, props, and entry/exit state needed for the test.
- `shot-plan.json`: add one to three real planned shots and their observable entry/exit state.
- `readiness-report.json`: mark each shot `ready`, `revise`, or `blocked` and record honest checks.

The files do not need to be published. Generic labels such as `CHAR-A`, `LOC-A`, and `PROP-A` are acceptable when the underlying state transition remains real.

## Run The Check (2 Minutes)

```bash
cineops validate pilot
cineops gate pilot
cineops evidence pilot --output cineops-evidence.json
```

`validate` checks artifact consistency. `gate` answers whether every shot is ready. A non-zero result is valid evidence, not a failed pilot.

`cineops-evidence.json` contains only aggregate counts, review decisions, finding codes, and gate status. It excludes titles, names, actions, prompts, IDs, messages, and filesystem paths. Inspect it before sharing anyway.

## Report The Result (3 Minutes)

Open a [Production adoption report](https://github.com/loriadatj-cyber/cineops-skills/issues/new?template=adoption-case.yml) and include:

- your relationship to the production and to CineOps maintainers;
- CineOps version and commands used;
- the baseline process or failure mode;
- what you directly observed, including no improvement or abandonment;
- friction, false positives, and missed defects;
- the contents of `cineops-evidence.json`, pasted in a fenced JSON block.

Do not attach the `pilot/` directory unless you deliberately created and reviewed an anonymized fixture for publication.

## Evidence Level

- A complete authorized report is normally Level 1 self-reported adoption.
- A reviewed `cineops-evidence.json` or anonymized reproducible fixture may support Level 2 verification.
- The maintainers assign the final level after checking authorization, independence, privacy, and reproducibility.

See [Adoption Evidence](ADOPTION.md) for the complete policy.
