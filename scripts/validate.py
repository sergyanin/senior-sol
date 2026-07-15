from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path


MANAGED_PROFILES = {
    "senior-sol-luna-low": ("gpt-5.6-luna", "low", False),
    "senior-sol-luna-medium": ("gpt-5.6-luna", "medium", False),
    "senior-sol-terra-low": ("gpt-5.6-terra", "low", True),
    "senior-sol-terra-medium": ("gpt-5.6-terra", "medium", True),
    "senior-sol-terra-high": ("gpt-5.6-terra", "high", True),
}

INCOMPLETE_MARKER = re.compile(
    r"\b(?:"
    + "|".join(
        ("TO" + "DO", "T" + "BD", "FIX" + "ME", "X" * 3, "PLACE" + "HOLDER")
    )
    + r")\b",
    re.IGNORECASE,
)
_UNIX_LOCAL_ROOTS = (
    "Us" + "ers",
    "ho" + "me",
    "ro" + "ot",
    "op" + "t",
    "pri" + "vate",
    "tm" + "p",
    "va" + "r",
    "et" + "c",
    "mn" + "t",
    "sr" + "v",
    "work" + "space",
    "us" + "r",
)
LOCAL_ABSOLUTE_PATH = re.compile(
    r"(?:"
    r"(?<![A-Za-z0-9])[A-Za-z]:(?:\\\\|[\\/](?![\\/]))[^\s`\"']+"
    r"|(?<![A-Za-z0-9@])/(?:"
    + "|".join(_UNIX_LOCAL_ROOTS)
    + r")(?:/|\b)[^\s`\"']*"
    r")"
)
DOCUMENTATION_URL = re.compile(r"\b(?:https?|git\+https)://[^\s`\"'<>]+", re.IGNORECASE)
_CREDENTIAL_SUFFIXES = (
    "api_" + "key",
    "client_" + "secret",
    "access_" + "token",
    "secret_" + "access_key",
    "access_" + "key",
    "private_" + "key",
    "to" + "ken",
    "pass" + "word",
    "pass" + "wd",
    "sec" + "ret",
)
CREDENTIAL_ASSIGNMENT = re.compile(
    r"^[ \t]*(?:(?:export|const|let|var)[ \t]+)?[\"']?"
    r"(?P<identifier>[A-Za-z_][A-Za-z0-9_-]*)[\"']?[ \t]*[:=][ \t]*"
    r"(?P<value>[^#\r\n]+)",
    re.IGNORECASE | re.MULTILINE,
)


def _frontmatter(text: str) -> dict[str, str] | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        closing = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return None
    values: dict[str, str] = {}
    for line in lines[1:closing]:
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip()
    return values


def _tracked_files(root: Path) -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z"],
            check=False,
            capture_output=True,
        )
    except OSError:
        result = None
    if result is not None and result.returncode == 0:
        return sorted(
            root / Path(os.fsdecode(item))
            for item in result.stdout.split(b"\0")
            if item
        )
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    )


def _has_nontrivial_credential_assignment(text: str) -> bool:
    placeholders = {
        "",
        "none",
        "null",
        "redacted",
        "<redacted>",
        "changeme",
        "example",
        "place" + "holder",
        "***",
    }
    dynamic_prefixes = (
        "${",
        "$env:",
        "os.getenv(",
        "os.environ",
        "environ.get(",
        "getenv(",
        "process.env",
        "secrets.",
        "env[",
        "environment.getenvironmentvariable(",
        "system.getenv(",
    )
    for match in CREDENTIAL_ASSIGNMENT.finditer(text):
        identifier = match.group("identifier").strip("_-").replace("-", "_").lower()
        if not any(
            identifier == suffix or identifier.endswith("_" + suffix)
            for suffix in _CREDENTIAL_SUFFIXES
        ):
            continue
        value = match.group("value").strip().rstrip(",;").strip().strip("\"'").strip()
        lowered = value.lower()
        if lowered in placeholders or lowered.startswith(dynamic_prefixes):
            continue
        if len(value) >= 6 and any(character.isalnum() for character in value):
            return True
    return False


