import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_README_TEXT = [
    "codex plugin marketplace add sergyanin/senior-sol",
    "$senior-sol",
    "install-agents.ps1",
    "install-agents.sh",
    "uninstall-agents.ps1",
    "uninstall-agents.sh",
    "AndyShaman/senior-fable",
    "MIT",
]


class DocumentationTests(unittest.TestCase):
    def test_readme_contains_public_usage_contract(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for required_text in REQUIRED_README_TEXT:
            with self.subTest(required_text=required_text):
                self.assertIn(required_text, readme)

    def test_license_is_mit_for_sergyanin(self):
        license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

        self.assertIn("MIT License", license_text)
        self.assertIn("Copyright (c) 2026 sergyanin", license_text)

    def test_manual_guide_has_exactly_seven_scenarios(self):
        scenarios = (ROOT / "docs" / "examples" / "delegation-scenarios.md").read_text(
            encoding="utf-8"
        )

        headings = [line for line in scenarios.splitlines() if line.startswith("## Scenario")]
        self.assertEqual(len(headings), 7)

    def test_release_checklist_contains_release_evidence(self):
        checklist = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")
        required_text = [
            "python -m unittest discover -s tests -v",
            "python scripts/validate.py",
            "official plugin validation",
            "marketplace installation",
            "new Codex thread",
            "v0.1.0",
        ]

        for item in required_text:
            with self.subTest(item=item):
                self.assertIn(item, checklist)


if __name__ == "__main__":
    unittest.main()
