# Playwright Browser Adapter

DesignForge ships an optional Playwright-based browser renderer that implements the provider-neutral `designforge-render-adapter-v1` contract.

The browser adapter is an execution provider, not part of DesignForge core. Core workspace, mapping, planning, Visual QA evidence, and renderer orchestration remain dependency-free.

## Scope

The adapter renders one explicit HTTP(S) page state into the DesignForge staging directory.

It does not:

- start or discover a development server;
- install Playwright;
- install browser binaries;
- authenticate to arbitrary applications automatically;
- inspect the screenshot;
- register checked Visual QA evidence;
- set a Visual QA verdict.

The caller is responsible for making the target page reachable and for supplying any application-specific setup needed before capture.

## Optional dependency

Install Playwright only in environments that need this adapter:

```bash
python -m pip install playwright
python -m playwright install chromium
```

Firefox and WebKit may be installed and selected explicitly when needed.

The portable DesignForge Skill does not declare Playwright as a mandatory dependency.

## Canonical command

```bash
python designforge/scripts/designforge.py visual render /path/to/project \
  --surface "Main Workspace" \
  --state "default" \
  --viewport "1440x900" \
  --adapter python designforge/adapters/playwright_browser.py \
    --url http://127.0.0.1:4173
```

After the command succeeds, inspect the exact staging artifact reported by `Render artifact:`. Only after that inspection may it be handed to `designforge visual capture`.

## Browser selection

Supported providers:

- `chromium` — default;
- `firefox`;
- `webkit`.

Example:

```bash
python designforge/scripts/designforge.py visual render /path/to/project \
  --surface "Settings" \
  --state "default" \
  --viewport "1280x800" \
  --adapter python designforge/adapters/playwright_browser.py \
    --url http://127.0.0.1:4173/settings \
    --browser firefox
```

## Viewport rules

By default the adapter reads `DESIGNFORGE_VIEWPORT` supplied by `visual render` and requires a numeric `WIDTHxHEIGHT` value.

If the DesignForge capture matrix intentionally uses a symbolic viewport such as `desktop`, pass an explicit adapter override:

```bash
--viewport 1440x900
```

Viewport dimensions are constrained to a bounded numeric range so malformed render requests fail before the browser starts.

## Capture controls

The adapter supports:

- `--wait-until commit|domcontentloaded|load|networkidle`;
- `--wait-for-selector <selector>`;
- `--selector <selector>` for a locator-only screenshot;
- `--full-page` for a full scrollable page screenshot;
- `--delay-ms <milliseconds>` for an explicit final settle delay;
- `--timeout-ms <milliseconds>`;
- `--device-scale-factor <number>`;
- `--color-scheme light|dark|no-preference`;
- `--headed` for local debugging;
- `--allow-animations` when the design review intentionally needs live animation state.

`--selector` and `--full-page` are mutually exclusive.

Animations are disabled by default and screenshots use CSS-pixel scale to improve repeatability across machines.

## URL boundary

The adapter accepts only explicit `http://` and `https://` URLs with a hostname.

It intentionally rejects schemes such as `file://` so the official browser provider is not an implicit local-file reader. Project-specific adapters may choose a different explicit security boundary when required.

## Output

The adapter writes:

```text
$DESIGNFORGE_OUTPUT_DIR/render.png
```

and emits this protocol result as its final stdout line:

```json
{"protocol":"designforge-render-adapter-v1","artifact":"render.png"}
```

The outer DesignForge renderer runner then performs staging containment, supported-format, non-empty-file, and lightweight PNG signature checks.

Successful rendering still does not mean the image was visually inspected.

## Failure behavior

The adapter exits non-zero with a concise error when, for example:

- the render protocol environment is missing or incorrect;
- the output directory is unavailable;
- the URL is invalid;
- the viewport is not numeric and no override was supplied;
- Playwright is not installed;
- the selected browser binary is unavailable;
- navigation or selector waiting times out;
- screenshot creation fails.

These failures propagate through `designforge visual render` without creating checked Visual QA evidence.

## Recommended browser workflow

```text
start application explicitly
  -> confirm target URL
  -> designforge visual render
  -> inspect returned staging artifact
  -> fix UI if needed
  -> render again
  -> inspect exact new artifact
  -> designforge visual capture
  -> designforge visual verdict
  -> designforge visual validate
```

Do not collapse the render and inspection steps. That boundary is part of DesignForge's evidence integrity model.
