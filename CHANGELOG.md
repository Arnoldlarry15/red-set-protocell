# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed (connectivity fix – 2026-03-17)
- **Production Front-end / Back-end Connectivity**: Resolved a startup crash in the
  Render-hosted backend and a misconfigured API URL in the Vercel-hosted frontend.

  **Root cause**: `render.yaml` left `RSP_ALLOWED_ORIGINS` as `sync: false` (manually
  managed), which allowed it to be accidentally set to `http://localhost:5173`. The
  production backend correctly rejects any localhost origin, so it crashed on every
  worker startup with:
  ```
  ValueError: FATAL: Production backend cannot trust localhost origin: http://localhost:5173
  Use separate backend instance for local development.
  ```
  Separately, `vercel.json` had no `VITE_API_BASE_URL` env var, so the Vercel build
  fell back to `http://localhost:8000` and the frontend could not reach the backend
  at all.

  **Changes**:
  - `render.yaml`: Replaced `sync: false` on `RSP_ALLOWED_ORIGINS` with the correct
    production value (`https://red-set-protocell.vercel.app`). The Render Blueprint now
    deploys with a valid CORS origin automatically, preventing this class of
    misconfiguration. The value can still be overridden in the Render Dashboard if
    your frontend URL differs.
  - `vercel.json`: Added `env.VITE_API_BASE_URL=https://red-set-protocell-api.onrender.com`
    so that every Vercel build bakes in the correct backend URL, enabling the frontend
    to reach the Render-deployed API.

### Added (v1.2.0)
- **Memory Leak Fix**: Bounded `strategy_performance` to prevent unbounded memory growth
  - Changed from unlimited `List[float]` to bounded `Deque[float]` with configurable max size
  - New `max_performance_history` parameter (default: 1000 scores per strategy)
  - Applied same pattern to `strategy_archetype_performance`
  - Prevents memory creep in long-running systems
  - Tests: 7 comprehensive tests for bounded performance tracking

- **Zero Fitness Score Handling**: Fixed edge case in `evolve_population` with epsilon floor
  - Adds epsilon (1e-10) to fitness weights to prevent `ValueError` when all scores are zero
  - Maintains fitness-based selection bias while handling edge cases gracefully
  - Handles negative scores robustly
  - Tests: 7 comprehensive tests for zero/negative fitness scenarios

- **SemanticIntensity Enum**: Type-safe semantic intensity control
  - Converted string-based `semantic_intensity` to `SemanticIntensity` Enum (LOW/MEDIUM/HIGH)
  - Maintains backward compatibility with string inputs ("low"/"medium"/"high")
  - Case-insensitive string conversion with fallback to MEDIUM for invalid values
  - Prevents typos and enables better IDE support
  - Tests: 6 comprehensive tests for enum and backward compatibility

### Added (v1.1.0)
- **Semantic Intensity Control**: Encoding transform now supports configurable drift control
  - Three intensity levels: low (conservative), medium (balanced), high (exploratory)
  - Low intensity uses simple, predictable transforms with minimal semantic drift
  - High intensity uses philosophical/metaphorical transforms for maximum exploration
  - UI configuration via dropdown in AttackConfig component
  - Backend API accepts `semantic_intensity` parameter in SessionConfig and ExperimentConfig
  - Default: medium (balanced semantic challenges)
  - Tests: 4 comprehensive tests covering all intensity levels

- **Early-Stage Adaptive Selector**: Handles sparse data gracefully with automatic fallback
  - Detects early-stage scenarios (< 20 samples) and uses simplified selection logic
  - Simplified uniform selection with novelty bonus during early stage
  - Automatic transition to sophisticated multi-dimensional weighting with sufficient data
  - Prevents "rocket engine on bicycle" state from causing issues
  - Tests: 3 tests for early/mature stage behavior

- **Multi-Dimensional Fitness**: Richer feedback signals beyond scalar scores
  - New `MultidimensionalFitness` class with three dimensions: effectiveness, consistency, novelty
  - Weighted aggregation with customizable weights (default: 60% effectiveness, 20% consistency, 20% novelty)
  - Full backward compatibility with scalar fitness scores
  - Prepares infrastructure for richer feedback from Spotter and EGG
  - Tests: 9 comprehensive tests including bounds checking, aggregation, and mixed types

- **Production Audit Documentation**: Comprehensive production readiness assessment (PRODUCTION_AUDIT.md)
- **Validation Scripts**: Automated production validation (validate_production.py) and cleanup audit (audit_cleanup.py)

- **Behavior-Aware Mutation System** (from previous release): Spotter now analyzes behavioral traits (verbosity, complexity, directness) in target responses and provides behavior-aware mutation guidance to the mutation engine
  - Added `_analyze_behavioral_traits()` method to Spotter to detect verbosity, complexity, and directness patterns
  - Added `_get_behavior_aware_recommendations()` to map behavioral traits to optimal mutation strategies
  - Extended mutation_guidance to include `behavioral_traits`, `strategy_biases`, and `behavior_context` fields
  - Modified `MutationEngine.mutate()` to accept and use `mutation_guidance` parameter for behavior-aware strategy selection
  - Updated `_select_strategy_adaptive()` to apply behavior biases alongside performance, novelty, and archetype biases
  - Integrated mutation_guidance flow through Sniper's evolution loop (stored in candidate feedback_history, extracted and passed to mutate)
  - Added 16 comprehensive tests for behavioral trait analysis, recommendations, and end-to-end behavior-aware evolution
  - Example: If Spotter detects "too verbose" response, it biases toward `structural_recombination` (+0.3) and away from `context_injection` (-0.2)

