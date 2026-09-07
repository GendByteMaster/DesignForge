#!/usr/bin/env python3
"""Provider-neutral renderer adapter runner for DesignForge Visual QA."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

from visual_qa import EVIDENCE_SUFFIXES, has_declared_render_signature, normalize_capture_value

PROTOCOL_VERSION = "designforge-render-adapter-v1"
STAGING_DIRNAME = "render-staging"
DEFAULT_TIMEOUT_SECONDS = 60


def cleanup(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except OSError:
        pass


def parse_result(stdout: str) -> tuple[dict[str, object] | None, str | None]:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, "renderer adapter produced no JSON result"
    try:
        payload = json.loads(lines[-1])
    except json.JSONDecodeError as exc:
        return None, f"renderer adapter result is not valid JSON: {exc}"
    if not isinstance(payload, dict):
        return None, "renderer adapter result must be a JSON object"
    return payload, None


def resolve_artifact(output_dir: Path, token: object) -> Path | None:
    if not isinstance(token, str) or not token.strip():
        return None
    raw = Path(token.strip())
    candidate = raw if raw.is_absolute() else output_dir / raw
    try:
        resolved = candidate.resolve()
        resolved.relative_to(output_dir.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def run_adapter(
    target: Path,
    command: list[str],
    surface: str,
    state: str,
    viewport: str,
    phase: str | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[Path | None, list[str]]:
    target = target.resolve()
    if not target.is_dir():
        return None, [f"target directory does not exist: {target}"]
    if not (target / ".DesignForge" / "STATE.md").is_file():
        return None, [".DesignForge/STATE.md not found; run init first"]
    if timeout < 1:
        return None, ["renderer adapter timeout must be greater than zero"]

    normalized_surface, error = normalize_capture_value("surface", surface)
    if error:
        return None, [error]
    normalized_state, error = normalize_capture_value("state", state)
    if error:
        return None, [error]
    normalized_viewport, error = normalize_capture_value("viewport", viewport)
    if error:
        return None, [error]

    command = list(command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        return None, ["renderer adapter command is required"]

    if phase:
        phase_dir = target / ".DesignForge" / "phases" / phase
        if not phase_dir.is_dir():
            return None, [f"phase directory not found: .DesignForge/phases/{phase}"]

    staging_root = target / ".DesignForge" / STAGING_DIRNAME
    run_dir = staging_root / uuid.uuid4().hex
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        return None, [f"failed to create renderer staging directory: {exc}"]

    env = os.environ.copy()
    env.update(
        {
            "DESIGNFORGE_RENDER_PROTOCOL": PROTOCOL_VERSION,
            "DESIGNFORGE_TARGET": str(target),
            "DESIGNFORGE_SURFACE": normalized_surface or "",
            "DESIGNFORGE_STATE": normalized_state or "",
            "DESIGNFORGE_VIEWPORT": normalized_viewport or "",
            "DESIGNFORGE_PHASE": phase or "",
            "DESIGNFORGE_OUTPUT_DIR": str(run_dir),
        }
    )

    try:
        completed = subprocess.run(
            command,
            cwd=target,
            env=env,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except FileNotFoundError:
        cleanup(run_dir)
        return None, [f"renderer adapter executable not found: {command[0]}"]
    except subprocess.TimeoutExpired:
        cleanup(run_dir)
        return None, [f"renderer adapter timed out after {timeout} seconds"]
    except OSError as exc:
        cleanup(run_dir)
        return None, [f"renderer adapter failed to start: {exc}"]

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        cleanup(run_dir)
        suffix = f": {detail[-1000:]}" if detail else ""
        return None, [f"renderer adapter exited with code {completed.returncode}{suffix}"]

    payload, parse_error = parse_result(completed.stdout)
    if parse_error:
        cleanup(run_dir)
        return None, [parse_error]
    assert payload is not None

    if payload.get("protocol") != PROTOCOL_VERSION:
        cleanup(run_dir)
        return None, [f"renderer adapter must return protocol '{PROTOCOL_VERSION}'"]

    artifact = resolve_artifact(run_dir, payload.get("artifact"))
    if artifact is None:
        cleanup(run_dir)
        return None, ["renderer adapter artifact must resolve inside DESIGNFORGE_OUTPUT_DIR"]
    if artifact.suffix.lower() not in EVIDENCE_SUFFIXES:
        cleanup(run_dir)
        return None, [f"renderer adapter produced unsupported render format: {artifact.suffix or '<none>'}"]
    if not artifact.is_file():
        cleanup(run_dir)
        return None, ["renderer adapter artifact was not created"]
    try:
        if artifact.stat().st_size == 0:
            cleanup(run_dir)
            return None, ["renderer adapter artifact is empty"]
    except OSError as exc:
        cleanup(run_dir)
        return None, [f"renderer adapter artifact cannot be inspected: {exc}"]
    if not has_declared_render_signature(artifact):
        cleanup(run_dir)
        return None, ["renderer adapter artifact has invalid render signature"]

    return artifact, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a DesignForge renderer adapter without registering inspected evidence")
    parser.add_argument("target", nargs="?", default=".")
    parser.add_argument("--surface", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--viewport", required=True)
    parser.add_argument("--phase")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--adapter", nargs=argparse.REMAINDER, required=True)
    args = parser.parse_args(argv)

    artifact, errors = run_adapter(
        Path(args.target),
        args.adapter,
        args.surface,
        args.state,
        args.viewport,
        args.phase,
        args.timeout,
    )
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    assert artifact is not None
    print(f"Render artifact: {artifact}")
    print("Inspect this artifact before registering it with 'designforge visual capture'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
