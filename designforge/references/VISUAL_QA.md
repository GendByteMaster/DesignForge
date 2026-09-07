# Visual QA Evidence Contract

DesignForge uses persistent render evidence to distinguish actual visual inspection from claims based only on source code, compilation, or tests.

## Scope

Visual QA may be product-wide or phase-scoped.

Product-wide artifact:

` .DesignForge/reviews/VISUAL_QA.md `

Product-wide evidence directory:

` .DesignForge/reviews/visual-evidence/ `

Phase-scoped artifact:

` .DesignForge/phases/<phase>/VISUAL_QA.md `

Phase-scoped evidence directory:

` .DesignForge/phases/<phase>/visual-evidence/ `

Checked captures must reference evidence inside the managed `visual-evidence/` directory associated with that Visual QA artifact. Do not point a checked capture at unrelated images or media elsewhere in the project.

## Canonical commands

Create a product-wide visual QA artifact:

```bash
python designforge/scripts/designforge.py visual init /path/to/project
```

Create a phase-scoped visual QA artifact:

```bash
python designforge/scripts/designforge.py visual init /path/to/project --phase 01-main-workspace
```

Import and register an inspected product-wide render:

```bash
python designforge/scripts/designforge.py visual capture /tmp/render.png /path/to/project \
  --surface "Application Shell" \
  --state "default" \
  --viewport "1440x900"
```

Import and register an inspected phase-scoped render:

```bash
python designforge/scripts/designforge.py visual capture /tmp/render.png /path/to/project \
  --surface "Main Workspace" \
  --state "focus" \
  --viewport "1440x900" \
  --phase 01-main-workspace
```

Set a validated verdict:

```bash
python designforge/scripts/designforge.py visual verdict pass /path/to/project --phase 01-main-workspace
```

Validate product-wide evidence:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project
```

Validate phase-scoped evidence:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project --phase 01-main-workspace
```

## Capture handoff

`visual capture` is the provider-neutral boundary between renderer-specific tooling and DesignForge persistent evidence.

The renderer may be a browser automation tool, emulator, simulator, native preview, screenshot API, desktop automation runtime, or any other environment capable of producing a supported image/video file. The renderer does not need to know DesignForge's internal directory layout.

Call `visual capture` only after inspecting the exact source render. Registration creates a checked capture row, so invoking the command is an explicit claim that the supplied artifact was reviewed.

The capture handoff:

- normalizes and validates surface, state, and viewport labels;
- rejects reserved Markdown delimiters that could corrupt the capture-matrix format;
- requires a supported media extension;
- rejects missing, empty, or invalid-signature media before scaffolding review state;
- initializes the appropriate Visual QA artifact when needed;
- copies external media into the matching managed `visual-evidence/` directory;
- never overwrites an existing managed capture; collisions receive a stable numeric suffix;
- records a project-relative evidence path;
- replaces the initial placeholder capture row when possible, otherwise appends a new checked row;
- validates the resulting Visual QA contract and rolls back the document/copy when registration would leave invalid state.

A renderer may also produce a file directly inside the managed evidence directory. In that case the handoff can register the existing file without making a second copy.

## Capture matrix

Each inspected render is recorded as a checked capture item containing:

- surface;
- state;
- viewport or native form factor;
- project-relative evidence path.

Mark an item checked only after the referenced render artifact was actually inspected. When using `visual capture`, inspection must happen before the command because the command writes the checked state automatically.

Supported evidence formats are:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`
- `.mp4`
- `.webm`

The file extension is not trusted by itself. DesignForge also performs a bounded magic-byte sanity check for the declared media format. This is intentionally lightweight and does not replace full image or video decoding.

## Verdicts

Allowed verdict status values:

- `pending`
- `pass`
- `pass-with-notes`
- `fail`
- `blocked`
- `unavailable`

`pass`, `pass-with-notes`, and `fail` require at least one checked capture backed by a real, non-empty render artifact.

`blocked` or `unavailable` may be used when the runtime cannot render or inspect the relevant surface. They must not be presented as successful visual validation.

Use `visual verdict` as the canonical status write path. It updates the verdict, immediately validates the complete Visual QA artifact, and restores the previous status if the requested verdict is not supported by the evidence contract. This prevents a failed `pass`/`fail` attempt from leaving persistent state in a contradictory condition.

## Mechanical validation

The validator checks:

- required Visual QA sections;
- valid verdict status;
- presence of a capture-matrix item;
- checked captures contain non-placeholder surface, state, viewport, and evidence values;
- evidence paths are project-relative and do not escape the project;
- evidence lives inside the managed `visual-evidence/` directory for the active product-wide or phase-scoped Visual QA artifact;
- evidence uses a supported render format;
- referenced evidence exists and is non-empty;
- evidence header bytes match the declared render format at a lightweight signature level;
- conclusive visual verdicts are backed by at least one inspected capture.

The validator does not judge visual quality, design taste, accessibility correctness, whether a screenshot semantically proves a finding, or whether media is fully decodable. Those remain agent inspection responsibilities.

## Workflow rules

During `build` and `review`:

1. render the affected state using whatever provider/runtime is available;
2. inspect that exact render before making an inspected-evidence claim;
3. hand the render to `designforge visual capture`, which persists it under the correct managed `visual-evidence/` directory and registers the checked capture;
4. record findings and accessibility observations;
5. fix material defects when the workflow permits implementation;
6. re-render and re-inspect affected states after fixes;
7. register fresh captures for materially changed states rather than relying on stale evidence;
8. set the final status with `designforge visual verdict`;
9. run `designforge visual validate` before claiming visual QA completed.

Do not claim that visual QA passed merely because source code looks correct, tests pass, or the application builds.

## Provider neutrality

DesignForge intentionally does not require Playwright, a specific browser, emulator, simulator, screenshot API, or desktop runtime. The renderer is an adapter supplied by the current environment. The public `visual capture` handoff means renderer adapters only need to produce a supported media file; DesignForge owns persistence, capture registration, path safety, and mechanical evidence validation.

This separation keeps the persistent `VISUAL_QA.md` contract identical across providers while allowing future browser/native capture adapters to remain thin and replaceable.
