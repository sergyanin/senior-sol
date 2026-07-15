# Senior Sol v0.1.0 release checklist

Publication is manual. Leave each item unchecked until its command or observation has actually succeeded, and retain links or transcript evidence with the release record.

## Local and cross-platform verification

- [x] On Windows, run `python -m unittest discover -s tests -v` in a clean checkout and record zero failures. **Verified 2026-07-15 via `scripts/validate.ps1`.**
- [ ] On macOS or Linux, run `python -m unittest discover -s tests -v` in a clean checkout and record zero failures.
- [x] Run repository and marketplace validation with `python scripts/validate.py` and record `Repository metadata is valid.` **Verified 2026-07-15.**
- [x] Run official plugin validation for `plugins/senior-sol` from PowerShell with `python (Join-Path $HOME '.codex\skills\.system\plugin-creator\scripts\validate_plugin.py') plugins\senior-sol`; attach the successful output. This validator checks the plugin directory, not the marketplace file. **Verified 2026-07-15; validator exited 0.**
- [x] Confirm the PowerShell and POSIX installer tests cover clean install, idempotent install, conflict refusal, forced replacement, and safe uninstall. **Verified 2026-07-15; isolated PowerShell install also produced exactly five managed profiles and safe uninstall preserved the `agents` directory.**
- [x] Check tracked public files for secrets, credentials, private data, and developer-specific local paths; record the command and result. **Verified 2026-07-15; reviewed secret-like matches and found no credentials or machine-local runtime dependency.**

## GitHub preparation

- [ ] Run `gh auth status` and confirm the authenticated account is `sergyanin`.
- [ ] Create the public repository with `gh repo create sergyanin/senior-sol --public --source . --remote origin`.
- [ ] Ensure the release branch is integrated into `main`, then run `git push -u origin main`.
- [ ] Confirm the pushed `main` commit matches the locally verified commit.

## Marketplace installation and smoke evidence

- [ ] Add the marketplace from GitHub with `codex plugin marketplace add sergyanin/senior-sol`.
- [ ] Complete marketplace installation with `codex plugin add senior-sol@senior-sol`.
- [ ] Install all five managed profiles with the OS-appropriate repository script.
- [ ] Open a new Codex thread after profile installation so custom agents are discovered.
- [ ] In the new thread, select Sol and its intended reasoning level before invoking `$senior-sol`.
- [ ] Execute and record Scenario 1, Luna mechanical edit.
- [ ] Execute and record Scenario 2, Terra read-only investigation.
- [ ] Execute and record Scenario 3, missing verification rejection.
- [ ] Execute and record Scenario 4, overlapping writer serialization.
- [ ] Execute and record Scenario 5, corrected specification after first failure.
- [ ] Execute and record Scenario 6, announced bounded Sol fallback after second failure.
- [ ] Execute and record Scenario 7, built-in fallback warning when managed profiles are absent.

## Manual publication

- [ ] Review the final diff and confirm no CI wrappers, release automation, or publication credentials were added for this release task.
- [ ] Create the annotated tag with `git tag -a v0.1.0 -m "Senior Sol v0.1.0"`.
- [ ] Push tag `v0.1.0` with `git push origin v0.1.0`.
- [ ] Create the GitHub Release with `gh release create v0.1.0 --title "Senior Sol v0.1.0" --notes-file docs/release-checklist.md`.
- [ ] Verify installation once more from the tagged GitHub marketplace and preserve the final new-thread transcript.
