from __future__ import annotations

import io
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from visual_ai_studio.web_app import create_app


def _client(tmp_path: Path) -> TestClient:
    return TestClient(create_app(data_root=tmp_path, web_dist=tmp_path / "missing-web"))


def _new_project(client: TestClient) -> dict[str, object]:
    response = client.post("/api/projects", json={})
    assert response.status_code == 200
    return response.json()


def _instagram_png() -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (1080, 1350), (25, 30, 48)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_web_flow_keeps_prompt_and_multi_image_contract(tmp_path: Path) -> None:
    client = _client(tmp_path)
    project = _new_project(client)
    project_id = str(project["id"])

    brief = dict(project["brief"])
    brief.update(
        {
            "title": "Série Instagram",
            "raw_idea": "Un atelier visuel nocturne très graphique.",
            "post_image_count": 3,
            "mode": "instagram",
            "target_width": 1080,
            "target_height": 1350,
            "aspect_ratio": "4:5",
        }
    )

    saved = client.put(
        f"/api/projects/{project_id}/brief",
        json={"brief": brief, "confirm_new_collection": False},
    )
    assert saved.status_code == 200
    assert saved.json()["project"]["brief"]["post_image_count"] == 3

    prepared = client.post(
        f"/api/projects/{project_id}/prompt",
        json={"brief": brief, "confirm_new_collection": False},
    )
    assert prepared.status_code == 200
    payload = prepared.json()
    assert payload["version"] == 1
    assert "Nombre de visuels principaux : 3" in payload["prompt_text"]
    assert "1080 x 1350 px" in payload["prompt_text"]
    assert "Instagram" in payload["prompt_text"]


def test_web_import_validation_approval_and_local_export(tmp_path: Path) -> None:
    client = _client(tmp_path)
    project = _new_project(client)
    project_id = str(project["id"])

    brief = dict(project["brief"])
    brief.update(
        {
            "title": "Export web",
            "raw_idea": "Une scène graphique.",
            "target_width": 1080,
            "target_height": 1350,
            "aspect_ratio": "4:5",
        }
    )
    prepared = client.post(
        f"/api/projects/{project_id}/prompt",
        json={"brief": brief, "confirm_new_collection": False},
    )
    assert prepared.status_code == 200

    imported = client.post(
        f"/api/projects/{project_id}/artifacts",
        files={"files": ("image.png", _instagram_png(), "image/png")},
    )
    assert imported.status_code == 200
    report = imported.json()
    assert report["automatic_checks_passed"] is True
    assert len(report["artifacts"]) == 1
    assert report["artifacts"][0]["artifact_type"] == "image"

    approved = client.post(
        f"/api/projects/{project_id}/approve",
        json={"approved": True},
    )
    assert approved.status_code == 200
    assert approved.json()["ready"] is True
    assert approved.json()["project"]["status"] == "Validé"

    exported = client.post(
        f"/api/projects/{project_id}/export",
        json={"approved": True},
    )
    assert exported.status_code == 200
    assert exported.headers["content-type"] == "application/zip"

    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        names = archive.namelist()
        assert any(name.endswith("/image.png") for name in names)
        assert any(name.endswith("/project.json") for name in names)


def test_web_storage_picker_stays_inside_docker_volume(tmp_path: Path) -> None:
    (tmp_path / "projects").mkdir(exist_ok=True)
    (tmp_path / "alternative").mkdir()
    client = _client(tmp_path)

    root = client.get("/api/storage/directories")
    assert root.status_code == 200
    children = {item["name"] for item in root.json()["children"]}
    assert "projects" in children
    assert "alternative" in children

    saved = client.put(
        "/api/settings",
        json={"projects_dir": str(tmp_path / "alternative")},
    )
    assert saved.status_code == 200
    assert Path(saved.json()["projects_dir"]).name == "alternative"

    outside = client.put(
        "/api/settings",
        json={"projects_dir": str(tmp_path.parent)},
    )
    assert outside.status_code == 400
