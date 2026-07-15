from __future__ import annotations

import json
import sys
from pathlib import Path


def validate_repository(root: Path) -> list[str]:
    errors: list[str] = []
    plugin = root / "plugins" / "senior-sol"
    manifest_path = plugin / ".codex-plugin" / "plugin.json"
    marketplace_path = root / ".agents" / "plugins" / "marketplace.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [str(exc)]

    if not isinstance(manifest, dict):
        errors.append("plugin manifest must be a JSON object")
    if not isinstance(marketplace, dict):
        errors.append("marketplace must be a JSON object")
    if errors:
        return errors

    if manifest.get("name") != plugin.name:
        errors.append("plugin folder and manifest name must both be senior-sol")
    if manifest.get("version") != "0.1.0":
        errors.append("plugin version must be 0.1.0")
    interface = manifest.get("interface", {})
    if not isinstance(interface, dict):
        errors.append("plugin interface must be a JSON object")
    elif interface.get("capabilities") != ["Read", "Write"]:
        errors.append("plugin capabilities must be exactly Read and Write")
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        errors.append("marketplace plugins must be a JSON array")
        return errors
    if len(entries) != 1:
        errors.append("marketplace must contain exactly the senior-sol plugin")
    elif not isinstance(entries[0], dict):
        errors.append("marketplace plugin entry must be a JSON object")
    else:
        entry = entries[0]
        if entry.get("name") != manifest.get("name"):
            errors.append("marketplace must contain exactly the senior-sol plugin")
        source = entry.get("source", {})
        if not isinstance(source, dict):
            errors.append("marketplace plugin source must be a JSON object")
        elif source.get("path") != "./plugins/senior-sol":
            errors.append("marketplace source path must be ./plugins/senior-sol")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    failures = validate_repository(repository)
    if failures:
        print("\n".join(f"ERROR: {item}" for item in failures))
        raise SystemExit(1)
    print("Repository metadata is valid.")
