#!/usr/bin/env python3
"""prepare-commit-msg hook: append token usage to Agent-Session line.

Reads Claude Code session JSONL files, computes tokens used since the
last commit, and appends to the Agent-Session trailer in the commit message.

Portable: derives the Claude Code project path from `git rev-parse --show-toplevel`.
"""

import json
import glob
import os
import subprocess
import sys


def get_claude_project_dir() -> str | None:
    """Derive the Claude Code project directory from the git repo root."""
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
    except subprocess.CalledProcessError:
        return None

    mangled = repo_root.replace("/", "-")
    claude_dir = os.path.expanduser(f"~/.claude/projects/{mangled}")
    return claude_dir if os.path.isdir(claude_dir) else None


def get_active_session_dir(claude_dir: str) -> str | None:
    """Find the most recently modified session directory."""
    session_dirs = [
        d
        for d in glob.glob(os.path.join(claude_dir, "*/"))
        if os.path.isdir(d)
    ]
    if not session_dirs:
        return None
    session_dirs.sort(key=os.path.getmtime, reverse=True)
    return session_dirs[0]


def sum_session_tokens(session_dir: str) -> tuple[int, int]:
    """Sum input and output tokens across all JSONL files in a session."""
    total_in = 0
    total_out = 0

    # Subagent files
    subagent_dir = os.path.join(session_dir, "subagents")
    jsonl_files = []
    if os.path.isdir(subagent_dir):
        jsonl_files.extend(glob.glob(os.path.join(subagent_dir, "*.jsonl")))

    # Main session file
    main_jsonl = session_dir.rstrip("/") + ".jsonl"
    if os.path.exists(main_jsonl):
        jsonl_files.append(main_jsonl)

    for filepath in jsonl_files:
        try:
            with open(filepath) as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        usage = entry.get("message", {}).get("usage", {})
                        if usage:
                            total_in += (
                                usage.get("input_tokens", 0)
                                + usage.get("cache_creation_input_tokens", 0)
                                + usage.get("cache_read_input_tokens", 0)
                            )
                            total_out += usage.get("output_tokens", 0)
                    except (json.JSONDecodeError, AttributeError):
                        continue
        except OSError:
            continue

    return total_in, total_out


def get_watermark(session_dir: str) -> tuple[int, int]:
    """Read the token watermark from the last commit."""
    watermark_file = os.path.join(session_dir, ".tokens-watermark")
    if os.path.exists(watermark_file):
        try:
            with open(watermark_file) as f:
                data = json.loads(f.read())
                return data.get("in", 0), data.get("out", 0)
        except (json.JSONDecodeError, OSError):
            pass
    return 0, 0


def set_watermark(session_dir: str, total_in: int, total_out: int) -> None:
    """Write the current token totals as the watermark for next commit."""
    watermark_file = os.path.join(session_dir, ".tokens-watermark")
    try:
        with open(watermark_file, "w") as f:
            json.dump({"in": total_in, "out": total_out}, f)
    except OSError:
        pass


def format_tokens(count: int) -> str:
    """Format token count with K suffix."""
    if count >= 1000:
        return f"{count / 1000:.1f}K"
    return str(count)


def update_commit_message(msg_file: str, tokens_in: int, tokens_out: int) -> None:
    """Append or update tokens in the Agent-Session line of the commit message."""
    with open(msg_file) as f:
        content = f.read()

    token_str = f"tokens={format_tokens(tokens_in)}/{format_tokens(tokens_out)}"

    if "Agent-Session:" in content:
        # Update existing Agent-Session line
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("Agent-Session:"):
                # Replace existing tokens= or append
                if "tokens=" in line:
                    import re

                    lines[i] = re.sub(
                        r"tokens=\S+", token_str, line
                    )
                else:
                    lines[i] = line.rstrip() + " " + token_str
                break
        content = "\n".join(lines)
    else:
        # No Agent-Session line — don't add one (human commit)
        return

    with open(msg_file, "w") as f:
        f.write(content)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(0)

    msg_file = sys.argv[1]
    # commit source: message, template, merge, squash, or commit (amend)
    commit_source = sys.argv[2] if len(sys.argv) > 2 else ""

    # Skip for merge and squash commits
    if commit_source in ("merge", "squash"):
        sys.exit(0)

    claude_dir = get_claude_project_dir()
    if not claude_dir:
        sys.exit(0)

    session_dir = get_active_session_dir(claude_dir)
    if not session_dir:
        sys.exit(0)

    total_in, total_out = sum_session_tokens(session_dir)
    watermark_in, watermark_out = get_watermark(session_dir)

    delta_in = total_in - watermark_in
    delta_out = total_out - watermark_out

    # Only annotate if there are actual tokens to report
    if delta_in > 0 or delta_out > 0:
        update_commit_message(msg_file, delta_in, delta_out)
        set_watermark(session_dir, total_in, total_out)


if __name__ == "__main__":
    main()
