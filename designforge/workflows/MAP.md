# Workflow: map

Map an existing product UI before redesign work.

## Goal

Create a trustworthy UI-focused view of the codebase so later design decisions are grounded in repository reality.

## Reads

- `.DesignForge/PROJECT.md`
- `.DesignForge/STATE.md`
- `.DesignForge/codebase/EVIDENCE.md` when generated
- package/project manifests, including bounded nested manifests in common multi-stack layouts
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

   This refreshes `.DesignForge/codebase/EVIDENCE.md` with observable signals such as bounded root/nested manifests, known package families, entry/shell candidates, UI-related file extensions, likely component/screen/style locations, and simple CSS statistics.
3. Treat generated evidence as a navigation aid, not as a conclusion. Verify relevant source files directly before making architectural or design claims.
4. Identify framework, styling system, UI libraries, routing, state management, animation libraries, icon system, fonts, and relevant build/test tooling.
5. For multi-stack or monorepo-style projects, identify which manifest belongs to the user-facing UI before assigning framework conclusions to the whole repository.
6. Map the application shell and navigation model. Use entry/shell candidates as starting points, then verify the actual composition in source.
7. Identify major screens, reusable components, feature-level components, and overlay systems.
8. Inspect current tokens, CSS variables, theme configuration, spacing, radii, typography, borders, elevation, and motion conventions.
9. Identify duplicated or competing component implementations.
10. Identify hardcoded styling where a shared system should exist, but do not treat every literal as drift without checking its context.
11. Identify UX/design risks with evidence:
    - weak hierarchy;
    - nested card-heavy layouts;
    - inconsistent spacing/radius/elevation;
    - inaccessible controls;
    - broken or unclear focus states;
    - responsive failures;
    - duplicate dialogs/menus/popovers;
    - unclear navigation or information architecture.
12. Map important screens and what users are trying to accomplish on each.
13. Record evidence, not vague aesthetic criticism.
14. Update `STATE.md` with mapping completion, material concerns, and next workflow.

## Scanner scope

The scanner intentionally reuses one bounded repository inventory rather than launching independent recursive searches for each signal.

Current manifest behavior:

- known manifests can be discovered at the repository root or up to three directories below it;
- common generated/dependency directories remain excluded before manifest discovery;
- manifest count, total file count, and text-file size are capped;
- nested `package.json` files contribute package-family evidence;
- malformed nested package manifests are reported as warnings with their repository-relative path;
- manifests deeper than the configured discovery depth are ignored rather than triggering unbounded traversal.

This supports common layouts such as:

```text
project/
├── Cargo.toml
└── desktop/
    └── package.json
```

and:

```text
project/
└── apps/
    └── web/
        └── package.json
```

without treating dependency trees as project structure.

## Evidence boundary

`EVIDENCE.md` deliberately reports facts such as:

- a package is present in a discovered `package.json`;
- a known application entry or shell filename exists;
- a CSS file contains a number of color literals or custom properties;
- files exist under likely component, route, screen, style, theme, or token directories.

Those facts do **not** by themselves prove that:

- a color literal is a design-system violation;
- an entry candidate is the active application shell;
- a component is duplicated or reusable;
- a route candidate is user-facing;
- a shadow/radius value is visually wrong;
- a library is actively used rather than merely installed;
- a package found in one nested app describes every UI surface in the repository.

The agent must inspect relevant implementation before promoting scanner signals into `STACK.md`, `COMPONENTS.md`, `STYLES.md`, `SCREENS.md`, or `CONCERNS.md`.

## Rules

- Do not redesign while mapping unless the user explicitly asks for immediate fixes.
- Do not infer architectural facts from filenames alone when code can verify them.
- Distinguish design debt from intentional product constraints.
- Avoid exhaustive low-value inventories. Focus on elements that affect redesign decisions.
- Repository reality overrides stale `.DesignForge/codebase/` documents.
- Generated `EVIDENCE.md` may be refreshed by the scanner; do not store durable human decisions there.
- Never recursively inspect generated/dependency directories merely to increase manifest recall.

## Completion

Mapping is complete when a new agent can answer:

- how the current interface is structured;
- which application/package manifests define the relevant UI surface;
- what the dominant UI primitives are;
- where styling conventions live;
- which screens and flows matter most;
- where design/system debt is concentrated;
- what must be preserved or migrated during redesign.
