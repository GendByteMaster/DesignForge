#!/usr/bin/env python3
"""Safe lifecycle helpers for DesignForge renderer staging artifacts."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path

STAGING_DIRNAME = "render-staging"
RUN_ID_PATTERN = re.compile(r"^[0-9a-f]{32}$")


@dataclass(frozen=True)
class StagingRun:
    run_id: str
    path: Path
    modified_at: float
    size_bytes: int


def _workspace_ready(target: Path) -> tuple[Path | None, list[str]]:
    target = target.resolve()
    if not target.is_dir():
        return None, [f"target directory does not exist: {target}"]
    workspace = target / ".DesignForge"
    if not (workspace / "STATE.md").is_file():
        return None, [".DesignForge/STATE.md not found; run init first"]
    return workspace, []


def staging_root(target: Path) -> Path:
    return target.resolve() / ".DesignForge" / STAGING_DIRNAME


def _safe_run_dir(root: Path, run_id: str) -> Path | None:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        return None
    candidate = root / run_id
    if not candidate.exists() or candidate.is_symlink() or not candidate.is_dir():
        return None
    try:
        resolved = candidate.resolve(strict=True)
        if resolved.parent != root.resolve(strict=False):
            return None
    except OSError:
        return None
    return candidate


def _directory_size(path: Path) -> int:
    total = 0
    try:
        for child in path.rglob("*"):
            if child.is_symlink() or not child.is_file():
                continue
            try:
                total += child.stat().st_size
            except OSError:
                continue
    except OSError:
        return total
    return total


def list_runs(target: Path) -> tuple[list[StagingRun], list[str]]:
    workspace, errors = _workspace_ready(target)
    if errors:
        return [], errors
    assert workspace is not None
    root = workspace / STAGING_DIRNAME
    if not root.exists():
        return [], []
    if root.is_symlink() or not root.is_dir():
        return [], [f".DesignForge/{STAGING_DIRNAME} must be a real directory"]

    runs: list[StagingRun] = []
    try:
        children = list(root.iterdir())
    except OSError as exc:
        return [], [f"failed to inspect renderer staging directory: {exc}"]

    for child in children:
        run_dir = _safe_run_dir(root, child.name)
        if run_dir is None:
            continue
        try:
            modified_at = run_dir.stat().st_mtime
        except OSError:
            continue
        runs.append(
            StagingRun(
                run_id=run_dir.name,
                path=run_dir,
                modified_at=modified_at,
                size_bytes=_directory_size(run_dir),
            )
        )

    runs.sort(key=lambda item: item.modified_at, reverse=True)
    return runs, []


def clean_runs(
    target: Path,
    *,
    run_id: str | None = None,
    older_than_hours: float | None = None,
    all_runs: bool = False,
    now: float | None = None,
) -> tuple[list[str], list[str]]:
    selectors = int(run_id is not None) + int(older_than_hours is not None) + int(all_runs)
    if selectors != 1:
        return [], ["choose exactly one cleanup selector: --run, --older-than-hours, or --all"]
    if older_than_hours is not None and older_than_hours < 0:
        return [], ["--older-than-hours must be zero or greater"]

    runs, errors = list_runs(target)
    if errors:
        return [], errors

    root = staging_root(target)
    selected: list[StagingRun] = []
    if run_id is not None:
        if not RUN_ID_PATTERN.fullmatch(run_id):
            return [], ["renderer staging run id must be a 32-character lowercase hex value"]
        run_dir = _safe_run_dir(root, run_id)
        if run_dir is None:
            return [], [f"renderer staging run not found or unsafe: {run_id}"]
        selected = [run for run in runs if run.run_id == run_id]
        if not selected:
            return [], [f"renderer staging run not found or unsafe: {run_id}"]
    elif all_runs:
        selected = runs
    else:
        assert older_than_hours is not None
        reference = time.time() if now is None else now
        cutoff = reference - (older_than_hours * 3600)
        selected = [run for run in runs if run.modified_at <= cutoff]

    removed: list[str] = []
    for run in selected:
        safe_dir = _safe_run_dir(root, run.run_id)
        if safe_dir is None:
            return removed, [f"renderer staging run became unsafe before deletion: {run.run_id}"]
        try:
            shutil.rmtree(safe_dir)
        except OSError as exc:
            return removed, [f"failed to remove renderer staging run {run.run_id}: {exc}"]
        removed.append(run.run_id)

    try:
        if root.is_dir() and not root.is_symlink() and not any(root.iterdir()):
            root.rmdir()
    except OSError:
        pass

    return removed, []


def _print_runs(runs: list[StagingRun]) -> None:
    if not runs:
        print("No renderer staging runs")
        return
    for run in runs:
        age_seconds = max(0, int(time.time() - run.modified_at))
        print(f"{run.run_id}\t{run.size_bytes}\t{age_seconds}s\t{run.path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect and explicitly clean DesignForge renderer staging runs")
    subparsers = parser.add_subparsers(dest="action", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("target", nargs="?", default=".")

    clean_parser = subparsers.add_parser("clean")
    clean_parser.add_argument("target", nargs="?", default=".")
    selector = clean_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--run")
    selector.add_argument("--older-than-hours", type=float)
    selector.add_argument("--all", action="store_true")

    args = parser.parse_args(argv)
    target = Path(args.target)

    if args.action == "list":
        runs, errors = list_runs(target)
        if errors:
            for error in errors:
                print(f"error: {error}", file=sys.stderr)
            return 1
        _print_runs(runs)
        return 0

    removed, errors = clean_runs(
        target,
        run_id=args.run,
        older_than_hours=args.older_than_hours,
        all_runs=args.all,
    )
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    if removed:
        for run_id in removed:
            print(f"Removed renderer staging run: {run_id}")
    else:
        print("No renderer staging runs matched the cleanup selector")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
