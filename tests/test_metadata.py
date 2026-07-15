import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate import validate_repository

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "senior-sol"


def validate_data(manifest, marketplace):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        manifest_path = root / "plugins" / "senior-sol" / ".codex-plugin" / "plugin.json"
        marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
        manifest_path.parent.mkdir(parents=True)
        marketplace_path.parent.mkdir(parents=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")
        return validate_repository(root)


class MetadataTests(unittest.TestCase):
    def test_validation_wrappers_and_ci_workflow(self):
        self.assertTrue((ROOT / "scripts" / "validate.ps1").is_file())
        self.assertTrue((ROOT / "scripts" / "validate.sh").is_file())

        workflow_path = ROOT / ".github" / "workflows" / "ci.yml"
        self.assertTrue(workflow_path.is_file())
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("ubuntu-latest", workflow)
        self.assertIn("windows-latest", workflow)
        self.assertIn("python -m unittest discover -s tests -v", workflow)
        self.assertIn("python scripts/validate.py", workflow)

    def test_plugin_manifest(self):
        data = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "senior-sol")
        self.assertEqual(data["version"], "0.1.0")
        self.assertEqual(data["skills"], "./skills/")
        self.assertEqual(data["license"], "MIT")
        self.assertEqual(data["repository"], "https://github.com/sergyanin/senior-sol")
        self.assertEqual(data["author"]["name"], "sergyanin")
        self.assertEqual(data["interface"]["capabilities"], ["Read", "Write"])

    def test_marketplace_points_to_plugin(self):
        data = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(data["name"], "senior-sol")
        self.assertEqual(len(data["plugins"]), 1)
        entry = data["plugins"][0]
        self.assertEqual(entry["name"], "senior-sol")
        self.assertEqual(entry["source"], {"source": "local", "path": "./plugins/senior-sol"})
        self.assertEqual(entry["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL"})
        self.assertEqual(entry["category"], "Productivity")

    def test_validator_rejects_manifest_array(self):
        errors = validate_data([], {"plugins": []})
        self.assertIn("plugin manifest must be a JSON object", errors)

    def test_validator_rejects_null_interface(self):
        manifest = {"name": "senior-sol", "version": "0.1.0", "interface": None}
        errors = validate_data(manifest, {"plugins": []})
        self.assertIn("plugin interface must be a JSON object", errors)

    def test_validator_rejects_non_list_plugins(self):
        manifest = {
            "name": "senior-sol",
            "version": "0.1.0",
            "interface": {"capabilities": ["Read", "Write"]},
        }
        errors = validate_data(manifest, {"plugins": {"senior-sol": {}}})
        self.assertIn("marketplace plugins must be a JSON array", errors)

    def test_validator_rejects_marketplace_array(self):
        manifest = {
            "name": "senior-sol",
            "version": "0.1.0",
            "interface": {"capabilities": ["Read", "Write"]},
        }
        errors = validate_data(manifest, [])
        self.assertIn("marketplace must be a JSON object", errors)

    def test_validator_rejects_non_object_plugin_entry(self):
        manifest = {
            "name": "senior-sol",
            "version": "0.1.0",
            "interface": {"capabilities": ["Read", "Write"]},
        }
        errors = validate_data(manifest, {"plugins": [None]})
        self.assertIn("marketplace plugin entry must be a JSON object", errors)

    def test_validator_rejects_non_object_plugin_source(self):
        manifest = {
            "name": "senior-sol",
            "version": "0.1.0",
            "interface": {"capabilities": ["Read", "Write"]},
        }
        marketplace = {"plugins": [{"name": "senior-sol", "source": None}]}
        errors = validate_data(manifest, marketplace)
        self.assertIn("marketplace plugin source must be a JSON object", errors)


if __name__ == "__main__":
    unittest.main()
