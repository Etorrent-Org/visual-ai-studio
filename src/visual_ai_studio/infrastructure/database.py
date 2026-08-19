from __future__ import annotations

import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from visual_ai_studio.domain.models import Artifact, Brief, Project, ReferenceValue
from visual_ai_studio.domain.statuses import ArtifactType, ProjectStatus, SyncStatus


class Base(DeclarativeBase):
    pass


class ProjectRow(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    collection_value: Mapped[str] = mapped_column(Text, default="")
    collection_is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    style: Mapped[str] = mapped_column(Text, default="")
    brief_json: Mapped[str] = mapped_column(Text, default="{}")
    prompt_text: Mapped[str] = mapped_column(Text, default="")
    prompt_hash: Mapped[str] = mapped_column(String(64), default="")
    prompt_brief_hash: Mapped[str] = mapped_column(String(64), default="")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    remote_url: Mapped[str] = mapped_column(Text, default="")
    artifacts: Mapped[list[ArtifactRow]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class ReferenceValueRow(Base):
    __tablename__ = "reference_values"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    value: Mapped[str] = mapped_column(Text)
    normalized_value: Mapped[str] = mapped_column(Text, index=True)
    source: Mapped[str] = mapped_column(String(32))
    is_new: Mapped[bool] = mapped_column(Boolean, default=False)
    sync_status: Mapped[str] = mapped_column(String(32), default=SyncStatus.SYNCED.value)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ArtifactRow(Base):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    artifact_type: Mapped[str] = mapped_column(String(32))
    filename: Mapped[str] = mapped_column(Text)
    local_path: Mapped[str] = mapped_column(Text)
    sha256: Mapped[str] = mapped_column(String(64))
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_status: Mapped[str] = mapped_column(String(32))
    project: Mapped[ProjectRow] = relationship(back_populates="artifacts")


class AutomationRunRow(Base):
    __tablename__ = "automation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    idempotency_key: Mapped[str] = mapped_column(String(64), index=True)
    request_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    response_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    execution_id: Mapped[str] = mapped_column(Text, default="")
    remote_url: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32))
    error_message: Mapped[str] = mapped_column(Text, default="")



def _migrate_legacy_schema(
    engine: Engine,
) -> None:
    inspector = inspect(engine)

    tables = set(
        inspector.get_table_names()
    )

    if "projects" in tables:
        columns = {
            item["name"]
            for item in inspector.get_columns(
                "projects"
            )
        }

        if (
            "notion_page_url" in columns
            and "remote_url" not in columns
        ):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE projects "
                        "RENAME COLUMN notion_page_url "
                        "TO remote_url"
                    )
                )

    inspector = inspect(engine)

    tables = set(
        inspector.get_table_names()
    )

    if (
        "n8n_runs" in tables
        and "automation_runs" not in tables
    ):
        with engine.begin() as connection:
            connection.execute(
                text(
                    "ALTER TABLE n8n_runs "
                    "RENAME TO automation_runs"
                )
            )

    inspector = inspect(engine)

    tables = set(
        inspector.get_table_names()
    )

    if "automation_runs" in tables:
        columns = {
            item["name"]
            for item in inspector.get_columns(
                "automation_runs"
            )
        }

        if (
            "notion_page_url" in columns
            and "remote_url" not in columns
        ):
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE automation_runs "
                        "RENAME COLUMN notion_page_url "
                        "TO remote_url"
                    )
                )


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{path.as_posix()}", future=True)
        self._sessions = sessionmaker(self.engine, expire_on_commit=False)

    def initialize(self) -> None:
        _migrate_legacy_schema(
            self.engine
        )

        Base.metadata.create_all(
            self.engine
        )
    def backup(self) -> Path | None:
        if not self.path.exists():
            return None
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        backup_path = self.path.with_name(f"{self.path.stem}-{stamp}.bak{self.path.suffix}")
        shutil.copy2(self.path, backup_path)
        return backup_path

    @contextmanager
    def session(self) -> Iterator[Session]:
        with self._sessions() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise


