#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "Vytvarim lokalni virtualni prostredi v $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

echo "Kontroluji Python zavislosti..."
"$VENV_DIR/bin/python" -m pip install -r "$ROOT_DIR/app/requirements.txt"

if [ "${TEATRUMDB_START_DB:-1}" != "0" ]; then
  "$ROOT_DIR/scripts/db-up.sh"
fi

echo "Spoustim TeatrumDB..."
exec "$VENV_DIR/bin/python" "$ROOT_DIR/app/app.py"
