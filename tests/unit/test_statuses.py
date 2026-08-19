from visual_ai_studio.domain.statuses import ProjectStatus


def test_only_three_business_statuses_are_exposed() -> None:
    assert list(ProjectStatus) == [
        ProjectStatus.BRIEF,
        ProjectStatus.VALIDATED,
        ProjectStatus.ARCHIVED,
    ]


def test_legacy_statuses_are_mapped() -> None:
    assert ProjectStatus("Brouillon") is ProjectStatus.BRIEF
    assert ProjectStatus("Prompt prêt") is ProjectStatus.BRIEF
    assert ProjectStatus("En attente de l'agent") is ProjectStatus.BRIEF
    assert ProjectStatus("Livrables à contrôler") is ProjectStatus.BRIEF

    assert ProjectStatus("Prêt pour n8n") is ProjectStatus.VALIDATED
    assert ProjectStatus("Envoyé") is ProjectStatus.VALIDATED
    assert ProjectStatus("Erreur n8n") is ProjectStatus.VALIDATED

    assert ProjectStatus("Archivé") is ProjectStatus.ARCHIVED