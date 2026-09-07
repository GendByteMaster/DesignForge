# DesignForge Workflow

DesignForge is a resumable design-engineering workflow backed by `.DesignForge/` project artifacts.

## Lifecycle

The canonical lifecycle is:

`DISCOVER -> UNDERSTAND -> DIRECT -> SYSTEMIZE -> PLAN -> DESIGN -> IMPLEMENT -> INSPECT -> ITERATE -> VERIFY -> GUARD`

Workflows may skip stages that are already complete and valid for the current task, but they must not silently bypass prerequisites that materially affect design quality.

## Workflow contracts

### init

Purpose: adopt DesignForge in a project and create the minimum persistent state required to continue work later.

Steps:

1. Detect whether the project is greenfield or existing.
2. Detect whether `.DesignForge/` already exists.
3. Read existing project documentation and relevant configuration.
4. Determine or infer the redesign freedom mode: `conservative`, `refactor`, or `reimagine`.
5. Create `.DesignForge/PROJECT.md`.
6. Create a concise `.DesignForge/STATE.md`.
7. Create only the next artifacts required by the task; do not scaffold the entire tree without need.
8. Record unresolved assumptions explicitly.

Completion: `PROJECT.md` and `STATE.md` exist and are internally consistent.

### map

Purpose: understand an existing UI implementation before redesigning it.

Steps:

1. Load `STATE.md` and `PROJECT.md` when present.
2. Inspect framework, styling system, UI libraries, routes, major layouts, state management, icon system, fonts, animation tooling, and tests.
3. Map application shell, navigation, important screens, reusable components, design tokens, and styling conventions.
4. Identify duplicated components, hardcoded styling, inconsistent spacing/radius/elevation, accessibility risks, responsive problems, and weak hierarchy.
5. Write only useful documents under `.DesignForge/codebase/`.
6. Update `STATE.md` with mapping status and material concerns.

Completion: the agent can explain how the existing interface is structured and where redesign risk is concentrated.

### discuss

Purpose: capture decisions that should persist across sessions.

Steps:

1. Read the current product and phase state.
2. Extract explicit user decisions, preferences, constraints, non-negotiable behavior, and rejected directions.
3. Store durable project-wide decisions in `PROJECT.md` or `DESIGN.md`.
4. Store phase-specific decisions in `phases/<phase>/CONTEXT.md`.
5. Do not turn temporary implementation details into permanent design principles.

Completion: future agents can recover the decisions without reading chat history.

### direct

Purpose: create or refine an original product-specific visual and UX direction.

Steps:

1. Load product context, platform constraints, mapped UI concerns, and relevant references.
2. Derive design goals from user jobs and interaction density.
3. Evaluate plausible directions internally; do not force the user to choose between superficial style variants unless a choice is genuinely needed.
4. Define a concrete design thesis.
5. Define Design DNA axes.
6. Define explicit anti-patterns and originality constraints.
7. Extract principles from references instead of copying them.
8. Write or update `.DesignForge/DESIGN.md`.
9. Update `STATE.md`.

Completion: implementation decisions can be judged against a clear design direction.

### systemize

Purpose: turn the design direction into implementation contracts.

Steps:

1. Define token layers: primitive, semantic, component where useful.
2. Define relevant color, typography, spacing, radius, border, elevation, opacity, motion, and breakpoint rules.
3. Define required component contracts and states.
4. Define layout and interaction patterns.
5. Define project-specific accessibility requirements.
6. Prefer existing/native accessible primitives before custom components.
7. Write `DESIGN_SYSTEM.md` and only necessary files under `.DesignForge/system/`.

Completion: broad implementation can proceed without inventing styling conventions ad hoc.

### plan

Purpose: convert the design direction and system into an implementation roadmap.

Steps:

1. Derive phases from the real product architecture and user flows.
2. Prioritize foundations and high-leverage structural work before polish.
3. Identify dependencies between phases.
4. For the active phase, create `CONTEXT.md`, `PLAN.md`, and `DESIGN.md` only if each is useful.
5. Include implementation scope, verification strategy, and visual-review requirements.
6. Update `ROADMAP.md` and `STATE.md`.

Completion: the next implementation unit is bounded, testable, and visually reviewable.

### build

Purpose: implement the active design phase and close the code-to-render loop.

Steps:

1. Load `STATE.md`.
2. Load active phase context and only relevant design-system files.
3. Inspect affected source code before changing it.
4. Reuse existing/native accessible primitives when possible.
5. Implement the phase without unrelated redesign work.
6. Run available lint, type, unit, integration, or build checks relevant to the changed code.
7. Render and inspect the affected UI when visual tooling exists.
8. Record material defects in phase `REVIEW.md`.
9. Fix material defects and inspect again.
10. Write or update phase `RESULT.md`.
11. Update `STATE.md` with completed work and next action.

Completion: code, design intent, checks, and visual result agree closely enough for the phase to progress.

### review

Purpose: inspect existing design work without expanding implementation scope unnecessarily.

Review dimensions where relevant:

- visual hierarchy;
- layout and alignment;
- spacing rhythm;
- typography;
- color and contrast;
- component consistency;
- states and feedback;
- responsive behavior;
- accessibility;
- motion;
- design-system compliance;
- fidelity to Design DNA.

Write findings to the active phase `REVIEW.md` or `.DesignForge/reviews/` depending on scope.

Severity guidance:

- blocker — prevents correct use, accessibility, or intended workflow;
- major — materially harms hierarchy, consistency, responsiveness, or design direction;
- minor — polish issue with limited impact;
- note — observation or future improvement.

### continue

Purpose: resume work with minimal rediscovery.

Steps:

1. Read `STATE.md` first.
2. Validate that referenced phase/artifacts still exist.
3. Read the current phase and only necessary design contracts.
4. Inspect source changes that may have occurred since the last DesignForge run.
5. Continue from `Next` unless user instructions supersede it.
6. Repair stale state if repository reality and `STATE.md` disagree.

Completion: work resumes from durable project state instead of chat memory.

### guard

Purpose: detect design-system drift in recent or proposed changes.

Look for:

- hardcoded colors where semantic tokens exist;
- one-off spacing or radius values outside the system;
- duplicated components;
- inaccessible custom primitives;
- new modal/menu/popover systems without justification;
- typography drift;
- inconsistent component states;
- unnecessary gradients, glass, shadows, or decorative motion;
- responsive regressions;
- changes that contradict `DESIGN.md` or `DESIGN_SYSTEM.md`.

Guard should report evidence and recommended fixes. Do not rewrite unrelated code merely to satisfy stylistic preference.

## State transitions

`STATE.md` is the canonical resume pointer, not a verbose history log.

Update it when:

- the active workflow changes;
- a phase starts or finishes;
- the design mode changes;
- a material design decision changes;
- a blocker appears or is resolved;
- the next action changes.

Do not duplicate full review reports or implementation summaries inside `STATE.md`.

## Failure handling

If a prerequisite is missing:

- recover it from repository evidence when possible;
- record the assumption if inference is necessary;
- ask the user only when the missing decision would materially change the outcome and cannot be safely inferred.

If visual tooling is unavailable, continue with code and design-system validation but explicitly mark visual verification as not performed.

If existing project conventions conflict with the target design direction, document the conflict and choose an approach appropriate to the selected redesign mode.
