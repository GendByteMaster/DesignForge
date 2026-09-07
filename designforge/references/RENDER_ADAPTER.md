# Renderer Adapter Contract

DesignForge renderer adapters provide a provider-neutral way to produce render artifacts for Visual QA without allowing the renderer itself to claim that visual inspection succeeded.

## Boundary

The adapter lifecycle is deliberately split into three steps:

1. `visual render` — run renderer-specific tooling and produce an uninspected staging artifact;
2. inspect — the agent or reviewer actually views that exact artifact;
3. `visual capture` — after inspection, persist it as checked DesignForge evidence.

A renderer adapter must never mark a capture as inspected and must never set a Visual QA verdict.

## Public command

```bash
python designforge/scripts/designforge.py visual render /path/to/project \
  --surface "Main Workspace" \
  --state "default" \
  --viewport "1440x900" \
  --adapter python /path/to/adapter.py
```

For a phase-scoped render:

```bash
python designforge/scripts/designforge.py visual render /path/to/project \
  --surface "Main Workspace" \
  --state "focus" \
  --viewport "1440x900" \
  --phase 01-main-workspace \
  --adapter python /path/to/adapter.py
```

`--adapter` consumes the remaining argv and must be the final DesignForge option. DesignForge invokes the argv directly with `shell=False`; it does not wrap the adapter in a shell command.

## Protocol

Current protocol identifier:

`designforge-render-adapter-v1`

DesignForge exposes the render request to the adapter through environment variables:

- `DESIGNFORGE_RENDER_PROTOCOL`
- `DESIGNFORGE_TARGET`
- `DESIGNFORGE_SURFACE`
- `DESIGNFORGE_STATE`
- `DESIGNFORGE_VIEWPORT`
- `DESIGNFORGE_PHASE`
- `DESIGNFORGE_OUTPUT_DIR`

`surface`, `state`, and `viewport` are normalized before the adapter starts. `DESIGNFORGE_PHASE` is empty for product-wide rendering.

The adapter must write its render artifact inside `DESIGNFORGE_OUTPUT_DIR` and print a JSON object as the final non-empty stdout line:

```json
{"protocol":"designforge-render-adapter-v1","artifact":"render.png"}
```

`artifact` may be relative to `DESIGNFORGE_OUTPUT_DIR` or an absolute path that still resolves inside that directory.

## Supported artifacts

The v1 runner accepts the same evidence media types as Visual QA:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`
- `.mp4`
- `.webm`

Before returning success, the runner verifies that the artifact:

- resolves inside its unique staging output directory;
- uses a supported extension;
- exists and is non-empty;
- passes the same bounded magic-byte sanity check used by Visual QA evidence validation.

The check does not fully decode media and must not be described as proof that the render is visually correct.

## Staging

Successful adapter runs produce artifacts under:

`.DesignForge/render-staging/<run-id>/`

Staging is intentionally separate from checked `visual-evidence/` directories. A staging artifact is only a candidate for inspection.

Invalid adapter runs remove their run-specific staging directory. Successful artifacts remain available so the agent can inspect the exact output before deciding whether to register it.

List managed staging runs with:

```bash
python designforge/scripts/designforge.py visual staging list /path/to/project
```

Cleanup is intentionally explicit and never occurs merely because rendering, capture, or validation succeeded:

```bash
python designforge/scripts/designforge.py visual staging clean /path/to/project \
  --run <run-id>
```

or:

```bash
python designforge/scripts/designforge.py visual staging clean /path/to/project \
  --older-than-hours 24
```

or, only when all pending managed staging runs may be discarded:

```bash
python designforge/scripts/designforge.py visual staging clean /path/to/project --all
```

Staging cleanup operates only on canonical direct-child run directories. Unknown entries and symbolic links are not managed runs, and persistent `visual-evidence/` is never part of staging cleanup.

See [render staging lifecycle](RENDER_STAGING.md) for the complete safety contract.

## Adapter result rules

A valid adapter must:

- exit with status `0`;
- emit a final-line JSON object;
- return the exact supported protocol identifier;
- point to one artifact inside the supplied output directory.

DesignForge rejects:

- missing executables;
- timeouts;
- non-zero exits;
- malformed result JSON;
- protocol mismatches;
- path escapes outside the staging directory;
- missing/empty artifacts;
- unsupported extensions;
- invalid declared media signatures.

## Inspection handoff

After `visual render` succeeds, the agent must inspect the returned `Render artifact` before calling `visual capture`.

Example handoff after inspection:

```bash
python designforge/scripts/designforge.py visual capture \
  /path/to/project/.DesignForge/render-staging/<run-id>/render.png \
  /path/to/project \
  --surface "Main Workspace" \
  --state "default" \
  --viewport "1440x900"
```

`visual capture` copies the inspected artifact into the appropriate managed evidence directory and writes the checked capture row. This separation is a core integrity rule: render generation and visual-inspection claims are different operations.

After successful capture, the original staging run may be removed explicitly. Removing the staging source must not remove the persistent captured evidence.

## Provider neutrality

Adapters can wrap any renderer capable of producing one supported media artifact, including:

- browser automation;
- screenshot services;
- desktop automation;
- Flutter/native previews;
- emulators and simulators;
- project-specific render harnesses.

DesignForge core does not require Playwright, Selenium, Flutter tooling, Xcode, Android tooling, or any other renderer dependency. Provider-specific adapters remain optional and replaceable.

## Security and execution model

The adapter command is explicit local argv supplied by the caller. DesignForge does not discover and execute arbitrary commands automatically and does not use `shell=True`.

Adapters should be treated as executable project tooling. Do not run untrusted adapters merely because a project contains an adapter-shaped file.

## v1 non-goals

The v1 contract does not:

- auto-discover adapters;
- install browser/native dependencies;
- judge visual quality;
- inspect the artifact on behalf of the agent;
- register checked evidence automatically;
- set verdicts;
- define provider-specific authentication or session management.

Those responsibilities stay outside the portable renderer boundary or belong to future optional adapter layers.
