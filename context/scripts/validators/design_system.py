#!/usr/bin/env python3
"""Validate frontend compliance with artefacts/design/design-system.md.

Checks:
- Only one CSS file (frontend/src/index.css); no component-scoped CSS.
- No Tailwind concrete colour classes for data-meaningful UI (use DaisyUI semantic).
- No direct imports from @heroicons/react outside the barrel file.
- Spacing scale: only gap-1, gap-2, gap-4, p-2, p-4, px-4 (md:gap-6, md:px-6 only in PriceHeader).

Run from repo root. Exits 0 if compliant, 1 with violations on stderr.

Until Phases 3–4 of the design-system migration are complete, spacing violations
are expected. Use SKIP=design-system git commit to bypass, or fix violations.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


# Repo root: script lives in context/scripts/validators/
REPO_ROOT = Path(__file__).resolve().parents[3]
FRONTEND_SRC = REPO_ROOT / "frontend" / "src"

# Allowed spacing tokens (design-system §1.2). Responsive md:gap-6, md:px-6 only in PriceHeader.
ALLOWED_SPACING = {
    "gap-1",
    "gap-2",
    "gap-4",
    "p-2",
    "p-4",
    "px-4",
    "md:gap-6",
    "md:px-6",
}

# Disallowed: Tailwind concrete colour classes for data/state (use text-success, text-error, etc.)
CONCRETE_COLOUR_PATTERN = re.compile(
    r"(?:text|bg|border)-"
    r"(?:green|red|amber|yellow|blue|gray|slate|zinc|neutral|stone)-\d+"
    r"(?:/\d+)?"
    r"(?:\s+dark:[^\s]+)?"
)

# Direct Heroicons import (barrel is components/icons/HeroIcons.tsx)
HEROICONS_IMPORT_PATTERN = re.compile(
    r"from\s+['\"]@heroicons/react"
)

# Disallowed spacing: values not in design-system §1.2.
# Allowed: gap-1, gap-2, gap-4; p-2, p-4; px-4; md:gap-6, md:px-6 only in PriceHeader.
# Match disallowed only: gap-0, gap-3, gap-5+, p-0, p-1, p-3, p-5+, px-0..3, px-5+, py/pt/pb/pl/pr-*.
DISALLOWED_SPACING_PATTERN = re.compile(
    r"\b(?:gap-(?:0|3|[5-9]|1[0-9]|\d{2,}|[0-9]\.[0-9]+)|"
    r"p-(?:0|1|3|[5-9]|1[0-9]|\d{2,}|[0-9]\.[0-9]+)|"
    r"px-(?:0|[1-3]|[5-9]|1[0-9]|\d{2,})|"
    r"py-[0-9]+|pt-[0-9]+|pb-[0-9]+|pl-[0-9]+|pr-[0-9]+)\b"
)


def check_css_files() -> list[str]:
    """Only index.css under frontend/src; no component-scoped CSS."""
    violations = []
    css_dir = FRONTEND_SRC
    if not css_dir.exists():
        return violations
    css_files = list(css_dir.rglob("*.css"))
    allowed = {css_dir / "index.css"}
    for f in css_files:
        if f not in allowed:
            violations.append(f"  {f.relative_to(REPO_ROOT)}: component-scoped CSS not allowed (design-system §1.1)")
    return violations


def check_concrete_colours(path: Path, content: str) -> list[tuple[int, str]]:
    """Tailwind concrete colour classes (use DaisyUI semantic tokens)."""
    violations = []
    for i, line in enumerate(content.splitlines(), 1):
        for m in CONCRETE_COLOUR_PATTERN.finditer(line):
            violations.append((i, f"  Line {i}: concrete colour '{m.group(0).strip()}' — use DaisyUI semantic (e.g. text-success, text-error) §1.4"))
    return violations


def check_heroicons_import(path: Path, content: str) -> list[tuple[int, str]]:
    """No direct @heroicons/react; use barrel components/icons/HeroIcons.tsx."""
    if "icons/HeroIcons" in str(path) or "HeroIcons.tsx" in path.name:
        return []
    violations = []
    for i, line in enumerate(content.splitlines(), 1):
        if HEROICONS_IMPORT_PATTERN.search(line):
            violations.append((i, f"  Line {i}: import from '@heroicons/react' — use barrel from components/icons/HeroIcons.tsx §1.3"))
    return violations


def check_spacing(path: Path, content: str) -> list[tuple[int, str]]:
    """Spacing scale: only allowed tokens; md:gap-6/md:px-6 only in PriceHeader."""
    violations = []
    is_price_header = "PriceHeader" in path.name and "price-header" in str(path)
    for i, line in enumerate(content.splitlines(), 1):
        for m in DISALLOWED_SPACING_PATTERN.finditer(line):
            token = m.group(0)
            if token in ("md:gap-6", "md:px-6") and is_price_header:
                continue
            violations.append((i, f"  Line {i}: spacing '{token}' — use only gap-1, gap-2, gap-4, p-2, p-4, px-4 (§1.2)"))
    return violations


def is_test_or_spec(path: Path) -> bool:
    return "__tests__" in path.parts or ".test." in path.name or ".spec." in path.name


def main() -> int:
    if not FRONTEND_SRC.exists():
        print("Frontend src not found; skipping design-system check.", file=sys.stderr)
        return 0

    all_violations: list[str] = []

    # 1. CSS files
    css_v = check_css_files()
    all_violations.extend(css_v)

    # 2. TSX/JSX in frontend/src (skip test files for colour/spacing to allow assertions)
    for ext in ("*.tsx", "*.jsx"):
        for path in FRONTEND_SRC.rglob(ext):
            if is_test_or_spec(path):
                continue
            try:
                content = path.read_text()
            except Exception as e:
                all_violations.append(f"  {path.relative_to(REPO_ROOT)}: read error — {e}")
                continue
            rel = path.relative_to(REPO_ROOT)

            for line_no, msg in check_concrete_colours(path, content):
                all_violations.append(f"{rel}:{line_no}\n{msg}")
            for line_no, msg in check_heroicons_import(path, content):
                all_violations.append(f"{rel}:{line_no}\n{msg}")
            for line_no, msg in check_spacing(path, content):
                all_violations.append(f"{rel}:{line_no}\n{msg}")

    if all_violations:
        print("Design system violations (artefacts/design/design-system.md):\n", file=sys.stderr)
        for v in all_violations:
            print(v, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
