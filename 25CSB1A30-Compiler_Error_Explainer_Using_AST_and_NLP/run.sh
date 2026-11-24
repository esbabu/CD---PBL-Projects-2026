#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ -d "$DIR/.venv" ]; then
    PYTHON="$DIR/.venv/bin/python"
elif [ -d "$DIR/venv" ]; then
    PYTHON="$DIR/venv/bin/python"
else
    PYTHON="python3"
fi

if [ "$1" == "--cli" ]; then
    shift
    exec "$PYTHON" src/main.py "$@"
elif [ "$1" == "--test" ]; then
    shift
    exec "$PYTHON" -m pytest tests/ "$@"
else
    echo "Starting Compiler Error Explainer & Auto-Healer GUI..."
    exec "$PYTHON" src/gui.py "$@"
fi
