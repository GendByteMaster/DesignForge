# DesignForge Artifact Contracts

DesignForge stores durable project-specific design context under `.DesignForge/` in the target software project.

Artifacts are contracts, not diaries. Keep them concise, current, and useful to future agent runs.

## Core artifacts

### PROJECT.md

Purpose: canonical product context.

Required sections when applicable:

- Product purpose
- Target users
- Primary user jobs
- Main workflows
- Target platforms
- Technical constraints
- Product constraints
- Redesign freedom mode
- Non-negotiable behavior
- Open assumptions

Update when product-level facts or constraints materially change.

### STATE.md

Purpose: smallest durable resume pointer.

Recommended fields:

- Current phase
- Current workflow
- Mode
- Status
- Completed
- Current focus
- Known blockers/issues
- Next

Rules:

- Keep short enough to load on every run.
- Do not copy full implementation summaries or review reports into it.
- Prefer references to phase artifacts when detail is needed.
- Repository reality wins if `STATE.md` becomes stale; repair state rather than trusting stale text.

### ROADMAP.md

Purpose: project-specific design implementation sequence.

Each phase should define:

- outcome;
- scope;
- dependencies;
- visual/UX significance;
- verification expectations;
- status.

Do not force a generic ten-phase roadmap. Derive phases from the product architecture and user flows.

### DESIGN.md

Purpose: canonical design direction.

Recommended sections:

- Design thesis
- Experience principles
- Design DNA
- Visual hierarchy
- Layout philosophy
- Typography character
- Color character
- Depth/elevation strategy
- Motion character
- Responsive philosophy
- Accessibility implications
- Explicit anti-patterns
- Reference-derived principles
- Originality constraints

Design DNA should use explicit axes instead of vague style adjectives.

### DESIGN_SYSTEM.md

Purpose: high-level contract for the active design system.

Include:

- token architecture;
- component strategy;
- layout rules;
- state model;
- responsive rules;
- accessibility contract;
- motion contract;
- links to detailed `system/` artifacts.

## codebase/

Create for existing products when mapping is useful.

### STACK.md

Capture framework, styling system, UI libraries, routing, state management, animation libraries, icon system, fonts, and relevant build/test tooling.

### UI_ARCHITECTURE.md

Capture application shell, navigation model, page/view hierarchy, major UI boundaries, reusable primitives, and feature-level component structure.

### COMPONENTS.md

Inventory important reusable components. Identify duplicated implementations, competing primitives, inconsistent state models, and likely consolidation targets.

### STYLES.md

Capture current CSS variables/tokens, utility conventions, hardcoded values, spacing patterns, radius patterns, elevation/shadow patterns, and typography scales.

### SCREENS.md

Map important routes/views/screens, their purpose, major actions, and important responsive differences.

### CONCERNS.md

Record design debt and risk with evidence. Typical categories:

- duplicate components;
- hardcoded styling;
- weak visual hierarchy;
- nested card-heavy layouts;
- inconsistent spacing/radius/elevation;
- competing overlay systems;
- accessibility defects;
- responsive failures;
- stale or unused UI code.

## research/

Create only when research materially informs design decisions.

### PRODUCT.md

Product model, workflows, constraints, competitive context, and information-density implications.

### USERS.md

Relevant user goals, accessibility needs, usage context, expertise level, frequency, and interaction patterns.

### REFERENCES.md

Store extracted principles from screenshots, products, platform guidelines, moodboards, and visual references.

Do not store instructions to clone a reference. Record:

- observed principle;
- why it is relevant;
- how it should be adapted;
- what should explicitly not be copied.

### PLATFORM.md

Record platform-specific conventions and constraints that materially affect the product experience.

## system/

Create detail only for domains the product needs.

Suggested files:

- `TOKENS.md`
- `COLOR.md`
- `TYPOGRAPHY.md`
- `SPACING.md`
- `LAYOUT.md`
- `COMPONENTS.md`
- `PATTERNS.md`
- `MOTION.md`
- `ACCESSIBILITY.md`

### Token rules

Prefer a layered model where useful:

`primitive -> semantic -> component`

Avoid unnecessary component-level tokens when a semantic token already expresses the intent.

### Component contracts

For each important component, document relevant aspects:

- role;
- anatomy;
- variants;
- sizes;
- interaction states;
- focus behavior;
- disabled/loading behavior;
- keyboard behavior;
- responsive behavior;
- motion;
- accessibility requirements.

Only define components actually needed by the product.

## phases/<phase>/

Phase folders are working memory for bounded design implementation units.

### CONTEXT.md

Durable phase-specific decisions and non-negotiables.

### RESEARCH.md

Only research needed for this phase.

### PLAN.md

Implementation sequence, affected areas, dependencies, verification strategy, and visual review plan.

### DESIGN.md

Phase-level design decisions that refine the global design direction without contradicting it.

### IMPLEMENTATION.md

Useful implementation notes, file/component mapping, migration concerns, and technical constraints.

### REVIEW.md

Observed defects and review findings. Prefer severity plus evidence.

### RESULT.md

What was actually implemented, checks performed, visual inspection status, unresolved issues, and follow-up work.

## reviews/

Use for cross-phase or product-wide review.

Suggested files:

- `VISUAL_AUDIT.md`
- `ACCESSIBILITY.md`
- `CONSISTENCY.md`
- `DRIFT.md`

Do not duplicate identical findings across multiple review artifacts. Reference the canonical finding when practical.

## Artifact quality rules

Every artifact should be:

- current;
- scoped;
- evidence-based where possible;
- free of chat-only context;
- explicit about assumptions;
- readable by a new agent without conversation history.

Delete or consolidate artifacts that become redundant. Persistent context is valuable only when it remains trustworthy.
