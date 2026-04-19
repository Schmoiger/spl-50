#!/usr/bin/env python3
"""Pre-commit hook: enforce that supabase is only imported in database-service.

Checks that no file passed as an argument contains ``import supabase`` or
``from supabase import``.  Exits with code 1 and an error message listing all
violating files if any violation is found.

Usage (invoked by pre-commit):
    uv run python context/scripts/validators/supabase_boundary.py <file> [<file> ...]
"""

import re
import sys

PATTERN = re.compile(r"^\s*(import supabase|from supabase\b)", re.MULTILINE)

violations: list[str] = []

for path in sys.argv[1:]:
    try:
        text = open(path).read()
    except Exception:
        continue
    if PATTERN.search(text):
        violations.append(path)

if violations:
    print("ERROR: supabase imported outside database-service:")
    for v in violations:
        print(f"  {v}")
    sys.exit(1)
