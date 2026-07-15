# Senior Sol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish `senior-sol` v0.1.0, a Codex plugin in which a user-selected Sol orchestrates model- and effort-specific Terra/Luna subagents and only implements code after two failed delegations.

**Architecture:** The public repository is a Codex marketplace containing one plugin under `plugins/senior-sol/`. The plugin bundles the orchestration skill, five custom-agent TOML templates, and native PowerShell/POSIX installers that copy those profiles into `$CODEX_HOME/agents`; Python standard-library tests validate metadata, behavioral contracts, and installer behavior without requiring model credentials.

**Tech Stack:** Codex plugin manifest and marketplace JSON, Agent Skills Markdown, Codex custom-agent TOML, Python 3.11 standard library and `unittest`, PowerShell 5.1+, POSIX shell, GitHub Actions.

## Global Constraints

- Release version is exactly `0.1.0`; validate it in `plugin.json` and release/tag metadata because marketplace entries have no version field; Git tag is exactly `v0.1.0`.
- Plugin, package folder, marketplace entry, and skill are named `senior-sol`.
- Authenticated GitHub-owner lookup with `gh api user --jq .login` is a prerequisite and yielded `sergyanin`; therefore the GitHub repository is `sergyanin/senior-sol`.
- The user chooses the main Sol model and reasoning level; the plugin never overrides either.
- Managed subagent profiles are exactly `senior-sol-luna-low`, `senior-sol-luna-medium`, `senior-sol-terra-low`, `senior-sol-terra-medium`, and `senior-sol-terra-high`.
- Terra profiles are read-only; Luna profiles inherit the parent write sandbox and are constrained by the delegation file scope.
- Sol does not edit implementation files before two corrected delegation attempts fail for the same bounded subtask.
- No MCP server, custom scheduler, GUI, telemetry, automated release publication, or non-Sol/Terra/Luna model support in v0.1.0.
- Runtime and test code use only platform tools and the Python standard library.
- Installers never overwrite conflicting agent files unless the user passes `--force` or `-Force`.
- Installers reject an `agents` directory or managed destination that is a directory, symlink, or reparse redirection, including in force mode; recursive test cleanup paths are verified under the system temp directory.
- Uninstallers touch only the five exact managed filenames and never remove the containing `agents` directory.
- Uninstallers apply the same real-directory symlink/reparse guard before deletion, so redirected external managed files remain untouched.
- Sol accepts writer work only after inspecting actual changed paths/content and independently rerunning or directly observing the exact definition-of-done check.
- An unavailable installed model/effort is not a model failure: retry once with the nearest same-role profile (Terra remains read-only), then warn and offer built-in `worker`/`explorer` without incrementing the two-failure counter.
- Repository validation enforces every required marketplace/plugin field and shape, including exact policy/capabilities and plugin version `0.1.0`; marketplace entries have no version field.
- README and public-facing plugin copy are English; the design specification remains Russian.

---

## File Map

- `.agents/plugins/marketplace.json` — public marketplace catalog pointing at `./plugins/senior-sol`.
- `.github/workflows/ci.yml` — Ubuntu and Windows validation matrix.
- `.gitignore` — Python and test artifacts only.
- `plugins/senior-sol/.codex-plugin/plugin.json` — plugin identity, skill path, and UI metadata.
- `plugins/senior-sol/skills/senior-sol/SKILL.md` — complete Sol routing, acceptance, retry, and fallback workflow.
- `plugins/senior-sol/agents/*.toml` — five installable model/effort profiles.
- `plugins/senior-sol/scripts/install-agents.ps1` — safe Windows installation.
- `plugins/senior-sol/scripts/uninstall-agents.ps1` — safe Windows removal.
- `plugins/senior-sol/scripts/install-agents.sh` — safe POSIX installation.
- `plugins/senior-sol/scripts/uninstall-agents.sh` — safe POSIX removal.
- `scripts/validate.py` — cross-platform structural and semantic validator.
- `scripts/validate.ps1` and `scripts/validate.sh` — native validator entry points.
- `tests/test_metadata.py` — manifest and marketplace tests.
- `tests/__init__.py` — makes direct dotted `unittest` targets deterministic.
- `tests/test_agents.py` — TOML profile contract tests.
- `tests/test_installers.py` — isolated installation, idempotence, conflict, force, and uninstall tests.
- `tests/test_skill_contract.py` — static orchestration policy tests.
- `tests/test_docs.py` — public command and release-document consistency tests.
- `docs/examples/delegation-scenarios.md` — seven manual smoke scenarios.
- `docs/release-checklist.md` — authenticated pre-release and marketplace checks.
- `README.md` — installation, activation, behavior, update, and removal guide.
- `LICENSE` — MIT license, copyright `sergyanin`.

