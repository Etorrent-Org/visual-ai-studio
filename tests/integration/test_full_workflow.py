from __future__ import annotations

from pathlib import Path

import httpx

from visual_ai_studio.domain.models import (
    Brief,
    HumanConfirmations,
)
from visual_ai_studio.domain.statuses import (
    ProjectStatus,
)
from visual_ai_studio.infrastructure.automation_runs import (
    AutomationRunRepository,
)
from visual_ai_studio.infrastructure.database import (
    ArtifactRepository,
    Database,
    ProjectRepository,
    ReferenceRepository,
)
from visual_ai_studio.infrastructure.webhook_client import (
    WebhookClient,
)
from visual_ai_studio.services.artifact_service import (
    ArtifactService,
)
from visual_ai_studio.services.project_service import (
    ProjectService,
)
from visual_ai_studio.services.submission_service import (
    SubmissionService,
)


def test_complete_local_workflow_with_fake_webhook(
    tmp_path: Path,
    artifact_package: object,
) -> None:
    database = Database(
        tmp_path / "workflow.db"
    )

    database.initialize()

    projects = ProjectRepository(
        database
    )

    references = ReferenceRepository(
        database
    )

    project_service = ProjectService(
        projects,
        references,
    )

    artifact_service = ArtifactService(
        ArtifactRepository(database),
        projects,
        tmp_path / "projects",
    )

    project = (
        project_service.create_project(
            "Demo visual"
        )
    )

    project = (
        project_service.save_brief(
            project,
            Brief(
                title="Demo visual",
                collection="Campagne demo",
                style="Editorial",
                raw_idea=(
                    "Une scène visuelle test"
                ),
            ),
        )
    )

    project = (
        project_service.generate_prompt(
            project
        )
    )

    project = (
        project_service.mark_sent_to_agent(
            project
        )
    )

    report = (
        artifact_service.import_package(
            project,
            artifact_package(),
        )
    )

    assert (
        report.automatic_checks_passed
    )

    confirmations = HumanConfirmations(
        approved=True
    )

    transport = httpx.MockTransport(
        lambda _request: httpx.Response(
            200,
            json={
                "status": "success",
                "execution_id": (
                    "fake-exec-42"
                ),
                "remote_url": (
                    "https://example.test/fake-result"
                ),
            },
        )
    )

    submission = SubmissionService(
        WebhookClient(
            "https://automation.test/webhook",
            "X-Token",
            "test-only-secret",
            transport=transport,
        ),
        AutomationRunRepository(
            database
        ),
        projects,
    )

    outcome = submission.submit(
        project,
        report.artifacts,
        report,
        confirmations,
    )

    reloaded = projects.get(
        project.id
    )

    assert outcome.status == "success"

    assert (
        outcome.execution_id
        == "fake-exec-42"
    )

    assert reloaded is not None

    assert (
        reloaded.status
        is ProjectStatus.VALIDATED
    )

    assert (
        reloaded.remote_url
        == "https://example.test/fake-result"
    )