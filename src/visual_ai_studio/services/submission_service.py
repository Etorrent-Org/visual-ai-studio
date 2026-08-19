from __future__ import annotations

from visual_ai_studio.domain.models import (
    Artifact,
    HumanConfirmations,
    Project,
    SubmissionOutcome,
    ValidationReport,
)
from visual_ai_studio.domain.statuses import (
    ProjectStatus,
)
from visual_ai_studio.infrastructure.automation_runs import (
    AutomationRunRepository,
)
from visual_ai_studio.infrastructure.database import (
    ProjectRepository,
)
from visual_ai_studio.infrastructure.webhook_client import (
    WebhookClient,
    idempotency_key,
)


def can_submit(
    report: ValidationReport | None,
    confirmations: HumanConfirmations,
) -> bool:
    return bool(report and report.automatic_checks_passed and confirmations.all_confirmed)


class SubmissionService:
    def __init__(
        self,
        client: WebhookClient,
        runs: AutomationRunRepository,
        projects: ProjectRepository,
    ) -> None:
        self.client = client
        self.runs = runs
        self.projects = projects

    def submit(
        self,
        project: Project,
        artifacts: list[Artifact],
        report: ValidationReport,
        confirmations: HumanConfirmations,
    ) -> SubmissionOutcome:
        if not can_submit(
            report,
            confirmations,
        ):
            return SubmissionOutcome(
                status="error",
                message=("Le résultat doit être validé avant l'envoi."),
            )

        key = idempotency_key(
            project.id,
            project.version,
        )

        run_id = self.runs.start(
            project.id,
            key,
        )

        outcome = self.client.submit(
            project,
            artifacts,
            report,
            confirmations,
        )

        self.runs.finish(
            run_id,
            status=outcome.status,
            http_status=outcome.http_status,
            execution_id=(outcome.execution_id),
            remote_url=(outcome.remote_url),
            error_message=("" if outcome.status == "success" else outcome.message),
        )

        project.status = ProjectStatus.VALIDATED

        if outcome.status == "success":
            project.remote_url = outcome.remote_url

        self.projects.save(project)

        return outcome
