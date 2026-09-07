#!/usr/bin/env python3
"""Provider-neutral visual QA scaffolding, capture handoff, and validation."""

from __future__ import annotations

import argparse
import re
import shutil
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
        evidence_dir(target, phase).mkdir(parents=True, exist_ok=True)
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


def has_declared_render_signature(path: Path) -> bool:
    """Perform a bounded magic-byte sanity check without decoding the media."""
    try:
        with path.open("rb") as stream:
            header = stream.read(16)
    except OSError:
        return False

    suffix = path.suffix.lower()
    if suffix == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    if suffix in {".jpg", ".jpeg"}:
        return header.startswith(b"\xff\xd8\xff")
    if suffix == ".gif":
        return header.startswith((b"GIF87a", b"GIF89a"))
    if suffix == ".webp":
        return len(header) >= 12 and header[:4] == b"RIFF" and header[8:12] == b"WEBP"
    if suffix == ".mp4":
        return len(header) >= 8 and header[4:8] == b"ftyp"
    if suffix == ".webm":
        return header.startswith(b"\x1a\x45\xdf\xa3")
    return False


def normalize_capture_value(label: str, value: str) -> tuple[str | None, str | None]:
    normalized = " ".join(value.strip().split())
    if not normalized:
        return None, f"{label} must not be empty"
    if any(token in normalized for token in ("|", "`", "<!--", "-->")):
        return None, f"{label} contains characters reserved by the Visual QA capture format"
    return normalized, None


def slugify_capture(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:48]


def next_capture_destination(directory: Path, surface: str, state: str, suffix: str) -> Path:
    stem_parts = [part for part in (slugify_capture(surface), slugify_capture(state)) if part]
    stem = "-".join(stem_parts) or "capture"
    candidate = directory / f"{stem}{suffix}"
    index = 2
    while candidate.exists():
        candidate = directory / f"{stem}-{index}{suffix}"
        index += 1
    return candidate


def insert_capture(text: str, line: str) -> str:
    lines = text.splitlines()

    for index, raw_line in enumerate(lines):
        match = CAPTURE_RE.match(raw_line.strip())
        if not match:
            continue
        values = (match.group(2), match.group(3), match.group(4), match.group(5))
        if match.group(1) == " " and any(is_placeholder(value) for value in values):
            lines[index] = line
            return "\n".join(lines) + "\n"

    try:
        heading_index = lines.index("## Capture matrix")
    except ValueError:
        return text

    insert_at = len(lines)
    for index in range(heading_index + 1, len(lines)):
        if lines[index].startswith("## "):
            insert_at = index
            break

    while insert_at > heading_index + 1 and not lines[insert_at - 1].strip():
        insert_at -= 1
    lines[insert_at:insert_at] = [line, ""]
    return "\n".join(lines) + "\n"


def register_capture(
    target: Path,
    source: Path,
    surface: str,
    state: str,
    viewport: str,
    phase: str | None = None,
) -> tuple[Path | None, list[str]]:
    target = target.resolve()
    if not target.exists() or not target.is_dir():
        return None, [f"target directory does not exist: {target}"]
    if not (target / ".DesignForge" / "STATE.md").is_file():
        return None, [".DesignForge/STATE.md not found; run init first"]

    normalized_values: dict[str, str] = {}
    for label, value in (("Surface", surface), ("State", state), ("Viewport", viewport)):
        normalized, error = normalize_capture_value(label, value)
        if error:
            return None, [error]
        assert normalized is not None
        normalized_values[label] = normalized

    source = source.expanduser().resolve()
    if not source.is_file():
        return None, [f"capture source file not found: {source}"]
    suffix = source.suffix.lower()
    if suffix not in EVIDENCE_SUFFIXES:
        return None, [f"capture source has unsupported render format: {source}"]
    try:
        if source.stat().st_size == 0:
            return None, [f"capture source file is empty: {source}"]
    except OSError as exc:
        return None, [f"capture source file cannot be inspected: {exc}"]
    if not has_declared_render_signature(source):
        return None, [f"capture source has invalid render signature: {source}"]

    review, errors = init_review(target, phase)
    if errors:
        return None, errors
    assert review is not None

    managed_root = evidence_dir(target, phase).resolve()
    try:
        managed_root.relative_to(target)
    except ValueError:
        return None, ["managed visual evidence directory escapes the target project"]
    managed_root.mkdir(parents=True, exist_ok=True)

    copied = False
    try:
        source.relative_to(managed_root)
        destination = source
    except ValueError:
        destination = next_capture_destination(
            managed_root,
            normalized_values["Surface"],
            normalized_values["State"],
            suffix,
        )
        try:
            shutil.copyfile(source, destination)
        except OSError as exc:
            return None, [f"failed to copy capture into managed evidence: {exc}"]
        copied = True

    try:
        relative_evidence = destination.relative_to(target).as_posix()
    except ValueError:
        if copied:
            destination.unlink(missing_ok=True)
        return None, ["managed visual evidence path escapes the target project"]

    try:
        original = review.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        if copied:
            destination.unlink(missing_ok=True)
        return None, [f"VISUAL_QA.md cannot be read as UTF-8: {exc}"]

    capture_line = (
        f"- [x] Surface: {normalized_values['Surface']} | "
        f"State: {normalized_values['State']} | "
        f"Viewport: {normalized_values['Viewport']} | "
        f"Evidence: `{relative_evidence}`"
    )
    if capture_line in original:
        return destination, []

    updated = insert_capture(original, capture_line)
    if updated == original:
        if copied:
            destination.unlink(missing_ok=True)
        return None, ["VISUAL_QA.md is missing a writable Capture matrix section"]

    try:
        review.write_text(updated, encoding="utf-8")
    except OSError as exc:
        if copied:
            destination.unlink(missing_ok=True)
        return None, [f"failed to update VISUAL_QA.md: {exc}"]

    validation_errors = validate_review(target, phase)
    if validation_errors:
        try:
            review.write_text(original, encoding="utf-8")
        finally:
            if copied:
                destination.unlink(missing_ok=True)
        return None, validation_errors

    return destination, []


