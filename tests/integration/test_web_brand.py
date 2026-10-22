"""Regression: static Japanese seal must be delivered by FastAPI, not HTML."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from visual_ai_studio.web_app import create_app


def test_japanese_brand_asset_is_served_as_svg(tmp_path: Path) -> None:
    root = tmp_path / "web"
    brand = root / "brand"
    brand.mkdir(parents=True)
    logo = '<svg xmlns="http://www.w3.org/2000/svg"><title>エルワン</title></svg>'
    (brand / "erwann-seal.svg").write_text(logo, encoding="utf-8")

    client = TestClient(create_app(data_root=tmp_path / "data", web_dist=root))
    result = client.get("/brand/erwann-seal.svg")
    assert result.status_code == 200
    assert "image/svg+xml" in result.headers["content-type"]
    assert "エルワン" in result.text
    assert client.get("/brand/missing.svg").status_code == 404
