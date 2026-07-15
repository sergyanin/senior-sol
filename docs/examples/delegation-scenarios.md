# Senior Sol manual delegation scenarios

Run these smoke scenarios in a disposable repository or branch. Start a new Codex thread with Sol selected, invoke `$senior-sol`, and retain the thread transcript as release evidence. A reviewer should be able to match each observation to the expected routing, evidence, and failure signal below.

## Scenario 1 — Luna mechanical edit

**Setup:** Create `sample.txt` containing `alpha` and allow only that file to change.

**Prompt:** `$senior-sol Replace alpha with beta in sample.txt, verify the file contains beta, and change nothing else.`

**Expected routing:** Sol supplies a bounded writer contract to `senior-sol-luna-low` because the task is a one-step mechanical edit.

**Expected evidence:** The Luna report contains `Done`, `Verified`, and `Not done / questions`; it identifies `sample.txt`, reports the exact verification performed, and the final diff changes only `alpha` to `beta`.

**Failure signal:** Sol edits the file without announcing fallback, chooses Terra or a stronger Luna profile without cause, accepts a report with no verification, or changes another file.

## Scenario 2 — Terra read-only investigation

**Setup:** Use a small repository with a known configuration-loading path and record `git status --short` before the run.

**Prompt:** `$senior-sol Trace where the application reads its configuration and identify the first validation boundary. Investigate only; do not edit files.`

**Expected routing:** Sol delegates the diagnosis to `senior-sol-terra-medium` with an explicit read-only scope and evidence requirement.

**Expected evidence:** The Terra report contains `Answer`, `Evidence`, `Ruled out`, and `Open questions`, cites file paths and line numbers, separates inference from observed facts, and leaves `git status --short` unchanged.

**Failure signal:** Any file changes, missing source citations, a writer profile, or acceptance of a report without all four researcher sections.

## Scenario 3 — Missing verification rejection

**Setup:** Contract simulation. Do not invoke a worker. Paste the exact prompt below into a new Sol thread; the included Fabricated Luna report intentionally omits `Verified`.

**Prompt:**

```text
$senior-sol Contract simulation. Do not edit files or delegate. Evaluate this fabricated worker result against the writer acceptance gate.

Goal: Replace alpha with beta.
Files: in scope: sample.txt / out of scope: every other path.
Constraints: preserve the trailing newline and make no other content changes.
Definition of done: `python -c "from pathlib import Path; assert Path('sample.txt').read_text() == 'beta\n'"` passes.

Fabricated Luna report:
Done: Replaced alpha with beta in sample.txt.
Not done / questions: None.

State whether Sol accepts or rejects the report and state the exact next action. Do not edit files.
```

**Expected routing:** This is an acceptance-contract simulation, so Sol does not delegate. Sol rejects the fabricated report because the required `Verified` section and observed command result are absent.

**Expected evidence:** Sol names the missing `Verified` section, refuses to present the edit as complete, and says the exact definition-of-done command must be run and reported before acceptance.

**Failure signal:** Sol accepts the fabricated report, edits a file, starts a delegation, or substitutes a generic verification request for the supplied command.

## Scenario 4 — Overlapping writer serialization

**Setup:** Define two independent-looking edits that both modify `shared.txt`; make their desired final contents compatible and explicit.

**Prompt:** `$senior-sol Apply both requested changes to shared.txt. Delegate where useful, but prevent concurrent writers from touching the same file.`

**Expected routing:** Sol recognizes the overlapping write scope and runs at most one writer for `shared.txt` at a time, passing the first accepted result into the second specification if two delegations are used.

**Expected evidence:** The transcript shows sequential delegation or one combined writer task, both requested changes appear in the final file, and verification runs after the final write.

**Failure signal:** Concurrent writers receive `shared.txt`, one edit overwrites the other, or Sol cannot account for the final file state.

## Scenario 5 — Corrected specification after first failure

**Setup:** Contract simulation. Do not invoke a worker. Paste the exact prompt below into a new Sol thread. The Fabricated Luna report exposes a Python 3.9 compatibility constraint omitted from the first specification.

**Prompt:**

