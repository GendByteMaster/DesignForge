# Workflow: map

Map an existing product UI before redesign work.

## Goal

Create a trustworthy UI-focused view of the codebase so later design decisions are grounded in repository reality.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- `.DesignForge/codebase/EVIDENCE.md` when generated
- package/project manifests
- route definitions
- layout/shell files
- styling configuration
- reusable UI primitives
- important screens/views
- existing design-system documentation when present

## Writes

The deterministic scanner may create:

- `EVIDENCE.md` — generated repository signals only; not a design audit.

The agent creates only useful interpreted files under `.DesignForge/codebase/`, typically:

- `STACK.md`
- `UI_ARCHITECTURE.md`
- `COMPONENTS.md`
- `STYLES.md`
- `SCREENS.md`
- `CONCERNS.md`

Update `.DesignForge/STATE.md`.

## Procedure

1. Load current project and state.
2. When repository filesystem access and Python are available, collect deterministic evidence first:

   ```bash
   python designforge/scripts/designforge.py scan /path/to/project
   ```

   This refreshes `.DesignForge/codebase/EVIDENCE.md` with observable signals such as manifests, known package families, UI-related file extensions, likely component/screen/style locations, and simple CSS statistics.
3. Treat generated evidence as a navigation aid, not as a conclusion. Verify relevant source files directly before making architectural or design claims.
4. Identify framework, styling system, UI libraries, routing, state management, animation libraries, icon system, fonts, and relevant build/test tooling.
5. Map the application shell and navigation model.
6. Identify major screens, reusable components, feature-level components, and overlay systems.
7. Inspect current tokens, CSS variables, theme configuration, spacing, radii, typography, borders, elevation, and motion conventions.
8. Identify duplicated or competing component implementations.
9. Identify hardcoded styling where a shared system should exist.
10. Identify UX/design risks with evidence:
    - weak hierarchy;
    - nested card-heavy layouts;
    - inconsistent spacing/radius/elevation;
    - inaccessible controls;
    - broken or unclear focus states;
    - responsive failures;
    - duplicate dialogs/menus/popovers;
    - unclear navigation or information architecture.
11. Map important screens and what users are trying to accomplish on each.
12. Record evidence, not vague aesthetic criticism.
13. Update `STATE.md` with mapping completion, material concerns, and next workflow.

## Evidence boundary

`EVIDENCE.md` deliberately reports facts such as:

- a package is present in `package.json`;
- a CSS file contains a number of color literals or custom properties;
- files exist under likely component, route, screen, style, theme, or token directories.

Those facts do **not** by themselves prove that:

- a color literal is a design-system violation;
- a component is duplicated or reusable;
- a route candidate is user-facing;
- a shadow/radius value is visually wrong;
- a library is actively used rather than merely installed.

The agent must inspect relevant implementation before promoting scanner signals into `STACK.md`, `COMPONENTS.md`, `STYLES.md`, `SCREENS.md`, or `CONCERNS.md`.

## Rules

- Do not redesign while mapping unless the user explicitly asks for immediate fixes.
- Do not infer architectural facts from filenames alone when code can verify them.
- Distinguish design debt from intentional product constraints.
- Avoid exhaustive low-value inventories. Focus on elements that affect redesign decisions.
- Repository reality overrides stale `.DesignForge/codebase/` documents.
- Generated `EVIDENCE.md` may be refreshed by the scanner; do not store durable human decisions there.

## Completion

Mapping is complete when a new agent can answer:

- how the current interface is structured;
- what the dominant UI primitives are;
- where styling conventions live;
- which screens and flows matter most;
- where design/system debt is concentrated;
- what must be preserved or migrated during redesign.
