# Workflow: map

Map an existing product UI before redesign work.

## Goal

Create a trustworthy UI-focused view of the codebase so later design decisions are grounded in repository reality.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- package/project manifests
- route definitions
- layout/shell files
- styling configuration
- reusable UI primitives
- important screens/views
- existing design-system documentation when present

## Writes

Create only useful files under `.DesignForge/codebase/`, typically:

- `STACK.md`
- `UI_ARCHITECTURE.md`
- `COMPONENTS.md`
- `STYLES.md`
- `SCREENS.md`
- `CONCERNS.md`

Update `.DesignForge/STATE.md`.

## Procedure

1. Load current project and state.
2. Identify framework, styling system, UI libraries, routing, state management, animation libraries, icon system, fonts, and relevant build/test tooling.
3. Map the application shell and navigation model.
4. Identify major screens, reusable components, feature-level components, and overlay systems.
5. Inspect current tokens, CSS variables, theme configuration, spacing, radii, typography, borders, elevation, and motion conventions.
6. Identify duplicated or competing component implementations.
7. Identify hardcoded styling where a shared system should exist.
8. Identify UX/design risks with evidence:
   - weak hierarchy;
   - nested card-heavy layouts;
   - inconsistent spacing/radius/elevation;
   - inaccessible controls;
   - broken or unclear focus states;
   - responsive failures;
   - duplicate dialogs/menus/popovers;
   - unclear navigation or information architecture.
9. Map important screens and what users are trying to accomplish on each.
10. Record evidence, not vague aesthetic criticism.
11. Update `STATE.md` with mapping completion, material concerns, and next workflow.

## Rules

- Do not redesign while mapping unless the user explicitly asks for immediate fixes.
- Do not infer architectural facts from filenames alone when code can verify them.
- Distinguish design debt from intentional product constraints.
- Avoid exhaustive low-value inventories. Focus on elements that affect redesign decisions.
- Repository reality overrides stale `.DesignForge/codebase/` documents.

## Completion

Mapping is complete when a new agent can answer:

- how the current interface is structured;
- what the dominant UI primitives are;
- where styling conventions live;
- which screens and flows matter most;
- where design/system debt is concentrated;
- what must be preserved or migrated during redesign.
