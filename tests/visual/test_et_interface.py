"""Revue graphique ET Design System : navigateur réel, environnement éphémère.

Ne contient aucun secret et n'appelle pas de webhook ou service personnel.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("ET_TEST_BASE_URL", "http://127.0.0.1:8000")
OUT = Path(os.environ.get("ET_TEST_OUTPUT", "artifacts/et-visual"))
OUT.mkdir(parents=True, exist_ok=True)

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("tablet", 768, 1024),
    ("mobile", 390, 844),
]


def main() -> None:
    reports = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for name, width, height in VIEWPORTS:
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=1,
                    locale="fr-FR",
                    reduced_motion="reduce",
                )
                runtime_errors: list[str] = []
                page.on("pageerror", lambda exc, errors=runtime_errors: errors.append(str(exc)))
                page.on(
                    "console",
                    lambda message, errors=runtime_errors: errors.append(message.text)
                    if message.type == "error"
                    else None,
                )
                response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
                assert response and response.status == 200, (
                    f"{name}: HTTP {response.status if response else 'no response'}"
                )
                page.locator(".app-shell.et-root").wait_for(timeout=20000)
                seal = page.locator(".et-seal-image")
                assert seal.is_visible(), f"{name}: sceau absent"
                assert seal.evaluate("(img) => img.complete && img.naturalWidth > 0"), (
                    f"{name}: image du sceau cassée"
                )
                assert page.locator(".brand-japanese").inner_text() == "エルワン"
                assert page.get_by_role("heading", name="Projets", exact=True).is_visible()
                page.screenshot(
                    path=str(OUT / f"visual-ai-{name}-projects.png"),
                    full_page=True,
                    animations="disabled",
                )
                viewport = page.evaluate("""() => ({
                    innerWidth: window.innerWidth,
                    scrollWidth: document.documentElement.scrollWidth,
                    background: getComputedStyle(
                        document.querySelector('.app-shell')
                    ).backgroundColor
                })""")
                assert viewport["scrollWidth"] <= viewport["innerWidth"] + 2, (
                    f"{name}: débordement horizontal de "
                    f"{viewport['scrollWidth'] - viewport['innerWidth']}px"
                )
                page.get_by_role("button", name="Administration").click()
                page.locator(".settings-card").first.wait_for(timeout=10000)
                page.screenshot(
                    path=str(OUT / f"visual-ai-{name}-admin.png"),
                    full_page=True,
                    animations="disabled",
                )
                page.get_by_role("button", name="Projets").click()
                page.get_by_role("heading", name="Projets", exact=True).wait_for()
                page.get_by_role("button", name="Nouveau projet").click()
                page.locator(".form-panel").first.wait_for(timeout=12000)
                page.screenshot(
                    path=str(OUT / f"visual-ai-{name}-brief.png"),
                    full_page=True,
                    animations="disabled",
                )
                assert not runtime_errors, f"{name}: erreurs navigateur: {runtime_errors}"
                reports.append(
                    {
                        "device": name,
                        "viewport": f"{width}x{height}",
                        "shell": "OK",
                        "seal": "OK",
                        "views": "projects/admin/brief",
                        "horizontal_overflow": 0,
                        "console_errors": 0,
                        "background": viewport["background"],
                    }
                )
                page.close()
        finally:
            browser.close()

    report_file = OUT / "report.json"
    report_file.write_text(
        json.dumps(reports, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(reports, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