---

### Task 1: Marketplace, Plugin Manifest, and Validation Foundation

**Files:**
- Create: `.gitignore`
- Create: `.agents/plugins/marketplace.json`
- Create: `plugins/senior-sol/.codex-plugin/plugin.json`
- Create: `scripts/validate.py`
- Create: `tests/__init__.py`
- Create: `tests/test_metadata.py`

**Interfaces:**
- Consumes: approved design at `docs/superpowers/specs/2026-07-15-senior-sol-design.md`.
- Produces: `scripts.validate.validate_repository(root: Path) -> list[str]`, returning an empty list on success and human-readable errors otherwise.

- [ ] **Step 1: Rename the initial branch and write failing metadata tests**

Run:

```powershell
git branch -m main
```

Create `tests/test_metadata.py` with tests that load both JSON files and assert:

```python
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
```

- [ ] **Step 2: Run the metadata tests and verify failure**

Run:

```powershell
python -m unittest tests.test_metadata -v
```

Expected: both tests error with `FileNotFoundError` because metadata files do not exist.

- [ ] **Step 3: Create the minimal plugin and marketplace metadata**

Create `plugins/senior-sol/.codex-plugin/plugin.json`:

```json
{
  "name": "senior-sol",
  "version": "0.1.0",
  "description": "Tech-lead orchestration for Codex: Sol decides, Terra investigates, and Luna implements.",
  "author": {
    "name": "sergyanin",
    "email": "sergyanin@users.noreply.github.com",
    "url": "https://github.com/sergyanin"
  },
  "license": "MIT",
  "repository": "https://github.com/sergyanin/senior-sol",
  "keywords": ["codex", "orchestration", "subagents", "sol", "terra", "luna"],
  "skills": "./skills/",
  "interface": {
    "displayName": "Senior Sol",
    "shortDescription": "Sol decides; Terra and Luna execute",
    "longDescription": "Keep architecture and acceptance in the Sol thread while routing investigations and implementation to model-specific Codex subagents.",
    "developerName": "sergyanin",
    "category": "Productivity",
    "capabilities": ["Read", "Write"],
    "defaultPrompt": ["Use Senior Sol to orchestrate this multi-step task."]
  }
}
```

Create `.agents/plugins/marketplace.json`:

```json
{
  "name": "senior-sol",
  "interface": {"displayName": "Senior Sol"},
  "plugins": [
    {
      "name": "senior-sol",
      "source": {"source": "local", "path": "./plugins/senior-sol"},
      "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
      "category": "Productivity"
    }
  ]
}
```

Create `.gitignore`:

```gitignore
__pycache__/
*.py[cod]
.coverage
.pytest_cache/
```

Create an empty `tests/__init__.py` so both dotted test targets and discovery work consistently.

- [ ] **Step 4: Add the repository validator and its direct entry point**

Create `scripts/validate.py` with:

```python
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

    if manifest.get("name") != plugin.name:
        errors.append("plugin folder and manifest name must both be senior-sol")
    if manifest.get("version") != "0.1.0":
        errors.append("plugin version must be 0.1.0")
    if manifest.get("interface", {}).get("capabilities") != ["Read", "Write"]:
        errors.append("plugin capabilities must be exactly Read and Write")
    entries = marketplace.get("plugins", [])
    if len(entries) != 1 or entries[0].get("name") != manifest.get("name"):
        errors.append("marketplace must contain exactly the senior-sol plugin")
    if entries and entries[0].get("source", {}).get("path") != "./plugins/senior-sol":
        errors.append("marketplace source path must be ./plugins/senior-sol")
    return errors


if __name__ == "__main__":
    repository = Path(__file__).resolve().parents[1]
    failures = validate_repository(repository)
    if failures:
        print("\n".join(f"ERROR: {item}" for item in failures))
        raise SystemExit(1)
    print("Repository metadata is valid.")
```

- [ ] **Step 5: Run tests and validator**

Run:

```powershell
python -m unittest tests.test_metadata -v
python scripts/validate.py
git diff --check
```

