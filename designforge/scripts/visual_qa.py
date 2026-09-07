#!/usr/bin/env python3
"""Provider-neutral visual QA scaffolding and mechanical validation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_PATH = SKILL_ROOT / "assets" / "reviews" / "VISUAL_QA.md"
REQUIRED_SECTIONS = (
    "## Scope",
    "## Capture matrix",
    "## Findings",
    "## Accessibility observations",
    "## Unverified states",
    "## Verdict",
)
VALID_STATUSES = {
    "pending",
    "pass",
    "pass-with-notes",
    "fail",
    "blocked",
    "unavailable",
}
EVIDENCE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".mp4", ".webm"}
CAPTURE_RE = re.compile(
    r"^- \[([ xX])\] Surface: (.*?) \| State: (.*?) \| Viewport: (.*?) \| Evidence: `([^`]+)`$"
)
STATUS_RE = re.compile(r"^Status:\s*([a-z-]+)\s*$", re.MULTILINE)


def review_path(target: Path, phase: str | None = None) -> Path:
    workspace = target.resolve() / ".DesignForge"
    if phase:
        return workspace / "phases" / phase / "VISUAL_QA.md"
    return workspace / "reviews" / "VISUAL_QA.md"


def evidence_dir(target: Path, phase: str | None = None) -> Path:
    return review_path(target, phase).parent / "visual-evidence"


def init_review(target: Path, phase: str | None = None, force: bool = False) -> tuple[Path | None, list[str]]:
    target = target.resolve()
    workspace = target / ".DesignForge"
    if not (workspace / "STATE.md").is_file():
        return None, [".DesignForge/STATE.md not found; run init first"]
    if not TEMPLATE_PATH.is_file():
        return None, ["visual QA template is missing from the skill package"]

    destination = review_path(target, phase)
    if phase and not destination.parent.is_dir():
        return None, [f"phase directory not found: .DesignForge/phases/{phase}"]
    if destination.exists() and not force:
        return destination, []

    destination.parent.mkdir(parents=True, exist_ok=True)
    evidence_dir(target, phase).mkdir(parents=True, exist_ok=True)
    destination.write_text(TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    return destination, []


def is_placeholder(value: str) -> bool:
    value = value.strip()
    return not value or "<!--" in value or "-->" in value


def safe_evidence_path(target: Path, token: str) -> Path | None:
    normalized = token.strip().replace("\\", "/")
    if not normalized or normalized.startswith("/"):
        return None
    relative = Path(normalized)
    if ".." in relative.parts:
        return None
    absolute = (target.resolve() / relative).resolve()
    try:
        absolute.relative_to(target.resolve())
    except ValueError:
        return None
    return absolute


def validate_review(target: Path, phase: str | None = None) -> list[str]:
    target = target.resolve()
    path = review_path(target, phase)
    if not path.is_file():
        return [f"visual QA artifact not found: {path.relative_to(target)}"]

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"VISUAL_QA.md cannot be read as UTF-8: {exc}"]

    errors: list[str] = []
    if not text.startswith("# Visual QA"):
        errors.append("VISUAL_QA.md must start with '# Visual QA'")
    for heading in REQUIRED_SECTIONS:
        if heading not in text:
            errors.append(f"VISUAL_QA.md missing {heading}")

    status_match = STATUS_RE.search(text)
    if not status_match:
        errors.append("VISUAL_QA.md must contain a Verdict status")
        status = None
    else:
        status = status_match.group(1)
        if status not in VALID_STATUSES:
            errors.append("VISUAL_QA.md has invalid Verdict status: " + status)

    captures: list[tuple[bool, str, str, str, str]] = []
    for raw_line in text.splitlines():
        match = CAPTURE_RE.match(raw_line.strip())
        if not match:
            continue
        checked = match.group(1).lower() == "x"
        captures.append((checked, match.group(2), match.group(3), match.group(4), match.group(5)))

    if not captures:
        errors.append("VISUAL_QA.md must contain at least one capture-matrix checklist item")
        return errors

    checked_count = 0
    for checked, surface, state, viewport, evidence in captures:
        if not checked:
            continue
        checked_count += 1
        for label, value in (("Surface", surface), ("State", state), ("Viewport", viewport), ("Evidence", evidence)):
            if is_placeholder(value):
                errors.append(f"checked capture has placeholder {label}")
        evidence_path = safe_evidence_path(target, evidence)
        if evidence_path is None:
            errors.append(f"checked capture evidence must be project-relative: {evidence}")
            continue
        if evidence_path.suffix.lower() not in EVIDENCE_SUFFIXES:
            errors.append(f"checked capture evidence has unsupported render format: {evidence}")
            continue
        if not evidence_path.is_file():
            errors.append(f"checked capture evidence file not found: {evidence}")
            continue
        try:
            if evidence_path.stat().st_size == 0:
                errors.append(f"checked capture evidence file is empty: {evidence}")
        except OSError:
            errors.append(f"checked capture evidence file cannot be inspected: {evidence}")

    if status in {"pass", "pass-with-notes", "fail"} and checked_count == 0:
        errors.append(f"Verdict status '{status}' requires at least one inspected render artifact")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold or validate DesignForge visual QA evidence")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("target", nargs="?", default=".")
    init_parser.add_argument("--phase")
    init_parser.add_argument("--force", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("target", nargs="?", default=".")
    validate_parser.add_argument("--phase")

    args = parser.parse_args(argv)
    target = Path(args.target)

    if args.command == "init":
        destination, errors = init_review(target, args.phase, args.force)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        assert destination is not None
        print(f"Visual QA artifact: {destination}")
        print(f"Visual evidence directory: {evidence_dir(target, args.phase)}")
        return 0

    errors = validate_review(target, args.phase)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("DesignForge visual QA validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
