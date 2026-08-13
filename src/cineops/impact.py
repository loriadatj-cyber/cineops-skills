"""Compute a conservative impact report between two continuity ledgers."""

from __future__ import annotations

from typing import Any


def _index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in items if isinstance(item, dict) and isinstance(item.get("id"), str)}


def compare_ledgers(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    changed_entities: list[dict[str, str]] = []
    changed_ids: set[str] = set()
    for kind in ("characters", "locations", "props"):
        old = _index(before.get(kind, []))
        new = _index(after.get(kind, []))
        for item_id in sorted(old.keys() | new.keys()):
            if item_id not in old:
                change = "added"
            elif item_id not in new:
                change = "removed"
            elif old[item_id] != new[item_id]:
                change = "modified"
            else:
                continue
            changed_ids.add(item_id)
            changed_entities.append({"kind": kind[:-1], "id": item_id, "change": change})

    affected_scenes: set[str] = set()
    for ledger in (before, after):
        for state in ledger.get("scene_states", []):
            if not isinstance(state, dict):
                continue
            references = set(state.get("characters", [])) | set(state.get("locations", [])) | set(state.get("props", []))
            if references & changed_ids and isinstance(state.get("scene_id"), str):
                affected_scenes.add(state["scene_id"])
    return {
        "changed_entities": changed_entities,
        "affected_scenes": sorted(affected_scenes),
        "review_required": bool(changed_entities),
    }
