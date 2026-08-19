from __future__ import annotations

from enum import StrEnum


class ProjectStatus(StrEnum):
    BRIEF = "Brief"
    VALIDATED = "Validé"
    ARCHIVED = "Archivé"

    @classmethod
    def _missing_(cls, value: object) -> ProjectStatus | None:
        if not isinstance(value, str):
            return None

        legacy = {
            "Brouillon": cls.BRIEF,
            "Prompt prêt": cls.BRIEF,
            "En attente de l'agent": cls.BRIEF,
            "Livrables à contrôler": cls.BRIEF,
            "Prêt pour n8n": cls.VALIDATED,
            "Envoyé": cls.VALIDATED,
            "Erreur n8n": cls.VALIDATED,
            "Archivé": cls.ARCHIVED,
        }

        return legacy.get(value)


class SyncStatus(StrEnum):
    SYNCED = "synced"
    PENDING = "pending"
    ERROR = "error"


class ArtifactType(StrEnum):
    IMAGE = "image"
    TEXT = "text"
    METADATA = "metadata"
    MANIFEST = "manifest"

    @classmethod
    def _missing_(cls, value: object) -> ArtifactType | None:
        if not isinstance(value, str):
            return None

        legacy = {
            "pinterest": cls.IMAGE,
            "synthese": cls.IMAGE,
            "notion": cls.TEXT,
        }

        return legacy.get(value)