def set_verdict(target: Path, status: str, phase: str | None = None) -> list[str]:
    target = target.resolve()
    if status not in VALID_STATUSES:
        return [f"invalid Visual QA verdict status: {status}"]

    review, errors = init_review(target, phase)
    if errors:
        return errors
    assert review is not None

    try:
        original = review.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"VISUAL_QA.md cannot be read as UTF-8: {exc}"]
    if not STATUS_RE.search(original):
        return ["VISUAL_QA.md must contain a Verdict status"]

    updated = STATUS_RE.sub(f"Status: {status}", original, count=1)
    try:
        review.write_text(updated, encoding="utf-8")
    except OSError as exc:
        return [f"failed to update VISUAL_QA.md verdict: {exc}"]

    validation_errors = validate_review(target, phase)
    if validation_errors:
        review.write_text(original, encoding="utf-8")
        return validation_errors
    return []


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
    managed_evidence_root = evidence_dir(target, phase).resolve()
    try:
        managed_evidence_label = managed_evidence_root.relative_to(target).as_posix()
    except ValueError:
        errors.append("managed visual evidence directory escapes the target project")
        return errors

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
        try:
            evidence_path.relative_to(managed_evidence_root)
        except ValueError:
            errors.append(
                f"checked capture evidence must live under {managed_evidence_label}: {evidence}"
            )
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
                continue
        except OSError:
            errors.append(f"checked capture evidence file cannot be inspected: {evidence}")
            continue
        if not has_declared_render_signature(evidence_path):
            errors.append(f"checked capture evidence has invalid render signature: {evidence}")

    if status in {"pass", "pass-with-notes", "fail"} and checked_count == 0:
        errors.append(f"Verdict status '{status}' requires at least one inspected render artifact")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scaffold, register, or validate DesignForge visual QA evidence")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("target", nargs="?", default=".")
    init_parser.add_argument("--phase")
    init_parser.add_argument("--force", action="store_true")

    capture_parser = subparsers.add_parser("capture")
    capture_parser.add_argument("source")
    capture_parser.add_argument("target", nargs="?", default=".")
    capture_parser.add_argument("--surface", required=True)
    capture_parser.add_argument("--state", required=True)
    capture_parser.add_argument("--viewport", required=True)
    capture_parser.add_argument("--phase")

    verdict_parser = subparsers.add_parser("verdict")
    verdict_parser.add_argument("status", choices=sorted(VALID_STATUSES))
    verdict_parser.add_argument("target", nargs="?", default=".")
    verdict_parser.add_argument("--phase")

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

    if args.command == "capture":
        destination, errors = register_capture(
            target,
            Path(args.source),
            args.surface,
            args.state,
            args.viewport,
            args.phase,
        )
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        assert destination is not None
        print(f"Visual capture registered: {destination}")
        return 0

    if args.command == "verdict":
        errors = set_verdict(target, args.status, args.phase)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        print(f"Visual QA verdict: {args.status}")
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
