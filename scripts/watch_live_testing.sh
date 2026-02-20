#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"
API_BASE_URL="${VITE_API_BASE_URL:-http://localhost:${BACKEND_PORT}}"
ALLOWED_ORIGINS="${RSP_ALLOWED_ORIGINS:-http://localhost:${FRONTEND_PORT}}"

BACKEND_LOG="${BACKEND_LOG:-$ROOT_DIR/.live-backend.log}"
FRONTEND_LOG="${FRONTEND_LOG:-$ROOT_DIR/.live-frontend.log}"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<USAGE
Run backend + frontend in live-watch mode for manual testing.

Usage:
  scripts/watch_live_testing.sh

Optional env vars:
  BACKEND_HOST, BACKEND_PORT
  FRONTEND_HOST, FRONTEND_PORT
  VITE_API_BASE_URL
  RSP_ALLOWED_ORIGINS
  RSP_DEMO_PASSWORD (defaults to 'changeme')
USAGE
  exit 0
fi

cleanup() {
  echo
  echo "[live-watch] stopping processes..."
  [[ -n "${BACKEND_PID:-}" ]] && kill "$BACKEND_PID" 2>/dev/null || true
  [[ -n "${FRONTEND_PID:-}" ]] && kill "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "[live-watch] backend log:  $BACKEND_LOG"
echo "[live-watch] frontend log: $FRONTEND_LOG"

echo "[live-watch] starting backend on ${BACKEND_HOST}:${BACKEND_PORT}"
(
  cd "$BACKEND_DIR"
  RSP_ENVIRONMENT=development \
  RSP_ALLOWED_ORIGINS="$ALLOWED_ORIGINS" \
  RSP_REQUIRE_AUTH=false \
  RSP_DEMO_PASSWORD="${RSP_DEMO_PASSWORD:-changeme}" \
  uvicorn app.api_server:app --host "$BACKEND_HOST" --port "$BACKEND_PORT"
) >"$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!

# Determine the host to probe: use localhost when binding to all interfaces, otherwise use BACKEND_HOST directly
_PROBE_HOST="localhost"
if [[ "$BACKEND_HOST" != "0.0.0.0" && "$BACKEND_HOST" != "::" ]]; then
  _PROBE_HOST="$BACKEND_HOST"
fi

# Wait until backend is reachable
for _ in {1..40}; do
  if curl -fsS "http://${_PROBE_HOST}:${BACKEND_PORT}/health" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

if ! curl -fsS "http://${_PROBE_HOST}:${BACKEND_PORT}/health" >/dev/null 2>&1; then
  echo "[live-watch] backend failed to start. See $BACKEND_LOG"
  exit 1
fi

echo "[live-watch] starting frontend on ${FRONTEND_HOST}:${FRONTEND_PORT}"
(
  cd "$FRONTEND_DIR"
  VITE_API_BASE_URL="$API_BASE_URL" npm run dev -- --host "$FRONTEND_HOST" --port "$FRONTEND_PORT"
) >"$FRONTEND_LOG" 2>&1 &
FRONTEND_PID=$!

echo
echo "[live-watch] READY"
echo "  UI:      http://localhost:${FRONTEND_PORT}/login"
echo "  API:     http://localhost:${BACKEND_PORT}/health"
echo "  API alt: http://localhost:${BACKEND_PORT}/api/health"
echo
echo "[live-watch] tailing logs. Press Ctrl+C to stop."
echo

tail -n +1 -f "$BACKEND_LOG" "$FRONTEND_LOG"
