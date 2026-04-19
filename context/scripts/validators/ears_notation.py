#!/usr/bin/env python3
"""Validate EARS notation in requirements files."""

import sys
import re
from pathlib import Path


# EARS patterns from EARS-notation-requirements.mdc
EARS_PATTERNS = {
    'ubiquitous': r'THE\s+\S+\s+SHALL\s+',
    'event': r'WHEN\s+.+?,\s+THE\s+\S+\s+SHALL\s+',
    'state': r'WHILE\s+.+?,\s+THE\s+\S+\s+SHALL\s+',
    'optional': r'IF\s+.+?,\s+THE\s+\S+\s+SHALL\s+',
    'forbidden': r'THE\s+\S+\s+SHALL\s+NOT\s+',
    'complex': r'WHEN\s+.+?,\s+IF\s+.+?,\s+THE\s+\S+\s+SHALL\s+'
}


def is_ears_requirement(line: str) -> bool:
    """Check if line matches any EARS pattern.

    Args:
        line: The line to check

    Returns:
        True if line matches EARS notation
    """
    line = line.strip()
    # EARS notation requires uppercase THE and SHALL
    # But we'll be case-insensitive in matching to be helpful
    for pattern in EARS_PATTERNS.values():
        if re.search(pattern, line, re.IGNORECASE):
            return True
    return False


def validate_requirements_file(file_path: Path) -> list[str]:
    """Validate requirements file for EARS notation.

    Args:
        file_path: Path to requirements file

    Returns:
        List of error messages
    """
    errors = []
    content = file_path.read_text()
    lines = content.split('\n')

    in_code_block = False

    for i, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        # Skip code blocks
        if in_code_block:
            continue

        line = line.strip()

        # Skip empty lines, headers, table separators, and list markers
        if not line or line.startswith('#') or line.startswith('|') or re.match(r'^[-*]\s', line):
            continue

        # If line looks like a requirement (mentions "shall"), validate EARS
        if 'shall' in line.lower():
            if not is_ears_requirement(line):
                errors.append(
                    f"Line {i}: Requirement doesn't match EARS notation\n"
                    f"  {line}\n"
                    f"  Expected patterns:\n"
                    f"    - THE [system] SHALL [action]\n"
                    f"    - WHEN [trigger], THE [system] SHALL [action]\n"
                    f"    - WHILE [state], THE [system] SHALL [action]\n"
                    f"    - IF [condition], THE [system] SHALL [action]\n"
                    f"    - THE [system] SHALL NOT [action]\n"
                    f"    - WHEN [trigger], IF [condition], THE [system] SHALL [action]"
                )

    return errors


def main():
    """Validate EARS notation in requirements files."""
    if len(sys.argv) < 2:
        print("Usage: ears_notation.py <requirements-file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    errors = validate_requirements_file(file_path)

    if errors:
        print(f"❌ EARS notation violations in {file_path.name}:\n")
        for error in errors:
            print(error)
            print()
        sys.exit(1)
    else:
        print(f"✅ {file_path.name} follows EARS notation")
        sys.exit(0)


if __name__ == '__main__':
    main()