Expected: 2 tests pass; validator prints `Repository metadata is valid.`; `git diff --check` prints nothing.

- [ ] **Step 6: Commit the metadata foundation**

```powershell
git add .gitignore .agents/plugins/marketplace.json plugins/senior-sol/.codex-plugin/plugin.json scripts/validate.py tests/__init__.py tests/test_metadata.py
git commit -m "feat: scaffold senior-sol marketplace plugin"
```

---

### Task 2: Model- and Effort-Specific Agent Profiles

**Files:**
- Create: `plugins/senior-sol/agents/senior-sol-luna-low.toml`
- Create: `plugins/senior-sol/agents/senior-sol-luna-medium.toml`
- Create: `plugins/senior-sol/agents/senior-sol-terra-low.toml`
- Create: `plugins/senior-sol/agents/senior-sol-terra-medium.toml`
- Create: `plugins/senior-sol/agents/senior-sol-terra-high.toml`
- Create: `tests/test_agents.py`
- Modify: `scripts/validate.py`

**Interfaces:**
- Consumes: `validate_repository(root)` from Task 1.
- Produces: five standalone Codex custom-agent files discoverable after copying to `$CODEX_HOME/agents/`; `MANAGED_PROFILES: dict[str, tuple[str, str, bool]]` in `scripts/validate.py`.

- [ ] **Step 1: Write failing profile-contract tests**

Create `tests/test_agents.py`:

```python
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate import MANAGED_PROFILES, validate_repository


class AgentProfileTests(unittest.TestCase):
    def test_exact_profile_set_and_settings(self):
        agent_dir = ROOT / "plugins" / "senior-sol" / "agents"
        self.assertEqual({p.stem for p in agent_dir.glob("*.toml")}, set(MANAGED_PROFILES))
        for name, (model, effort, read_only) in MANAGED_PROFILES.items():
            data = tomllib.loads((agent_dir / f"{name}.toml").read_text(encoding="utf-8"))
            self.assertEqual(data["name"], name)
            self.assertEqual(data["model"], model)
            self.assertEqual(data["model_reasoning_effort"], effort)
            self.assertTrue(data["description"])
            self.assertTrue(data["developer_instructions"])
            self.assertEqual(data.get("sandbox_mode") == "read-only", read_only)

    def test_repository_validator_accepts_profiles(self):
        self.assertEqual(validate_repository(ROOT), [])
```

- [ ] **Step 2: Run the profile tests and verify failure**

Run `python -m unittest tests.test_agents -v`.

Expected: import fails because `MANAGED_PROFILES` is not defined.

- [ ] **Step 3: Define the exact profile matrix in the validator**

Add near the top of `scripts/validate.py`:

```python
MANAGED_PROFILES = {
    "senior-sol-luna-low": ("gpt-5.6-luna", "low", False),
    "senior-sol-luna-medium": ("gpt-5.6-luna", "medium", False),
    "senior-sol-terra-low": ("gpt-5.6-terra", "low", True),
    "senior-sol-terra-medium": ("gpt-5.6-terra", "medium", True),
    "senior-sol-terra-high": ("gpt-5.6-terra", "high", True),
}
```

Extend `validate_repository` to parse every expected file with `tomllib`, reject missing or extra TOMLs, verify name/model/effort, require non-empty instructions, and require `sandbox_mode = "read-only"` only for Terra. Convert parse errors into returned validation errors instead of exceptions.

- [ ] **Step 4: Create the two Luna executor profiles**

Each Luna TOML uses the matching name/effort and this complete instruction contract:

```toml
name = "senior-sol-luna-low"
description = "Mechanical implementation from a complete Senior Sol specification."
model = "gpt-5.6-luna"
model_reasoning_effort = "low"
developer_instructions = """
Execute the supplied specification literally. Work only in the listed file scope.
Do not introduce architecture, adjacent refactors, or optional features.
Stop and return a question when a design decision is missing.
Verify the result with the exact definition-of-done command.
Report only these sections: Done, Verified, Not done / questions.
"""
```

Create `senior-sol-luna-medium.toml` with the same instructions, `name = "senior-sol-luna-medium"`, description `Multi-step implementation from a complete Senior Sol specification.`, and `model_reasoning_effort = "medium"`.

- [ ] **Step 5: Create the three read-only Terra profiles**

Each Terra file uses its matching effort and:

