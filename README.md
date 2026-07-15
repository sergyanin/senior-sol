# Senior Sol

## Value proposition

Senior Sol is a Codex orchestration plugin for substantial multi-step engineering work. Sol keeps architecture, decisions, acceptance, and the final answer in the main thread while delegating bounded work to model-specific Terra researchers and Luna implementers.

## Routing table

| Work | Managed profile | Reasoning | Write access |
| --- | --- | --- | --- |
| One-step mechanical edit | `senior-sol-luna-low` | low | yes |
| Explicit multi-step implementation | `senior-sol-luna-medium` | medium | yes |
| Fast evidence collection | `senior-sol-terra-low` | low | no |
| Investigation, diagnosis, or review | `senior-sol-terra-medium` | medium | no |
| Security, migration, or contested conclusion | `senior-sol-terra-high` | high | no |

## Safety guarantees

- Sol owns ambiguous decisions and accepts delegated results only when the required report sections and verification evidence are present.
- Terra profiles run read-only. Luna receives an exact file scope, constraints, and definition-of-done command.
- Independent work runs in parallel only for disjoint write scopes; overlapping writers are serialized.
- A failed delegation is diagnosed before retrying with a materially corrected specification. An unchanged specification is never retried.
- After two model failures on one bounded subtask, Sol announces fallback, implements only that subtask, verifies it, and discloses the fallback in the final report. Environment and permission failures do not count as model failures.

## Requirements

- Codex with plugin and custom-agent support.
- Git for loading the GitHub marketplace.
- PowerShell on Windows or a POSIX shell on macOS/Linux for managed-profile installation.
- The user must select Sol as the main-thread model and choose its reasoning level before activating Senior Sol. The plugin does not change either setting.

## Marketplace install

Add the public marketplace and install the plugin:

```text
codex plugin marketplace add sergyanin/senior-sol
codex plugin add senior-sol@senior-sol
```

## Profile install on Windows

From a checkout of `https://github.com/sergyanin/senior-sol`, run:

```powershell
powershell -NoProfile -File plugins/senior-sol/scripts/install-agents.ps1
```

Use `-Force` only when you intend to replace locally modified managed profiles. The installer does not overwrite conflicts by default.

## Profile install on POSIX

From a checkout of `https://github.com/sergyanin/senior-sol`, run:

```sh
sh plugins/senior-sol/scripts/install-agents.sh
```

Use `--force` only when you intend to replace locally modified managed profiles. After either profile installer finishes, open a new Codex thread so Codex discovers the custom agents.

## Activation

In that new thread, select Sol and its reasoning level, then invoke the skill explicitly:

```text
$senior-sol Orchestrate this multi-step task: <describe the outcome and constraints>.
```

Senior Sol is opt-in and does not activate for ordinary requests.

## Fallback behavior

If an installed managed profile's model or reasoning effort is unavailable, that availability failure does not count toward the two model-failure attempts. Senior Sol retries once with the nearest available profile of the same role; Terra remains read-only. If no same-role managed profile can run, Senior Sol warns the user and offers the built-in `worker` or `explorer` without incrementing the fallback counter, explaining that its model and reasoning effort are not pinned.

If managed profiles are absent and installation is declined or unavailable, Senior Sol applies the same warning before offering a built-in agent. The same acceptance and evidence gates still apply. See the [manual delegation scenarios](docs/examples/delegation-scenarios.md) for the expected routing and failure signals.

## Update

Refresh the GitHub marketplace snapshot, reinstall the plugin, and refresh the managed profiles from an updated checkout:

```text
codex plugin marketplace upgrade senior-sol
codex plugin remove senior-sol@senior-sol
codex plugin add senior-sol@senior-sol
```

From the updated repository checkout, replace the managed profiles on Windows:

```powershell
powershell -NoProfile -File plugins/senior-sol/scripts/install-agents.ps1 -Force
```

Or replace them on POSIX:

```sh
sh plugins/senior-sol/scripts/install-agents.sh --force
```

Then open a new Codex thread so Codex discovers the updated plugin and profiles.

## Uninstall

Remove only the five managed profiles before removing the plugin and marketplace:

```powershell
powershell -NoProfile -File plugins/senior-sol/scripts/uninstall-agents.ps1
```

```sh
sh plugins/senior-sol/scripts/uninstall-agents.sh
```

```text
codex plugin remove senior-sol@senior-sol
codex plugin marketplace remove senior-sol
```

The profile uninstallers preserve unrelated files in the Codex agents directory.

## Development validation

From the repository root, run:

```text
python -m unittest discover -s tests -v
python scripts/validate.py
```

Release behavior is also checked with the seven manual scenarios and the [release checklist](docs/release-checklist.md).

## Inspiration

Senior Sol was inspired by [AndyShaman/senior-fable](https://github.com/AndyShaman/senior-fable) and adapts the senior-orchestrator idea to Codex plugins and custom agents.

## License

Senior Sol is released under the [MIT](LICENSE) license.