```text
$senior-sol Contract simulation. Do not edit files or delegate. Diagnose the fabricated first failure and write the complete corrected delegation contract for attempt two.

First specification:
Goal: Reject an empty format name before parsing.
Files: in scope: src/config.py, tests/test_config.py / out of scope: every other path.
Constraints: preserve the public parse_config signature and existing exception types.
Definition of done: `python -m unittest tests.test_config -v` passes.

Fabricated Luna report:
Done: Added the empty-name guard with a match statement and added a regression test.
Verified: `python -m unittest tests.test_config -v` failed during import with SyntaxError on Python 3.9 at the match statement.
Not done / questions: The suite does not import on the supported runtime.

The product supports Python 3.9. State the failure cause, then return the corrected Goal, Files, Constraints, Definition of done, and Report format. Do not edit files.
```

**Expected routing:** Sol identifies the omitted Python 3.9 constraint as the cause and prepares attempt two for `senior-sol-luna-medium` or the nearest stronger suitable Luna profile. The corrected specification keeps the same two-file scope and explicitly prohibits `match` syntax and other Python 3.10-only features.

**Expected evidence:** The returned contract includes the exact Goal and Files, adds “remain compatible with Python 3.9” to Constraints, retains `python -m unittest tests.test_config -v` as Definition of done, and requires the writer report sections `Done`, `Verified`, and `Not done / questions`.

**Failure signal:** Sol repeats the first specification unchanged, expands the file scope, omits Python 3.9 compatibility, edits files during the simulation, or treats the failed report as successful.

## Scenario 6 — Announced bounded Sol fallback after second failure

**Setup:** Contract simulation. Do not invoke a worker. Paste the exact prompt below into a new Sol thread. It contains two Fabricated Luna reports for the same bounded subtask and a materially corrected second specification.

**Prompt:**

```text
$senior-sol Contract simulation. Do not edit files or delegate. Apply the two-attempt fallback policy to these supplied contracts and fabricated reports, then state the next decision and exact bounded fallback contract.

Attempt one contract:
Goal: Reject a whitespace-only project name.
Files: in scope: src/project.py, tests/test_project.py / out of scope: every other path.
Constraints: preserve the public create_project signature.
Definition of done: `python -m unittest tests.test_project -v` passes.

Fabricated Luna report for attempt one:
Done: Added a stripped-name check and a regression test.
Verified: `python -m unittest tests.test_project -v` failed: expected ProjectNameError, got ValueError.
Not done / questions: Required exception type was not specified.

Attempt two corrected contract:
Goal: Reject a whitespace-only project name with ProjectNameError.
Files: in scope: src/project.py, tests/test_project.py / out of scope: every other path.
Constraints: preserve the public create_project signature; raise the existing ProjectNameError; do not edit any other path.
Definition of done: `python -m unittest tests.test_project -v` passes.

Fabricated Luna report for attempt two:
Done: Added the ProjectNameError guard, but also refactored src/cli.py.
Verified: `python -m unittest tests.test_project -v` still failed because a tab-only name was accepted.
Not done / questions: Tab-only input remains unhandled and src/cli.py is outside scope.

State the policy decision before any implementation. Then provide the exact fallback Goal, Files, Constraints, Definition of done, and required final disclosure. Do not edit files.
```

**Expected routing:** Sol counts two model failures on the same bounded subtask, announces that it is entering Sol fallback before implementation, and limits the fallback contract to `src/project.py` and `tests/test_project.py`. The contract requires all whitespace-only names to raise the existing `ProjectNameError`, preserves the public signature, prohibits every other path, and retains the exact unittest command.

**Expected evidence:** Sol distinguishes the first missing-constraint failure from the second corrected-attempt failure, explicitly rejects the out-of-scope `src/cli.py` edit, supplies the bounded fallback contract, and promises to disclose main-agent implementation plus observed verification in the final synthesis.

**Failure signal:** Sol silently enters fallback, retries a third delegation, includes `src/cli.py` in scope, weakens the exception or verification constraints, edits files during the simulation, or omits the required final disclosure.

## Scenario 7 — Built-in fallback warning without managed profiles

**Setup:** Use an isolated `CODEX_HOME` without the five `senior-sol-*` TOML profiles and decline or make unavailable the offered profile installer.

**Prompt:** `$senior-sol Investigate this multi-step issue using the available agents.`

**Expected routing:** Sol detects the missing profiles, explains reduced guarantees, asks before installation, and—only after installation is declined or unavailable—uses suitable built-in worker or explorer agents.

**Expected evidence:** Before delegation, the transcript explicitly warns that built-in agent model and reasoning effort are not pinned; researcher and writer acceptance schemas still apply.

**Failure signal:** Managed profile names are invoked despite being absent, installation runs without consent, delegation starts without the reduced-guarantee warning, or the evidence gates are dropped.
