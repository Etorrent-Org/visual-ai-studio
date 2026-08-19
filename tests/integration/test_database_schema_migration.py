from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy import inspect

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

    inspector = inspect(
        database.engine
    )

    tables = set(
        inspector.get_table_names()
    )

    assert "automation_runs" in tables
    assert "n8n_runs" not in tables

    project_columns = {
        item["name"]
        for item in inspector.get_columns(
            "projects"
        )
    }

    assert "remote_url" in project_columns
    assert "notion_page_url" not in project_columns

    automation_columns = {
        item["name"]
        for item in inspector.get_columns(
            "automation_runs"
        )
    }

    assert "remote_url" in automation_columns
    assert "notion_page_url" not in automation_columns