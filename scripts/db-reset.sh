#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "Zastavuji Oracle DB a mazu perzistentni data..."
docker compose -f "$ROOT_DIR/docker-compose.yml" down -v
echo "Hotovo."
