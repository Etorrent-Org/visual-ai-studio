from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

from .database import (
    AutomationRunRow,
    Database,
)


class AutomationRunRepository:
    def __init__(
        self,
        database: Database,
    ) -> None:
        self.database = database

    def start(
        self,
        project_id: UUID,
        key: str,
    ) -> str:
        run_id = str(uuid4())

        with self.database.session() as session:
            session.add(
                AutomationRunRow(
                    id=run_id,
                    project_id=str(
                        project_id
                    ),
                    idempotency_key=key,
                    request_at=datetime.now(
                        UTC
                    ),
                    status="pending",
                )
            )

        return run_id

    def finish(
        self,
        run_id: str,
        *,
        status: str,
        http_status: int | None,
        execution_id: str,
        remote_url: str,
        error_message: str,
    ) -> None:
        with self.database.session() as session:
            row = session.get(
                AutomationRunRow,
                run_id,
            )

            if row is None:
                raise LookupError(
                    "Exécution webhook inconnue : "
                    f"{run_id}"
                )

            row.response_at = datetime.now(
                UTC
            )
            row.status = status
            row.http_status = http_status
            row.execution_id = execution_id
            row.remote_url = remote_url
            row.error_message = (
                error_message
            )