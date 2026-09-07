#!/usr/bin/env python3
"""Stamp and verify freshness of interpreted DesignForge codebase maps."""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

from evidence_scanner import MANIFESTS, SOURCE_EXTENSIONS, STYLE_EXTENSIONS
from validate_mapping_artifacts import ARTIFACT_NAMES, section, validate

MAP_STATE_NAME = "MAP_STATE.md"
PATH_TOKEN_RE = re.compile(r"`([^`]+)`")
DIGEST_LINE_RE = re.compile(r"^- `([^`]+)`: `(sha256:[0-9a-f]{64}|missing)`$")
BASELINE_COMMIT_RE = re.compile(r"^- Git commit: `([^`]+)`$")
DIRTY_PATH_RE = re.compile(r"^- `([^`]+)`$")
CONFIG_PREFIXES = (
    "tailwind.config",
    "postcss.config",
    "vite.config",
    "next.config",
    "nuxt.config",
    "svelte.config",
    "tsconfig",
    "components.json",
)
DESIGN_DOC_NAMES = {
    "DESIGN_SYSTEM.md",
    "DESIGN.md",
    "STYLEGUIDE.md",
    "STYLE_GUIDE.md",
}


def run_git(target: Path, *args: str) -> subprocess.CompletedProcess[bytes] | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(target), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError:
        return None
    return result if result.returncode == 0 else None


def git_root(target: Path) -> Path | None:
    result = run_git(target, "rev-parse", "--show-toplevel")
    if not result:
        return None
    try:
        return Path(result.stdout.decode("utf-8").strip()).resolve()
    except UnicodeDecodeError:
        return None


def git_commit(target: Path) -> str | None:
    result = run_git(target, "rev-parse", "HEAD")
    if not result:
        return None
    try:
        return result.stdout.decode("ascii").strip()
    except UnicodeDecodeError:
        return None


def decode_nul_paths(payload: bytes) -> list[str]:
    values: list[str] = []
    for raw in payload.split(b"\0"):
        if not raw:
            continue
        try:
            values.append(raw.decode("utf-8"))
        except UnicodeDecodeError:
            continue
    return values


def to_target_relative(target: Path, repo_root: Path, repo_paths: list[str]) -> set[str]:
    target = target.resolve()
    result: set[str] = set()
    for value in repo_paths:
        absolute = (repo_root / value).resolve()
        try:
            relative = absolute.relative_to(target)
        except ValueError:
            continue
        result.add(relative.as_posix())
    return result


def git_worktree_paths(target: Path) -> set[str] | None:
    repo_root = git_root(target)
    if repo_root is None:
        return None
    collected: set[str] = set()
    commands = (
        ("diff", "--name-only", "-z", "--", "."),
        ("diff", "--cached", "--name-only", "-z", "--", "."),
        ("ls-files", "--others", "--exclude-standard", "-z", "--", "."),
    )
    for command in commands:
        result = run_git(target, *command)
        if result is None:
            return None
        collected.update(to_target_relative(target, repo_root, decode_nul_paths(result.stdout)))
    return collected


def git_changed_since(target: Path, baseline: str) -> set[str] | None:
    repo_root = git_root(target)
    if repo_root is None:
        return None
    result = run_git(target, "diff", "--name-only", "-z", f"{baseline}..HEAD", "--", ".")
    if result is None:
        return None
    return to_target_relative(target, repo_root, decode_nul_paths(result.stdout))


def is_ui_relevant(path: str) -> bool:
    candidate = Path(path)
    suffix = candidate.suffix.lower()
    name = candidate.name
    lower_name = name.lower()
    if suffix in SOURCE_EXTENSIONS or suffix in STYLE_EXTENSIONS:
        return True
    if name in MANIFESTS or name in DESIGN_DOC_NAMES:
        return True
    return any(lower_name.startswith(prefix) for prefix in CONFIG_PREFIXES)


def sha256_file(path: Path) -> str:
    if not path.is_file():
        return "missing"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def safe_repo_path(target: Path, token: str) -> str | None:
    token = token.strip().replace("\\", "/")
    if not token or token.startswith("/") or token.startswith(".DesignForge/"):
        return None
    candidate = Path(token)
    if ".." in candidate.parts:
        return None
    absolute = (target / candidate).resolve()
    try:
        absolute.relative_to(target.resolve())
    except ValueError:
        return None
    return candidate.as_posix()


def evidence_paths(target: Path) -> set[str]:
    codebase = target / ".DesignForge" / "codebase"
    paths: set[str] = set()
    for name in ARTIFACT_NAMES:
        artifact = codebase / name
        if not artifact.is_file():
            continue
        text = artifact.read_text(encoding="utf-8")
        evidence = section(text, "## Evidence index")
        for token in PATH_TOKEN_RE.findall(evidence):
            path = safe_repo_path(target, token)
            if path:
                paths.add(path)
    return paths


