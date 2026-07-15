import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "senior-sol"


class MetadataTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
