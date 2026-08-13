"""Privacy-safe technical evidence for external CineOps pilots."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from . import __version__
from .validator import Finding, load_json, summarize, validate_project, validate_release_gate


def _document(root: Path, name: str) -> dict[str, Any]:
    try:
        value = load_json(root / name)
    except (OSError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _items(document: dict[str, Any], key: str) -> list[Any]:
    value = document.get(key)
    return value if isinstance(value, list) else []


def _finding_codes(findings: list[Finding]) -> dict[str, int]:
    return dict(sorted(Counter(finding.code for finding in findings).items()))


def build_evidence_summary(root: Path) -> dict[str, Any]:
    """Return aggregate evidence without creative content or identifiers."""
    project = _document(root, "project.json")
    shots = _document(root, "shot-plan.json")
    readiness = _document(root, "readiness-report.json")

    episodes = _items(project, "episodes")
    scene_count = sum(
        len(episode.get("scenes", []))
        for episode in episodes
        if isinstance(episode, dict) and isinstance(episode.get("scenes", []), list)
    )
    shot_items = _items(shots, "shots")
    reviews = _items(readiness, "reviews")
    decisions: Counter[str] = Counter()
    for review in reviews:
        if not isinstance(review, dict):
            decisions["invalid"] += 1
            continue
        decision = review.get("decision")
        decisions[decision if decision in {"ready", "revise", "blocked"} else "invalid"] += 1

    validation_findings = validate_project(root)
    gate_findings = validate_release_gate(root)
    validation_summary = summarize(validation_findings)
    gate_summary = summarize(gate_findings)

    return {
        "evidence_format": "cineops-pilot-evidence-1.0",
        "cineops_version": __version__,
        "privacy": {
            "creative_content_included": False,
            "identifiers_included": False,
            "paths_included": False,
            "review_before_sharing": True,
        },
        "artifact_counts": {
            "episodes": len(episodes),
            "scenes": scene_count,
            "shots": len(shot_items),
            "reviews": len(reviews),
        },
        "review_decisions": dict(sorted(decisions.items())),
        "validation": {
            "valid": validation_summary["error"] == 0,
            "summary": validation_summary,
            "finding_codes": _finding_codes(validation_findings),
        },
        "release_gate": {
            "release_ready": gate_summary["error"] == 0,
            "summary": gate_summary,
            "finding_codes": _finding_codes(gate_findings),
        },
    }