def _ensure_utc(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


class ProjectRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def save(self, project: Project) -> Project:
        with self.database.session() as session:
            row = session.get(ProjectRow, str(project.id))
            if row is None:
                row = ProjectRow(id=str(project.id))
                session.add(row)
            row.title = project.title
            row.slug = project.slug
            row.status = project.status.value
            row.collection_value = project.brief.collection
            row.collection_is_new = project.brief.collection_is_new
            row.style = project.brief.style
            row.brief_json = project.brief.model_dump_json()
            row.prompt_text = project.prompt_text
            row.prompt_hash = project.prompt_hash
            row.prompt_brief_hash = project.prompt_brief_hash
            row.version = project.version
            row.created_at = project.created_at
            row.updated_at = project.updated_at
            row.archived_at = project.archived_at
            row.remote_url = project.remote_url
        return project

    def get(self, project_id: UUID | str) -> Project | None:
        with self.database.session() as session:
            row = session.get(ProjectRow, str(project_id))
            return self._to_domain(row) if row else None

    def list(self, include_archived: bool = False) -> list[Project]:
        statement = select(ProjectRow).order_by(ProjectRow.updated_at.desc())
        if not include_archived:
            statement = statement.where(ProjectRow.archived_at.is_(None))
        with self.database.session() as session:
            return [self._to_domain(row) for row in session.scalars(statement)]

    @staticmethod
    def _to_domain(row: ProjectRow) -> Project:
        return Project(
            id=UUID(row.id),
            title=row.title,
            slug=row.slug,
            status=ProjectStatus(row.status),
            brief=Brief.model_validate_json(row.brief_json),
            prompt_text=row.prompt_text,
            prompt_hash=row.prompt_hash,
            prompt_brief_hash=row.prompt_brief_hash,
            version=row.version,
            created_at=_ensure_utc(row.created_at),
            updated_at=_ensure_utc(row.updated_at),
            archived_at=_ensure_utc(row.archived_at) if row.archived_at else None,
            remote_url=row.remote_url,
        )


class ReferenceRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def seed(self, references: list[ReferenceValue]) -> None:
        with self.database.session() as session:
            for item in references:
                present = session.scalar(
                    select(ReferenceValueRow).where(
                        ReferenceValueRow.type == item.type,
                        ReferenceValueRow.normalized_value == item.normalized_value,
                    )
                )
                if present is None:
                    session.add(self._to_row(item))

    def add(self, item: ReferenceValue) -> ReferenceValue:
        with self.database.session() as session:
            present = session.scalar(
                select(ReferenceValueRow).where(
                    ReferenceValueRow.type == item.type,
                    ReferenceValueRow.normalized_value == item.normalized_value,
                )
            )
            if present:
                raise ValueError(f"La valeur « {present.value} » existe déjà.")
            session.add(self._to_row(item))
        return item

    def list(self, reference_type: str) -> list[ReferenceValue]:
        statement = (
            select(ReferenceValueRow)
            .where(ReferenceValueRow.type == reference_type)
            .order_by(ReferenceValueRow.value)
        )
        with self.database.session() as session:
            return [self._to_domain(row) for row in session.scalars(statement)]

    @staticmethod
    def _to_row(item: ReferenceValue) -> ReferenceValueRow:
        return ReferenceValueRow(
            id=str(item.id),
            type=item.type,
            value=item.value,
            normalized_value=item.normalized_value,
            source=item.source,
            is_new=item.is_new,
            sync_status=item.sync_status.value,
            updated_at=item.updated_at,
        )

    @staticmethod
    def _to_domain(row: ReferenceValueRow) -> ReferenceValue:
        return ReferenceValue(
            id=UUID(row.id),
            type=row.type,
            value=row.value,
            normalized_value=row.normalized_value,
            source=row.source,
            is_new=row.is_new,
            sync_status=SyncStatus(row.sync_status),
            updated_at=_ensure_utc(row.updated_at),
        )


class ArtifactRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def replace_for_project(self, project_id: UUID, artifacts: list[Artifact]) -> None:
        with self.database.session() as session:
            previous = session.scalars(
                select(ArtifactRow).where(ArtifactRow.project_id == str(project_id))
            )
            for row in previous:
                session.delete(row)
            for item in artifacts:
                session.add(
                    ArtifactRow(
                        id=str(item.id),
                        project_id=str(project_id),
                        artifact_type=item.artifact_type.value,
                        filename=item.filename,
                        local_path=str(item.local_path),
                        sha256=item.sha256,
                        width=item.width,
                        height=item.height,
                        validation_status=item.validation_status,
                    )
                )

    def list_for_project(self, project_id: UUID) -> list[Artifact]:
        with self.database.session() as session:
            rows = session.scalars(
                select(ArtifactRow).where(ArtifactRow.project_id == str(project_id))
            )
            return [
                Artifact(
                    id=UUID(row.id),
                    project_id=UUID(row.project_id),
                    artifact_type=ArtifactType(row.artifact_type),
                    filename=row.filename,
                    local_path=Path(row.local_path),
                    sha256=row.sha256,
                    width=row.width,
                    height=row.height,
                    validation_status=row.validation_status,
                )
                for row in rows
            ]
