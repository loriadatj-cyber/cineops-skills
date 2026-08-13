# Maintainer Pilot 001: Anonymized Transfer Sequence

## Record

- Case ID: `maintainer-001-anonymized-transfer-sequence`
- CineOps version: post-`0.1.0` main branch with `cineops gate`
- Capture date: 2026-08-13
- Evidence level: 0
- Participant relationship: maintainer-operated private production
- Permission status: owner-authorized local analysis; public record is anonymized
- External adoption count: 0

This is a real workflow pilot, not an independent adoption claim. It must not be included among the three external cases required by roadmap Issue #2.

## Production Scope

- Short-form narrative sequence, approximately 36 seconds assembled
- One scene normalized into seven component shots
- Source platform: LibTV
- Commands used: authenticated read-only node inventory, `cineops validate`, and `cineops gate`
- Stages used: inventory intake, continuity normalization, structural validation, release gating

## Baseline

The live canvas had a final assembly whose name marked it locked, plus a current-production group containing component clips, boundary frames, candidates, and older assemblies. The canvas inventory did not provide a machine-readable cross-shot state contract or a release decision per component shot.

## Observations

| Observation | Baseline | With CineOps | Collection method | Confidence |
| --- | --- | --- | --- | --- |
| Inventory scope | 242 canvas nodes; 32 nodes in the current-production group | Seven component shots normalized | Read-only CLI counts and deterministic mapping | High for counts; medium for mapping |
| Structural handoff | No four-artifact contract | `cineops validate` reports zero findings | CLI output | High |
| Release readiness | A filename marked the assembly locked | `cineops gate` rejects all seven `revise` decisions | CLI output | High |
| Visual continuity | Encoded partly in node names | Remains unknown without frame-level review | Inventory limitation observed directly | High |

The directly observed result is that CineOps can normalize this inventory into an inspectable handoff and prevent a structurally valid but unreviewed sequence from being treated as release-ready. It does not prove that the private media has continuity defects.

## Failures And Friction

- Mapping platform node names to stable production IDs was manual.
- Source node IDs and citations have no first-class artifact field yet.
- `cineops validate` correctly checks structure but does not represent release readiness; this pilot led to the separate `cineops gate` command.
- Camera, blocking, performance, and final-frame continuity cannot be verified from inventory metadata alone.
- The component durations total 32 seconds while the named assembly is 36.08 seconds; handles, transitions, or an omitted segment remain unverified.

## Reproducible Artifacts

The four JSON artifacts in this directory preserve the seven-shot handoff while replacing creative names and removing all media, prompts, account data, canvas identifiers, and node identifiers. `source-evidence.json` records the privacy transform and observed counts.

```bash
cineops validate adoption/pilots/maintainer-001-anonymized-transfer-sequence
cineops gate adoption/pilots/maintainer-001-anonymized-transfer-sequence
```

Expected result: structural validation succeeds; release gating fails with seven `revision-required` findings.

## Maintainer Review

- Evidence checked by: repository maintainer
- Verification performed: live read-only inventory count, artifact validation, release gate test
- Remaining uncertainty: all visual and editorial judgments
- Accepted evidence level: 0