```toml
name = "senior-sol-terra-medium"
description = "Read-only codebase investigation, diagnosis, and review for Senior Sol."
model = "gpt-5.6-terra"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"
developer_instructions = """
Investigate exhaustively inside the supplied scope without modifying files.
Return distilled conclusions instead of raw exploration output.
Separate verified evidence from inference and cite file paths and line numbers.
Report only these sections: Answer, Evidence, Ruled out, Open questions.
"""
```

Create the low file with name `senior-sol-terra-low`, effort `low`, and description `Fast read-only search and evidence collection for Senior Sol.` Create the high file with name `senior-sol-terra-high`, effort `high`, and description `Deep read-only analysis for security, migrations, and contested results.`

- [ ] **Step 6: Run profile and repository tests**

Run:

```powershell
python -m unittest tests.test_agents tests.test_metadata -v
python scripts/validate.py
```

Expected: all tests pass and validator prints `Repository metadata is valid.`

- [ ] **Step 7: Commit the profiles**

```powershell
git add plugins/senior-sol/agents scripts/validate.py tests/test_agents.py
git commit -m "feat: add managed Terra and Luna profiles"
```

---

### Task 3: Safe PowerShell Agent Installation

**Files:**
- Create: `plugins/senior-sol/scripts/install-agents.ps1`
- Create: `plugins/senior-sol/scripts/uninstall-agents.ps1`
- Create: `tests/test_installers.py`

**Interfaces:**
- Consumes: the five TOMLs from Task 2 and environment variable `CODEX_HOME`.
- Produces: `install-agents.ps1 [-Force]` and `uninstall-agents.ps1`, with exit code 0 on complete success and 1 on any conflict/error.

- [ ] **Step 1: Write failing PowerShell installer tests**

Create `tests/test_installers.py` using `unittest`, `tempfile.TemporaryDirectory`, and `subprocess.run`. Add helper `powershell_executable()` that returns `pwsh` when available, otherwise `powershell`, otherwise skips the PowerShell class. Tests must:

```python
def run_script(executable, script, codex_home, *args):
    env = os.environ.copy()
    env["CODEX_HOME"] = str(codex_home)
    return subprocess.run(
        [executable, "-NoProfile", "-File", str(script), *args],
        text=True, capture_output=True, env=env, check=False,
    )
```

Assert clean install creates exactly the five managed files, second install returns 0 and reports `unchanged`, a modified destination returns 1 and reports `conflict`, `-Force` restores the template, and uninstall removes managed files while preserving `agents/unrelated.toml` and the `agents` directory.

- [ ] **Step 2: Run the PowerShell tests and verify failure**

Run:

```powershell
python -m unittest tests.test_installers.PowerShellInstallerTests -v
```

Expected: tests fail because `install-agents.ps1` and `uninstall-agents.ps1` do not exist.

- [ ] **Step 3: Implement the PowerShell installer**

Implement `install-agents.ps1` with `[CmdletBinding()] param([switch]$Force)`, `$ErrorActionPreference = 'Stop'`, a literal array of the five filenames, and these state transitions:

```powershell
$codexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }
$source = Join-Path (Split-Path -Parent $PSScriptRoot) 'agents'
$target = Join-Path $codexHome 'agents'
New-Item -ItemType Directory -Path $target -Force | Out-Null

if (-not (Test-Path -LiteralPath $destination)) {
    Copy-Item -LiteralPath $origin -Destination $destination
    Write-Output "created: $name"
} elseif ((Get-FileHash -LiteralPath $origin).Hash -eq (Get-FileHash -LiteralPath $destination).Hash) {
    Write-Output "unchanged: $name"
} elseif ($Force) {
    Copy-Item -LiteralPath $origin -Destination $destination -Force
    Write-Output "replaced: $name"
} else {
    Write-Output "conflict: $name"
    $hadConflict = $true
}
```

Process every known file so the summary is complete, then `exit 1` when `$hadConflict` is true and `exit 0` otherwise. Do not enumerate or modify unrelated destination files.

- [ ] **Step 4: Implement the PowerShell uninstaller**

Use the same literal filename array. Resolve `$target` from `CODEX_HOME`; for each exact name, call `Remove-Item -LiteralPath $path` when present and print `removed: name`, otherwise print `missing: name`. Never use recurse, wildcards, or remove the directory.

- [ ] **Step 5: Run PowerShell installer tests**

Run:

