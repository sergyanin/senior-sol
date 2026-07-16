# Startup Gate Model Detection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent false non-Sol startup refusals while retaining an explicit authoritative non-Sol guard.

**Architecture:** Keep model selection outside the plugin and encode only the observable decision boundary in the skill contract. Protect the wording with a focused unit test, then validate behavior through the existing seven manual smoke scenarios.

**Tech Stack:** Markdown skill contract, Python `unittest`, Codex CLI plugin tooling, PowerShell smoke harness.

## Global Constraints

- Do not mutate the main model or reasoning effort.
- Do not weaken managed-profile checks or delegation acceptance gates.
- Do not publish `v0.1.0` unless all seven smoke scenarios pass.

---

### Task 1: Startup-gate contract

**Files:**
- Modify: `tests/test_skill_contract.py`
- Modify: `plugins/senior-sol/skills/senior-sol/SKILL.md`

**Interfaces:**
- Consumes: explicit `$senior-sol` invocation and any authoritative exact runtime model metadata.
- Produces: a deterministic proceed/stop rule that never relies on generic identity text or self-identification.

- [ ] **Step 1: Write the failing test**

Add a test requiring the startup gate to state that generic runtime identity and model self-identification are not authoritative, that missing authoritative metadata permits continuation after explicit invocation, and that exact authoritative non-Sol metadata still causes a stop.

- [ ] **Step 2: Run the focused test to verify RED**

Run: `python -m unittest tests.test_skill_contract.SkillContractTests.test_startup_gate_uses_only_authoritative_exact_model_metadata -v`

Expected: FAIL because the current skill relies on visible runtime context and lacks the required deterministic boundary.

- [ ] **Step 3: Write the minimal skill change**

Replace only the startup-gate model-detection paragraph with the approved external-selection and authoritative-metadata contract.

- [ ] **Step 4: Run focused and full verification**

Run the focused test, `python -m unittest discover -s tests -v`, `python scripts/validate.py`, and the official plugin validator. Expected: all exit 0.

### Task 2: Installed plugin and release smoke

**Files:**
- Modify through supported tooling: plugin manifest cachebuster only if required by the installer workflow.
- Record evidence under a new disposable release-smoke evidence directory.

**Interfaces:**
- Consumes: locally validated plugin source and five managed agent profiles.
- Produces: a newly installed plugin cache entry and a seven-scenario evidence summary.

- [ ] **Step 1: Update cachebuster and reinstall**

Use the plugin-creator cachebuster helper, confirm the configured marketplace source, and reinstall `senior-sol` without hand-editing marketplace configuration.

- [ ] **Step 2: Execute all seven scenarios**

Use `gpt-5.6-sol` with reasoning effort `medium`, preserve each JSONL transcript and final message, and keep fixture repositories isolated.

- [ ] **Step 3: Verify release gate**

Require 7 PASS / 0 FAIL, clean fixture scopes, restored managed profiles, passing unit tests, and passing repository validation. If any scenario fails, keep the release gate closed and diagnose before publication.

- [ ] **Step 4: Publish the fix only after verification**

Commit the tested changes, push `main`, confirm CI, then proceed with the existing annotated-tag and GitHub Release checklist.
