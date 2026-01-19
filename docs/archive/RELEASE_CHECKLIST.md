# Release Checklist for v1.0.0

This document outlines the complete checklist for releasing a new version of Red Set ProtoCell.

## Pre-Release Checklist

### 1. Code Quality & Testing
- [ ] All CI/CD workflows pass (tests, linting, type checking)
- [ ] Test coverage is ≥80% on core backend logic
- [ ] All tests pass on supported platforms (Ubuntu, Windows, macOS)
- [ ] All tests pass on supported Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
- [ ] No known critical bugs
- [ ] Integration tests pass with real API backends (OpenAI, Anthropic)
- [ ] Web UI functional tests pass
- [ ] Docker builds complete successfully

### 2. Security
- [ ] CodeQL security scan passes with no high/critical issues
- [ ] Dependency vulnerability scan complete
- [ ] No known security vulnerabilities in dependencies
- [ ] All Dependabot alerts resolved
- [ ] Security policy (SECURITY.md) is up to date
- [ ] Ethical guardrails (EGG) tested and verified
- [ ] API key handling reviewed

### 3. Documentation
- [ ] README.md is up to date with latest features
- [ ] CHANGELOG.md is updated with all changes
- [ ] All badges in README are working
- [ ] Installation instructions verified
- [ ] API documentation is current
- [ ] Contributing guidelines (CONTRIBUTING.md) reviewed
- [ ] Security disclosure process documented
- [ ] Deployment guides verified
- [ ] Quick start guide tested

### 4. Version Management
- [ ] Version number updated in pyproject.toml
- [ ] Version follows semantic versioning (MAJOR.MINOR.PATCH)
- [ ] Git tag created for release
- [ ] Release notes drafted
- [ ] Breaking changes documented (if any)
- [ ] Migration guide created (if needed)

### 5. Dependencies
- [ ] All dependencies up to date (or pinned versions documented)
- [ ] requirements.txt reviewed and verified
- [ ] No deprecated dependencies
- [ ] License compatibility verified
- [ ] Dependency audit complete

### 6. Build & Distribution
- [ ] Python wheel builds successfully
- [ ] Package can be installed via pip
- [ ] Docker image builds and runs
- [ ] Docker image pushed to registry (if applicable)
- [ ] All examples run successfully
- [ ] Demo scripts verified

## Release Process

### Step 1: Update Version
```bash
# Update version in pyproject.toml
version = "1.0.0"

# Commit version bump
git add rsp-core/backend/pyproject.toml
git commit -m "chore: bump version to 1.0.0"
```

### Step 2: Update CHANGELOG
```bash
# Update CHANGELOG.md
# - Move [Unreleased] changes to [1.0.0]
# - Add release date
# - Update version links at bottom

git add CHANGELOG.md
git commit -m "docs: update CHANGELOG for v1.0.0"
```

### Step 3: Create Git Tag
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
git push origin main
```

### Step 4: Create GitHub Release
1. Go to GitHub repository
2. Click "Releases" → "Create a new release"
3. Select tag v1.0.0
4. Title: "Red Set ProtoCell v1.0.0"
5. Copy release notes from CHANGELOG
6. Upload artifacts (if any)
7. Mark as "Latest release"
8. Publish release

### Step 5: Verify Installation
```bash
# Test installation from source
pip install git+https://github.com/Arnoldlarry15/red-set-protocell.git@v1.0.0

# Verify version
python -c "import app; print(app.__version__)"

# Run smoke test
cd rsp-core/backend
python -m pytest tests/test_config.py -v
```

### Step 6: Post-Release Tasks
- [ ] Verify GitHub release is published
- [ ] Update documentation website (if applicable)
- [ ] Announce release (blog, social media, mailing list)
- [ ] Close milestone (if applicable)
- [ ] Update project board
- [ ] Monitor for issues

## Hotfix Process

For critical bugs that require immediate patching:

1. Create hotfix branch from main: `git checkout -b hotfix/v1.0.1 v1.0.0`
2. Fix the bug
3. Update version to 1.0.1
4. Update CHANGELOG with [1.0.1] section
5. Create PR and merge after review
6. Follow release process above with v1.0.1

## Semantic Versioning Guidelines

Red Set ProtoCell follows [Semantic Versioning 2.0.0](https://semver.org/):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backwards compatible
- **PATCH** version (0.0.X): Backwards compatible bug fixes

### Examples:
- `1.0.0` → `2.0.0`: Breaking API changes (e.g., agent interface changed)
- `1.0.0` → `1.1.0`: New features (e.g., new mutation strategy added)
- `1.0.0` → `1.0.1`: Bug fixes (e.g., scoring calculation corrected)

## Upgrade Policy

### Supported Versions
- Latest major version: Full support (security + features)
- Previous major version: Security updates only (6 months)
- Older versions: No support (upgrade recommended)

### Breaking Changes
- Must be documented in CHANGELOG
- Migration guide required
- Deprecation warnings in previous minor version (if possible)
- Minimum 1 minor version notice before removal

## Deprecation Policy

When deprecating features:

1. Add deprecation warning in current release
2. Document in CHANGELOG and README
3. Provide alternative/migration path
4. Remove in next MAJOR version

### Deprecation Warning Example:
```python
import warnings

def deprecated_function():
    warnings.warn(
        "deprecated_function() is deprecated and will be removed in v2.0.0. "
        "Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... implementation
```

## Rollback Procedure

If critical issues are discovered post-release:

1. Document the issue
2. Create hotfix or revert problematic changes
3. Release patch version immediately
4. Update CHANGELOG with fix details
5. Notify users via GitHub release notes

## Communication Checklist

- [ ] Release announcement prepared
- [ ] Known issues documented
- [ ] Breaking changes highlighted
- [ ] Migration guide available (if needed)
- [ ] Update roadmap for next version

## Notes

- **Test Thoroughly**: Release only when all quality gates pass
- **Communicate Early**: Announce breaking changes in advance
- **Document Everything**: Users rely on clear documentation
- **Respect Semver**: Proper versioning builds trust
- **Support Users**: Be responsive to issues post-release
