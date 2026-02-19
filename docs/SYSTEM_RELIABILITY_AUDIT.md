# System Reliability & Security Audit (Production SRE Framing)

Date: 2026-02-19
Scope: `backend/app`, `backend/tests`, `frontend/src`, dependency manifests, route contract surfaces.

## 1) Threat Modeling Pass

### User-controlled input paths reviewed
- Prompt inputs and user inputs sent to target backends (`Target.execute`, API session config endpoints).
- Auth/API-key validation endpoint (`/auth/validate-llm-key`).
- Config CRUD endpoints (`/remote/config/*`).
- Logging and error-handling paths.

### Findings
- **Error leakage risk**: multiple API handlers previously returned `HTTPException(..., detail=str(e))`, exposing internals to clients.
- **Credential leakage risk in logs**: provider error strings can include credential-like tokens.
- **Rate limiting present** via middleware, but in-memory buckets are per-process and non-distributed.

### Changes applied
- Replaced stringified internal exception details with generic `"Internal server error"` for 500s in `api_server.py`.
- Added `redact_sensitive_text()` and used it in API-key validation failure logging.

## 2) Configuration State Invariants

### Current invariant checks
- Scoring weights sum to ~1.0.
- Mutation/confidence thresholds constrained to [0,1].

### Additional ambiguous/illegal states identified
- `TargetConfig.backend=OPENAI` while fallback can pull `ANTHROPIC_API_KEY` (compatibility mode), causing auth mismatch risk.
- `concurrent_rounds > 1` with default in-memory session state may create cross-round contention depending on orchestrator usage.
- `enable_perturbations=True` with latency perturbation introduces execution-time variance (expected but conflicts with strict determinism claims).

## 3) Determinism Integrity Audit

### Nondeterminism sources found
- Random perturbations (`random.choice`, `random.uniform`, truncation probability).
- Time-based logic (`datetime.now`) and timestamped runtime metadata.
- Async scheduling order for concurrent execution paths.

### Recommendation
- Introduce an explicit deterministic mode that disables latency/temperature jitter/truncation and enforces seed propagation end-to-end.

## 4) Concurrency & Async Safety

### Finding
- Simulated latency in perturbations was implemented with `time.sleep()` in backend execution flow, which blocks the event loop under async load.

### Change applied
- Converted latency perturbation delay to `await asyncio.sleep(...)` by making post-perturbation path async.

## 5) Load Sensitivity & Resource Hygiene

### Findings
- SDK/API clients are reused per backend instance (good).
- Rate limiting buckets are unbounded per distinct client IP and process-local (memory growth and no cross-instance coordination).
- `/auth/validate-llm-key` can still trigger provider calls; now format precheck minimizes obvious noise.

## 6) Dependency Hygiene

### Findings
- Could not run `pip-audit` in this environment (tool missing).
- `npm audit` endpoint returned 403 from registry in this environment.

### Recommendation
- Add CI job with `pip-audit` + `npm audit` in a network context with registry access.

## 7) API Contract Stability

### Reviewed
- Error/status behavior for auth and key validation routes.

### Improvements made
- Internal 500 responses now normalized to generic detail strings in `api_server.py`.

## 8) Logging Discipline Audit

### Changes applied
- Added credential redaction utility for API-key validation logs.
- Added redacted error logging for target backend execution exceptions.

## 9) Frontend State Safety

### Current state
- Stable ref capture in `NeuralBackground` effect cleanup path is implemented to avoid stale-ref cleanup bugs.
- Animation frame cancellation is implemented in `NeuralBackground` cleanup to prevent animation loops from continuing after component unmount.
- Three.js resource disposal is implemented in `NeuralBackground` cleanup (geometries, materials, renderer) to prevent GPU and memory leaks.

### Outstanding risks
- `NeuralBackground` cleanup path does **not yet** cancel outstanding animation frames, which can cause animation loops to continue after component unmount.
- `NeuralBackground` does **not yet** dispose of allocated Three.js resources (e.g., geometries, materials, textures), leading to potential GPU and memory leaks over time.
- Dashboard updates rely on WebSocket stream sequencing; additional race-condition tests are recommended for reconnect edge cases.

## 10) Architectural Drift Review

### Drift points observed
- `api_server.py` mixes transport, orchestration setup, in-memory user/config storage, and WebSocket event transport concerns in one module.

### Recommendation
- Split into `routes/*`, `services/*`, and `runtime/*` modules; retain API layer as thin transport boundary.

## Failure Injection Coverage Added

- API-key validation logs redact credential-like values when provider errors include key fragments.
- Registration path failure injection verifies no internal exception detail leakage in client 500 responses.

