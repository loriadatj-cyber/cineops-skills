import json
import unittest
from pathlib import Path

import jsonschema


ROOT = Path(__file__).resolve().parents[1]


class SchemaTests(unittest.TestCase):
    def _assert_project_matches_published_schemas(self, project: Path):
        pairs = (
            ("project.schema.json", "project.json"),
            ("continuity-ledger.schema.json", "continuity-ledger.json"),
            ("shot-plan.schema.json", "shot-plan.json"),
            ("readiness-report.schema.json", "readiness-report.json"),
        )
        for schema_name, artifact_name in pairs:
            with self.subTest(schema=schema_name):
                schema = json.loads((ROOT / "schemas" / schema_name).read_text(encoding="utf-8"))
                artifact = json.loads((project / artifact_name).read_text(encoding="utf-8"))
                jsonschema.Draft202012Validator.check_schema(schema)
                jsonschema.validate(artifact, schema)

    def test_example_matches_published_schemas(self):
        self._assert_project_matches_published_schemas(ROOT / "examples" / "glass-elevator")

    def test_maintainer_pilot_matches_published_schemas(self):
        self._assert_project_matches_published_schemas(
            ROOT / "adoption" / "pilots" / "maintainer-001-anonymized-transfer-sequence"
        )


if __name__ == "__main__":
    unittest.main()
