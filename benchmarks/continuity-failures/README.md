# Continuity Failure Corpus

This directory contains an original, synthetic benchmark for deterministic CineOps validation. It does not contain production scripts, private project files, generated media, or copyrighted excerpts.

## Reproduce

The `base/` directory is a valid two-shot production handoff. Each file in `cases/` applies one documented mutation to that baseline and declares the exact finding that must result.

Run the corpus tests with:

```bash
python -m unittest tests.test_validator.ValidatorTests.test_benchmark_corpus_is_reproducible -v
```

The test fails when an expected finding is missed or when a case produces an unexpected extra finding. The manifest pins both the corpus version and artifact schema version.

## Scope And Limitations

- The corpus measures deterministic artifact-contract validation, not story quality or model quality.
- State continuity is compared only for keys present in both an earlier shot's exit state and the next shot's entry state within the same scene.
- Source revision checks run only when both the shot and canonical scene state declare a revision.
- The cases are intentionally small so that a failure has one primary cause.
- Passing this corpus does not prove that a production is visually coherent or ready to publish.

All corpus materials are licensed under Apache-2.0 with the rest of this repository.
