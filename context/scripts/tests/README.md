# Context Scripts Test Suite

Comprehensive tests for validation and generation scripts in `context/scripts/`.

## Test Coverage

### Validators (38 tests)

**conventional_commits.py** (11 tests)
- Valid commit format
- Invalid formats: no scope, too long, past tense
- Agent session metadata validation
- Co-Authored-By format
- Merge commit handling

**ears_notation.py** (10 tests)
- All EARS patterns: ubiquitous, event, state, optional, forbidden, complex
- Valid/invalid requirements files
- Code block exclusion
- Pattern recognition

**british_english.py** (7 tests)
- Valid British English
- American spelling detection: color, behavior, organize, center, license
- Code block and inline code exclusion

**metrics_logging.py** (10 tests)
- Valid JSONL format
- Required fields validation
- Timestamp, event, token source validation
- Handoff/escalate event requirements
- Empty files and invalid JSON handling

### Agent Validator (12 tests)

**validate_agent_definitions.py**
- YAML frontmatter validation
- Required fields: name, model, allowed_tools
- Hardcoded path detection
- Relative path flagging
- Critical reminders attribution
- {project-root} placeholder support
- Referenced standards/rules existence checks

### Generator (22 tests)

**generate_claude_md.py**
- Workflow loading and parsing
- Agent definition loading
- Description extraction
- Mermaid diagram generation with dependencies and gates
- Phase details with outputs and validation
- Agent reference by category
- Quality gates with criteria
- Workflow rules and warnings
- Complete CLAUDE.md structure
- Portable path generation

## Running Tests

```bash
# All tests
uv run pytest context/scripts/tests/ -v

# Specific test file
uv run pytest context/scripts/tests/test_validators.py -v

# With coverage
uv run pytest context/scripts/tests/ --cov=context/scripts --cov-report=html

# Single test
uv run pytest context/scripts/tests/test_validators.py::TestConventionalCommits::test_valid_commit -v
```

## Test Fixtures

Located in `fixtures/`:
- Commit messages (valid/invalid variants)
- Requirements files (valid/invalid EARS notation)
- British English samples
- Metrics JSONL files
- Workflow YAML
- Agent definitions (valid/invalid variants)

## Dependencies

- pytest >= 7.4.0
- pytest-cov >= 4.1.0 (optional, for coverage reports)
- pyyaml >= 6.0

Installed via root `pyproject.toml` dev dependencies.

## Test Organisation

```
tests/
├── README.md           # This file
├── conftest.py         # Pytest configuration and fixtures
├── test_validators.py  # Tests for all 4 validators
├── test_agent_validator.py  # Tests for agent definition validator
├── test_generator.py   # Tests for CLAUDE.md generator
└── fixtures/           # Test data files
```

## Adding New Tests

1. Create fixture files in `fixtures/` if needed
2. Add fixture functions to `conftest.py`
3. Write test functions following existing patterns
4. Run tests to verify: `uv run pytest context/scripts/tests/ -v`

## Coverage Goals

- Validators: 100% (critical for enforcement)
- Generator: 90%+ (comprehensive but allows some edge cases)
- Agent validator: 100% (ensures portable agent definitions)
