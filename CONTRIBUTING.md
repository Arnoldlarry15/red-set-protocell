# Contributing to Red Set ProtoCell

Thank you for your interest in contributing to Red Set ProtoCell (RSP)! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Ethical Guidelines](#ethical-guidelines)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors. We pledge to:

- Be respectful and considerate of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community and project
- Show empathy towards other community members

### Unacceptable Behavior

- Use of sexualized language or imagery
- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Python 3.8+** installed
2. **Git** configured with your GitHub account
3. **Virtual environment** tools (venv or virtualenv)
4. Basic understanding of:
   - Python programming
   - Async/await patterns
   - Git workflows
   - AI safety concepts

### Setting Up Your Development Environment

```bash
# 1. Fork the repository on GitHub
# 2. Clone your fork
git clone https://github.com/YOUR_USERNAME/red-set-protocell.git
cd red-set-protocell

# 3. Add upstream remote
git remote add upstream https://github.com/Arnoldlarry15/red-set-protocell.git

# 4. Create virtual environment
cd rsp-core/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Install development tools
pip install black flake8 mypy pytest pytest-asyncio pytest-cov

# 7. Verify installation
pytest tests/ -v
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

#### 🐛 Bug Reports

Found a bug? Please open an issue with:

- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version)
- Relevant log output
- Screenshots (if applicable)

**Template:**
```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
1. Run command '...'
2. With configuration '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.10.5]
- RSP Version: [e.g., 1.0.0]

**Additional Context**
Any other context about the problem.
```

#### 🆕 Feature Requests

Have an idea? Open an issue with:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if any)
- Potential challenges or concerns

#### 💻 Code Contributions

Contribute code for:

- Bug fixes
- New features
- Performance improvements
- Code refactoring
- Test coverage improvements

#### 📚 Documentation

Improve documentation:

- Fix typos or unclear explanations
- Add examples or tutorials
- Translate documentation
- Improve API documentation
- Add diagrams or visualizations

## Development Workflow

### Branch Strategy

```
main                    # Stable releases
├── develop            # Integration branch
│   ├── feature/xxx    # New features
│   ├── bugfix/xxx     # Bug fixes
│   └── docs/xxx       # Documentation
```

### Creating a Branch

```bash
# Update your main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description

# Or for documentation
git checkout -b docs/what-you-are-documenting
```

### Making Changes

1. **Make your changes** in logical, focused commits
2. **Follow coding standards** (see below)
3. **Write tests** for new functionality
4. **Update documentation** as needed
5. **Run tests** to ensure nothing breaks

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type check
mypy app/
```

### Committing Changes

Use clear, descriptive commit messages:

```bash
# Good commit messages
git commit -m "Add support for Claude 3.5 Sonnet model"
git commit -m "Fix EGG false positive on educational content"
git commit -m "Update README with Docker deployment instructions"

# Bad commit messages
git commit -m "Fix bug"
git commit -m "Update stuff"
git commit -m "WIP"
```

**Commit Message Format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**

```
feat: Add support for Gemini API backend

- Implement GeminiBackend class in target.py
- Add API key validation
- Update configuration to include Gemini option
- Add integration tests

Closes #123
```

## Extension Points & Templates

### Using Contributor Templates

RSP provides **ready-to-use templates** to guide you in extending the system safely and correctly. These templates include safety warnings, integration steps, and example code.

**📁 Location**: `rsp-core/backend/templates/`

**Available Templates**:

1. **new_agent_template.py**
   - For: Creating new agents (e.g., custom evaluators)
   - Includes: Stateless design patterns, integration checklist
   
2. **new_engine_template.py**
   - For: Creating processing engines (e.g., custom selection)
   - Includes: Pure function patterns, batch processing examples
   
3. **new_target_backend_template.py**
   - For: Adding LLM provider support (e.g., Gemini, Cohere)
   - Includes: API integration patterns, security guidelines
   
4. **new_mutation_strategy_template.py**
   - For: Adding adversarial transformation techniques
   - Includes: Safety constraints, testing examples

**Quick Start**:

```bash
cd rsp-core/backend

# Copy template
cp templates/new_agent_template.py app/agents/my_agent.py

# Follow TODO comments in the file
# Create tests
touch tests/test_my_agent.py

# See template README for detailed guide
cat templates/README.md
```

**Why use templates?**
- ✅ Avoid common mistakes (stateful agents, EGG bypass, etc.)
- ✅ Follow architectural patterns automatically
- ✅ Include safety guidelines and warnings
- ✅ Get integration steps and test examples
- ✅ Maintain consistency across codebase

**Detailed documentation**: See `rsp-core/backend/templates/README.md`

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length**: 88 characters (Black default)
- **Indentation**: 4 spaces
- **Quotes**: Double quotes for strings (Black default)
- **Imports**: Organized in groups (stdlib, third-party, local)

### Code Formatting

Use **Black** for automatic formatting:

```bash
# Format all files
black app/ tests/

# Check without modifying
black --check app/ tests/
```

### Linting

Use **Flake8** for linting:

```bash
# Lint all files
flake8 app/ tests/

# Configuration (.flake8):
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv,.pytest_cache
```

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Dict, Optional

def process_prompt(
    prompt: str,
    max_length: int = 100,
    metadata: Optional[Dict[str, str]] = None
) -> List[str]:
    """Process a prompt and return results."""
    # Implementation
    return results
```

### Docstrings

Use **Google-style** docstrings:

```python
def evaluate_response(
    response: str,
    l1_score: float,
    l2_score: float,
    l3_score: float
) -> EvaluationResult:
    """
    Evaluate a response using 3-layer scoring.
    
    Args:
        response: The LLM response to evaluate
        l1_score: Linguistic safety score (0.0-1.0)
        l2_score: Security exploitability score (0.0-1.0)
        l3_score: Cognitive stability score (0.0-1.0)
    
    Returns:
        Complete evaluation result with global score
    
    Raises:
        ValueError: If scores are out of range
    
    Examples:
        >>> result = evaluate_response("Hello", 0.1, 0.2, 0.1)
        >>> print(result.global_score)
        0.17
    """
    # Implementation
```

### Naming Conventions

```python
# Classes: PascalCase
class MutationEngine:
    pass

# Functions/methods: snake_case
def compute_global_score():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_ROUNDS = 100
DEFAULT_MODEL = "gpt-3.5-turbo"

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

## Testing Requirements

### Test Coverage Goals

- **Unit tests**: >90% coverage for core modules
- **Integration tests**: Cover all API integrations
- **Edge cases**: Test boundary conditions and error cases

### Writing Tests

#### Unit Test Example

```python
# tests/test_new_feature.py
import pytest
from app.core.new_feature import NewFeature

class TestNewFeature:
    """Test suite for NewFeature class."""
    
    def test_basic_functionality(self):
        """Test basic operation."""
        feature = NewFeature()
        result = feature.process("input")
        assert result == "expected"
    
    def test_edge_case_empty_input(self):
        """Test handling of empty input."""
        feature = NewFeature()
        with pytest.raises(ValueError):
            feature.process("")
    
    @pytest.mark.asyncio
    async def test_async_operation(self):
        """Test async functionality."""
        feature = NewFeature()
        result = await feature.async_process("input")
        assert isinstance(result, str)
```

#### Integration Test Example

```python
# tests/test_integration.py
import pytest
import os

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
@pytest.mark.asyncio
async def test_end_to_end_workflow():
    """Test complete workflow with real API."""
    # Setup
    config = get_test_config()
    orchestrator = setup_system(config)
    
    # Execute
    stats = await orchestrator.run_session()
    
    # Verify
    assert stats['session']['total_rounds'] > 0
    assert 0.0 <= stats['scores']['average_global_score'] <= 1.0
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_egg.py -v

# Run tests matching pattern
pytest tests/ -k "test_mutation" -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html --cov-report=term

# Skip integration tests (no API calls)
pytest tests/ -v -m "not integration"
```

## Documentation

### Types of Documentation

1. **Code Documentation**: Docstrings, comments
2. **README**: Project overview, quick start
3. **Technical Docs**: Architecture, API reference
4. **Tutorials**: Step-by-step guides
5. **Examples**: Sample code and use cases

### Documentation Standards

- **Clarity**: Write for your target audience
- **Accuracy**: Keep docs in sync with code
- **Completeness**: Cover all public APIs
- **Examples**: Provide practical examples
- **Formatting**: Use proper Markdown syntax

### Updating Documentation

When changing code, update:

1. **Docstrings** in affected modules
2. **README.md** if user-facing changes
3. **IMPLEMENTATION.md** if architecture changes
4. **CONTRIBUTING.md** if process changes
5. **Examples** in docs/ directory

## Pull Request Process

### Before Submitting

Ensure your PR:

- [ ] Follows coding standards
- [ ] Includes tests for new functionality
- [ ] All tests pass locally
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts with main
- [ ] Ethical guidelines are followed

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a Pull Request** on GitHub

3. **Fill out the PR template**:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests pass locally

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Ethical guidelines followed

## Related Issues
Closes #123
Relates to #456
```

4. **Wait for review** from maintainers

### Code Review Process

Reviewers will check:

- Code quality and style
- Test coverage
- Documentation completeness
- Security implications
- Ethical compliance
- Performance impact

### Addressing Review Feedback

```bash
# Make requested changes
git add <files>
git commit -m "Address review feedback: <description>"
git push origin feature/your-feature-name

# If major changes needed, consider rebasing
git fetch upstream
git rebase upstream/main
git push origin feature/your-feature-name --force
```

### Merging

Once approved:

1. Maintainer will merge your PR
2. Your branch will be deleted (optional)
3. You'll be added to contributors list

## Ethical Guidelines

### Core Principles

All contributions must adhere to:

1. **Defense-Only**: No offensive capabilities
2. **No Real Harm**: No real exploits or malware
3. **Privacy-Preserving**: Respect user privacy
4. **Transparent**: Open and auditable
5. **Responsible**: Consider broader implications

### Prohibited Contributions

❌ **DO NOT** contribute:

- Real exploit code or payloads
- Real malware generation capabilities
- Mechanisms to bypass EGG
- Tools for production system attacks
- Privacy-violating features
- Unethical attack vectors

### Ethical Review

Significant contributions undergo ethical review:

1. **Technical Review**: Code quality and functionality
2. **Ethical Review**: Alignment with principles
3. **Security Review**: No introduction of vulnerabilities

### Questions?

If unsure about ethical implications:

1. Open a discussion issue
2. Ask maintainers for guidance
3. Err on the side of caution

## Recognition

Contributors are recognized through:

- **GitHub Contributors Page**: Automatic listing
- **Release Notes**: Mentioned in version releases
- **CHANGELOG**: Credited for significant changes
- **Academic Citations**: For research contributions

## Getting Help

### Resources

- **Documentation**: Read README and docs/
- **Issues**: Search existing issues
- **Discussions**: Ask questions in GitHub Discussions
- **Examples**: Check examples/ directory

### Contact

- **GitHub Issues**: Technical questions
- **GitHub Discussions**: General questions
- **Email**: For private concerns

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Red Set ProtoCell! Your efforts help make AI systems safer for everyone. 🙏
