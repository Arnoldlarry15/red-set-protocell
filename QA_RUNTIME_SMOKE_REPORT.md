# Runtime Smoke Report (CI + UI)

Date: 2026-02-19
Scope: Local CI-equivalent commands, backend API runtime checks, and UI interaction checks.

## What worked

1. **Frontend production build succeeded**
   - `npm run build` completed and generated `dist/` artifacts.

2. **Backend service booted in development mode**
   - API server starts with explicit CORS origin and demo password.
   - Health endpoint (`GET /health`) returns healthy status.

3. **Core session lifecycle endpoints respond**
   - `POST /session/start` returns session ID and initialized status.
   - `POST /session/{id}/execute` starts asynchronous execution.
   - `GET /session/{id}/stats` returns structured stats payload.

4. **Login page renders correctly in browser smoke test**
   - `/login` loads and displays backend selector, API key input, and submit action.

## What did not work (or is environment-limited)

1. **Full CI-equivalent pytest command cannot run in this container currently**
   - `pytest-cov` and `pytest-asyncio` could not be fetched due proxy/network restrictions in this environment.
   - Result: standard CI pytest invocation with coverage flags fails locally here.
   - Workaround test used: `python -m pytest -o addopts='' tests/test_config.py -q` (passes 13 tests).

2. **UI login attempt showed generic `Network Error` in browser-container run**
   - The browser-container environment did not reach backend API from frontend JS during Playwright run.
   - This appears environment/tunneling specific (direct `curl` to backend from host works).
   - User-visible impact in this run: error message is generic and does not indicate whether issue is CORS, DNS/host mapping, or offline backend.

3. **Execution against external LLM provider fails in this environment**
   - Session execution reached provider call path but failed with `openai.APIConnectionError` caused by HTTP proxy restrictions (`403 Forbidden`).
   - This is an environment connectivity issue, not a local route/startup failure.

## UX and integration notes

- `GET /health` and `GET /api/health` both exist and return healthy status. Both bare and `/api`-prefixed paths are now registered as part of the route-prefix compatibility fix.
- API-key validation endpoint does fast local prefix checks and then attempts a real provider call. In no-egress or proxy-restricted environments, users can see failures even with otherwise valid flows.

## Artifacts from UI smoke test

- `ui-home.png`
- `ui-login.png`
- `ui-login-invalid.png`

