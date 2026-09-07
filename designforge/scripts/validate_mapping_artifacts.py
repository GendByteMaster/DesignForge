#!/usr/bin/env python3
"""Validate interpreted DesignForge codebase mapping artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ARTIFACT_NAMES = (
    "STACK.md",
    "UI_ARCHITECTURE.md",
    "COMPONENTS.md",
    "STYLES.md",
    "SCREENS.md",
    "CONCERNS.md",
)
REQUIRED_SECTIONS = (
    "## Scope",
    "## Verified findings",
    "## Inferences",
    "## Unknowns",
    "## Evidence index",
)
PLACEHOLDERS = {"- None yet.", "- None."}
PATH_RE = re.compile(r"`[^`]+(?:/[^`]+|\.[A-Za-z0-9]+)[^`]*`")


def section(text: str, heading: str) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    end = text.find("\n## ", start)
    if end < 0:
        end = len(text)
    return text[start:end].strip()


def substantive(body: str) -> bool:
    """Return whether a section contains an explicit non-placeholder list item.

    Mapping findings use Markdown list items as the machine-checkable unit. Free
    prose in a section may explain the contract and must not be mistaken for a
    finding that requires provenance.
    """

    findings = [
        line.strip()
        for line in body.splitlines()
        if line.strip().startswith("- ")
    ]
    return any(line not in PLACEHOLDERS for line in findings)


def validate_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{path.name}: cannot read UTF-8 text: {exc}"]

    if not text.startswith("# "):
        errors.append(f"{path.name}: must start with a level-1 title")
    for heading in REQUIRED_SECTIONS:
        if heading not in text:
            errors.append(f"{path.name}: missing {heading}")

    verified = section(text, "## Verified findings")
    evidence = section(text, "## Evidence index")
    if substantive(verified) and not PATH_RE.search(evidence):
        errors.append(
            f"{path.name}: verified findings require a repository-relative path in Evidence index"
        )
    return errors


def validate(target: Path, allow_empty: bool = False) -> list[str]:
    workspace = target.resolve() / ".DesignForge"
    if not (workspace / "STATE.md").is_file():
        return [".DesignForge/STATE.md not found; run init first"]

    codebase = workspace / "codebase"
    files = [codebase / name for name in ARTIFACT_NAMES if (codebase / name).is_file()]
    if not files and not allow_empty:
        return ["no interpreted mapping artifacts found under .DesignForge/codebase/"]

    errors: list[str] = []
    for path in files:
        errors.extend(validate_file(path))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate DesignForge mapping artifact provenance")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--allow-empty", action="store_true")
    args = parser.parse_args(argv)

    errors = validate(Path(args.target), args.allow_empty)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("DesignForge mapping artifact validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
