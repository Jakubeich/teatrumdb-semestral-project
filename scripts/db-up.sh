#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$ROOT_DIR/docker-compose.yml"
CONTAINER_NAME="teatrumdb-oracle"
MAX_ATTEMPTS="${DB_WAIT_ATTEMPTS:-90}"
SLEEP_SECONDS="${DB_WAIT_INTERVAL:-5}"

if [ -f "$ROOT_DIR/.env" ]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
fi

echo "Startuji Oracle DB v Dockeru..."
docker compose -f "$COMPOSE_FILE" up -d oracle

echo "Cekam na pripravenou databazi..."
for ((attempt=1; attempt<=MAX_ATTEMPTS; attempt++)); do
  status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER_NAME" 2>/dev/null || true)"
  if [ "$status" = "healthy" ]; then
    echo "Oracle DB je pripravena."
    exit 0
  fi

  echo "  pokus $attempt/$MAX_ATTEMPTS: stav = ${status:-neznamy}"
  sleep "$SLEEP_SECONDS"
done

echo "Oracle DB se nepodarilo pripravit vcas." >&2
echo "Posledni logy kontejneru:" >&2
docker logs --tail 200 "$CONTAINER_NAME" >&2 || true
exit 1
