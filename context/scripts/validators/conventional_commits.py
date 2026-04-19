#!/usr/bin/env python3
"""Validate conventional commit message format."""

import sys
import re
from pathlib import Path


def validate_commit_message(msg: str) -> tuple[bool, str]:
    """Validate commit message against conventional commits format.

    Args:
        msg: The commit message to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    lines = msg.strip().split('\n')

    if not lines:
        return False, "Empty commit message"

    # Check subject line format: type(scope): description
    subject = lines[0]

    # Valid types from conventional-commits.mdc
    valid_types = r'(feat|fix|test|refactor|docs|chore|perf)'

    # Pattern: type(scope): description
    # Scope: lowercase alphanumeric with hyphens
    # Description: imperative, max 72 chars total
    pattern = rf'^{valid_types}\([a-z][a-z0-9-]*\): .{{1,}}$'

    if not re.match(pattern, subject):
        return False, (
            f"Invalid subject line: '{subject}'\n"
            "Expected: type(scope): description\n"
            "Valid types: feat, fix, test, refactor, docs, chore, perf\n"
            "Scope: lowercase, alphanumeric with hyphens\n"
            "Example: feat(auth): add token refresh endpoint"
        )

    # Check max 72 characters
    if len(subject) > 72:
        return False, f"Subject line too long ({len(subject)} chars, max 72): {subject}"

    # Check description is imperative (basic heuristic: shouldn't end in 'ed', 'ing')
    description = subject.split(': ', 1)[1] if ': ' in subject else ''
    if description:
        first_word = description.split()[0].lower()
        if first_word.endswith('ed') or first_word.endswith('ing'):
            return False, (
                f"Description should use imperative mood: '{description}'\n"
                "Use 'add' not 'added', 'fix' not 'fixing'"
            )

    # If Co-Authored-By present, validate format
    has_coauthor = False
    for line in lines:
        if line.startswith('Co-Authored-By:'):
            has_coauthor = True
            if not re.match(r'^Co-Authored-By: .+ <.+@.+\..+>$', line):
                return False, f"Invalid Co-Authored-By format: {line}"

    # If Agent-Session present, validate it's an agent commit (triplet: tool, model, agents)
    # Required: tool, model, agents. Optional: duration (orchestrator), tokens (hook-injected)
    has_agent_session = False
    for line in lines:
        if line.startswith('Agent-Session:'):
            has_agent_session = True
            pattern = (
                r'^Agent-Session: tool=[a-z0-9-]+ model=[a-z0-9.-]+ agents=[a-z0-9,-]+'
                r'( duration=\d+[mh])?'
                r'( dispatch=(human|orchestrator))?'
                r'( interactions=\d+)?'
                r'( approvals=\d+)?'
                r'( tokens=\d+(\.\d+)?K?/\d+(\.\d+)?K?)?$'
            )
            if not re.match(pattern, line):
                return False, (
                    f"Invalid Agent-Session format: {line}\n"
                    "Expected: Agent-Session: tool=<tool> model=<model> agents=<agents>"
                    " [duration=45m] [dispatch=orchestrator] [interactions=0] [approvals=2]"
                    " [tokens=8.2K/5.1K]\n"
                    "Triplet: tool (e.g. cursor, claude-code), model (e.g. sonnet, opus),"
                    " agents from context/agents (e.g. python-coder)"
                )

    # If Agent-Session present, Co-Authored-By is required
    if has_agent_session and not has_coauthor:
        return False, "Agent commits require Co-Authored-By line when Agent-Session is present"

    return True, ""


def main():
    """Read commit message from file and validate."""
    if len(sys.argv) < 2:
        print("Usage: conventional_commits.py <commit-msg-file>")
        sys.exit(1)

    msg_file = Path(sys.argv[1])

    if not msg_file.exists():
        print(f"❌ File not found: {msg_file}")
        sys.exit(1)

    msg = msg_file.read_text()

    # Skip merge commits and revert commits
    if msg.startswith('Merge ') or msg.startswith('Revert '):
        sys.exit(0)

    is_valid, error = validate_commit_message(msg)

    if not is_valid:
        print(f"❌ Invalid commit message:\n{error}")
        sys.exit(1)
    else:
        print("✅ Commit message valid")
        sys.exit(0)


if __name__ == '__main__':
    main()
