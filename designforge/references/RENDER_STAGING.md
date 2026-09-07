# Render Staging Lifecycle

## Scope

Render staging stores renderer-adapter output that has not yet been promoted to persistent inspected Visual QA evidence.

Staging is temporary operational state under:

`.DesignForge/render-staging/<run-id>/`

Staging artifacts are never equivalent to checked Visual QA evidence. An agent must inspect the exact artifact and register it through `designforge visual capture` before making inspected-evidence claims.

## Managed run identity

A managed staging run uses a direct child directory whose name is a 32-character lowercase hexadecimal UUID token.

DesignForge only treats directories matching that identity as managed runs. Unknown files, unknown directories, nested aliases, and symbolic links are not staging runs and must not be deleted by staging cleanup.

## Listing

Use the main CLI:

`designforge visual staging list <target>`

The command reports managed run ids, approximate stored bytes, and their project-local staging paths.

Listing is read-only. It must not promote, inspect, capture, or remove artifacts.

## Explicit cleanup

Cleanup is always explicit. DesignForge must not automatically delete a render merely because rendering succeeded, capture occurred, a verdict was set, or a new session started.

Exactly one cleanup selector is required:

- `designforge visual staging clean <target> --run <run-id>` — remove one known managed run;
- `designforge visual staging clean <target> --older-than-hours <hours>` — remove managed runs at or older than the requested age;
- `designforge visual staging clean <target> --all` — remove all managed staging runs.

Age-based cleanup may use `0` to intentionally match all currently existing managed runs. Prefer a non-zero retention window when uninspected output may still be useful.

## Safety boundaries

Staging lifecycle operations must:

- require an initialized `.DesignForge` workspace;
- operate only below `.DesignForge/render-staging/`;
- accept only canonical managed run ids for direct run deletion;
- reject path traversal and malformed run ids;
- ignore symbolic-link run entries;
- ignore and preserve unmanaged files/directories;
- never follow a staging-root symbolic link;
- require one explicit cleanup selector;
- never clean persistent `visual-evidence/` directories.

If a managed run becomes unsafe or changes identity between selection and deletion, abort rather than widening the deletion scope.

## Relationship to Visual QA

The lifecycle is intentionally asymmetric:

`render -> staging -> inspect -> capture -> persistent visual-evidence`

`visual capture` copies inspected render output into the corresponding managed Visual QA evidence directory. The staging source may remain afterward until explicitly cleaned.

Deleting a staging run after successful capture must not delete the persistent captured evidence.

A staging artifact can be discarded without a verdict if it was never useful, but discarding it must not be represented as completed visual inspection.

## Provider neutrality

Staging is shared by all renderer adapters. Browser, emulator, simulator, native-preview, screenshot, or future providers use the same lifecycle and must not invent provider-specific persistent staging semantics.
