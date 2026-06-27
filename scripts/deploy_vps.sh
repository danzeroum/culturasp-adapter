#!/usr/bin/env bash
#
# CulturaSP-Adapter — VPS deploy bootstrap.
#
# Clones (or updates) the repo into $TARGET_DIR and brings up the full Docker
# stack (api + scraper + postgres + redis), runs DB migrations and waits for the
# API to become healthy. Idempotent — safe to re-run to update.
#
# Quick start (run on the VPS):
#   curl -fsSL https://raw.githubusercontent.com/danzeroum/culturasp-adapter/main/scripts/deploy_vps.sh | bash
#
# Configurable via environment variables:
#   TARGET_DIR  (default: /opt/btv)
#   REPO_URL    (default: https://github.com/danzeroum/culturasp-adapter.git)
#   BRANCH      (default: main)
#
set -euo pipefail

TARGET_DIR="${TARGET_DIR:-/opt/btv}"
REPO_URL="${REPO_URL:-https://github.com/danzeroum/culturasp-adapter.git}"
BRANCH="${BRANCH:-main}"

log()  { printf '\033[1;34m▶ %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✓ %s\033[0m\n' "$*"; }
err()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; }
die()  { err "$*"; exit 1; }

# Use sudo only when not already root (and only if available).
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  if command -v sudo >/dev/null 2>&1; then SUDO="sudo"; else
    die "need root to manage ${TARGET_DIR}: run as root or install sudo"
  fi
fi

# --- preflight ---------------------------------------------------------------
log "Checking prerequisites"
command -v git >/dev/null 2>&1 || die "git not found — install git first"
command -v docker >/dev/null 2>&1 || die "docker not found — install Docker Engine: https://docs.docker.com/engine/install/"
docker compose version >/dev/null 2>&1 || die "'docker compose' (v2) plugin not found — install the Compose plugin"
ok "git + docker + docker compose present"

# --- clone or update ---------------------------------------------------------
if [ -d "$TARGET_DIR/.git" ]; then
  log "Updating existing checkout in $TARGET_DIR"
  git -C "$TARGET_DIR" fetch --prune origin
  git -C "$TARGET_DIR" checkout "$BRANCH"
  git -C "$TARGET_DIR" pull --ff-only origin "$BRANCH"
else
  if [ -e "$TARGET_DIR" ] && [ -n "$(ls -A "$TARGET_DIR" 2>/dev/null || true)" ]; then
    die "$TARGET_DIR exists and is not a git checkout — move it aside or set TARGET_DIR"
  fi
  log "Creating $TARGET_DIR and cloning $REPO_URL ($BRANCH)"
  $SUDO mkdir -p "$TARGET_DIR"
  $SUDO chown -R "$(id -u):$(id -g)" "$TARGET_DIR"
  git clone -b "$BRANCH" "$REPO_URL" "$TARGET_DIR"
fi
cd "$TARGET_DIR"
ok "Repo ready at $(pwd) ($(git rev-parse --short HEAD))"

# --- environment -------------------------------------------------------------
if [ ! -f .env ]; then
  cp .env.example .env
  ok "Created .env from .env.example — review secrets (e.g. POSTGRES_PASSWORD) before exposing publicly"
else
  ok ".env already present — leaving it untouched"
fi

# Compose wrapper: base + production override.
dc() { docker compose -f docker-compose.yml -f docker-compose.prod.yml "$@"; }

# --- build & data tier -------------------------------------------------------
log "Building images (this can take a few minutes on first run)"
dc build

log "Starting data services (postgres, redis)"
dc up -d postgres redis

log "Waiting for Postgres to become healthy"
pg_cid="$(dc ps -q postgres)"
for _ in $(seq 1 60); do
  status="$(docker inspect -f '{{.State.Health.Status}}' "$pg_cid" 2>/dev/null || echo starting)"
  [ "$status" = "healthy" ] && break
  sleep 2
done
[ "${status:-}" = "healthy" ] || die "Postgres did not become healthy in time"
ok "Postgres healthy"

# --- migrations --------------------------------------------------------------
log "Applying database migrations (alembic upgrade head)"
if dc run --rm api alembic upgrade head; then
  ok "Migrations applied"
else
  err "alembic failed — the scheduler's create_all() will still create tables, continuing"
fi

# --- app tier ----------------------------------------------------------------
log "Starting application services (api, scraper)"
dc up -d api scraper

# --- health check ------------------------------------------------------------
log "Waiting for the API health endpoint"
healthy=0
for _ in $(seq 1 30); do
  if command -v curl >/dev/null 2>&1; then
    curl -fsS http://localhost:8000/health >/dev/null 2>&1 && { healthy=1; break; }
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- http://localhost:8000/health >/dev/null 2>&1 && { healthy=1; break; }
  else
    break  # no http client available; skip the active check
  fi
  sleep 2
done

echo
dc ps
echo
if [ "$healthy" -eq 1 ]; then
  ok "Deploy complete — API is up at http://localhost:8000  (docs: /docs)"
else
  err "Deploy finished but /health did not respond yet. Check logs: (cd $TARGET_DIR && docker compose logs -f api)"
fi
