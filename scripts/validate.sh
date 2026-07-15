#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
if command -v python >/dev/null 2>&1; then
    python_command=python
elif command -v python.exe >/dev/null 2>&1; then
    python_command=python.exe
else
    printf '%s\n' 'python interpreter not found' >&2
    exit 127
fi
"$python_command" -m unittest discover -s tests -v
"$python_command" scripts/validate.py
