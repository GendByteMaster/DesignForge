# Visual QA Evidence Contract

DesignForge uses persistent render evidence to distinguish actual visual inspection from claims based only on source code, compilation, or tests.

## Scope

Visual QA may be product-wide or phase-scoped.

Product-wide artifact:

` .DesignForge/reviews/VISUAL_QA.md `

Phase-scoped artifact:

` .DesignForge/phases/<phase>/VISUAL_QA.md `

Associated render evidence lives beside the artifact in a `visual-evidence/` directory.

## Canonical commands

Create a product-wide visual QA artifact:

```bash
python designforge/scripts/designforge.py visual init /path/to/project
```

Create a phase-scoped visual QA artifact:

```bash
python designforge/scripts/designforge.py visual init /path/to/project --phase 01-main-workspace
```

Validate product-wide evidence:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project
```

Validate phase-scoped evidence:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project --phase 01-main-workspace
```

## Capture matrix

Each inspected render is recorded as a checked capture item containing:

- surface;
- state;
- viewport or native form factor;
- project-relative evidence path.

Mark an item checked only after the referenced render artifact was actually inspected.

Supported evidence formats are:

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`
- `.mp4`
- `.webm`

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

## Mechanical validation

The validator checks:

- required Visual QA sections;
- valid verdict status;
- presence of a capture-matrix item;
- checked captures contain non-placeholder surface, state, viewport, and evidence values;
- evidence paths are project-relative and do not escape the project;
- evidence uses a supported render format;
- referenced evidence exists and is non-empty;
- conclusive visual verdicts are backed by at least one inspected capture.

The validator does not judge visual quality, design taste, accessibility correctness, or whether a screenshot semantically proves a finding. Those remain agent inspection responsibilities.

## Workflow rules

During `build` and `review`:

1. render the affected state using whatever provider/runtime is available;
2. save the render artifact under the appropriate `visual-evidence/` directory;
3. inspect the artifact;
4. mark the capture checked only after inspection;
5. record findings and accessibility observations;
6. fix material defects when the workflow permits implementation;
7. re-render affected states after fixes;
8. set the final verdict;
9. run `designforge visual validate` before claiming visual QA completed.

Do not claim that visual QA passed merely because source code looks correct, tests pass, or the application builds.

## Provider neutrality

DesignForge intentionally does not require Playwright, a specific browser, emulator, simulator, screenshot API, or desktop runtime. The renderer is an adapter supplied by the current environment. The persistent `VISUAL_QA.md` contract and evidence validator remain the same across providers.
