---
name: senior-sol
description: Use only when the user explicitly invokes Senior Sol or asks for Senior Sol orchestration on substantial multi-step work.
---

# Senior Sol

## Startup gate

Do not change the main thread's model or reasoning effort. The user selects Sol and its effort. If the visible runtime context indicates that the main model is not Sol, stop and ask the user to select Sol before activation.

Resolve `CODEX_HOME`, then check for all five managed profiles: `senior-sol-luna-low`, `senior-sol-luna-medium`, `senior-sol-terra-low`, `senior-sol-terra-medium`, and `senior-sol-terra-high`. If any are missing, explain the reduced guarantees and ask before running the OS-appropriate installer located under this plugin's scripts directory. After installation, stop and ask the user to open a new Codex thread so custom agents are discovered. If installation is declined or unavailable, use built-in worker/explorer agents and explicitly warn that model and effort are not pinned.

## Delegation matrix

Use `senior-sol-luna-low` for one-step mechanical edits, `senior-sol-luna-medium` for explicit multi-step implementation, `senior-sol-terra-low` for fast evidence collection, `senior-sol-terra-medium` for investigation, diagnosis, or review, and `senior-sol-terra-high` for security, migrations, or contested conclusions. Terra is read-only. Keep ambiguous decisions in the Sol thread.

## Delegation contract

Every delegation must contain this concrete contract:

Goal: Add one verified capability or return one evidence-backed conclusion.

Files: in scope: the exact listed paths / out of scope: every other path.

Constraints: preserve the decisions, compatibility limits, and prohibitions supplied by Sol.

Definition of done: run the exact command or perform the exact check supplied by Sol.

Report format: use the writer or researcher schema selected by Sol.

Run independent work in parallel only when write scopes are disjoint. One writer per file set.

### Fully specified writer example

Delegate to `senior-sol-luna-medium`:

Goal: Add validation that rejects an empty project name.

Files: in scope: `src/project.py`, `tests/test_project.py` / out of scope: every other path.

Constraints: preserve the public function signature and current exception types; do not edit configuration or documentation; use test-driven development.

Definition of done: run `python -m unittest tests.test_project -v` and report its actual result.

Report format: writer schema.

The writer report must use:

- Done: exact edits made.
- Verified: commands run and their observed results.
- Not done / questions: remaining work, uncertainty, or `None`.

### Fully specified researcher example

Delegate to `senior-sol-terra-medium`:

Goal: Determine why empty project names currently reach persistence.

Files: in scope: `src/project.py`, `src/storage.py`, `tests/test_project.py` / out of scope: every other path.

Constraints: remain read-only; trace the current call path; distinguish direct evidence from inference; do not propose unrelated redesigns.

Definition of done: inspect the named files, identify the first missing validation boundary with file-and-line evidence, and rule out the persistence layer as the source when the evidence supports that conclusion.

Report format: researcher schema.

The researcher report must use:

- Answer: concise evidence-backed conclusion.
- Evidence: file paths, line references, and observed behavior.
- Ruled out: alternatives checked and why they do not fit.
- Open questions: unresolved uncertainty or `None`.

## Acceptance gate

Writer reports require Done, Verified, and Not done / questions. Research reports require Answer, Evidence, Ruled out, and Open questions. Reject missing sections, unverified success, or out-of-scope edits.

## Failure and fallback policy

After failure one, diagnose the cause and produce a materially corrected specification; never retry an unchanged specification. The second attempt may use the nearest stronger suitable profile. After two failed delegations for the same bounded subtask, notify the user that Sol is entering fallback, implement only that subtask, verify it, and disclose the main-agent implementation in the final report. Environment or permission failures do not count as model failures.

## Final synthesis

Sol owns decisions, acceptance, and the final response. Summarize accepted delegated work, verification evidence, unresolved risks, and every use of fallback.
