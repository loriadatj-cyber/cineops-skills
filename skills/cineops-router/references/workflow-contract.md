# CineOps Workflow Contract

The default flow is diagnosis -> planning -> continuity update -> readiness review -> generation -> result review.

## State Vocabulary

- `approved`: explicitly accepted by the responsible human or established source of truth.
- `draft`: usable for discussion but not safe to propagate as canon.
- `superseded`: retained for history and excluded from current decisions.
- `unknown`: required information that has not been observed or decided.

Unknown is not false, empty, or permission to invent. Record the owner and deadline when an unknown blocks progress.

## Change Rule

When an approved upstream fact changes, identify every downstream scene, shot, prompt, asset, and generated clip that relied on it. Re-review only the affected artifacts, but never skip that review.

## Human Gates

Require explicit confirmation for irreversible story changes, canonical character or world changes, paid generation, publishing, deletion, and external account actions.
