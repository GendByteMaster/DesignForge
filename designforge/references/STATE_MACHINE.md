# DesignForge State Machine

DesignForge separates design reasoning from deterministic workflow state management.

The Markdown workflows describe what an agent should reason about and produce. The operational state machine defines how the active workflow may move between those stages without accidentally skipping major prerequisites.

## Commands

Use `transition` for normal workflow progress:

```bash
python designforge/scripts/designforge.py transition map --target /path/to/project
```

Use `state` only as a low-level recovery or explicit override tool when repairing stale state or applying a deliberate manual correction:

```bash
python designforge/scripts/designforge.py state \
  --target /path/to/project \
  --workflow build \
  --status in-progress
```

`transition` validates the current workflow and rejects non-standard jumps unless `--force` is explicitly supplied.

## Normal transitions

| Current | Allowed next workflows |
| --- | --- |
| `init` | `map`, `discuss`, `direct`, `continue` |
| `map` | `discuss`, `direct`, `systemize`, `plan`, `continue` |
| `discuss` | `direct`, `systemize`, `plan`, `build`, `continue` |
| `direct` | `discuss`, `systemize`, `plan`, `continue` |
| `systemize` | `direct`, `plan`, `build`, `continue` |
| `plan` | `discuss`, `direct`, `systemize`, `build`, `continue` |
| `build` | `build`, `plan`, `review`, `continue` |
| `review` | `build`, `plan`, `guard`, `continue` |
| `continue` | any workflow except `init` |
| `guard` | `build`, `review`, `guard`, `continue` |

The graph intentionally contains bounded loops. Design work is iterative, so review may return to build, implementation may return to plan, and direction/system work may be revisited when new evidence requires it.

## Status values

The operational toolkit currently recognizes:

- `initialized`
- `ready`
- `in-progress`
- `blocked`
- `review`
- `complete`

Workflow and status are separate. For example, a project may be in workflow `review` with status `blocked`, or in workflow `guard` with status `complete`.

## Force transitions

Use `--force` only when the requested transition is intentional and the normal graph does not represent the recovery path:

```bash
python designforge/scripts/designforge.py transition guard \
  --target /path/to/project \
  --force
```

A forced transition should be treated as an explicit override, not as the normal lifecycle.

## Validation

`validate --target` checks runtime state integrity, including:

- required `.DesignForge/PROJECT.md` and `.DesignForge/STATE.md`;
- valid mode, workflow, and status values;
- agreement between `PROJECT.md` redesign mode and `STATE.md` mode;
- existence of the active phase directory when a phase is referenced.

The validator checks structural integrity. It does not decide whether the design itself is good; visual quality remains the responsibility of the design workflows and visual QA loop.
