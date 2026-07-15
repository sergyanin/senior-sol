#!/bin/sh

set -u

case "$#" in
    0)
        ;;
    *)
        printf '%s\n' 'usage: uninstall-agents.sh' >&2
        exit 2
        ;;
esac

codex_home="${CODEX_HOME:-${HOME}/.codex}"
target_dir="$codex_home/agents"

if [ -L "$target_dir" ]; then
    printf 'refusing redirected agents directory: %s\n' "$target_dir" >&2
    exit 1
fi
if [ -e "$target_dir" ] && [ ! -d "$target_dir" ]; then
    printf 'agents target exists but is not a directory: %s\n' "$target_dir" >&2
    exit 1
fi

for name in \
    senior-sol-luna-low.toml \
    senior-sol-luna-medium.toml \
    senior-sol-terra-high.toml \
    senior-sol-terra-low.toml \
    senior-sol-terra-medium.toml
do
    path="$target_dir/$name"
    if [ -f "$path" ]; then
        rm "$path" || exit 1
        printf 'removed: %s\n' "$name"
    else
        printf 'missing: %s\n' "$name"
    fi
done

exit 0
