# DesignForge

DesignForge is a persistent, agent-driven design workflow for creating, implementing, reviewing, and evolving original software product interfaces and design systems.

## Status

DesignForge is under active development.

Current development branch: `dev/master`.

Roadmap: [Issue #1 — DesignForge v0.1 persistent design workflow engine](https://github.com/GendByteMaster/DesignForge/issues/1)

## Architecture

DesignForge intentionally separates the distributable skill package from project-local runtime state:

- `designforge/` — portable Agent Skills package distributed with DesignForge.
- `.DesignForge/` — persistent design memory created inside a target software project.

This keeps the design workflow provider-neutral while allowing each coding agent to discover the same skill package through its own project-local skills directory.

## Skill package

```text
designforge/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── PROJECT.md
│   ├── STATE.md
│   ├── ROADMAP.md
│   ├── DESIGN.md
│   ├── DESIGN_SYSTEM.md
│   ├── codebase/
│   │   ├── STACK.md
│   │   ├── UI_ARCHITECTURE.md
│   │   ├── COMPONENTS.md
│   │   ├── STYLES.md
│   │   ├── SCREENS.md
│   │   └── CONCERNS.md
│   └── reviews/
│       └── VISUAL_QA.md
├── references/
│   ├── WORKFLOW.md
│   ├── STATE_MACHINE.md
│   ├── ARTIFACTS.md
│   └── VISUAL_QA.md
├── scripts/
│   ├── designforge.py
│   ├── evidence_scanner.py
│   ├── installer.py
│   ├── install_skill.py
│   ├── mapping_freshness.py
│   ├── state_machine.py
│   ├── validate_mapping_artifacts.py
│   ├── validate_skill_package.py
│   └── visual_qa.py
└── workflows/
    ├── INIT.md
    ├── MAP.md
    ├── DISCUSS.md
    ├── DIRECT.md
    ├── SYSTEMIZE.md
    ├── PLAN.md
    ├── BUILD.md
    ├── REVIEW.md
    ├── CONTINUE.md
    └── GUARD.md
```

`SKILL.md` keeps portable skill metadata limited to `name` and `description`. OpenAI-specific interface metadata lives separately in `agents/openai.yaml` so provider details do not leak into the core skill contract.

## Coding-agent installation

DesignForge currently supports explicit **project-local** installation for Codex and Claude Code.

### Codex

```bash
python designforge/scripts/install_skill.py codex /path/to/project
```

Installs a real copy of the skill at:

```text
/path/to/project/.agents/skills/designforge/
```

### Claude Code

```bash
python designforge/scripts/install_skill.py claude /path/to/project
```

Installs a real copy of the skill at:

```text
/path/to/project/.claude/skills/designforge/
```

The installer does not use symlinks. Existing installations are preserved by default. To intentionally replace an existing project-local copy:

```bash
python designforge/scripts/install_skill.py codex /path/to/project --force
```

Replacement is staged before the existing installation is swapped, reducing the chance of leaving a partially copied skill behind.

Global/user installation is intentionally not part of this v0.1 layer yet. Project-local paths are explicit and reproducible; user-level Codex conventions are still evolving, so DesignForge does not hardcode an ambiguous global destination.

## Lifecycle

```text
DISCOVER
  ↓
UNDERSTAND
  ↓
DIRECT
  ↓
SYSTEMIZE
  ↓
PLAN
  ↓
DESIGN
  ↓
IMPLEMENT
  ↓
INSPECT
  ↓
ITERATE
  ↓
VERIFY
  ↓
GUARD
```

The lifecycle is resumable. A workflow may skip stages that are already complete and valid, but it must not silently bypass prerequisites that materially affect design quality.

## Core principles

- **Product before pixels** — understand users, workflows, platform, density, and constraints before styling.
- **Original direction, not cloned products** — references inform principles rather than becoming templates.
- **Persistent state over chat memory** — durable decisions live in `.DesignForge/`.
- **Design system by default** — tokens, components, states, layout, motion, and accessibility are first-class contracts.
- **Accessibility is a hard constraint** — visual originality must not reduce usability or semantics.
- **Visual QA requires evidence** — when rendering is available, visual claims must be backed by inspected persistent render artifacts rather than compilation or source inspection alone.
- **Progressive context loading** — load `STATE.md`, the active phase, and only relevant design contracts.
- **Guard against design drift** — recent changes should be checked against the active design system and Design DNA.
- **Evidence before conclusions** — deterministic scanners may collect repository signals, but agents must verify relevant source before turning signals into design findings.
- **Provenance before persistence** — durable mapping separates verified facts, inferences, unknowns, and the repository evidence supporting verified findings.
- **Freshness before reuse** — a structurally valid map is not assumed current forever; DesignForge can detect when its cited sources, mapping artifacts, or relevant UI code changed.

## Runtime workspace

A target project may progressively create a workspace such as:

```text
.DesignForge/
├── PROJECT.md
├── STATE.md
├── ROADMAP.md
├── DESIGN.md
├── DESIGN_SYSTEM.md
├── codebase/
│   ├── EVIDENCE.md
│   ├── MAP_STATE.md
│   ├── STACK.md
│   ├── UI_ARCHITECTURE.md
│   ├── COMPONENTS.md
│   ├── STYLES.md
│   ├── SCREENS.md
│   └── CONCERNS.md
├── research/
├── system/
├── phases/
│   └── 01-main-workspace/
│       ├── CONTEXT.md
│       ├── RESEARCH.md
│       ├── PLAN.md
│       ├── DESIGN.md
│       ├── IMPLEMENTATION.md
│       ├── REVIEW.md
│       ├── RESULT.md
│       ├── VISUAL_QA.md
│       └── visual-evidence/
└── reviews/
    ├── VISUAL_QA.md
    └── visual-evidence/
```

Not every file or directory should be created immediately. DesignForge creates artifacts only when they become useful.

### Core runtime artifacts

- `PROJECT.md` — product context, users, workflows, platforms, constraints, redesign mode, and non-negotiable behavior.
- `STATE.md` — concise resume pointer for the current workflow and phase.
- `ROADMAP.md` — project-specific design implementation phases.
- `DESIGN.md` — canonical design thesis and Design DNA.
- `DESIGN_SYSTEM.md` — high-level design-system contract.
- `codebase/EVIDENCE.md` — refreshable scanner output containing observable repository signals, not durable design conclusions.
- interpreted `codebase/*.md` maps — durable source-verified codebase understanding with explicit provenance and uncertainty boundaries.
- `codebase/MAP_STATE.md` — generated freshness baseline for interpreted mapping; contains mechanical hashes/Git state, not design decisions.
- `reviews/VISUAL_QA.md` or `phases/<phase>/VISUAL_QA.md` — persistent visual inspection contract and verdict.
- sibling `visual-evidence/` — managed screenshots or render recordings referenced by checked Visual QA captures.

## Operational toolkit

DesignForge includes a dependency-free Python CLI for deterministic workspace operations. The agent workflows remain the design intelligence layer; the CLI handles mechanical state, evidence collection, provenance support, mapping freshness, and Visual QA evidence validation that should not depend on prompt behavior.

Requirements: Python 3.11+.

### Initialize a project

```bash
python designforge/scripts/designforge.py init /path/to/project --mode refactor
```

`init` creates only the minimum persistent workspace:

```text
.DesignForge/
├── PROJECT.md
└── STATE.md
```

It is idempotent by default. Existing root artifacts are preserved. Use `--force` only when intentionally resetting DesignForge-managed root templates.

### Move through workflows safely

Use `transition` for normal lifecycle progress:

```bash
python designforge/scripts/designforge.py transition map \
  --target /path/to/project
```

The state machine rejects non-standard jumps that would skip major workflow prerequisites. Iterative loops such as `build -> review -> build` remain allowed.

Use an explicit forced transition only for an intentional recovery path:

```bash
python designforge/scripts/designforge.py transition guard \
  --target /path/to/project \
  --force
```

See [`designforge/references/STATE_MACHINE.md`](designforge/references/STATE_MACHINE.md) for the transition graph.

### Collect codebase evidence

During the `map` workflow, DesignForge can collect deterministic repository evidence:

```bash
python designforge/scripts/designforge.py scan /path/to/project
```

The scanner refreshes:

```text
.DesignForge/codebase/EVIDENCE.md
```

It currently records bounded, observable signals such as:

- root and bounded nested project manifests;
- known frontend framework/package families aggregated from discovered `package.json` files;
- UI library, styling, motion, icon, and state-management package signals;
- application entry/shell candidates such as `App.tsx`, `main.tsx`, `main.dart`, and similar conventional entry files;
- relevant source/style extension counts;
- likely component, screen/route, style/theme/token paths;
- common frontend configuration files;
- simple CSS counts for color literals, custom properties, radii, shadows, and `!important`.

Manifest discovery reuses the same bounded repository inventory as the rest of the scanner. Known manifests are considered at the repository root and up to three directories below it, which supports common multi-stack layouts such as `desktop/package.json` and `apps/web/package.json` without starting a separate unbounded recursive search. Malformed nested package manifests are reported with their repository-relative path.

The scanner excludes common dependency/generated directories such as `.git`, `.DesignForge`, `node_modules`, `.next`, `dist`, `build`, `coverage`, `target`, and vendor environments. It also applies file-count, manifest-count, manifest-depth, and file-size limits so repository inspection remains bounded.

`EVIDENCE.md` is intentionally **not** a design audit. A package being installed does not prove it is actively used; a color literal does not automatically mean design-system drift; an entry candidate does not prove it is the active application shell; and a package found in one nested app does not automatically describe every UI surface in a multi-stack repository. The `map` workflow must verify relevant source files before creating durable findings in `STACK.md`, `UI_ARCHITECTURE.md`, `COMPONENTS.md`, `STYLES.md`, `SCREENS.md`, or `CONCERNS.md`.

### Interpreted mapping provenance

The six canonical mapping templates under `designforge/assets/codebase/` use the same minimal contract:

```text
Scope
Verified findings
Inferences
Unknowns
Evidence index
```

This prevents repository facts from being silently mixed with agent assumptions. A verified finding should be an explicit Markdown list item and must be traceable to repository-relative evidence. Inferences remain interpretations until confirmed, and unresolved gaps remain visible under `Unknowns`.

Validate interpreted mapping artifacts with:

```bash
python designforge/scripts/validate_mapping_artifacts.py /path/to/project
```

The validator is deliberately read-only. It checks the document contract and requires path-like provenance when substantive verified findings exist. It does **not** decide whether a cited source actually proves a finding, so source inspection remains the agent's responsibility.

### Stamp and check mapping freshness

After interpreted mapping has been source-checked and provenance validation passes, create a freshness baseline:

```bash
python designforge/scripts/designforge.py mapping stamp /path/to/project
```

This creates:

```text
.DesignForge/codebase/MAP_STATE.md
```

The baseline records SHA-256 digests for cited source files and interpreted mapping artifacts. When Git is available, it also records the mapped commit and UI-relevant working-tree state.

Before a later workflow reuses the saved map as current truth, check it:

```bash
python designforge/scripts/designforge.py mapping check /path/to/project
```

A map is reported stale when, for example:

- a cited source changed or disappeared;
- an interpreted mapping artifact changed after the stamp;
- UI-relevant working-tree changes diverged from the baseline;
- UI-relevant committed files changed after the mapped commit.

A Git commit changing by itself is not enough to invalidate the map. Documentation-only commits such as README changes do not make mapping stale unless mapped/UI-relevant evidence also changed.

Freshness still works without Git through content digests. Older workspaces that have interpreted mapping but no `MAP_STATE.md` should be treated as freshness-unknown; inspect, validate, and stamp them before relying on those maps.

If a freshness check fails, do not simply stamp again. Reinspect the reported changes, refresh the affected mapping findings, rerun provenance validation, and only then create a new baseline.

### Create a phase

```bash
python designforge/scripts/designforge.py phase "Main Workspace" --target /path/to/project
```

This creates a numbered phase such as:

```text
.DesignForge/phases/01-main-workspace/
├── CONTEXT.md
├── RESEARCH.md
├── PLAN.md
├── DESIGN.md
├── IMPLEMENTATION.md
├── REVIEW.md
└── RESULT.md
```

and moves `STATE.md` to the new phase planning state. Phase-scoped `VISUAL_QA.md` and `visual-evidence/` are created only when visual inspection becomes relevant.

### Record and validate Visual QA

Visual QA is provider-neutral. DesignForge does not require one browser, screenshot API, simulator, emulator, or native preview provider. The active runtime renders the UI; DesignForge persists and validates the evidence contract.

Initialize product-wide Visual QA:

```bash
python designforge/scripts/designforge.py visual init /path/to/project
```

This creates:

```text
.DesignForge/reviews/
├── VISUAL_QA.md
└── visual-evidence/
```

For an active phase:

```bash
python designforge/scripts/designforge.py visual init /path/to/project --phase 01-main-workspace
```

After rendering and inspecting the affected states, save evidence under the associated managed `visual-evidence/` directory, mark only actually inspected captures as checked, set an accurate verdict, and validate it:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project
```

or:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project --phase 01-main-workspace
```

A conclusive verdict (`pass`, `pass-with-notes`, or `fail`) requires at least one checked capture backed by managed render evidence. Mechanical validation checks that the evidence path is project-relative, remains inside the associated `visual-evidence/` directory, uses a supported format, exists, is non-empty, and has a lightweight media signature matching the declared PNG/JPEG/GIF/WebP/MP4/WebM format.

The validator deliberately does not judge visual quality, accessibility correctness, screenshot semantics, or full media decodability. Those remain agent inspection responsibilities. If the runtime cannot render or inspect the UI, record `blocked` or `unavailable` rather than claiming successful visual validation.

See [`designforge/references/VISUAL_QA.md`](designforge/references/VISUAL_QA.md) for the complete evidence contract.

### Low-level state recovery

`state` intentionally bypasses the transition graph and exists for recovery, stale-state repair, or explicit manual overrides:

```bash
python designforge/scripts/designforge.py state \
  --target /path/to/project \
  --workflow build \
  --status in-progress \
  --phase 01-main-workspace
```

Normal workflow progress should use `transition` instead.

Supported redesign modes:

- `conservative`
- `refactor`
- `reimagine`

Supported workflows:

- `init`
- `map`
- `discuss`
- `direct`
- `systemize`
- `plan`
- `build`
- `review`
- `continue`
- `guard`

## Validation

Validate runtime/workflow structure:

```bash
python designforge/scripts/designforge.py validate
```

Validate the canonical portable Agent Skills package and OpenAI interface metadata:

```bash
python designforge/scripts/validate_skill_package.py
```

Validate interpreted mapping provenance in a target project:

```bash
python designforge/scripts/validate_mapping_artifacts.py /path/to/project
```

Check whether an already-stamped interpreted map is still current:

```bash
python designforge/scripts/designforge.py mapping check /path/to/project
```

Validate product-wide Visual QA evidence:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project
```

Validate phase-scoped Visual QA evidence:

```bash
python designforge/scripts/designforge.py visual validate /path/to/project --phase 01-main-workspace
```

Validate runtime structure plus a target project's persistent workspace:

```bash
python designforge/scripts/designforge.py validate --target /path/to/project
```

Validation covers:

- canonical `SKILL.md` metadata;
- required `agents/openai.yaml` interface metadata;
- required workflow, asset, reference, and script resources;
- required provenance-aware mapping templates and their common sections;
- presence of the mapping provenance validator and freshness checker in the portable skill package;
- mapping evidence presence for substantive verified findings;
- required Visual QA template, validator, and reference contract resources;
- Visual QA document structure, verdict values, managed evidence containment, supported render formats, non-empty evidence, and lightweight media signatures when `visual validate` is run;
- valid mode/workflow/status values;
- agreement between `PROJECT.md` and `STATE.md` redesign modes;
- existence of an active phase directory when one is referenced.

Mapping freshness and Visual QA remain explicit checks rather than unconditional global workspace-validation failures because implementation work can intentionally stale a map and not every runtime can render every UI surface.

## Redesign modes

DesignForge supports three freedom levels:

- `conservative` — preserve information architecture and major layouts while improving the visual system.
- `refactor` — allow hierarchy, layout, component, and interaction changes while preserving core product flows.
- `reimagine` — preserve required product capabilities and business logic while allowing a new UX architecture and visual system.

## Workflow playbooks

- `init` — initialize `.DesignForge/` and establish persistent project state.
- `map` — collect evidence, inspect source, produce provenance-aware interpreted maps, and stamp a freshness baseline.
- `discuss` — persist design decisions, constraints, preferences, and rejected directions.
- `direct` — create or refine the product-specific visual/UX direction.
- `systemize` — translate the direction into design-system contracts.
- `plan` — build a bounded, visually verifiable roadmap and phase plan.
- `build` — implement the active phase, produce render evidence when tooling allows, and perform technical + visual validation.
- `review` — perform evidence-based visual, UX, accessibility, and system review using persistent render evidence when available.
- `continue` — resume from persistent state with minimal rediscovery and verify required mapping freshness before reuse.
- `guard` — detect design-system drift in recent or proposed UI changes.

## Development verification

CI validates the operational and installation layers on Python 3.11, 3.12, and 3.13.

Local checks:

```bash
python -m py_compile designforge/scripts/designforge.py
python -m py_compile designforge/scripts/state_machine.py
python -m py_compile designforge/scripts/evidence_scanner.py
python -m py_compile designforge/scripts/installer.py
python -m py_compile designforge/scripts/install_skill.py
python -m py_compile designforge/scripts/validate_skill_package.py
python -m py_compile designforge/scripts/validate_mapping_artifacts.py
python -m py_compile designforge/scripts/mapping_freshness.py
python -m py_compile designforge/scripts/visual_qa.py
python designforge/scripts/designforge.py validate
python designforge/scripts/validate_skill_package.py
python -m unittest discover -s tests -v
```

The test suite includes:

- persistent workspace initialization and idempotency;
- workflow state transitions and forced recovery;
- phase scaffolding;
- deterministic UI/codebase evidence scanning, including bounded nested manifests and entry/shell candidates;
- generated/dependency directory exclusion and nested-manifest depth limits;
- provenance-aware mapping artifact validation;
- verified-finding evidence requirements and uncertainty-section contracts;
- mapping freshness stamp/check behavior;
- public `designforge mapping stamp|check` CLI coverage;
- cited source and interpreted mapping artifact digest invalidation;
- UI-relevant committed/worktree freshness detection;
- non-UI Git drift false-positive protection;
- non-Git digest-based freshness behavior;
- product-wide and phase-scoped Visual QA scaffolding;
- public `designforge visual init|validate` CLI coverage;
- conclusive Visual QA verdict evidence requirements;
- managed visual-evidence path containment;
- supported PNG/JPEG/GIF/WebP/MP4/WebM signature checks and fake-media rejection;
- Codex and Claude project-local skill installation;
- installation conflict/force behavior;
- an end-to-end lifecycle against a representative React/Vite-style project fixture.

End-to-end mapping lifecycle:

```text
init
  -> map
  -> scan evidence
  -> verify source
  -> validate mapping provenance
  -> stamp mapping freshness
  -> check mapping freshness
  -> direct
```

Main design lifecycle then continues through:

```text
direct
  -> systemize
  -> phase/plan
  -> build
  -> render/capture when available
  -> visual validate
  -> review
  -> guard
  -> validate
```

## Current development focus

The v0.1 foundation now includes persistent artifacts, idempotent initialization, phase scaffolding, deterministic workflow transitions, structural validation, bounded multi-stack UI/codebase evidence collection, provenance-aware interpreted mapping, mapping freshness baselines and stale-map detection, canonical skill-package validation, project-local Codex/Claude installation, provider-neutral persistent Visual QA evidence contracts, product-wide and phase-scoped Visual QA CLI operations, managed render-evidence validation, CI, and an end-to-end lifecycle test.

The next major proof point is **renderer/capture adapter integration**: environments with browser, screenshot, emulator, simulator, or native-app tooling should be able to produce managed Visual QA evidence automatically, while DesignForge keeps the core workflow and evidence contract provider-neutral. That layer should exercise real rendered states end-to-end and make it easier for `build` and `review` to close the render -> inspect -> fix -> re-render loop without hardcoding one rendering provider.
