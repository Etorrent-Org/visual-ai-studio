from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import inspect

from visual_ai_studio.application import migrate_legacy_database
from visual_ai_studio.infrastructure.database import (
    Database,
)


def test_old_database_names_are_migrated(
    tmp_path: Path,
) -> None:
    path = tmp_path / "legacy.db"

    with sqlite3.connect(path) as connection:
        connection.execute(
            """
            CREATE TABLE projects (
                id TEXT PRIMARY KEY,
                notion_page_url TEXT DEFAULT ''
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE n8n_runs (
                id TEXT PRIMARY KEY,
                notion_page_url TEXT DEFAULT ''
            )
            """
        )

    database = Database(path)

    database.initialize()

    inspector = inspect(database.engine)

    tables = set(inspector.get_table_names())

    assert "automation_runs" in tables
    assert "n8n_runs" not in tables

    project_columns = {item["name"] for item in inspector.get_columns("projects")}

    assert "remote_url" in project_columns
    assert "notion_page_url" not in project_columns

    automation_columns = {item["name"] for item in inspector.get_columns("automation_runs")}

    assert "remote_url" in automation_columns
    assert "notion_page_url" not in automation_columns


def test_legacy_database_is_copied_when_current_database_has_no_projects(
    tmp_path: Path,
) -> None:
    legacy = tmp_path / "ia-art-studio.db"
    current = tmp_path / "visual-ai-studio.db"

    with sqlite3.connect(legacy) as connection:
        connection.execute("CREATE TABLE projects (id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO projects (id) VALUES ('legacy-project')")

    with sqlite3.connect(current) as connection:
        connection.execute("CREATE TABLE projects (id TEXT PRIMARY KEY)")

    assert migrate_legacy_database(current, legacy)
    assert (tmp_path / "visual-ai-studio.pre-ia-art-migration.db").exists()

    with sqlite3.connect(current) as connection:
        ids = [row[0] for row in connection.execute("SELECT id FROM projects")]

    assert ids == ["legacy-project"]


def test_legacy_database_does_not_overwrite_existing_projects(
    tmp_path: Path,
) -> None:
    legacy = tmp_path / "ia-art-studio.db"
    current = tmp_path / "visual-ai-studio.db"

    for path, project_id in ((legacy, "legacy-project"), (current, "current-project")):
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TABLE projects (id TEXT PRIMARY KEY)")
            connection.execute("INSERT INTO projects (id) VALUES (?)", (project_id,))

    assert not migrate_legacy_database(current, legacy)

    with sqlite3.connect(current) as connection:
        ids = [row[0] for row in connection.execute("SELECT id FROM projects")]

    assert ids == ["current-project"]
