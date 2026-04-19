#!/usr/bin/env python3
"""Validate agent definition integrity."""

import sys
from pathlib import Path
import re
import yaml

def validate_agent_definition(file_path: Path) -> list[str]:
    """Validate single agent definition.

    Args:
        file_path: Path to agent definition file

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    content = file_path.read_text()

    # Extract frontmatter
    if not content.startswith('---'):
        errors.append("Missing YAML frontmatter")
        return errors

    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("Invalid YAML frontmatter structure")
        return errors

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return errors

    # Check required frontmatter fields
    required = ['name', 'model']
    for field in required:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Validate standards references
    if 'standards' in frontmatter:
        for standard in frontmatter['standards']:
            standard_path = Path('context/standards') / standard
            if not standard_path.exists():
                errors.append(f"Referenced standard doesn't exist: {standard}")

    # Validate rules references
    if 'rules' in frontmatter:
        for rule in frontmatter['rules']:
            rule_path = Path('context/rules') / rule
            if not rule_path.exists():
                errors.append(f"Referenced rule doesn't exist: {rule}")

    # Check for hardcoded paths
    body = parts[2]
    if '/Users/' in body or '/home/' in body:
        errors.append("Contains hardcoded absolute paths")

    # Check for {project-root} usage instead of relative paths
    if './artefacts/' in body:
        errors.append("Contains relative paths - use {project-root}/artefacts/ instead")

    # Check for Critical Reminders section and attribution
    if 'Critical Reminders' in body:
        # Find reminder section
        reminder_match = re.search(r'## Critical Reminders.*?(?=##|$)', body, re.DOTALL)
        if reminder_match:
            reminders = reminder_match.group(0)
            # Check each line has attribution
            for line in reminders.split('\n'):
                if line.strip().startswith('-') and '(' not in line:
                    errors.append(f"Reminder missing attribution: {line.strip()}")

    # Check for Required Standards section
    if 'Required Standards' not in body:
        errors.append("Missing 'Required Standards' section")

    # Check for Required Rules section
    if 'Required Rules' not in body:
        errors.append("Missing 'Required Rules' section")

    return errors

def main():
    """Validate all agent definitions."""
    agents_dir = Path('context/agents')

    if not agents_dir.exists():
        print("❌ context/agents/ directory not found")
        sys.exit(1)

    all_errors = {}
    agent_count = 0

    for agent_file in agents_dir.glob('*.md'):
        if agent_file.name in ['TEMPLATE.md', 'README.md', 'MODEL-RECOMMENDATIONS.md']:
            continue

        agent_count += 1
        errors = validate_agent_definition(agent_file)
        if errors:
            all_errors[agent_file.name] = errors

    if all_errors:
        print(f"❌ Validation failed for {len(all_errors)}/{agent_count} agents:\n")
        for file, errors in all_errors.items():
            print(f"{file}:")
            for error in errors:
                print(f"  - {error}")
        sys.exit(1)
    else:
        print(f"✅ All {agent_count} agent definitions valid")
        sys.exit(0)

if __name__ == '__main__':
    main()
