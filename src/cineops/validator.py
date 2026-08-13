"""Deterministic validation for CineOps project artifacts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ID_PATTERNS = {
    "episode": re.compile(r"^EP\d{3}$"),
    "scene": re.compile(r"^SC\d{3}$"),
    "shot": re.compile(r"^SH\d{3}$"),
    "character": re.compile(r"^CHAR-[A-Z0-9-]+$"),
    "location": re.compile(r"^LOC-[A-Z0-9-]+$"),
    "prop": re.compile(r"^PROP-[A-Z0-9-]+$"),
}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.severity.upper():7} {self.code:24} {self.path}: {self.message}"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _finding(severity: str, code: str, path: str, message: str) -> Finding:
    return Finding(severity, code, path, message)


def _require(mapping: dict[str, Any], keys: tuple[str, ...], path: str) -> list[Finding]:
    return [
        _finding("error", "required-field", path, f"missing required field '{key}'")
        for key in keys
        if key not in mapping
    ]


def _check_ids(items: Any, kind: str, path: str) -> tuple[set[str], list[Finding]]:
    findings: list[Finding] = []
    ids: set[str] = set()
    if not isinstance(items, list):
        return ids, [_finding("error", "expected-list", path, "must be a list")]
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            findings.append(_finding("error", "expected-object", item_path, "must be an object"))
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not ID_PATTERNS[kind].fullmatch(item_id):
            findings.append(_finding("error", "invalid-id", item_path, f"expected a valid {kind} id"))
            continue
        if item_id in ids:
            findings.append(_finding("error", "duplicate-id", item_path, f"duplicate id '{item_id}'"))
        ids.add(item_id)
    return ids, findings


def _check_refs(values: Any, allowed: set[str], path: str, kind: str) -> list[Finding]:
    if values is None:
        return []
    if not isinstance(values, list):
        return [_finding("error", "expected-list", path, "references must be a list")]
    return [
        _finding("error", "unknown-reference", f"{path}[{index}]", f"unknown {kind} '{value}'")
        for index, value in enumerate(values)
        if value not in allowed
    ]


def _check_state_transition(
    previous: dict[str, Any],
    current: dict[str, Any],
    current_path: str,
) -> list[Finding]:
    findings: list[Finding] = []
    for key in sorted(previous.keys() & current.keys()):
        if previous[key] != current[key]:
            findings.append(
                _finding(
                    "error",
                    "shot-state-mismatch",
                    f"{current_path}.{key}",
                    f"entry state {current[key]!r} does not match previous exit state {previous[key]!r}",
                )
            )
    return findings


def validate_project(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    paths = {
        "project": root / "project.json",
        "ledger": root / "continuity-ledger.json",
        "shots": root / "shot-plan.json",
        "review": root / "readiness-report.json",
    }
    documents: dict[str, Any] = {}
    for name, path in paths.items():
        if not path.exists():
            findings.append(_finding("error", "missing-file", path.name, "required artifact is missing"))
            continue
        try:
            documents[name] = load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            findings.append(_finding("error", "invalid-json", path.name, str(exc)))

    if findings:
        return findings

    project = documents["project"]
    ledger = documents["ledger"]
    shots = documents["shots"]
    review = documents["review"]
    for name, document in documents.items():
        if not isinstance(document, dict):
            findings.append(_finding("error", "expected-object", paths[name].name, "top level must be an object"))
    if findings:
        return findings

    findings += _require(project, ("schema_version", "project_id", "title", "episodes"), "project.json")
    findings += _require(ledger, ("schema_version", "characters", "locations", "props", "scene_states"), "continuity-ledger.json")
    findings += _require(shots, ("schema_version", "shots"), "shot-plan.json")
    findings += _require(review, ("schema_version", "reviews"), "readiness-report.json")

    episode_ids, result = _check_ids(project.get("episodes", []), "episode", "project.json.episodes")
    findings += result
    scene_items: list[Any] = []
    for index, episode in enumerate(project.get("episodes", [])):
        if isinstance(episode, dict):
            scenes = episode.get("scenes", [])
            if not isinstance(scenes, list):
                findings.append(_finding("error", "expected-list", f"project.json.episodes[{index}].scenes", "must be a list"))
            else:
                scene_items.extend(scenes)
    scene_ids, result = _check_ids(scene_items, "scene", "project.json.scenes")
    findings += result
    character_ids, result = _check_ids(ledger.get("characters", []), "character", "continuity-ledger.json.characters")
    findings += result
    location_ids, result = _check_ids(ledger.get("locations", []), "location", "continuity-ledger.json.locations")
    findings += result
    prop_ids, result = _check_ids(ledger.get("props", []), "prop", "continuity-ledger.json.props")
    findings += result
    shot_ids, result = _check_ids(shots.get("shots", []), "shot", "shot-plan.json.shots")
    findings += result

    if not episode_ids:
        findings.append(_finding("error", "empty-production", "project.json.episodes", "at least one episode is required"))

    previous_order = -1
    previous_shot_by_scene: dict[str, dict[str, Any]] = {}
    scene_state_by_id = {
        state.get("scene_id"): state
        for state in ledger.get("scene_states", [])
        if isinstance(state, dict) and isinstance(state.get("scene_id"), str)
    }
    for index, shot in enumerate(shots.get("shots", [])):
        if not isinstance(shot, dict):
            continue
        path = f"shot-plan.json.shots[{index}]"
        findings += _require(shot, ("id", "scene_id", "order", "duration_seconds", "purpose", "action", "camera", "entry_state", "exit_state"), path)
        scene_id = shot.get("scene_id")
        if scene_id not in scene_ids:
            findings.append(_finding("error", "unknown-reference", path + ".scene_id", f"unknown scene '{scene_id}'"))
        order = shot.get("order")
        if not isinstance(order, int) or order <= previous_order:
            findings.append(_finding("error", "shot-order", path + ".order", "orders must be strictly increasing integers"))
        elif isinstance(order, int):
            previous_order = order
        duration = shot.get("duration_seconds")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
            findings.append(_finding("error", "invalid-duration", path + ".duration_seconds", "must be greater than zero"))
        findings += _check_refs(shot.get("characters"), character_ids, path + ".characters", "character")
        findings += _check_refs(shot.get("props"), prop_ids, path + ".props", "prop")
        location_id = shot.get("location_id")
        if location_id is not None and location_id not in location_ids:
            findings.append(_finding("error", "unknown-reference", path + ".location_id", f"unknown location '{location_id}'"))

        entry_state = shot.get("entry_state")
        exit_state = shot.get("exit_state")
        previous_shot = previous_shot_by_scene.get(scene_id)
        if previous_shot is not None and isinstance(entry_state, dict):
            previous_exit = previous_shot.get("exit_state")
            if isinstance(previous_exit, dict):
                findings += _check_state_transition(previous_exit, entry_state, path + ".entry_state")
        if isinstance(scene_id, str):
            previous_shot_by_scene[scene_id] = shot

        shot_revision = shot.get("source_revision")
        scene_state = scene_state_by_id.get(scene_id)
        ledger_revision = scene_state.get("source_revision") if isinstance(scene_state, dict) else None
        if shot_revision is not None and ledger_revision is not None and shot_revision != ledger_revision:
            findings.append(
                _finding(
                    "error",
                    "source-revision-mismatch",
                    path + ".source_revision",
                    f"shot uses revision '{shot_revision}' but canonical scene state uses '{ledger_revision}'",
                )
            )

    reviewed: set[str] = set()
    for index, item in enumerate(review.get("reviews", [])):
        path = f"readiness-report.json.reviews[{index}]"
        if not isinstance(item, dict):
            findings.append(_finding("error", "expected-object", path, "must be an object"))
            continue
        findings += _require(item, ("shot_id", "decision", "checks", "notes"), path)
        shot_id = item.get("shot_id")
        if shot_id not in shot_ids:
            findings.append(_finding("error", "unknown-reference", path + ".shot_id", f"unknown shot '{shot_id}'"))
        else:
            reviewed.add(shot_id)
        if item.get("decision") not in {"ready", "revise", "blocked"}:
            findings.append(_finding("error", "invalid-decision", path + ".decision", "use ready, revise, or blocked"))
        checks = item.get("checks")
        if not isinstance(checks, dict) or any(value not in {"pass", "fail", "unknown"} for value in checks.values()):
            findings.append(_finding("error", "invalid-checks", path + ".checks", "check values must be pass, fail, or unknown"))
        elif item.get("decision") == "ready":
            unresolved = sorted(key for key, value in checks.items() if value != "pass")
            if unresolved:
                findings.append(
                    _finding(
                        "error",
                        "ready-check-failed",
                        path + ".checks",
                        "ready decisions require every check to pass; unresolved: " + ", ".join(unresolved),
                    )
                )
    for shot_id in sorted(shot_ids - reviewed):
        findings.append(_finding("warning", "unreviewed-shot", "readiness-report.json", f"shot '{shot_id}' has no readiness review"))

    state_scenes: set[str] = set()
    for index, state in enumerate(ledger.get("scene_states", [])):
        path = f"continuity-ledger.json.scene_states[{index}]"
        if not isinstance(state, dict):
            findings.append(_finding("error", "expected-object", path, "must be an object"))
            continue
        scene_id = state.get("scene_id")
        if scene_id not in scene_ids:
            findings.append(_finding("error", "unknown-reference", path + ".scene_id", f"unknown scene '{scene_id}'"))
        else:
            state_scenes.add(scene_id)
    for scene_id in sorted(scene_ids - state_scenes):
        findings.append(_finding("warning", "missing-scene-state", "continuity-ledger.json", f"scene '{scene_id}' has no canonical state"))
    return findings


def summarize(findings: list[Finding]) -> dict[str, int]:
    counts = {"error": 0, "warning": 0, "info": 0}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    return counts
