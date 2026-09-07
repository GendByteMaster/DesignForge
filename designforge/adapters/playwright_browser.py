#!/usr/bin/env python3
"""Optional Playwright browser renderer for the DesignForge render-adapter protocol."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PROTOCOL_VERSION = "designforge-render-adapter-v1"
VIEWPORT_RE = re.compile(r"^(?P<width>\d{2,5})x(?P<height>\d{2,5})$")
BROWSERS = ("chromium", "firefox", "webkit")
WAIT_UNTIL = ("commit", "domcontentloaded", "load", "networkidle")
COLOR_SCHEMES = ("light", "dark", "no-preference")


def fail(message: str) -> int:
    print(f"error: {message}", file=sys.stderr)
    return 1


def parse_viewport(value: str) -> tuple[int, int] | None:
    match = VIEWPORT_RE.fullmatch(value.strip())
    if not match:
        return None
    width = int(match.group("width"))
    height = int(match.group("height"))
    if not (100 <= width <= 16384 and 100 <= height <= 16384):
        return None
    return width, height


def validate_url(value: str) -> str | None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"}:
        return "browser adapter URL must use http:// or https://"
    if not parsed.hostname:
        return "browser adapter URL must include a hostname"
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render one browser state as an uninspected DesignForge staging artifact"
    )
    parser.add_argument("--url", required=True, help="explicit page URL to render")
    parser.add_argument("--browser", choices=BROWSERS, default="chromium")
    parser.add_argument(
        "--viewport",
        help="WIDTHxHEIGHT override; defaults to DESIGNFORGE_VIEWPORT when numeric",
    )
    parser.add_argument("--wait-until", choices=WAIT_UNTIL, default="load")
    parser.add_argument("--wait-for-selector")
    parser.add_argument("--selector", help="capture one locator instead of the full page viewport")
    parser.add_argument("--full-page", action="store_true")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--allow-animations", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=30000)
    parser.add_argument("--delay-ms", type=int, default=0)
    parser.add_argument("--device-scale-factor", type=float, default=1.0)
    parser.add_argument("--color-scheme", choices=COLOR_SCHEMES, default="light")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if os.environ.get("DESIGNFORGE_RENDER_PROTOCOL") != PROTOCOL_VERSION:
        return fail(f"expected DESIGNFORGE_RENDER_PROTOCOL={PROTOCOL_VERSION}")

    output_token = os.environ.get("DESIGNFORGE_OUTPUT_DIR", "").strip()
    if not output_token:
        return fail("DESIGNFORGE_OUTPUT_DIR is required")
    output_dir = Path(output_token).resolve()
    if not output_dir.is_dir():
        return fail("DESIGNFORGE_OUTPUT_DIR must reference an existing directory")

    url_error = validate_url(args.url)
    if url_error:
        return fail(url_error)

    viewport_token = args.viewport or os.environ.get("DESIGNFORGE_VIEWPORT", "")
    viewport = parse_viewport(viewport_token)
    if viewport is None:
        return fail(
            "browser viewport must be numeric WIDTHxHEIGHT; pass --viewport when the DesignForge viewport label is symbolic"
        )
    width, height = viewport

    if args.timeout_ms < 1:
        return fail("--timeout-ms must be greater than zero")
    if args.delay_ms < 0:
        return fail("--delay-ms must be zero or greater")
    if not (0.1 <= args.device_scale_factor <= 8.0):
        return fail("--device-scale-factor must be between 0.1 and 8.0")
    if args.selector and args.full_page:
        return fail("--selector and --full-page cannot be used together")

    try:
        from playwright.sync_api import (
            Error as PlaywrightError,
            TimeoutError as PlaywrightTimeoutError,
            sync_playwright,
        )
    except ImportError:
        return fail(
            "Playwright is not installed; install the optional dependency with 'python -m pip install playwright' and install a browser with 'python -m playwright install chromium'"
        )

    output = output_dir / "render.png"
    browser = None
    context = None
    try:
        with sync_playwright() as playwright:
            browser_type = getattr(playwright, args.browser)
            browser = browser_type.launch(headless=not args.headed)
            context = browser.new_context(
                viewport={"width": width, "height": height},
                device_scale_factor=args.device_scale_factor,
                color_scheme=args.color_scheme,
            )
            page = context.new_page()
            page.goto(args.url, wait_until=args.wait_until, timeout=args.timeout_ms)

            if args.wait_for_selector:
                page.locator(args.wait_for_selector).wait_for(
                    state="visible", timeout=args.timeout_ms
                )
            if args.delay_ms:
                page.wait_for_timeout(args.delay_ms)

            screenshot_options = {
                "path": str(output),
                "animations": "allow" if args.allow_animations else "disabled",
                "caret": "hide",
                "scale": "css",
                "timeout": args.timeout_ms,
            }
            if args.selector:
                page.locator(args.selector).screenshot(**screenshot_options)
            else:
                page.screenshot(full_page=args.full_page, **screenshot_options)
    except PlaywrightTimeoutError as exc:
        return fail(f"Playwright render timed out: {exc}")
    except PlaywrightError as exc:
        return fail(f"Playwright render failed: {exc}")
    except OSError as exc:
        return fail(f"failed to write browser render artifact: {exc}")
    finally:
        if context is not None:
            try:
                context.close()
            except Exception:
                pass
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass

    if not output.is_file() or output.stat().st_size == 0:
        return fail("Playwright completed without creating a non-empty render.png")

    print(json.dumps({"protocol": PROTOCOL_VERSION, "artifact": output.name}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
