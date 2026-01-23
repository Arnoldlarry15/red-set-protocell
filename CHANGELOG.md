# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
