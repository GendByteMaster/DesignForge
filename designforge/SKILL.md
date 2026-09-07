---
name: designforge
description: "Design and redesign software product interfaces using a persistent, file-backed workflow. Use for greenfield UI creation, visual/UX redesigns, design-system generation, UI architecture, design tokens, component systems, responsive behavior, accessibility, motion, visual QA, and design-drift review in software projects."
---

# DesignForge

DesignForge is a persistent design-engineering workflow for creating, implementing, reviewing, and evolving original software product interfaces.

The user's explicit instructions always take precedence over this skill. Do not allow DesignForge guidance to block or override a clear user request.

## Core outcome

Do not treat UI work as "write frontend code and make it look good." Build a coherent chain from product intent to rendered interface:

`understand -> direct -> systemize -> plan -> implement -> inspect -> iterate -> verify -> guard`

For existing products, first understand the current UI architecture and constraints. For greenfield products, establish product and platform context before choosing a visual direction.

## Persistent project workspace

DesignForge stores durable project-specific design context in a project-local `.DesignForge/` directory.

At minimum, workflows may create and maintain:

- `PROJECT.md` — product purpose, users, workflows, constraints, platform, redesign mode.
- `STATE.md` — small resumable workflow state; keep concise enough to load every run.
- `ROADMAP.md` — design-oriented implementation phases derived from the project.
- `DESIGN.md` — canonical design thesis and Design DNA.
- `DESIGN_SYSTEM.md` — high-level design-system contract.
- `codebase/` — UI-focused mapping of an existing project.
- `research/` — product, users, platform, and reference analysis.
- `system/` — detailed tokens, components, layout, motion, and accessibility contracts.
- `phases/` — phase context, plans, implementation notes, reviews, results, and phase-scoped visual evidence.
- `reviews/` — product-wide visual, accessibility, consistency, drift, and visual-evidence reviews.

Create artifacts progressively. Do not generate every possible file when it would add noise.

See [workflow reference](references/WORKFLOW.md), [artifact contracts](references/ARTIFACTS.md), and [visual QA evidence contract](references/VISUAL_QA.md).

## Redesign freedom modes

Use one explicit mode and persist it in `.DesignForge/PROJECT.md` and `.DesignForge/STATE.md`:

- `conservative` — preserve information architecture and major layouts; improve the visual system.
- `refactor` — allow hierarchy, layout, component, and interaction changes while preserving core product flows.
- `reimagine` — preserve required capabilities and business logic, but allow a new UX architecture and visual system.

If the user clearly requests a level of freedom, use it. If not, infer the least destructive mode that still satisfies the task and record the assumption.

## Design direction

Before broad implementation, create or update `.DesignForge/DESIGN.md` with a concrete design thesis and Design DNA.

Describe the direction using explicit axes such as:

- density;
- geometry;
- contrast;
- depth;
- typography character;
- motion character;
- chrome;
- color character;
- information hierarchy;
- interaction character.

Originality must come from product reasoning, not random styling. References may inform principles but must not be copied pixel-for-pixel or used as a substitute for product-specific decisions.

## Design-system policy

Define a coherent system before large-scale UI implementation. Prefer token layering:

`primitive -> semantic -> component`

Define only the domains the product actually needs, including where relevant:

- color;
- typography;
- spacing;
- radius;
- border;
- elevation;
- opacity;
- motion;
- breakpoints;
- component contracts;
- layout patterns;
- accessibility rules.

When choosing implementation primitives, prefer:

`platform/native primitive -> existing project component -> existing accessible UI library -> accessible headless primitive -> custom component`

Do not introduce a parallel design system without a documented reason.

## Anti-generic rules

Do not default to a generic AI-generated SaaS aesthetic.

Avoid unless justified by the product direction:

- oversized hero typography;
- excessive cards or nested cards;
- arbitrary glassmorphism;
- decorative gradients;
- excessive roundness;
- gratuitous shadows;
- decorative animation;
- icon-only controls with unclear meaning;
- hardcoded one-off colors or spacing values when tokens exist.

Layout must derive from user workflows and information density, not from a generic dashboard template.

## Accessibility

Accessibility is a design constraint, not a final polish pass.

Preserve or improve, where applicable:

- semantic roles and accessible names;
- keyboard navigation;
- visible focus;
- focus order and focus trapping;
- contrast;
- interactive target size;
- error and status communication;
- disabled and loading semantics;
- reduced-motion behavior;
- screen-reader-relevant state.

Do not trade accessibility for visual originality.

## Visual QA

A visual phase is not complete merely because code compiles or tests pass.

When browser, emulator, simulator, screenshot, or other render-inspection tooling is available:

1. initialize product-wide or phase-scoped Visual QA with `designforge visual init`;
2. render the affected UI;
3. save render evidence beside `VISUAL_QA.md` under the corresponding `visual-evidence/` directory;
4. inspect hierarchy, spacing, alignment, typography, contrast, density, component states, responsive behavior, and obvious accessibility problems;
5. mark a capture checked only after the referenced render artifact was actually inspected;
6. compare the result against `.DesignForge/DESIGN.md` and relevant system contracts;
7. record findings and accessibility observations;
8. fix material defects when the active workflow permits implementation;
9. re-render affected states after fixes;
10. set an accurate Visual QA verdict and run `designforge visual validate` before claiming visual QA completed.

`pass`, `pass-with-notes`, and `fail` require at least one checked capture backed by a real, non-empty render artifact. Compilation, tests, or source inspection alone are not visual evidence.

When visual tooling is unavailable, use an explicit `blocked` or `unavailable` verdict and record the limitation instead of pretending visual validation occurred.

The render provider is intentionally not fixed. Use browser, native preview, emulator, simulator, screenshot, or equivalent tooling available in the current runtime while keeping the same persistent evidence contract.

See [visual QA evidence contract](references/VISUAL_QA.md).

## Workflow selection

Use the smallest workflow that satisfies the task:

- initialize or adopt DesignForge -> `init`;
- understand an existing UI codebase -> `map`;
- capture decisions and constraints -> `discuss`;
- create/refine visual direction -> `direct`;
- create design-system contracts -> `systemize`;
- create roadmap or phase plan -> `plan`;
- implement the active phase -> `build`;
- inspect existing work without unrelated implementation -> `review`;
- resume from persistent state -> `continue`;
- detect design-system drift in recent changes -> `guard`.

Detailed lifecycle and transition rules are in [references/WORKFLOW.md](references/WORKFLOW.md).

## Context discipline

Do not load all `.DesignForge/` documents on every run.

Always prefer:

1. `STATE.md`;
2. current task or phase context;
3. only the design-system references relevant to the affected area;
4. affected source files;
5. broader research or history only when necessary.

Keep `STATE.md` concise and update it after meaningful workflow transitions.

## Completion rule

Before declaring design work complete, verify that:

- the requested scope is implemented;
- the result follows the active design direction;
- relevant tokens and component contracts are respected;
- responsive behavior was considered when applicable;
- accessibility constraints were not knowingly regressed;
- visual inspection was performed when tooling allowed it;
- any claimed conclusive visual verdict is backed by persistent inspected render evidence and passes `designforge visual validate`;
- phase review/result artifacts are current;
- `STATE.md` accurately describes what is complete and what remains.