def render_state(commit: str | None, dirty: set[str] | None, digests: dict[str, str]) -> str:
    dirty_values = sorted(dirty or set())
    lines = [
        "# Mapping Freshness State",
        "",
        "> Generated by DesignForge. Refresh this file after a completed, provenance-validated map. Do not store design conclusions here.",
        "",
        "## Baseline",
        "",
        "- Schema: `1`",
        f"- Git commit: `{commit or 'unavailable'}`",
        f"- Relevant working-tree paths: `{len(dirty_values)}`",
        f"- Referenced source paths: `{len(digests)}`",
        "",
        "## Relevant working-tree paths",
        "",
    ]
    lines.extend(f"- `{path}`" for path in dirty_values) if dirty_values else lines.append("- None.")
    lines.extend(["", "## Source digests", ""])
    lines.extend(f"- `{path}`: `{digest}`" for path, digest in sorted(digests.items()))
    lines.extend(
        [
            "",
            "## Freshness contract",
            "",
            "A map is stale when a referenced source changes or disappears, when UI-relevant working-tree paths differ from this baseline, or when UI-relevant committed files changed since the mapped Git commit. Non-UI Git drift may be reported without invalidating the map.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_state(path: Path) -> tuple[str | None, set[str], dict[str, str]]:
    text = path.read_text(encoding="utf-8")
    commit: str | None = None
    dirty: set[str] = set()
    digests: dict[str, str] = {}
    current = ""
    for line in text.splitlines():
        if line.startswith("## "):
            current = line
            continue
        match = BASELINE_COMMIT_RE.match(line)
        if match:
            value = match.group(1)
            commit = None if value == "unavailable" else value
            continue
        if current == "## Relevant working-tree paths":
            match = DIRTY_PATH_RE.match(line)
            if match and match.group(1) != "None.":
                dirty.add(match.group(1))
        elif current == "## Source digests":
            match = DIGEST_LINE_RE.match(line)
            if match:
                digests[match.group(1)] = match.group(2)
    return commit, dirty, digests


def stamp(target: Path) -> list[str]:
    target = target.resolve()
    errors = validate(target)
    if errors:
        return errors
    referenced = evidence_paths(target)
    if not referenced:
        return ["no repository-relative evidence paths found in interpreted mapping artifacts"]

    dirty = git_worktree_paths(target)
    relevant_dirty = {path for path in (dirty or set()) if is_ui_relevant(path)}
    sources = referenced | relevant_dirty
    digests = {path: sha256_file(target / path) for path in sorted(sources)}
    missing = sorted(path for path in referenced if digests[path] == "missing")
    if missing:
        return ["referenced evidence path is missing: " + path for path in missing]

    destination = target / ".DesignForge" / "codebase" / MAP_STATE_NAME
    destination.write_text(render_state(git_commit(target), relevant_dirty if dirty is not None else None, digests), encoding="utf-8")
    return []


def check(target: Path) -> list[str]:
    target = target.resolve()
    state_path = target / ".DesignForge" / "codebase" / MAP_STATE_NAME
    if not state_path.is_file():
        return [".DesignForge/codebase/MAP_STATE.md not found; stamp mapping freshness after map"]
    try:
        baseline_commit, baseline_dirty, digests = parse_state(state_path)
    except (OSError, UnicodeDecodeError):
        return ["MAP_STATE.md could not be read"]
    if not digests:
        return ["MAP_STATE.md contains no source digests"]

    stale: list[str] = []
    for path, expected in sorted(digests.items()):
        actual = sha256_file(target / path)
        if actual != expected:
            stale.append(f"source changed: {path}")

    current_dirty = git_worktree_paths(target)
    if current_dirty is not None:
        relevant_dirty = {path for path in current_dirty if is_ui_relevant(path)}
        if relevant_dirty != baseline_dirty:
            added = sorted(relevant_dirty - baseline_dirty)
            removed = sorted(baseline_dirty - relevant_dirty)
            stale.extend(f"new UI-relevant working-tree change: {path}" for path in added)
            stale.extend(f"baseline UI-relevant working-tree change disappeared: {path}" for path in removed)

    current_commit = git_commit(target)
    if baseline_commit and current_commit and baseline_commit != current_commit:
        changed = git_changed_since(target, baseline_commit)
        if changed is None:
            stale.append("Git commit changed and relevant diff could not be verified")
        else:
            stale.extend(
                f"UI-relevant committed change since mapping: {path}"
                for path in sorted(path for path in changed if is_ui_relevant(path))
            )

    return stale


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stamp or verify DesignForge mapping freshness")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("stamp", "check"):
        sub = subparsers.add_parser(command)
        sub.add_argument("target", nargs="?", default=".")
    args = parser.parse_args(argv)
    target = Path(args.target)

    errors = stamp(target) if args.command == "stamp" else check(target)
    if errors:
        for error in errors:
            print(f"stale: {error}" if args.command == "check" else f"error: {error}", file=sys.stderr)
        return 1

    if args.command == "stamp":
        print("DesignForge mapping freshness baseline stamped")
    else:
        print("DesignForge mapping freshness check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