```powershell
python -m unittest tests.test_installers.PowerShellInstallerTests -v
```

Expected: clean, idempotence, conflict/force, and uninstall tests all pass.

- [ ] **Step 6: Commit the PowerShell installers**

```powershell
git add plugins/senior-sol/scripts/install-agents.ps1 plugins/senior-sol/scripts/uninstall-agents.ps1 tests/test_installers.py
git commit -m "feat: add safe PowerShell agent installer"
```

---

### Task 4: Safe POSIX Agent Installation

**Files:**
- Create: `plugins/senior-sol/scripts/install-agents.sh`
- Create: `plugins/senior-sol/scripts/uninstall-agents.sh`
- Modify: `tests/test_installers.py`

**Interfaces:**
- Consumes: the same five TOMLs and `CODEX_HOME` contract as Task 3.
- Produces: `install-agents.sh [--force]` and `uninstall-agents.sh` with output vocabulary identical to PowerShell.

- [ ] **Step 1: Add failing POSIX tests**

Add `PosixInstallerTests` to `tests/test_installers.py`, skipped when `bash` is unavailable. Reuse the same assertion helper and scenarios, invoking scripts as `[bash, script, *args]`; pass `--force` in the replacement test.

- [ ] **Step 2: Run POSIX tests and verify failure**

Run `python -m unittest tests.test_installers.PosixInstallerTests -v`.

Expected: tests fail because both `.sh` scripts are missing.

- [ ] **Step 3: Implement the POSIX installer**

Create `install-agents.sh` with `set -u`, an explicit `case` accepting only no argument or `--force`, and:

```sh
codex_home="${CODEX_HOME:-${HOME}/.codex}"
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=$(CDPATH= cd -- "$script_dir/../agents" && pwd)
target_dir="$codex_home/agents"
mkdir -p -- "$target_dir" || exit 1
```

Loop over the same five literal filenames. Use `cmp -s` for equality, `cp "$origin" "$destination"` for create/replace, the exact output verbs `created`, `unchanged`, `replaced`, and `conflict`, and an integer `had_conflict` checked after the loop. Quote every path. The filenames are fixed and never begin with `-`, so this remains portable to macOS/BSD utilities without GNU-only flags.

- [ ] **Step 4: Implement the POSIX uninstaller**

Resolve the same target directory, loop over only the five literal names, call `rm "$path"` for existing regular files, and print `removed`/`missing`. Never call recursive removal or remove the target directory.

- [ ] **Step 5: Run all installer tests**

Run:

```powershell
python -m unittest tests.test_installers -v
```

Expected: both native suites pass where their shell is present; no test changes files outside its temporary `CODEX_HOME`.

- [ ] **Step 6: Commit the POSIX installers**

```powershell
git add plugins/senior-sol/scripts/install-agents.sh plugins/senior-sol/scripts/uninstall-agents.sh tests/test_installers.py
git commit -m "feat: add safe POSIX agent installer"
```

---

### Task 5: Senior Sol Orchestration Skill

**Files:**
- Create: `plugins/senior-sol/skills/senior-sol/SKILL.md`
- Create: `tests/test_skill_contract.py`
- Modify: `scripts/validate.py`

**Interfaces:**
- Consumes: managed agent names and install scripts from Tasks 2–4.
- Produces: user-invoked `$senior-sol` workflow and an exact delegation/report protocol.

- [ ] **Step 1: Write failing skill-contract tests**

Create `tests/test_skill_contract.py` that reads the skill and asserts:

```python
REQUIRED_HEADINGS = {
    "## Startup gate", "## Delegation matrix", "## Delegation contract",
    "## Acceptance gate", "## Failure and fallback policy", "## Final synthesis",
}
REQUIRED_PROFILES = {
    "senior-sol-luna-low", "senior-sol-luna-medium", "senior-sol-terra-low",
    "senior-sol-terra-medium", "senior-sol-terra-high",
}
```

Also assert that the frontmatter name is `senior-sol`; all five names occur; `Goal:`, `Files:`, `Constraints:`, `Definition of done:`, and `Report format:` occur; both report schemas occur; the text explicitly says not to retry an unchanged spec; fallback requires two failed delegations, user notification, bounded scope, verification, and final disclosure; main-model or reasoning-setting mutation commands do not occur.

- [ ] **Step 2: Run the contract tests and verify failure**

