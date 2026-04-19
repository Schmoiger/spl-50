"""Tests for validation scripts."""

import pytest
from pathlib import Path
import sys

# Add parent directory to path so we can import validators
sys.path.insert(0, str(Path(__file__).parent.parent / 'validators'))

from conventional_commits import validate_commit_message
from ears_notation import validate_requirements_file, is_ears_requirement
from british_english import validate_british_english
from metrics_logging import validate_metrics_file, validate_metrics_entry


class TestConventionalCommits:
    """Tests for conventional commit validator."""

    def test_valid_commit(self, valid_commit):
        """Test that valid commit passes validation."""
        msg = valid_commit.read_text()
        is_valid, error = validate_commit_message(msg)
        assert is_valid, f"Expected valid commit to pass: {error}"
        assert error == ""

    def test_invalid_no_scope(self, invalid_commit_no_scope):
        """Test that commit without scope fails validation."""
        msg = invalid_commit_no_scope.read_text()
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "Invalid subject line" in error

    def test_invalid_too_long(self, invalid_commit_too_long):
        """Test that commit over 72 chars fails validation."""
        msg = invalid_commit_too_long.read_text()
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "too long" in error

    def test_invalid_past_tense(self, invalid_commit_past_tense):
        """Test that past tense description fails validation."""
        msg = invalid_commit_past_tense.read_text()
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "imperative mood" in error

    def test_valid_with_agent_session(self, valid_commit_with_agent_session):
        """Test that agent session metadata is validated."""
        msg = valid_commit_with_agent_session.read_text()
        is_valid, error = validate_commit_message(msg)
        assert is_valid, f"Expected valid agent commit to pass: {error}"

    def test_merge_commit_allowed(self, merge_commit):
        """Test that merge commits don't require validation."""
        # Note: Main script skips merge commits, so we test the detection
        msg = merge_commit.read_text()
        assert msg.startswith('Merge ')

    def test_empty_commit_fails(self):
        """Test that empty commit message fails."""
        is_valid, error = validate_commit_message("")
        assert not is_valid
        # Empty string still fails validation, error message indicates invalid format
        assert "Invalid subject line" in error or "Empty" in error

    def test_invalid_type(self):
        """Test that invalid commit type fails."""
        msg = "invalid(scope): description"
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "Invalid subject line" in error

    def test_invalid_scope_uppercase(self):
        """Test that uppercase scope fails."""
        msg = "feat(DataService): add feature"
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "Invalid subject line" in error

    def test_coauthor_format(self):
        """Test Co-Authored-By format validation."""
        msg = """feat(test): valid subject

Co-Authored-By: Invalid Format"""
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "Co-Authored-By format" in error

    def test_agent_session_requires_coauthor(self):
        """Test that Agent-Session requires Co-Authored-By."""
        msg = """feat(test): valid subject

Agent-Session: tool=cursor model=sonnet agents=python-coder tokens=1K/2K duration=5m"""
        is_valid, error = validate_commit_message(msg)
        assert not is_valid
        assert "require Co-Authored-By" in error


class TestEARSNotation:
    """Tests for EARS notation validator."""

    def test_valid_requirements(self, valid_requirements):
        """Test that valid EARS requirements pass."""
        errors = validate_requirements_file(valid_requirements)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"

    def test_invalid_requirements(self, invalid_requirements):
        """Test that invalid requirements fail."""
        errors = validate_requirements_file(invalid_requirements)
        assert len(errors) > 0
        assert any("EARS notation" in error for error in errors)

    def test_ubiquitous_pattern(self):
        """Test ubiquitous EARS pattern recognition."""
        assert is_ears_requirement("THE system SHALL fetch data")
        assert is_ears_requirement("the system shall fetch data")  # case insensitive

    def test_event_pattern(self):
        """Test event-driven EARS pattern."""
        assert is_ears_requirement("WHEN user clicks button, THE system SHALL save data")

    def test_state_pattern(self):
        """Test state-driven EARS pattern."""
        assert is_ears_requirement("WHILE offline, THE system SHALL use cached data")

    def test_optional_pattern(self):
        """Test optional EARS pattern."""
        assert is_ears_requirement("IF user is admin, THE system SHALL show controls")

    def test_forbidden_pattern(self):
        """Test forbidden EARS pattern."""
        assert is_ears_requirement("THE system SHALL NOT store passwords in plain text")

    def test_complex_pattern(self):
        """Test complex EARS pattern."""
        assert is_ears_requirement(
            "WHEN user requests data, IF cache is stale, THE system SHALL fetch from API"
        )

    def test_non_ears_requirement(self):
        """Test that non-EARS text is not matched."""
        assert not is_ears_requirement("The system should do something")
        assert not is_ears_requirement("Users must be able to view data")

    def test_code_blocks_ignored(self, tmp_path):
        """Test that code blocks are ignored."""
        req_file = tmp_path / "test.md"
        req_file.write_text("""# Requirements

```python
# This shall not be validated
system.shall_do_something()
```

THE system SHALL validate requirements.
""")
        errors = validate_requirements_file(req_file)
        assert len(errors) == 0