def _load_json(path: Path, label: str, errors: list[str]) -> object:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"cannot read {label} {path.as_posix()}: {exc}")
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"invalid {label} {path.as_posix()}: {exc}")
        return {}


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    plugin = root / "plugins" / "senior-sol"
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    manifest = _load_json(manifest_path, "plugin manifest", errors)
    marketplace = _load_json(marketplace_path, "marketplace", errors)

    manifest_is_object = isinstance(manifest, dict)
    marketplace_is_object = isinstance(marketplace, dict)
    if not manifest_is_object:
        errors.append("plugin manifest must be a JSON object")
        manifest = {}
    if not marketplace_is_object:
        errors.append("marketplace must be a JSON object")
        marketplace = {}

    if manifest.get("name") != plugin.name:
        errors.append("plugin name must be senior-sol")
    if manifest.get("version") != "0.1.0":
        errors.append("plugin version must be exactly 0.1.0")
    if not isinstance(manifest.get("description"), str) or not manifest.get("description", "").strip():
        errors.append("plugin description must be a non-empty string")
    author = manifest.get("author")
    if not isinstance(author, dict):
        errors.append("plugin author must be a JSON object")
    elif not isinstance(author.get("name"), str) or not author.get("name", "").strip():
        errors.append("plugin author.name must be a non-empty string")
    skills_path = manifest.get("skills")
    if skills_path != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    if manifest.get("license") != "MIT":
        errors.append("plugin license must be MIT")
    if manifest.get("repository") != "https://github.com/sergyanin/senior-sol":
        errors.append("plugin repository must be https://github.com/sergyanin/senior-sol")
    interface = manifest.get("interface", {})
    if not isinstance(interface, dict):
        errors.append("plugin interface must be a JSON object")
    else:
        for field in (
            "displayName",
            "shortDescription",
            "longDescription",
            "developerName",
            "category",
        ):
            value = interface.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"plugin interface.{field} must be a non-empty string")
        if interface.get("capabilities") != ["Read", "Write"]:
            errors.append("plugin capabilities must be exactly Read and Write")
        default_prompt = interface.get("defaultPrompt")
        if (
            not isinstance(default_prompt, list)
            or not default_prompt
            or any(not isinstance(item, str) or not item.strip() for item in default_prompt)
        ):
            errors.append(
                "plugin interface.defaultPrompt must be a non-empty list of non-empty strings"
            )

    if marketplace.get("name") != "senior-sol":
        errors.append("marketplace name must be senior-sol")
    marketplace_interface = marketplace.get("interface")
    if not isinstance(marketplace_interface, dict):
        errors.append("marketplace interface must be a JSON object")
    elif marketplace_interface.get("displayName") != "Senior Sol":
        errors.append("marketplace displayName must be Senior Sol")
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        errors.append("marketplace plugins must be a JSON array")
        entries = []
    if marketplace_is_object and len(entries) != 1:
        errors.append("marketplace must contain exactly one plugin entry")
    if len(entries) == 1 and not isinstance(entries[0], dict):
        errors.append("marketplace plugin entry must be a JSON object")
    elif len(entries) == 1:
        entry = entries[0]
        if entry.get("name") != "senior-sol":
            errors.append("marketplace plugin entry name must be senior-sol")
        source = entry.get("source", {})
        if not isinstance(source, dict):
            errors.append("marketplace plugin source must be a JSON object")
        else:
            if source.get("source") != "local":
                errors.append("marketplace source.source must be local")
            if source.get("path") != "./plugins/senior-sol":
                errors.append("marketplace source path must be ./plugins/senior-sol")
        policy = entry.get("policy")
        if not isinstance(policy, dict):
            errors.append("marketplace policy must be a JSON object")
        elif policy != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
            errors.append("marketplace policy must be exactly AVAILABLE/ON_INSTALL")
        if entry.get("category") != "Productivity":
            errors.append("marketplace category must be Productivity")

    agent_dir = plugin / "agents"
    actual_profiles = {path.stem for path in agent_dir.glob("*.toml")}
    expected_profiles = set(MANAGED_PROFILES)
    for name in sorted(expected_profiles - actual_profiles):
        errors.append(f"missing managed agent profile: {name}.toml")
    for name in sorted(actual_profiles - expected_profiles):
        errors.append(f"unexpected agent profile: {name}.toml")

    for name in sorted(expected_profiles & actual_profiles):
        profile_path = agent_dir / f"{name}.toml"
        try:
            profile = tomllib.loads(profile_path.read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f"invalid agent profile {name}.toml: {exc}")
            continue

        model, effort, read_only = MANAGED_PROFILES[name]
        if profile.get("name") != name:
            errors.append(f"agent profile {name}.toml must declare name {name}")
        if profile.get("model") != model:
            errors.append(f"agent profile {name}.toml must use model {model}")
        if profile.get("model_reasoning_effort") != effort:
            errors.append(f"agent profile {name}.toml must use reasoning effort {effort}")
        if not profile.get("description"):
            errors.append(f"agent profile {name}.toml must have a description")
        if not profile.get("developer_instructions"):
            errors.append(f"agent profile {name}.toml must have developer instructions")
        expected_sandbox = "read-only" if read_only else None
        if profile.get("sandbox_mode") != expected_sandbox:
            errors.append(
                f"agent profile {name}.toml must have sandbox_mode {expected_sandbox!r}"
            )

    skill_path = plugin / "skills" / "senior-sol" / "SKILL.md"
    if not skill_path.is_file():
        errors.append("missing Senior Sol skill: plugins/senior-sol/skills/senior-sol/SKILL.md")
    else:
        try:
            skill_text = skill_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"cannot read Senior Sol skill: {exc}")
        else:
            metadata = _frontmatter(skill_text)
            if metadata is None:
                errors.append("Senior Sol skill must have opening frontmatter delimiters")
            elif metadata.get("name") != "senior-sol":
                errors.append("Senior Sol skill frontmatter must declare name: senior-sol")

    for path in _tracked_files(root):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("docs/superpowers/"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        except OSError as exc:
            errors.append(f"cannot scan tracked text {relative}: {exc}")
            continue
        without_urls = DOCUMENTATION_URL.sub("", text)
        if LOCAL_ABSOLUTE_PATH.search(without_urls):
            errors.append(f"local absolute path found in {relative}")
        if INCOMPLETE_MARKER.search(text):
            errors.append(f"incomplete marker found in {relative}")
        if _has_nontrivial_credential_assignment(text):
            errors.append(f"credential assignment found in {relative}")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    failures = validate_repository(repository)
    if failures:
        print("\n".join(f"ERROR: {item}" for item in failures))
        raise SystemExit(1)
    print("Repository metadata is valid.")