### Changed
- **Mutation Engine Architecture**: Addressed design tensions with code improvements
  - Encoding transforms now configurable to control semantic drift
  - Adaptive selector handles early-stage data sparsity gracefully
  - Fitness signals enhanced with multi-dimensional scoring infrastructure
  - All improvements include UI configuration, tests, and backward compatibility
  
- **Evolution Philosophy**: Moved from statistical adaptation (score-based only) to behavior-aware adaptation (score + behavioral traits)
- **Mutation Strategy Selection**: Now considers four factors: performance history, novelty bonus, archetype correlations, and behavioral traits

### Technical Details
- Behavioral trait analysis uses pattern matching and statistical measures (word count, sentence complexity, hedging detection)
- Strategy biases range from -0.5 to +0.8, applied additively to strategy weights in adaptive selection
- Backward compatible: mutation_guidance is optional, existing code continues to work unchanged
- All existing tests pass (97 tests in mutation/spotter modules)

## [1.0.0] - 2026-01-22

### Added
- Initial production-ready release
- Multi-agent AI red teaming architecture
- Dual-agent Sniper/Spotter system
- Web UI with glassmorphism design and modern React components
- Real API integrations (OpenAI, Anthropic)
- Ethical Guardrail Governor (EGG)
- 3-layer scoring taxonomy (Linguistic Safety, Security Exploitability, Cognitive Stability)
- Evolutionary attack strategies with fitness-guided selection
- Six mutation strategies (lexical, encoding, structural, role-play, context, obfuscation)
- Seven attack domains (injection, refusal erosion, jailbreak, PII extraction, policy circumvention, cognitive manipulation, context confusion)
- Comprehensive test suite (24+ test files, 282 tests)
- Docker and Docker Compose support for easy deployment
- FastAPI-based API server with production middleware
- WebSocket support for real-time attack streaming
- Time tracking analytics and cost management
- Strategy tuning and optimization
- Perturbation engine for payload generation
- Selection engine with tournament and fitness-based selection
- Model zoo support for multiple LLM providers
- Benchmarking capabilities for model comparison
- Telemetry and metrics export (JSON, CSV formats)
- Uncertainty tracking with confidence intervals
- Comprehensive CI/CD infrastructure with GitHub Actions
- Automated testing workflow on multiple platforms (Ubuntu, Windows, macOS)
- Code quality checks (flake8, black, mypy)
- Security scanning with CodeQL
- Dependency vulnerability scanning with Dependabot
- Coverage reporting with 70% minimum threshold
- Configuration files for all quality tools (.flake8, mypy.ini, pyproject.toml)
- Daily automated builds
- Quality badges in README
- **Production Deployment**: Frontend on Vercel, Backend on Render
- **Navigation Component**: Global navigation with logout functionality
- **Admin Dashboard**: User management, model comparison, infrastructure monitoring
- **Error Handling**: Comprehensive error messages and network failure detection
- **Loading States**: Visual feedback during async operations

### Features
- **Defense-Only System**: No real malware generation
- **Zero-Retention Policy**: Configurable data cleanup
- **Ethical Guardrails**: Mandatory content filtering
- **Human-in-the-Loop**: Results require validation
- **Transparency**: Open-source and auditable
- **Scalability**: Async/parallel execution support
- **Policy Locking**: Versioned attack policies and immutable experiment artifacts
- **Reproducibility**: Deterministic seeds and replay infrastructure

### Fixed
- **Frontend API Endpoints**: Corrected URL paths to match backend routes (removed /api prefix)
- **UI Connectivity**: Fixed all API calls to properly connect to backend
- **Model Comparison**: Now functional with proper error handling
- **User Management**: Add users functionality working with validation
- **Test Runs**: Session controls properly connected to backend
- **Profile Saving**: Remote config save/load functionality operational
- **Dependency Vulnerability**: Resolved lodash prototype pollution (moderate severity)
- **Error Handling**: Added comprehensive error messages for network failures
- **Loading States**: Added visual feedback during async operations
- **CORS Configuration**: Documented production settings for Vercel + Render deployment

### Documentation
- Comprehensive README with examples and live demo links
- Contributing guidelines
- Security policy
- Multiple implementation guides
- API documentation
- Deployment guides (DEPLOYMENT.md with production URLs)
- Web UI setup guide
- Quick start guide
- Production deployment checklist

### Testing
- 282/282 tests passing (100% pass rate)
- 76% code coverage (exceeds 70% target)
- Unit tests for all major components
- Integration tests
- Async test support
- Mock and real API backend tests
- Edge case coverage

### Security
- Ethical content filtering
- API key management
- Input sanitization
- Safe prompt generation
- Zero-retention mode
- CodeQL security analysis workflow
- Weekly dependency vulnerability scans
- Automated dependency update via Dependabot

[1.0.0]: https://github.com/Arnoldlarry15/red-set-protocell/releases/tag/v1.0.0
