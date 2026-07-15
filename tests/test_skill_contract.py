import json
import shutil
import tempfile
import unittest
from pathlib import Path

from scripts.validate import validate_repository


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "plugins" / "senior-sol" / "skills" / "senior-sol" / "SKILL.md"
SKILL_TEXT = SKILL_PATH.read_text(encoding="utf-8")

REQUIRED_HEADINGS = {
    "## Startup gate",
    "## Delegation matrix",
    "## Delegation contract",
    "## Acceptance gate",
    "## Failure and fallback policy",
    "## Final synthesis",
}
REQUIRED_PROFILES = {
    "senior-sol-luna-low",
    "senior-sol-luna-medium",
    "senior-sol-terra-low",
    "senior-sol-terra-medium",
    "senior-sol-terra-high",
}
WRITER_SCHEMA = ("Done", "Verified", "Not done / questions")
RESEARCHER_SCHEMA = ("Answer", "Evidence", "Ruled out", "Open questions")


def copy_repository() -> tempfile.TemporaryDirectory:
    directory = tempfile.TemporaryDirectory()
    root = Path(directory.name)
    for relative in (".agents", "plugins", "scripts", "tests"):
        source = ROOT / relative
        if source.exists():
            shutil.copytree(source, root / relative)
    return directory


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_declares_public_skill_name(self):
        self.assertTrue(SKILL_TEXT.startswith("---\n"))
        frontmatter = SKILL_TEXT.split("---", 2)[1]
        self.assertIn("name: senior-sol", frontmatter.splitlines())

    def test_required_workflow_sections_and_profiles_are_present(self):
        for heading in REQUIRED_HEADINGS:
            self.assertIn(heading, SKILL_TEXT)
        for profile in REQUIRED_PROFILES:
            self.assertIn(profile, SKILL_TEXT)

    def test_delegation_contract_and_both_report_schemas_are_explicit(self):
        for field in (
            "Goal:",
            "Files:",
            "Constraints:",
            "Definition of done:",
            "Report format:",
        ):
            self.assertIn(field, SKILL_TEXT)
        for section in WRITER_SCHEMA + RESEARCHER_SCHEMA:
            self.assertIn(section, SKILL_TEXT)
        self.assertIn("One writer per file set.", SKILL_TEXT)

    def test_retry_and_fallback_policy_is_bounded_and_disclosed(self):
        required_phrases = (
            "never retry an unchanged specification",
            "After two failed delegations",
            "notify the user",
            "same bounded subtask",
            "implement only that subtask",
            "verify it",
            "disclose the main-agent implementation in the final report",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, SKILL_TEXT)

    def test_skill_does_not_mutate_main_model_or_reasoning_settings(self):
        forbidden_commands = (
            "codex -m ",
            "codex --model ",
            "/model",
            "config set model",
            "model_reasoning_effort =",
        )
        for command in forbidden_commands:
            self.assertNotIn(command, SKILL_TEXT)


class SkillValidatorTests(unittest.TestCase):
    def test_validator_requires_manifest_skill_path(self):
        with copy_repository() as directory:
            root = Path(directory)
            manifest_path = root / "plugins" / "senior-sol" / ".codex-plugin" / "plugin.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["skills"] = "./other-skills/"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            errors = validate_repository(root)

        self.assertIn("plugin skills path must be ./skills/", errors)

    def test_validator_parses_frontmatter_and_requires_skill_name(self):
        with copy_repository() as directory:
            root = Path(directory)
            skill_path = root / "plugins" / "senior-sol" / "skills" / "senior-sol" / "SKILL.md"
            skill_path.write_text(SKILL_TEXT.replace("name: senior-sol", "name: other", 1), encoding="utf-8")

            errors = validate_repository(root)

        self.assertIn("Senior Sol skill frontmatter must declare name: senior-sol", errors)

    def test_validator_scans_public_runtime_text_but_excludes_plan_docs(self):
        with copy_repository() as directory:
            root = Path(directory)
            public_file = root / "plugins" / "senior-sol" / "skills" / "public-note.md"
            public_file.write_text("TODO use C:\\Users\\author\\plugin", encoding="utf-8")
            excluded = root / "docs" / "superpowers" / "plan.md"
            excluded.parent.mkdir(parents=True)
            excluded.write_text("TODO use C:\\Users\\author\\plugin", encoding="utf-8")

            errors = validate_repository(root)

        self.assertTrue(any("local absolute path" in error and "public-note.md" in error for error in errors))
        self.assertTrue(any("incomplete marker" in error and "public-note.md" in error for error in errors))
        self.assertFalse(any("plan.md" in error for error in errors))

    def test_validator_accumulates_errors_instead_of_exiting_early(self):
        with copy_repository() as directory:
            root = Path(directory)
            skill_path = root / "plugins" / "senior-sol" / "skills" / "senior-sol" / "SKILL.md"
            skill_path.unlink()
            profile_path = root / "plugins" / "senior-sol" / "agents" / "senior-sol-luna-low.toml"
            profile_path.unlink()

            errors = validate_repository(root)

        self.assertTrue(any("skill" in error.lower() for error in errors))
        self.assertIn("missing managed agent profile: senior-sol-luna-low.toml", errors)


if __name__ == "__main__":
    unittest.main()
