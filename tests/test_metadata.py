import json
import copy
import tempfile
import unittest
from pathlib import Path

from scripts.validate import validate_repository

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "senior-sol"
VALID_MANIFEST = json.loads((PLUGIN / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
VALID_MARKETPLACE = json.loads((ROOT / ".agents" / "plugins" / "marketplace.json").read_text(encoding="utf-8"))


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
        shell_wrapper = ROOT / "scripts" / "validate.sh"
        self.assertTrue(shell_wrapper.is_file())
        shell_text = shell_wrapper.read_text(encoding="utf-8")
        self.assertIn("command -v python", shell_text)
        self.assertIn("command -v python.exe", shell_text)

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

    def test_validator_rejects_each_required_marketplace_field_and_shape(self):
        cases = (
            ("top-level name", lambda data: data.__setitem__("name", "other"), "marketplace name must be senior-sol"),
            ("interface object", lambda data: data.__setitem__("interface", None), "marketplace interface must be a JSON object"),
            ("display name", lambda data: data["interface"].__setitem__("displayName", "Other"), "marketplace displayName must be Senior Sol"),
            ("entry count", lambda data: data.__setitem__("plugins", []), "marketplace must contain exactly one plugin entry"),
            ("entry object", lambda data: data.__setitem__("plugins", [None]), "marketplace plugin entry must be a JSON object"),
            ("entry name", lambda data: data["plugins"][0].__setitem__("name", "other"), "marketplace plugin entry name must be senior-sol"),
            ("source kind", lambda data: data["plugins"][0]["source"].__setitem__("source", "url"), "marketplace source.source must be local"),
            ("source path", lambda data: data["plugins"][0]["source"].__setitem__("path", "./other"), "marketplace source path must be ./plugins/senior-sol"),
            ("policy shape", lambda data: data["plugins"][0].__setitem__("policy", []), "marketplace policy must be a JSON object"),
            ("installation policy", lambda data: data["plugins"][0]["policy"].__setitem__("installation", "BLOCKED"), "marketplace policy must be exactly AVAILABLE/ON_INSTALL"),
            ("authentication policy", lambda data: data["plugins"][0]["policy"].__setitem__("authentication", "NONE"), "marketplace policy must be exactly AVAILABLE/ON_INSTALL"),
            ("category", lambda data: data["plugins"][0].__setitem__("category", "Other"), "marketplace category must be Productivity"),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                marketplace = copy.deepcopy(VALID_MARKETPLACE)
                mutate(marketplace)
                self.assertIn(expected, validate_data(VALID_MANIFEST, marketplace))

    def test_validator_rejects_each_required_plugin_field_and_shape(self):
        cases = (
            ("name", lambda data: data.__setitem__("name", "other"), "plugin name must be senior-sol"),
            ("version", lambda data: data.__setitem__("version", "0.1"), "plugin version must be exactly 0.1.0"),
            ("description", lambda data: data.__setitem__("description", ""), "plugin description must be a non-empty string"),
            ("author object", lambda data: data.__setitem__("author", None), "plugin author must be a JSON object"),
            ("author name", lambda data: data["author"].__setitem__("name", ""), "plugin author.name must be a non-empty string"),
            ("skills", lambda data: data.__setitem__("skills", "./other/"), "plugin skills path must be ./skills/"),
            ("license", lambda data: data.__setitem__("license", "Other"), "plugin license must be MIT"),
            ("repository", lambda data: data.__setitem__("repository", "https://example.com/other"), "plugin repository must be https://github.com/sergyanin/senior-sol"),
            ("interface object", lambda data: data.__setitem__("interface", None), "plugin interface must be a JSON object"),
            ("displayName", lambda data: data["interface"].__setitem__("displayName", ""), "plugin interface.displayName must be a non-empty string"),
            ("shortDescription", lambda data: data["interface"].__setitem__("shortDescription", ""), "plugin interface.shortDescription must be a non-empty string"),
            ("longDescription", lambda data: data["interface"].__setitem__("longDescription", ""), "plugin interface.longDescription must be a non-empty string"),
            ("developerName", lambda data: data["interface"].__setitem__("developerName", ""), "plugin interface.developerName must be a non-empty string"),
            ("category", lambda data: data["interface"].__setitem__("category", ""), "plugin interface.category must be a non-empty string"),
            ("capabilities", lambda data: data["interface"].__setitem__("capabilities", ["Read"]), "plugin capabilities must be exactly Read and Write"),
            ("defaultPrompt type", lambda data: data["interface"].__setitem__("defaultPrompt", "prompt"), "plugin interface.defaultPrompt must be a non-empty list of non-empty strings"),
            ("defaultPrompt empty", lambda data: data["interface"].__setitem__("defaultPrompt", []), "plugin interface.defaultPrompt must be a non-empty list of non-empty strings"),
            ("defaultPrompt item", lambda data: data["interface"].__setitem__("defaultPrompt", [""]), "plugin interface.defaultPrompt must be a non-empty list of non-empty strings"),
        )
        for label, mutate, expected in cases:
            with self.subTest(label=label):
                manifest = copy.deepcopy(VALID_MANIFEST)
                mutate(manifest)
                self.assertIn(expected, validate_data(manifest, VALID_MARKETPLACE))


if __name__ == "__main__":
    unittest.main()
