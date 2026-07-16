import json
import shutil
import subprocess
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


def track_all_files(root: Path) -> None:
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "core.autocrlf=false", "add", "."],
        cwd=root,
        check=True,
        capture_output=True,
    )


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

    def test_writer_acceptance_requires_independent_diff_and_definition_of_done_evidence(self):
        required_phrases = (
            "inspect the actual changed paths and content",
            "independently rerun or directly observe the exact Definition of done check",
            "Only accept the writer result after both checks pass",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, SKILL_TEXT)

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

    def test_unavailable_managed_model_has_a_non_failure_route(self):
        required_phrases = (
            "does not count toward the two model-failure attempts",
            "retry once with the nearest available profile of the same role",
            "Terra remains read-only",
            "warn the user and offer the built-in `worker` or `explorer` fallback",
            "do not increment the fallback counter",
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

    def test_startup_gate_uses_only_authoritative_exact_model_metadata(self):
        required_phrases = (
            "Model selection is an external prerequisite",
            "Do not infer the main model from generic system identity text or model self-identification",
            "If authoritative runtime metadata is unavailable, explicit invocation of `$senior-sol` is sufficient to continue",
            "If authoritative runtime metadata explicitly identifies the configured main model as non-Sol, stop",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, SKILL_TEXT)
        self.assertNotIn("visible runtime context", SKILL_TEXT)

    def test_startup_gate_checks_only_installed_agent_profile_paths(self):
        required_phrases = (
            "check only the five exact files under `$CODEX_HOME/agents/`",
            "Copies inside the plugin cache or plugin source do not count as installed profiles",
        )
        for phrase in required_phrases:
            self.assertIn(phrase, SKILL_TEXT)


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
            machine_path = "C:" + "\\Users\\author\\plugin"
            marker = "TO" + "DO"
            public_file.write_text(marker + " use " + machine_path, encoding="utf-8")
            excluded = root / "docs" / "superpowers" / "plan.md"
            excluded.parent.mkdir(parents=True)
            excluded.write_text(marker + " use " + machine_path, encoding="utf-8")

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

    def test_validator_accumulates_independent_errors_with_bad_metadata(self):
        with copy_repository() as directory:
            root = Path(directory)
            manifest_path = root / "plugins" / "senior-sol" / ".codex-plugin" / "plugin.json"
            manifest_path.write_text("{not valid json", encoding="utf-8")
            marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
            marketplace_path.unlink()
            profile_path = root / "plugins" / "senior-sol" / "agents" / "senior-sol-luna-low.toml"
            profile_path.unlink()
            skill_path = root / "plugins" / "senior-sol" / "skills" / "senior-sol" / "SKILL.md"
            skill_path.write_text(SKILL_TEXT.replace("name: senior-sol", "name: other", 1), encoding="utf-8")
            public_file = root / "plugins" / "senior-sol" / "bad-note.md"
            machine_path = "C:" + "\\Users\\author\\plugin"
            marker = "TO" + "DO"
            public_file.write_text(marker + " inspect " + machine_path, encoding="utf-8")

            errors = validate_repository(root)

        self.assertTrue(any("plugin.json" in error for error in errors))
        self.assertTrue(any("marketplace.json" in error for error in errors))
        self.assertIn("missing managed agent profile: senior-sol-luna-low.toml", errors)
        self.assertIn("Senior Sol skill frontmatter must declare name: senior-sol", errors)
        self.assertIn("local absolute path found in plugins/senior-sol/bad-note.md", errors)
        self.assertIn("incomplete marker found in plugins/senior-sol/bad-note.md", errors)

    def test_validator_detects_json_escaped_windows_absolute_path(self):
        with copy_repository() as directory:
            root = Path(directory)
            public_file = root / "plugins" / "senior-sol" / "escaped-path.json"
            public_file.write_text(
                json.dumps({"path": "C:" + "\\Users\\author\\plugin"}),
                encoding="utf-8",
            )

            errors = validate_repository(root)

        self.assertIn(
            "local absolute path found in plugins/senior-sol/escaped-path.json",
            errors,
        )

    def test_validator_scans_tracked_github_and_test_files_for_credentials(self):
        with copy_repository() as directory:
            root = Path(directory)
            workflow = root / ".github" / "workflows" / "leak.yml"
            workflow.parent.mkdir(parents=True)
            credential_key = "api_" + "key"
            credential_value = "live-" + "credential-123456"
            workflow.write_text(f'{credential_key}: "{credential_value}"\n', encoding="utf-8")
            test_fixture = root / "tests" / "credential-fixture.txt"
            test_fixture.write_text(f'{"access_" + "token"}={credential_value}\n', encoding="utf-8")
            track_all_files(root)

            errors = validate_repository(root)

        self.assertIn("credential assignment found in .github/workflows/leak.yml", errors)
        self.assertIn("credential assignment found in tests/credential-fixture.txt", errors)

    def test_validator_detects_prefixed_credential_identifiers(self):
        with copy_repository() as directory:
            root = Path(directory)
            fixture = root / "tests" / "prefixed-credentials.txt"
            identifiers = (
                "OPENAI_" + "API_KEY",
                "GITHUB_" + "TOKEN",
                "AWS_" + "SECRET_ACCESS_KEY",
            )
            fixture.write_text(
                "\n".join(
                    f'{identifier}="live-{index}-credential-value"'
                    for index, identifier in enumerate(identifiers, 1)
                )
                + "\n",
                encoding="utf-8",
            )
            track_all_files(root)

            errors = validate_repository(root)

        self.assertIn("credential assignment found in tests/prefixed-credentials.txt", errors)

    def test_validator_ignores_prefixed_credentials_loaded_from_environment(self):
        with copy_repository() as directory:
            root = Path(directory)
            fixture = root / "tests" / "dynamic-credentials.txt"
            api_identifier = "OPENAI_" + "API_KEY"
            token_identifier = "GITHUB_" + "TOKEN"
            secret_identifier = "AWS_" + "SECRET_ACCESS_KEY"
            client_identifier = "SERVICE_" + "CLIENT_SECRET"
            access_identifier = "SERVICE_" + "ACCESS_TOKEN"
            fixture.write_text(
                f'{api_identifier} = os.getenv("API_KEY")\n'
                f'{token_identifier} = os.environ["GITHUB_TOKEN"]\n'
                f'{secret_identifier} = Environment.GetEnvironmentVariable("AWS_SECRET_ACCESS_KEY")\n'
                f'{client_identifier} = getenv("CLIENT_SECRET")\n'
                f'{access_identifier} = process.env.ACCESS_TOKEN\n'
                f'{token_identifier} = $env:GITHUB_TOKEN\n',
                encoding="utf-8",
            )
            track_all_files(root)

            errors = validate_repository(root)

        self.assertNotIn("credential assignment found in tests/dynamic-credentials.txt", errors)

    def test_validator_detects_broad_windows_and_unix_machine_local_paths(self):
        with copy_repository() as directory:
            root = Path(directory)
            fixture = root / "tests" / "local-paths.txt"
            windows_path = "C:" + "\\build\\cache"
            unix_path = "/op" + "t/private/cache"
            fixture.write_text(f"{windows_path}\n{unix_path}\n", encoding="utf-8")
            track_all_files(root)

            errors = validate_repository(root)

        self.assertIn("local absolute path found in tests/local-paths.txt", errors)

    def test_validator_ignores_urls_env_references_detector_source_and_untracked_files(self):
        with copy_repository() as directory:
            root = Path(directory)
            safe = root / "tests" / "safe-security-examples.txt"
            credential_key = "api_" + "key"
            safe.write_text(
                "https://example.com/opt/install\n"
                "https://docs.example.com/Users/guide\n"
                f'{credential_key} = "${{{credential_key.upper()}}}"\n',
                encoding="utf-8",
            )
            track_all_files(root)
            untracked = root / "tests" / "untracked-secret.txt"
            untracked.write_text(
                ("password" + "=live-untracked-credential\n"),
                encoding="utf-8",
            )

            errors = validate_repository(root)

        security_errors = [
            error for error in errors if "credential assignment" in error or "local absolute path" in error
        ]
        self.assertEqual(security_errors, [])


if __name__ == "__main__":
    unittest.main()