Run `python -m unittest tests.test_skill_contract -v`.

Expected: test setup errors because `SKILL.md` is missing.

- [ ] **Step 3: Write the complete skill workflow**

Create `SKILL.md` with frontmatter description that triggers only when the user explicitly invokes Senior Sol or asks for this orchestration on substantial multi-step work. The body must implement these exact sections and rules:

```markdown
## Startup gate

Do not change the main thread's model or reasoning effort. The user selects Sol and its effort. If the visible runtime context indicates that the main model is not Sol, stop and ask the user to select Sol before activation.
Resolve CODEX_HOME, then check for all five managed profiles. If any are missing, explain the reduced guarantees and ask before running the OS-appropriate installer located under this plugin's scripts directory. After installation, stop and ask the user to open a new Codex thread so custom agents are discovered. If installation is declined or unavailable, use built-in worker/explorer agents and explicitly warn that model and effort are not pinned.

## Delegation matrix

Use Luna low for one-step mechanical edits, Luna medium for explicit multi-step implementation, Terra low for fast evidence collection, Terra medium for investigation/diagnosis/review, and Terra high for security, migrations, or contested conclusions. Terra is read-only. Keep ambiguous decisions in the Sol thread.

## Delegation contract

Goal: Add one verified capability or return one evidence-backed conclusion.
Files: in scope: the exact listed paths / out of scope: every other path.
Constraints: preserve the decisions, compatibility limits, and prohibitions supplied by Sol.
Definition of done: run the exact command or perform the exact check supplied by Sol.
Report format: use the writer or researcher schema selected by Sol.

Run independent work in parallel only when write scopes are disjoint. One writer per file set.

## Acceptance gate

Writer reports require Done, Verified, and Not done / questions. Research reports require Answer, Evidence, Ruled out, and Open questions. Reject missing sections, unverified success, or out-of-scope edits.

## Failure and fallback policy

After failure one, diagnose the cause and produce a materially corrected specification; never retry an unchanged specification. The second attempt may use the nearest stronger suitable profile. After two failed delegations for the same bounded subtask, notify the user that Sol is entering fallback, implement only that subtask, verify it, and disclose the main-agent implementation in the final report. Environment or permission failures do not count as model failures.

## Final synthesis

Sol owns decisions, acceptance, and the final response. Summarize accepted delegated work, verification evidence, unresolved risks, and every use of fallback.
```

Use the concrete contract text above in the actual skill and add one fully specified writer example plus one fully specified researcher example.

- [ ] **Step 4: Extend repository validation for skill integrity**

Update `validate_repository` to require the skill path from `manifest["skills"]`, parse the opening YAML-like frontmatter delimiters, require `name: senior-sol`, and use `git ls-files` (with an explicit complete fallback for isolated tests) to scan every public tracked text file, including `.github/` and tests. Exclude only design/plan artifacts under `docs/superpowers/`; parse complete assignment identifiers and reject nontrivial values for common credential suffixes (including prefixed API keys, tokens, and secret access keys), broad Windows/Unix machine-local absolute paths, and incomplete markers without treating dynamic environment lookups, documentation URLs, or the detector's own source as findings. Return errors instead of exiting early.

- [ ] **Step 5: Run skill, metadata, and profile tests**

Run:

```powershell
python -m unittest tests.test_skill_contract tests.test_agents tests.test_metadata -v
python scripts/validate.py
```

Expected: all tests pass; validator reports success.

- [ ] **Step 6: Commit the orchestration skill**

```powershell
git add plugins/senior-sol/skills scripts/validate.py tests/test_skill_contract.py
git commit -m "feat: add Senior Sol orchestration workflow"
```

---

### Task 6: Public Documentation and Release Evidence

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `docs/examples/delegation-scenarios.md`
- Create: `docs/release-checklist.md`
- Create: `tests/test_docs.py`

**Interfaces:**
- Consumes: real GitHub owner `sergyanin`, exact script names, profiles, and behavior from Tasks 2–5.
- Produces: install/update/remove instructions and seven reviewable manual smoke scenarios.

- [ ] **Step 1: Write failing documentation consistency tests**

Create `tests/test_docs.py` that asserts README contains:

```python
REQUIRED_README_TEXT = [
    "codex plugin marketplace add sergyanin/senior-sol",
    "$senior-sol",
    "install-agents.ps1", "install-agents.sh",
    "uninstall-agents.ps1", "uninstall-agents.sh",
    "AndyShaman/senior-fable", "MIT",
]
```

