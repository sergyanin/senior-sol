# Startup Gate Model Detection Design

## Problem

Senior Sol was invoked through `codex exec -m gpt-5.6-sol`, but the startup gate interpreted generic runtime wording such as `Codex/GPT-5` as proof that the main model was not Sol. Four of seven release-smoke scenarios stopped before their intended routing behavior could run.

## Decision

Model selection remains an external prerequisite owned by the user or invoking CLI. Senior Sol must not infer the configured model from generic system identity text, model self-identification, or the absence of exact model metadata.

The skill may stop only when authoritative runtime metadata explicitly identifies the configured main model and that exact value is not a Sol model. When authoritative metadata is unavailable, explicit `$senior-sol` invocation is sufficient to continue, while the skill continues to leave the main model and reasoning effort unchanged.

## Scope

- Update the startup-gate wording in `plugins/senior-sol/skills/senior-sol/SKILL.md`.
- Add a contract regression test in `tests/test_skill_contract.py`.
- Preserve profile discovery, delegation, acceptance, retry, and fallback behavior.
- Reinstall the updated plugin through the supported cachebuster flow.
- Repeat all seven documented release-smoke scenarios.

## Acceptance

- The contract explicitly rejects generic identity text and self-identification as model evidence.
- The contract still stops for authoritative metadata that explicitly names a non-Sol main model.
- The skill never changes the main model or reasoning effort.
- Repository, plugin, and unit validation pass.
- All seven release-smoke scenarios pass before release publication proceeds.
