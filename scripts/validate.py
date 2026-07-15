from __future__ import annotations

import json
import re
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

TEXT_SUFFIXES = {
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
INCOMPLETE_MARKER = re.compile(
    r"\b(?:"
    + "|".join(
        ("TO" + "DO", "T" + "BD", "FIX" + "ME", "X" * 3, "PLACE" + "HOLDER")
    )
    + r")\b",
    re.IGNORECASE,
)
LOCAL_ABSOLUTE_PATH = re.compile(
    r"(?:[A-Za-z]:(?:\\\\|[\\/](?![\\/]))|(?<![A-Za-z0-9@])/(?:Users|home)/)[^\s`\"']+"
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


def _public_runtime_text_files(root: Path) -> list[Path]:
    files: set[Path] = set()
    for directory in (root / ".agents", root / "docs", root / "plugins", root / "scripts"):
        if directory.exists():
            files.update(path for path in directory.rglob("*") if path.is_file())
    files.update(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES
    )
    return sorted(path for path in files if path.suffix.lower() in TEXT_SUFFIXES)


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
        errors.append("plugin folder and manifest name must both be senior-sol")
    if manifest.get("version") != "0.1.0":
        errors.append("plugin version must be 0.1.0")
    skills_path = manifest.get("skills")
    if skills_path != "./skills/":
        errors.append("plugin skills path must be ./skills/")
    interface = manifest.get("interface", {})
    if not isinstance(interface, dict):
        errors.append("plugin interface must be a JSON object")
    elif interface.get("capabilities") != ["Read", "Write"]:
        errors.append("plugin capabilities must be exactly Read and Write")
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        errors.append("marketplace plugins must be a JSON array")
        entries = []
    if marketplace_is_object and len(entries) != 1:
        errors.append("marketplace must contain exactly the senior-sol plugin")
    if len(entries) == 1 and not isinstance(entries[0], dict):
        errors.append("marketplace plugin entry must be a JSON object")
    elif len(entries) == 1:
        entry = entries[0]
        if entry.get("name") != manifest.get("name"):
            errors.append("marketplace must contain exactly the senior-sol plugin")
        source = entry.get("source", {})
        if not isinstance(source, dict):
            errors.append("marketplace plugin source must be a JSON object")
        elif source.get("path") != "./plugins/senior-sol":
            errors.append("marketplace source path must be ./plugins/senior-sol")

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

    for path in _public_runtime_text_files(root):
        relative = path.relative_to(root).as_posix()
        if relative.startswith("docs/superpowers/"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"cannot scan tracked text {relative}: {exc}")
            continue
        if LOCAL_ABSOLUTE_PATH.search(text):
            errors.append(f"local absolute path found in {relative}")
        if INCOMPLETE_MARKER.search(text):
            errors.append(f"incomplete marker found in {relative}")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    failures = validate_repository(repository)
    if failures:
        print("\n".join(f"ERROR: {item}" for item in failures))
        raise SystemExit(1)
    print("Repository metadata is valid.")
