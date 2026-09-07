# DesignForge

DesignForge is a persistent, agent-driven design workflow for creating, implementing, reviewing, and evolving original software product interfaces and design systems.

## Status

DesignForge is under active development.

Current development branch: `dev/master`.

Roadmap: [Issue #1 — DesignForge v0.1 persistent design workflow engine](https://github.com/GendByteMaster/DesignForge/issues/1)

## Architecture

DesignForge intentionally separates the distributable skill package from project-local runtime state:

- `designforge/` — Agent Skills-compatible package distributed with DesignForge.
- `.DesignForge/` — persistent design memory created inside a target software project.

This keeps the skill reusable while allowing each product to maintain its own design context, roadmap, decisions, system contracts, reviews, and resumable state.

## Skill package

```text
designforge/
├── SKILL.md
├── assets/
│   ├── PROJECT.md
│   ├── STATE.md
│   ├── ROADMAP.md
│   ├── DESIGN.md
│   └── DESIGN_SYSTEM.md
├── references/
│   ├── WORKFLOW.md
│   └── ARTIFACTS.md
├── scripts/
│   └── designforge.py
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
- **Visual QA is required when tooling allows** — compiling is not enough for visual work.
- **Progressive context loading** — load `STATE.md`, the active phase, and only relevant design contracts.
- **Guard against design drift** — recent changes should be checked against the active design system and Design DNA.

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
├── research/
├── system/
├── phases/
└── reviews/
```

Not every file or directory should be created immediately. DesignForge creates artifacts only when they become useful.

### Core runtime artifacts

- `PROJECT.md` — product context, users, workflows, platforms, constraints, redesign mode, and non-negotiable behavior.
- `STATE.md` — concise resume pointer for the current workflow and phase.
- `ROADMAP.md` — project-specific design implementation phases.
- `DESIGN.md` — canonical design thesis and Design DNA.
- `DESIGN_SYSTEM.md` — high-level design-system contract.

## Operational toolkit

DesignForge includes a dependency-free Python CLI for deterministic workspace operations. The agent workflows remain the design intelligence layer; the CLI handles mechanical state that should not depend on prompt behavior.

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

and moves `STATE.md` to the new phase planning state.

### Update workflow state

```bash
python designforge/scripts/designforge.py state \
  --target /path/to/project \
  --workflow build \
  --status in-progress \
  --phase 01-main-workspace
```

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

### Validate

Validate the DesignForge skill package:

```bash
python designforge/scripts/designforge.py validate
```

Validate the skill package and a target project's persistent workspace:

```bash
python designforge/scripts/designforge.py validate --target /path/to/project
```

Validation currently checks the core Skill metadata, required workflow/assets, and the runtime `PROJECT.md`/`STATE.md` state contract.

## Redesign modes

DesignForge supports three freedom levels:

- `conservative` — preserve information architecture and major layouts while improving the visual system.
- `refactor` — allow hierarchy, layout, component, and interaction changes while preserving core product flows.
- `reimagine` — preserve required product capabilities and business logic while allowing a new UX architecture and visual system.

## Workflow playbooks

- `init` — initialize `.DesignForge/` and establish persistent project state.
- `map` — inspect and map an existing UI/codebase.
- `discuss` — persist design decisions, constraints, preferences, and rejected directions.
- `direct` — create or refine the product-specific visual/UX direction.
- `systemize` — translate the direction into design-system contracts.
- `plan` — build a bounded, visually verifiable roadmap and phase plan.
- `build` — implement the active phase and perform technical + visual validation.
- `review` — perform evidence-based visual, UX, accessibility, and system review.
- `continue` — resume from persistent state with minimal rediscovery.
- `guard` — detect design-system drift in recent or proposed UI changes.

## Development verification

CI validates the operational layer on Python 3.11, 3.12, and 3.13.

Local checks:

```bash
python -m py_compile designforge/scripts/designforge.py
python designforge/scripts/designforge.py validate
python -m unittest discover -s tests -v
```

## Current development focus

The v0.1 foundation now includes both the persistent Markdown workflow model and the first deterministic operational toolkit. The next layer is deeper state validation, workflow/state transition rules, installation/adoption guidance for coding agents, and an end-to-end test against a representative software project before the first PR to `master`.