Assert `docs/examples/delegation-scenarios.md` has exactly seven `## Scenario` headings and the release checklist mentions `python -m unittest discover -s tests -v`, `python scripts/validate.py`, official plugin validation, marketplace installation, a new Codex thread, and tag `v0.1.0`.

- [ ] **Step 2: Run documentation tests and verify failure**

Run `python -m unittest tests.test_docs -v`.

Expected: errors because all four public documents are absent.

- [ ] **Step 3: Write README and MIT license**

README sections are: value proposition; routing table; safety guarantees; requirements; marketplace install; profile install on Windows and POSIX; activation with `$senior-sol`; fallback behavior; update; uninstall; development validation; inspiration; license. Use concrete repository command `codex plugin marketplace add sergyanin/senior-sol`, explain that users select Sol and its reasoning level before activation, and require a new Codex thread after profile installation so the custom agents are discovered.

Write the standard MIT license with `Copyright (c) 2026 sergyanin`.

- [ ] **Step 4: Write the seven manual smoke scenarios**

For each scenario, include Setup, Prompt, Expected routing, Expected evidence, and Failure signal. The seven cases are: Luna mechanical edit; Terra read-only investigation; missing verification rejection with independent diff/check requirements; overlapping writer serialization; corrected specification after first failure; announced bounded Sol fallback after second failure; installed-profile availability routing plus built-in fallback warning (also covering missing profiles).

- [ ] **Step 5: Write the release checklist**

Include unchecked items for clean tests on both OSes, repository validation, official plugin validation, `gh auth status`, creating `sergyanin/senior-sol`, pushing `main`, adding the marketplace from GitHub, installing the plugin, opening a new Codex thread, executing all seven scenarios, checking for secrets/local paths, tagging `v0.1.0`, and creating the GitHub Release. Publication stays manual.

- [ ] **Step 6: Run documentation tests**

Run:

```powershell
python -m unittest tests.test_docs -v
python scripts/validate.py
```

Expected: documentation tests and validator pass.

- [ ] **Step 7: Commit public documentation**

```powershell
git add README.md LICENSE docs/examples docs/release-checklist.md tests/test_docs.py
git commit -m "docs: add public usage and release guidance"
```

---

### Task 7: Native Validation Wrappers and Cross-Platform CI

**Files:**
- Create: `scripts/validate.ps1`
- Create: `scripts/validate.sh`
- Create: `.github/workflows/ci.yml`
- Modify: `scripts/validate.py`
- Modify: `tests/test_metadata.py`

**Interfaces:**
- Consumes: all repository artifacts and tests from Tasks 1–6.
- Produces: one-command local validation and required Windows/Ubuntu GitHub checks.

- [ ] **Step 1: Add failing wrapper-presence and workflow tests**

Extend `tests/test_metadata.py` to assert both wrappers and `.github/workflows/ci.yml` exist. Assert the workflow text contains `ubuntu-latest`, `windows-latest`, `python -m unittest discover -s tests -v`, and `python scripts/validate.py`.

- [ ] **Step 2: Run the extended metadata tests and verify failure**

Run `python -m unittest tests.test_metadata -v`.

Expected: wrapper/workflow test fails because the files do not exist.

- [ ] **Step 3: Add native validation wrappers**

Create `scripts/validate.ps1`:

```powershell
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    python scripts/validate.py
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
```

Create `scripts/validate.sh`:

```sh
#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
python -m unittest discover -s tests -v
python scripts/validate.py
```

- [ ] **Step 4: Add GitHub Actions matrix**

Create `.github/workflows/ci.yml` triggered on pushes and pull requests. Use matrix OS values `[ubuntu-latest, windows-latest]`, `actions/checkout@v4`, `actions/setup-python@v5` with Python `3.11`, then run:

```yaml
- name: Run tests
  run: python -m unittest discover -s tests -v
- name: Validate repository
  run: python scripts/validate.py
```

Do not add publishing credentials or release automation.

- [ ] **Step 5: Run all local tests through the native wrapper**

Run:

```powershell
powershell -NoProfile -File scripts/validate.ps1
git diff --check
```

Expected: all tests pass, repository validator reports success, and diff check is silent. If `bash` is available, also run `bash scripts/validate.sh` with the same expected result.

- [ ] **Step 6: Run the official plugin validator**

