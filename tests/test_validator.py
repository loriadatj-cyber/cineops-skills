import json
import tempfile
import unittest
from pathlib import Path

from cineops.cli import command_init
from cineops.impact import compare_ledgers
from cineops.validator import summarize, validate_project


ROOT = Path(__file__).resolve().parents[1]


class ValidatorTests(unittest.TestCase):
    def test_valid_example_has_no_findings(self):
        findings = validate_project(ROOT / "examples" / "glass-elevator")
        self.assertEqual([], findings)

    def test_broken_example_fails_for_real_reasons(self):
        findings = validate_project(ROOT / "examples" / "broken-handoff")
        codes = {finding.code for finding in findings}
        self.assertIn("unknown-reference", codes)
        self.assertIn("invalid-duration", codes)
        self.assertIn("unreviewed-shot", codes)
        self.assertIn("missing-scene-state", codes)
        self.assertGreater(summarize(findings)["error"], 0)

    def test_init_creates_a_valid_shape(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.assertEqual(0, command_init(target))
            self.assertEqual(0, summarize(validate_project(target))["error"])

    def test_missing_artifacts_are_reported_without_crashing(self):
        with tempfile.TemporaryDirectory() as directory:
            findings = validate_project(Path(directory))
            self.assertEqual(4, sum(finding.code == "missing-file" for finding in findings))

    def test_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            command_init(target)
            project_path = target / "project.json"
            project = json.loads(project_path.read_text(encoding="utf-8"))
            project["episodes"].append(project["episodes"][0])
            project_path.write_text(json.dumps(project), encoding="utf-8")
            self.assertIn("duplicate-id", {item.code for item in validate_project(target)})

    def test_impact_finds_changed_entity_and_scene(self):
        before = {
            "characters": [{"id": "CHAR-MARA", "name": "Mara"}],
            "locations": [],
            "props": [],
            "scene_states": [{"scene_id": "SC001", "characters": ["CHAR-MARA"]}],
        }
        after = json.loads(json.dumps(before))
        after["characters"][0]["wardrobe"] = "red coat"
        report = compare_ledgers(before, after)
        self.assertEqual(["SC001"], report["affected_scenes"])
        self.assertTrue(report["review_required"])


if __name__ == "__main__":
    unittest.main()
