#!/usr/bin/env python3
"""Validate agent metrics logging format."""

import sys
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = ['ts', 'task', 'agent', 'event', 'tokens']
VALID_EVENTS = ['start', 'handoff', 'escalate', 'complete', 'blocked']
VALID_TOKEN_SOURCES = ['api_response', 'estimated', 'unavailable']


def validate_metrics_entry(entry: dict[str, Any], line_num: int) -> list[str]:
    """Validate a single metrics log entry.

    Args:
        entry: The parsed JSON entry
        line_num: Line number in file

    Returns:
        List of validation errors
    """
    errors = []

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"Line {line_num}: Missing required field '{field}'")

    if errors:
        return errors

    # Validate timestamp format (ISO 8601)
    ts = entry.get('ts', '')
    if not ts.endswith('Z') and '+' not in ts and not ts.endswith(']'):
        errors.append(
            f"Line {line_num}: Invalid timestamp format '{ts}', expected ISO 8601 (e.g., 2025-01-28T09:00:00Z)"
        )

    # Validate event
    event = entry.get('event', '')
    if event not in VALID_EVENTS:
        errors.append(
            f"Line {line_num}: Invalid event '{event}', must be one of: {', '.join(VALID_EVENTS)}"
        )

    # Validate tokens
    tokens = entry.get('tokens', {})
    if not isinstance(tokens, dict):
        errors.append(f"Line {line_num}: 'tokens' must be an object")
    else:
        if 'in' not in tokens or 'out' not in tokens:
            errors.append(f"Line {line_num}: 'tokens' must have 'in' and 'out' fields")

        if 'source' not in tokens:
            errors.append(f"Line {line_num}: 'tokens' must have 'source' field")
        elif tokens['source'] not in VALID_TOKEN_SOURCES:
            errors.append(
                f"Line {line_num}: Invalid token source '{tokens['source']}', "
                f"must be one of: {', '.join(VALID_TOKEN_SOURCES)}"
            )

        # Validate token values are numbers
        for key in ['in', 'out']:
            if key in tokens and not isinstance(tokens[key], (int, float)):
                errors.append(f"Line {line_num}: tokens.{key} must be a number")

    # Validate 'to' field for handoff/escalate
    if event in ['handoff', 'escalate']:
        if 'to' not in entry:
            errors.append(f"Line {line_num}: '{event}' event requires 'to' field")

    return errors


def validate_metrics_file(file_path: Path) -> list[str]:
    """Validate metrics log file.

    Args:
        file_path: Path to metrics JSONL file

    Returns:
        List of validation errors
    """
    all_errors = []

    try:
        content = file_path.read_text()
        lines = content.strip().split('\n')

        if not content.strip():
            # Empty file is valid
            return []

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                all_errors.append(f"Line {line_num}: Invalid JSON - {e}")
                continue

            errors = validate_metrics_entry(entry, line_num)
            all_errors.extend(errors)

    except Exception as e:
        all_errors.append(f"Error reading file: {e}")

    return all_errors


def main():
    """Validate metrics log file."""
    if len(sys.argv) < 2:
        print("Usage: metrics_logging.py <metrics-file.jsonl>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Only validate .jsonl files in metrics/ directory
    if file_path.suffix != '.jsonl' or 'metrics' not in str(file_path):
        sys.exit(0)

    errors = validate_metrics_file(file_path)

    if errors:
        print(f"❌ Metrics logging violations in {file_path.name}:\n")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print(f"✅ {file_path.name} follows metrics logging format")
        sys.exit(0)


if __name__ == '__main__':
    main()
