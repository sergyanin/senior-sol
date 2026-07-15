#!/bin/sh

set -u

force=0
case "$#" in
    0)
        ;;
    1)
        case "$1" in
            --force)
                force=1
                ;;
            *)
                printf '%s\n' 'usage: install-agents.sh [--force]' >&2
                exit 2
                ;;
        esac
        ;;
    *)
        printf '%s\n' 'usage: install-agents.sh [--force]' >&2
        exit 2
        ;;
esac

codex_home="${CODEX_HOME:-${HOME}/.codex}"
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_dir=$(CDPATH= cd -- "$script_dir/../agents" && pwd)
target_dir="$codex_home/agents"
mkdir -p -- "$target_dir" || exit 1

had_conflict=0
for name in \
    senior-sol-luna-low.toml \
    senior-sol-luna-medium.toml \
    senior-sol-terra-high.toml \
    senior-sol-terra-low.toml \
    senior-sol-terra-medium.toml
do
    origin="$source_dir/$name"
    destination="$target_dir/$name"

    if [ ! -e "$destination" ]; then
        cp "$origin" "$destination" || exit 1
        printf 'created: %s\n' "$name"
    elif cmp -s "$origin" "$destination"; then
        printf 'unchanged: %s\n' "$name"
    elif [ "$force" -eq 1 ]; then
        cp "$origin" "$destination" || exit 1
        printf 'replaced: %s\n' "$name"
    else
        printf 'conflict: %s\n' "$name"
        had_conflict=1
    fi
done

if [ "$had_conflict" -ne 0 ]; then
    exit 1
fi

exit 0
