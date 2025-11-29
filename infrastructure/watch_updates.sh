#!/usr/bin/env bash
set -euo pipefail

REPO_DIR=${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}
INFRA_DIR=${INFRA_DIR:-"$REPO_DIR/infrastructure"}
FLAGS_DIR=${FLAGS_DIR:-"$REPO_DIR/flags"}

mkdir -p "$FLAGS_DIR"

echo "[watch_updates] Watching $FLAGS_DIR for update_requested flag"

while true; do
  if [ -f "$FLAGS_DIR/update_requested" ]; then
    echo "[watch_updates] Update requested detected"
    rm -f "$FLAGS_DIR/update_requested"

    # Pull latest code
    if [ -d "$REPO_DIR/.git" ]; then
      echo "[watch_updates] git pull"
      (cd "$REPO_DIR" && git pull || true)
    fi

    # Build & start services
    echo "[watch_updates] docker compose up -d --build"
    if command -v docker compose &>/dev/null; then
      (cd "$INFRA_DIR" && docker compose up -d --build)
    else
      (cd "$INFRA_DIR" && docker-compose up -d --build)
    fi

    # Run DB initialization/migrations
    echo "[watch_updates] applying database migrations"
    if command -v docker compose &>/dev/null; then
      (cd "$INFRA_DIR" && docker compose exec -T backend python - <<'PY'
import asyncio
from app.core.init_db import init_db
asyncio.run(init_db())
PY
      )
    else
      (cd "$INFRA_DIR" && docker-compose exec -T backend python - <<'PY'
import asyncio
from app.core.init_db import init_db
asyncio.run(init_db())
PY
      )
    fi

    echo "[watch_updates] update completed"
  fi
  sleep 10
done
