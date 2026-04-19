#!/usr/bin/env python3
"""Validate British English spelling."""

import sys
import re
from pathlib import Path


# Common American → British spelling pairs from british-english.mdc
SPELLING_RULES = {
    r'\bcolou?r\b': ('color', 'colour'),
    r'\bfavou?r\b': ('favor', 'favour'),
    r'\bhonou?r\b': ('honor', 'honour'),
    r'\blabou?r\b': ('labor', 'labour'),
    r'\bneighbou?r\b': ('neighbor', 'neighbour'),
    r'\bbehaviou?r\b': ('behavior', 'behaviour'),
    r'\b(organ|real|recogn|special|general)i[sz]e\b': ('organize/realize/...', 'organise/realise/...'),
    r'\bcente?r\b': ('center', 'centre'),
    r'\bmete?r\b': ('meter', 'metre'),
    r'\blicen[cs]e\b': ('license (noun)', 'licence (noun)'),
    r'\bdefen[cs]e\b': ('defense', 'defence'),
    r'\boffen[cs]e\b': ('offense', 'offence'),
}


def validate_british_english(file_path: Path) -> list[str]:
    """Check for American English spellings.

    Args:
        file_path: Path to file to check

    Returns:
        List of violations
    """
    violations = []
    content = file_path.read_text()
    lines = content.split('\n')

    in_code_block = False

    for i, line in enumerate(lines, 1):
        # Track code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue

        # Skip code blocks, inline code, and markdown tables
        if in_code_block or '`' in line or line.strip().startswith('|'):
            continue

        # Check for American spellings
        # color vs colour
        if re.search(r'\bcolor\b', line, re.IGNORECASE):
            if not re.search(r'\bcolour\b', line, re.IGNORECASE):
                violations.append(
                    f"Line {i}: Use 'colour' instead of 'color'\n"
                    f"  {line.strip()}"
                )

        # behavior vs behaviour
        if re.search(r'\bbehavior\b', line, re.IGNORECASE):
            violations.append(
                f"Line {i}: Use 'behaviour' instead of 'behavior'\n"
                f"  {line.strip()}"
            )

        # organize vs organise (and similar -ize/-ise)
        for word in ['organize', 'realize', 'recognize', 'specialize', 'generalize']:
            if re.search(rf'\b{word}\b', line, re.IGNORECASE):
                british = word.replace('ize', 'ise')
                violations.append(
                    f"Line {i}: Use '{british}' instead of '{word}'\n"
                    f"  {line.strip()}"
                )

        # center vs centre
        if re.search(r'\bcenter\b', line, re.IGNORECASE):
            violations.append(
                f"Line {i}: Use 'centre' instead of 'center'\n"
                f"  {line.strip()}"
            )

        # license (noun) vs licence
        # Note: "license" as a verb is correct in British English too
        # We'll flag it and let humans decide based on context
        if re.search(r'\blicense\b', line, re.IGNORECASE):
            if not re.search(r'\blicen[cs]ing\b', line, re.IGNORECASE):  # Skip verb forms
                violations.append(
                    f"Line {i}: Use 'licence' for noun, 'license' for verb\n"
                    f"  {line.strip()}"
                )

    return violations


def main():
    """Validate British English in file."""
    if len(sys.argv) < 2:
        print("Usage: british_english.py <file>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Skip if not a text file
    if file_path.suffix not in ['.md', '.py', '.ts', '.tsx', '.js', '.jsx', '.txt']:
        sys.exit(0)

    violations = validate_british_english(file_path)

    if violations:
        print(f"❌ American English found in {file_path.name}:\n")
        for violation in violations:
            print(violation)
            print()
        sys.exit(1)
    else:
        print(f"✅ {file_path.name} uses British English")
        sys.exit(0)


if __name__ == '__main__':
    main()
