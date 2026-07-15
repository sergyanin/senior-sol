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

        completed_local_items = [
            "- [x] On Windows, run `python -m unittest discover -s tests -v` in a clean checkout and record zero failures. **Verified 2026-07-15 via `scripts/validate.ps1`.**",
            "- [x] On macOS or Linux, run `python -m unittest discover -s tests -v` in a clean checkout and record zero failures. **Verified 2026-07-15 on GitHub Actions `ubuntu-latest`.**",
            "- [x] Run repository and marketplace validation with `python scripts/validate.py` and record `Repository metadata is valid.` **Verified 2026-07-15.**",
            "- [x] Run official plugin validation for `plugins/senior-sol` from PowerShell with `python (Join-Path $HOME '.codex\\skills\\.system\\plugin-creator\\scripts\\validate_plugin.py') plugins\\senior-sol`; attach the successful output. This validator checks the plugin directory, not the marketplace file. **Verified 2026-07-15; validator exited 0.**",
            "- [x] Confirm the PowerShell and POSIX installer tests cover clean install, idempotent install, conflict refusal, forced replacement, and safe uninstall. **Verified 2026-07-15; isolated PowerShell install also produced exactly five managed profiles and safe uninstall preserved the `agents` directory.**",
            "- [x] Check tracked public files for secrets, credentials, private data, and developer-specific local paths; record the command and result. **Verified 2026-07-15; reviewed secret-like matches and found no credentials or machine-local runtime dependency.**",
        ]
        for item in completed_local_items:
            with self.subTest(completed_local_item=item):
                self.assertIn(item, checklist)

        completed_github_items = [
            "- [x] Run `gh auth status` and confirm the authenticated account is `sergyanin`. **Verified 2026-07-15.**",
            "- [x] Create the public repository `sergyanin/senior-sol`, configure `origin`, and confirm public visibility. **Verified 2026-07-15: https://github.com/sergyanin/senior-sol.**",
            "- [x] Open draft PR #1 from `feat/initial-plugin` to `main` and confirm its Windows and Ubuntu checks pass. **Verified 2026-07-15: https://github.com/sergyanin/senior-sol/pull/1.**",
        ]
        for item in completed_github_items:
            with self.subTest(completed_github_item=item):
                self.assertIn(item, checklist)

        pending_publication_items = [
            "- [ ] Ensure the release branch is integrated into `main`, then run `git push -u origin main`.",
            "- [ ] Confirm the pushed `main` commit matches the locally verified commit.",
            "- [ ] Add the marketplace from GitHub with `codex plugin marketplace add sergyanin/senior-sol`.",
            "- [ ] Complete marketplace installation with `codex plugin add senior-sol@senior-sol`.",
            "- [ ] Install all five managed profiles with the OS-appropriate repository script.",
            "- [ ] Open a new Codex thread after profile installation so custom agents are discovered.",
            "- [ ] In the new thread, select Sol and its intended reasoning level before invoking `$senior-sol`.",
            "- [ ] Execute and record Scenario 1, Luna mechanical edit.",
            "- [ ] Execute and record Scenario 2, Terra read-only investigation.",
            "- [ ] Execute and record Scenario 3, missing verification rejection.",
            "- [ ] Execute and record Scenario 4, overlapping writer serialization.",
            "- [ ] Execute and record Scenario 5, corrected specification after first failure.",
            "- [ ] Execute and record Scenario 6, announced bounded Sol fallback after second failure.",
            "- [ ] Execute and record Scenario 7, installed-profile same-role retry and warned built-in fallback.",
            "- [ ] Create the annotated tag with `git tag -a v0.1.0 -m \"Senior Sol v0.1.0\"`.",
            "- [ ] Push tag `v0.1.0` with `git push origin v0.1.0`.",
            "- [ ] Create the GitHub Release with `gh release create v0.1.0 --title \"Senior Sol v0.1.0\" --notes-file docs/release-checklist.md`.",
            "- [ ] Verify installation once more from the tagged GitHub marketplace and preserve the final new-thread transcript.",
        ]
        for item in pending_publication_items:
            with self.subTest(pending_publication_item=item):
                self.assertIn(item, checklist)

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

    def test_manual_release_docs_cover_installed_profile_availability_fallback(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        scenarios = (ROOT / "docs" / "examples" / "delegation-scenarios.md").read_text(
            encoding="utf-8"
        )
        checklist = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")

        for phrase in (
            "installed managed profile's model or reasoning effort is unavailable",
            "nearest available profile of the same role",
            "Terra remains read-only",
            "does not count toward the two model-failure attempts",
            "built-in `worker` or `explorer`",
        ):
            with self.subTest(readme_phrase=phrase):
                self.assertIn(phrase, readme)

        for phrase in (
            "installed-but-unavailable profile",
            "exactly one same-role retry",
            "leaves the two-attempt fallback counter unchanged",
        ):
            with self.subTest(scenario_phrase=phrase):
                self.assertIn(phrase, scenarios)

        self.assertIn(
            "## Scenario 7 — Installed-profile same-role retry and built-in fallback",
            scenarios,
        )

        self.assertIn(
            "- [ ] Execute and record Scenario 7, installed-profile same-role retry "
            "and warned built-in fallback.",
            checklist,
        )


if __name__ == "__main__":
    unittest.main()
