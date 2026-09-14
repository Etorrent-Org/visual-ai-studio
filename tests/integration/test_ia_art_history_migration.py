from __future__ import annotations

import sqlite3
from pathlib import Path
from uuid import UUID

from visual_ai_studio.application import migrate_legacy_database
from visual_ai_studio.domain.output_modes import OutputMode
from visual_ai_studio.domain.statuses import ArtifactType, ProjectStatus
from visual_ai_studio.infrastructure.database import (
    ArtifactRepository,
    Database,
    ProjectRepository,
)

PROJECT_ID = "11111111-1111-4111-8111-111111111111"
ARTIFACT_ID = "22222222-2222-4222-8222-222222222222"


def _create_ia_art_database(path: Path) -> None:
    with sqlite3.connect(path) as connection:
        connection.executescript(
            """
            CREATE TABLE projects (
                id VARCHAR(36) PRIMARY KEY,
                title TEXT NOT NULL,
                slug VARCHAR(255) NOT NULL,
                status VARCHAR(64) NOT NULL,
                collection_value TEXT DEFAULT '',
                collection_is_new BOOLEAN DEFAULT 0,
                style TEXT DEFAULT '',
                brief_json TEXT DEFAULT '{}',
                prompt_text TEXT DEFAULT '',
                prompt_hash VARCHAR(64) DEFAULT '',
                prompt_brief_hash VARCHAR(64) DEFAULT '',
                version INTEGER DEFAULT 1,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                archived_at DATETIME,
                notion_page_url TEXT DEFAULT ''
            );

            CREATE TABLE artifacts (
                id VARCHAR(36) PRIMARY KEY,
                project_id VARCHAR(36) NOT NULL,
                artifact_type VARCHAR(32) NOT NULL,
                filename TEXT NOT NULL,
                local_path TEXT NOT NULL,
                sha256 VARCHAR(64) NOT NULL,
                width INTEGER,
                height INTEGER,
                validation_status VARCHAR(32) NOT NULL
            );
            """
        )
        connection.execute(
            """
            INSERT INTO projects (
                id, title, slug, status, collection_value, collection_is_new, style,
                brief_json, prompt_text, prompt_hash, prompt_brief_hash, version,
                created_at, updated_at, archived_at, notion_page_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                PROJECT_ID,
                "Ancien projet",
                "ancien-projet",
                "Brouillon",
                "Archives",
                0,
                "Illustration",
                '{"title":"Ancien projet","raw_idea":"Historique IA-Art"}',
                "",
                "",
                "",
                1,
                "2026-08-20 10:00:00.000000",
                "2026-08-20 10:00:00.000000",
                None,
                "https://notion.example/ancien-projet",
            ),
        )
        connection.execute(
            """
            INSERT INTO artifacts (
                id, project_id, artifact_type, filename, local_path, sha256,
                width, height, validation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ARTIFACT_ID,
                PROJECT_ID,
                "pinterest",
                "ancien-visuel.png",
                str(path.parent / "ancien-visuel.png"),
                "0" * 64,
                1000,
                1500,
                "validated",
            ),
        )


def test_ia_art_history_is_readable_after_migration(tmp_path: Path) -> None:
    legacy = tmp_path / "ia-art-studio.db"
    current = tmp_path / "visual-ai-studio.db"
    _create_ia_art_database(legacy)

    assert migrate_legacy_database(current, legacy)

    database = Database(current)
    database.initialize()

    project = ProjectRepository(database).get(UUID(PROJECT_ID))
    assert project is not None
    assert project.title == "Ancien projet"
    assert project.status is ProjectStatus.BRIEF
    assert project.brief.mode is OutputMode.INSTAGRAM
    assert project.brief.post_image_count == 1
    assert project.remote_url == "https://notion.example/ancien-projet"

    artifacts = ArtifactRepository(database).list_for_project(UUID(PROJECT_ID))
    assert len(artifacts) == 1
    assert artifacts[0].artifact_type is ArtifactType.IMAGE
