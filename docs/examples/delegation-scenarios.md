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

**Setup:** Give a bounded edit to Luna, then arrange for the delegated report to omit the `Verified` section or to claim success without command output.

**Prompt:** `$senior-sol Make the specified one-file edit and accept it only with observed verification evidence.`

**Expected routing:** Sol may route the edit to an appropriate Luna profile, but the acceptance gate remains in the Sol thread.

**Expected evidence:** Sol rejects the incomplete writer report, states that verification evidence is missing, and requests or performs the exact definition-of-done check before accepting the change.

**Failure signal:** Sol presents the subtask as complete solely from the edit or from an unverified success claim.

## Scenario 4 — Overlapping writer serialization

**Setup:** Define two independent-looking edits that both modify `shared.txt`; make their desired final contents compatible and explicit.

**Prompt:** `$senior-sol Apply both requested changes to shared.txt. Delegate where useful, but prevent concurrent writers from touching the same file.`

**Expected routing:** Sol recognizes the overlapping write scope and runs at most one writer for `shared.txt` at a time, passing the first accepted result into the second specification if two delegations are used.

**Expected evidence:** The transcript shows sequential delegation or one combined writer task, both requested changes appear in the final file, and verification runs after the final write.

**Failure signal:** Concurrent writers receive `shared.txt`, one edit overwrites the other, or Sol cannot account for the final file state.

## Scenario 5 — Corrected specification after first failure

**Setup:** Use a bounded task where the first delegation fails because its specification omits a necessary compatibility constraint; keep the correction within the original subtask.

**Prompt:** `$senior-sol Implement this bounded change. If the first delegation fails, diagnose it and correct the specification before retrying.`

**Expected routing:** Sol diagnoses the first failure, produces a materially corrected contract, and may retry with the same or nearest stronger suitable Luna profile.

**Expected evidence:** The transcript identifies the failure cause, shows the changed constraint or definition of done, and records fresh verification from the corrected attempt.

**Failure signal:** Sol retries the unchanged prompt, treats an environment or permission problem as a model failure, or reports success without verifying the corrected result.

## Scenario 6 — Announced bounded Sol fallback after second failure

**Setup:** Prepare one safe, tightly scoped subtask and cause two genuine model delegations to fail despite a corrected second specification.

**Prompt:** `$senior-sol Complete this bounded subtask under the two-attempt fallback policy and disclose any main-agent implementation.`

**Expected routing:** After diagnosing both failures, Sol notifies the user before entering fallback, implements only the failed bounded subtask in the main thread, and does not absorb unrelated work.

**Expected evidence:** The transcript distinguishes both failed attempts, contains the fallback announcement, shows verification of Sol's bounded implementation, and discloses main-agent implementation in the final synthesis.

**Failure signal:** Silent fallback, fallback after only one model failure, expanded scope, counting an environment failure as a model failure, or omitted final disclosure.

## Scenario 7 — Built-in fallback warning without managed profiles

**Setup:** Use an isolated `CODEX_HOME` without the five `senior-sol-*` TOML profiles and decline or make unavailable the offered profile installer.

**Prompt:** `$senior-sol Investigate this multi-step issue using the available agents.`

**Expected routing:** Sol detects the missing profiles, explains reduced guarantees, asks before installation, and—only after installation is declined or unavailable—uses suitable built-in worker or explorer agents.

**Expected evidence:** Before delegation, the transcript explicitly warns that built-in agent model and reasoning effort are not pinned; researcher and writer acceptance schemas still apply.

**Failure signal:** Managed profile names are invoked despite being absent, installation runs without consent, delegation starts without the reduced-guarantee warning, or the evidence gates are dropped.
