# Workflow: map

Map an existing product UI before redesign work.

## Goal

Create a trustworthy UI-focused view of the codebase so later design decisions are grounded in repository reality and can be detected when they become stale.

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

Use the canonical provenance-aware templates under `designforge/assets/codebase/` when creating these artifacts. Each interpreted mapping artifact separates `Verified findings`, `Inferences`, `Unknowns`, and an `Evidence index`.

After interpreted mapping has passed provenance validation, DesignForge may create:

- `MAP_STATE.md` — generated mechanical freshness baseline for the verified map; not a design artifact.

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
13. Write interpreted findings using the mapping provenance contract:
    - source-confirmed facts under `Verified findings`;
    - agent interpretation under `Inferences`;
    - material gaps under `Unknowns`;
    - repository-relative source/test/render evidence under `Evidence index`.
14. When interpreted mapping artifacts exist and the validator is available, run:

   ```bash
   python designforge/scripts/validate_mapping_artifacts.py /path/to/project
   ```

   Fix structural provenance failures before declaring mapping complete. Passing this validator confirms the document contract and presence of evidence references; it does not prove semantic correctness.
15. After provenance validation passes and the source evidence has been rechecked, stamp the mapping freshness baseline:

   ```bash
   python designforge/scripts/designforge.py mapping stamp /path/to/project
   ```

   This writes `.DesignForge/codebase/MAP_STATE.md` with content digests for cited sources and interpreted mapping artifacts, plus a Git/UI-change baseline when Git is available.
16. Immediately verify the stamped baseline when practical:

   ```bash
   python designforge/scripts/designforge.py mapping check /path/to/project
   ```
17. Update `STATE.md` with mapping completion, material concerns, and next workflow.

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

## Provenance boundary

The provenance validator is intentionally mechanical. It can verify that interpreted mapping documents use the required sections and that substantive verified list items have at least one path-like reference in the evidence index. It cannot determine whether the cited source actually proves the finding.

Therefore:

- never use validator success as a substitute for source inspection;
- never cite `EVIDENCE.md` alone as proof of an inferred architecture or design defect;
- prefer stable repository paths plus symbols/selectors/routes/tests over fragile line-only citations;
- re-check mappings after material codebase changes before reusing them in a redesign plan.

## Freshness boundary

`MAP_STATE.md` detects mechanical reasons a saved interpreted map may no longer represent repository reality. A freshness check becomes stale when, for example:

- a cited source file changes or disappears;
- an interpreted mapping artifact changes after the baseline was stamped;
- the set of UI-relevant working-tree changes differs from the stamped baseline;
- UI-relevant committed files changed after the mapped Git commit.

A different Git commit alone is not enough to invalidate the map. Non-UI drift such as documentation-only commits should not make the map stale when no mapped source or UI-relevant path changed.

Freshness is also available without Git: cited source and mapping-artifact content digests still protect the baseline.

If `mapping check` reports stale state:

1. do not simply restamp the existing conclusions;
2. inspect the reported source/UI changes;
3. refresh only the affected interpreted mapping areas when possible;
4. rerun provenance validation;
5. stamp a new baseline only after the affected findings are current again.

For older `.DesignForge/` workspaces with interpreted maps but no `MAP_STATE.md`, freshness is unknown rather than automatically invalid. If later workflows depend on the map, validate and stamp it before treating it as current.

## Rules

- Do not redesign while mapping unless the user explicitly asks for immediate fixes.
- Do not infer architectural facts from filenames alone when code can verify them.
- Distinguish design debt from intentional product constraints.
- Avoid exhaustive low-value inventories. Focus on elements that affect redesign decisions.
- Repository reality overrides stale `.DesignForge/codebase/` documents.
- Generated `EVIDENCE.md` may be refreshed by the scanner; do not store durable human decisions there.
- Generated `MAP_STATE.md` is a freshness baseline; do not store design conclusions or user decisions there.
- Never recursively inspect generated/dependency directories merely to increase manifest recall.
- Never promote an inference to verified only because it appears plausible.
- Never restamp a stale map merely to silence a freshness failure.

## Completion

Mapping is complete when a new agent can answer:

- how the current interface is structured;
- which application/package manifests define the relevant UI surface;
- what the dominant UI primitives are;
- where styling conventions live;
- which screens and flows matter most;
- where design/system debt is concentrated;
- what must be preserved or migrated during redesign;
- which statements are verified, inferred, or still unknown;
- which repository evidence supports each substantive verified finding.

When interpreted mapping artifacts exist and the relevant tooling is available:

- provenance validation must pass;
- `MAP_STATE.md` must be stamped only after source reinspection;
- an immediate freshness check should pass before the mapping workflow is marked complete.
