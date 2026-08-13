import copy
import json
import tempfile
import unittest
from pathlib import Path

from cineops.cli import command_gate, command_init
from cineops.impact import compare_ledgers
from cineops.validator import summarize, validate_project, validate_release_gate


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

    def test_benchmark_corpus_is_reproducible(self):
        corpus = ROOT / "benchmarks" / "continuity-failures"
        manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual("0.1.0", manifest["corpus_version"])
        self.assertEqual("1.0", manifest["artifact_schema_version"])
        self.assertEqual("Apache-2.0", manifest["license"])
        self.assertEqual(12, len(manifest["cases"]))
        self.assertEqual(12, len(set(manifest["cases"])))

        base = {
            path.name: json.loads(path.read_text(encoding="utf-8"))
            for path in (corpus / "base").glob("*.json")
        }
        self.assertEqual([], validate_project(corpus / "base"))

        for case_name in manifest["cases"]:
            with self.subTest(case=case_name):
                case = json.loads((corpus / "cases" / case_name).read_text(encoding="utf-8"))
                documents = copy.deepcopy(base)
                for mutation in case["mutations"]:
                    target = documents[mutation["artifact"]]
                    for segment in mutation["path"][:-1]:
                        target = target[segment]
                    final = mutation["path"][-1]
                    if mutation["operation"] == "set":
                        target[final] = mutation["value"]
                    elif mutation["operation"] == "append":
                        target[final].append(mutation["value"])
                    elif mutation["operation"] == "delete":
                        del target[final]
                    else:
                        self.fail(f"unknown mutation operation: {mutation['operation']}")

                with tempfile.TemporaryDirectory() as directory:
                    fixture = Path(directory)
                    for name, document in documents.items():
                        (fixture / name).write_text(json.dumps(document), encoding="utf-8")
                    actual = {
                        (finding.severity, finding.code, finding.path)
                        for finding in validate_project(fixture)
                    }

                expected = {
                    (item["severity"], item["code"], item["path"])
                    for item in case["expected_findings"]
                }
                self.assertEqual(expected, actual)

    def test_release_gate_accepts_ready_project(self):
        findings = validate_release_gate(ROOT / "examples" / "glass-elevator")
        self.assertEqual(0, summarize(findings)["error"])

    def test_release_gate_rejects_revise_blocked_and_unreviewed_shots(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            command_init(target)
            self.assertEqual(1, command_gate(target, output_json=True))
            findings = validate_release_gate(target)
            self.assertIn("revision-required", {item.code for item in findings})

            report_path = target / "readiness-report.json"
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report["reviews"][0]["decision"] = "blocked"
            report_path.write_text(json.dumps(report), encoding="utf-8")
            self.assertIn("blocked-shot", {item.code for item in validate_release_gate(target)})

            report["reviews"] = []
            report_path.write_text(json.dumps(report), encoding="utf-8")
            self.assertIn("unreviewed-shot-gate", {item.code for item in validate_release_gate(target)})

    def test_maintainer_pilot_is_structurally_valid_but_not_release_ready(self):
        pilot = ROOT / "adoption" / "pilots" / "maintainer-001-anonymized-transfer-sequence"
        self.assertEqual([], validate_project(pilot))
        gate_findings = validate_release_gate(pilot)
        self.assertEqual(7, summarize(gate_findings)["error"])
        self.assertEqual({"revision-required"}, {item.code for item in gate_findings})


if __name__ == "__main__":
    unittest.main()
