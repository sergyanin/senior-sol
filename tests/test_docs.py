import re
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

        sections = re.findall(
            r"(?ms)^## Scenario .*?(?=^## Scenario |\Z)",
            scenarios,
        )
        self.assertEqual(len(sections), 7)
        for number, section in enumerate(sections, 1):
            with self.subTest(scenario=number):
                for field in (
                    "Setup",
                    "Prompt",
                    "Expected routing",
                    "Expected evidence",
                    "Failure signal",
                ):
                    self.assertIn(f"**{field}:**", section)

        for number in (3, 5, 6):
            with self.subTest(contract_simulation=number):
                section = sections[number - 1]
                self.assertIn("Contract simulation", section)
                self.assertIn("Fabricated Luna report", section)
                self.assertIn("Do not edit files", section)
                self.assertIn("in scope:", section)

        for vague_instruction in ("arrange for", "cause two", "Use a bounded task"):
            with self.subTest(vague_instruction=vague_instruction):
                self.assertNotIn(vague_instruction, scenarios)

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

        checklist_items = [line for line in checklist.splitlines() if line.startswith("- [")]
        self.assertTrue(checklist_items)
        for item in checklist_items:
            with self.subTest(unchecked_item=item):
                self.assertRegex(item, r"^- \[ \] ")

        repository_validation = (
            "Run repository and marketplace validation with "
            "`python scripts/validate.py`"
        )
        official_validation = (
            "`python (Join-Path $HOME '.codex\\skills\\.system\\plugin-creator\\scripts\\"
            "validate_plugin.py') plugins\\senior-sol`"
        )
        self.assertIn(repository_validation, checklist)
        self.assertIn(official_validation, checklist)

    def test_readme_update_repeats_full_profile_installer_commands(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "powershell -NoProfile -File "
            "plugins/senior-sol/scripts/install-agents.ps1 -Force",
            readme,
        )
        self.assertIn(
            "sh plugins/senior-sol/scripts/install-agents.sh --force",
            readme,
        )


if __name__ == "__main__":
    unittest.main()
