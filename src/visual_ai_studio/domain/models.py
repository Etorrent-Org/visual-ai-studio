from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .output_modes import OutputMode
from .statuses import ArtifactType, ProjectStatus, SyncStatus


def utc_now() -> datetime:
    return datetime.now(UTC)


class Brief(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = ""
    mode: OutputMode = OutputMode.PINTEREST
    audience: str = ""
    target_width: int | None = None
    target_height: int | None = None
    aspect_ratio: str = ""
    text_overlay: str = ""
    collection: str = ""
    collection_is_new: bool = False
    style: str = ""
    raw_idea: str = ""
    intent: str = ""
    subject: str = ""
    setting: str = ""
    ambience: str = ""
    palette: str = ""
    lighting: str = ""
    materials: str = ""
    composition: str = ""
    detail_level: str = ""
    required_elements: str = ""
    forbidden_elements: str = ""
    reference_image: str = ""
    reference_note: str = ""
    board: str = ""
    notes: str = ""

    @field_validator("reference_image")
    @classmethod
    def normalize_reference_path(cls, value: str) -> str:
        return str(Path(value)) if value else ""


class Project(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = "Projet sans titre"
    slug: str = "projet-sans-titre"
    status: ProjectStatus = ProjectStatus.BRIEF
    brief: Brief = Field(default_factory=Brief)
    prompt_text: str = ""
    prompt_hash: str = ""
    prompt_brief_hash: str = ""
    version: int = 1
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    archived_at: datetime | None = None
    remote_url: str = ""


class ReferenceValue(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: str
    value: str
    normalized_value: str
    source: str = "user"
    is_new: bool = False
    sync_status: SyncStatus = SyncStatus.SYNCED
    updated_at: datetime = Field(default_factory=utc_now)


class Artifact(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    artifact_type: ArtifactType
    filename: str
    local_path: Path
    sha256: str
    width: int | None = None
    height: int | None = None
    validation_status: str = "pending"


class ValidationIssue(BaseModel):
    code: str
    message: str
    blocking: bool = True
    artifact: str | None = None


class ValidationReport(BaseModel):
    artifacts: list[Artifact] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)
    markdown_metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def blocking_issues(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if issue.blocking]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [issue for issue in self.issues if not issue.blocking]

    @property
    def automatic_checks_passed(self) -> bool:
        return not self.blocking_issues


class HumanConfirmations(BaseModel):
    approved: bool = False

    @property
    def all_confirmed(self) -> bool:
        return self.approved

class SubmissionOutcome(BaseModel):
    status: str
    retryable: bool = False
    unknown: bool = False
    execution_id: str = ""
    remote_url: str = ""
    message: str = ""
    http_status: int | None = None
    duplicate_avoided: bool = False