Run from `D:\Code_dev\senior-sol`:

```powershell
python C:\Users\yanin\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py plugins\senior-sol
```

Expected: validator exits 0 and reports the `senior-sol` plugin valid. If it rejects an optional manifest field, remove only that unsupported optional field, add a regression assertion for the accepted manifest shape, and rerun all validation.

- [ ] **Step 7: Commit CI and validation wrappers**

```powershell
git add .github/workflows/ci.yml scripts/validate.ps1 scripts/validate.sh scripts/validate.py tests/test_metadata.py
git commit -m "ci: validate senior-sol on Windows and Ubuntu"
```

---

### Task 8: Pre-Publication Integration Verification

**Files:**
- Modify only when verification exposes a defect: files owned by Tasks 1–7.
- Update: `docs/release-checklist.md` with local verification results; leave remote-publication items unchecked until they occur.

**Interfaces:**
- Consumes: complete local v0.1.0 repository.
- Produces: clean local release candidate ready for GitHub publication.

- [ ] **Step 1: Verify the complete suite from a clean process**

Run:

```powershell
git status --short
powershell -NoProfile -File scripts/validate.ps1
python C:\Users\yanin\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py plugins\senior-sol
git diff --check
```

Expected: clean status before checklist edits, all tests pass, official validator exits 0, and diff check is silent.

- [ ] **Step 2: Verify installation against an isolated Codex home**

Run:

```powershell
$tempRoot = [System.IO.Path]::GetFullPath($env:TEMP).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
$tempHome = [System.IO.Path]::GetFullPath((Join-Path $tempRoot 'senior-sol-release-check'))
if (-not $tempHome.StartsWith($tempRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "Refusing recursive cleanup outside system temp"
}
Remove-Item -LiteralPath $tempHome -Recurse -Force -ErrorAction SilentlyContinue
$env:CODEX_HOME = $tempHome
powershell -NoProfile -File plugins/senior-sol/scripts/install-agents.ps1
Get-ChildItem -LiteralPath (Join-Path $tempHome 'agents') | Select-Object -ExpandProperty Name
powershell -NoProfile -File plugins/senior-sol/scripts/uninstall-agents.ps1
Remove-Item Env:CODEX_HOME
```

Expected: exactly five managed names are listed; uninstall removes those files and keeps the `agents` directory.

- [ ] **Step 3: Audit tracked files for secrets and machine-local paths**

Run the enforced `python scripts/validate.py` tracked-file scan, which uses `git ls-files` and covers `.github/`, tests, and every other public tracked text file while excluding only `docs/superpowers/` design/plan artifacts. It rejects nontrivial credential assignments and broad Windows/Unix machine-local absolute paths while ignoring documentation URLs and detector-source literals. For an independent manual cross-check, run:

```powershell
git grep -n -I -E 'BEGIN (RSA|OPENSSH|EC) PRIVATE KEY|api[_-]?key|secret|token' -- . ':!docs/superpowers/plans/*'
git grep -n -I -F 'D:\Code_dev' -- . ':!docs/superpowers/*'
```

Expected: no secret-like values and no runtime/documentation dependency on the development machine. Descriptive words such as `token` in design documents are reviewed manually and are not credentials.

- [ ] **Step 4: Mark only completed local checklist items and commit**

Update `docs/release-checklist.md` with the date `2026-07-15` and check the completed local validation, installer, and secret-scan items. Do not check GitHub repository creation, push, marketplace installation, manual model scenarios, tag, or release until each actually occurs.

```powershell
git add docs/release-checklist.md
git commit -m "docs: record local v0.1.0 verification"
git status --short
git log --oneline --decorate -10
```

Expected: clean working tree and a linear series of focused commits ending in local release verification.

---

## Publication Follow-Up

Remote publication is an external-state action and begins only after explicit confirmation at execution time. The exact commands are:

```powershell
gh repo create sergyanin/senior-sol --public --source . --remote origin --push
git tag -a v0.1.0 -m 'Senior Sol v0.1.0'
git push origin v0.1.0
gh release create v0.1.0 --title 'Senior Sol v0.1.0' --notes-file docs/release-checklist.md
```

Before tagging, install the GitHub marketplace with `codex plugin marketplace add sergyanin/senior-sol`, install `senior-sol` in the Codex app, open a new thread, run all seven manual scenarios, and record the results in `docs/release-checklist.md`.