class TestBritishEnglish:
    """Tests for British English validator."""

    def test_valid_british_english(self, valid_british_english):
        """Test that British English passes validation."""
        violations = validate_british_english(valid_british_english)
        assert len(violations) == 0, f"Expected no violations, got: {violations}"

    def test_invalid_american_english(self, invalid_british_english):
        """Test that American English fails validation."""
        violations = validate_british_english(invalid_british_english)
        assert len(violations) > 0
        # Should catch: color, behavior, organize, center, license
        assert len(violations) >= 4

    def test_color_vs_colour(self):
        """Test color/colour detection."""
        # Create temp file with American spelling
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("The color is red\n")
            f.flush()
            violations = validate_british_english(Path(f.name))
            assert len(violations) > 0
            assert any("colour" in v for v in violations)
            Path(f.name).unlink()

    def test_behavior_vs_behaviour(self):
        """Test behavior/behaviour detection."""
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("The behavior is normal\n")
            f.flush()
            violations = validate_british_english(Path(f.name))
            assert len(violations) > 0
            assert any("behaviour" in v for v in violations)
            Path(f.name).unlink()

    def test_organize_vs_organise(self):
        """Test organize/organise detection."""
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("Users can organize their files\n")
            f.flush()
            violations = validate_british_english(Path(f.name))
            assert len(violations) > 0
            assert any("organise" in v for v in violations)
            Path(f.name).unlink()

    def test_code_blocks_ignored(self, tmp_path):
        """Test that code blocks are ignored."""
        test_file = tmp_path / "test.md"
        test_file.write_text("""# Documentation

```python
# color = "red"  # This should be ignored
print("color")
```

The colour is red.
""")
        violations = validate_british_english(test_file)
        assert len(violations) == 0

    def test_inline_code_ignored(self, tmp_path):
        """Test that inline code is ignored."""
        test_file = tmp_path / "test.md"
        test_file.write_text("Use the `color` parameter.\n\nThe colour is red.")
        violations = validate_british_english(test_file)
        # Should only catch "color" if not in inline code
        # Current implementation checks for backticks in line
        assert len(violations) == 0  # Line has backticks, so skipped


class TestMetricsLogging:
    """Tests for metrics logging validator."""

    def test_valid_metrics(self, valid_metrics):
        """Test that valid metrics pass validation."""
        errors = validate_metrics_file(valid_metrics)
        assert len(errors) == 0, f"Expected no errors, got: {errors}"

    def test_invalid_metrics(self, invalid_metrics):
        """Test that invalid metrics fail validation."""
        errors = validate_metrics_file(invalid_metrics)
        assert len(errors) > 0

    def test_missing_required_field(self):
        """Test that missing required field is caught."""
        entry = {
            "ts": "2025-01-28T09:00:00Z",
            "task": "TEST-001",
            # Missing 'agent', 'event', 'tokens'
        }
        errors = validate_metrics_entry(entry, 1)
        assert len(errors) >= 3  # Should catch all missing fields
        assert any("agent" in e for e in errors)
        assert any("event" in e for e in errors)
        assert any("tokens" in e for e in errors)

    def test_invalid_timestamp(self):
        """Test that invalid timestamp format is caught."""
        entry = {
            "ts": "2025-01-28",  # Missing time and timezone
            "task": "TEST-001",
            "agent": "test-agent",
            "event": "start",
            "tokens": {"in": 100, "out": 50, "source": "api_response"}
        }
        errors = validate_metrics_entry(entry, 1)
        assert len(errors) > 0
        assert any("timestamp" in e.lower() for e in errors)

    def test_invalid_event(self):
        """Test that invalid event type is caught."""
        entry = {
            "ts": "2025-01-28T09:00:00Z",
            "task": "TEST-001",
            "agent": "test-agent",
            "event": "invalid-event",
            "tokens": {"in": 100, "out": 50, "source": "api_response"}
        }
        errors = validate_metrics_entry(entry, 1)
        assert len(errors) > 0
        assert any("event" in e.lower() for e in errors)

    def test_invalid_token_source(self):
        """Test that invalid token source is caught."""
        entry = {
            "ts": "2025-01-28T09:00:00Z",
            "task": "TEST-001",
            "agent": "test-agent",
            "event": "start",
            "tokens": {"in": 100, "out": 50, "source": "invalid"}
        }
        errors = validate_metrics_entry(entry, 1)
        assert len(errors) > 0
        assert any("source" in e.lower() for e in errors)

    def test_missing_tokens_fields(self):
        """Test that missing token fields are caught."""
        entry = {
            "ts": "2025-01-28T09:00:00Z",
            "task": "TEST-001",
            "agent": "test-agent",
            "event": "start",
            "tokens": {"source": "api_response"}  # Missing 'in' and 'out'
        }
        errors = validate_metrics_entry(entry, 1)
        assert len(errors) > 0
        assert any("'in' and 'out'" in e for e in errors)

    def test_handoff_requires_to_field(self):
        """Test that handoff event requires 'to' field."""
        entry = {
            "ts": "2025-01-28T09:00:00Z",
            "task": "TEST-001",
            "agent": "test-agent",
            "event": "handoff",
            # Missing 'to' field
            "tokens": {"in": 100, "out": 50, "source": "api_response"}
        }
        errors = validate_metrics_entry(entry, 1)
        assert len(errors) > 0
        assert any("'to' field" in e for e in errors)

    def test_empty_file_valid(self, tmp_path):
        """Test that empty metrics file is valid."""
        empty_file = tmp_path / "metrics" / "empty.jsonl"
        empty_file.parent.mkdir(exist_ok=True)
        empty_file.write_text("")
        errors = validate_metrics_file(empty_file)
        assert len(errors) == 0

    def test_invalid_json(self, tmp_path):
        """Test that invalid JSON is caught."""
        bad_file = tmp_path / "metrics" / "bad.jsonl"
        bad_file.parent.mkdir(exist_ok=True)
        bad_file.write_text("not valid json\n")
        errors = validate_metrics_file(bad_file)
        assert len(errors) > 0
        assert any("Invalid JSON" in e for e in errors)
