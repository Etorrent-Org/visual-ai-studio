from __future__ import annotations

import pytest

from visual_ai_studio.domain.normalization import (
    create_collection_reference,
    deduplicate_values,
    find_close_values,
    normalize_value,
    slugify,
)
from visual_ai_studio.domain.statuses import SyncStatus


def test_normalization_handles_spaces_case_accents_and_unicode() -> None:
    assert normalize_value("  GUERRIÈRES   du futur ") == "guerrieres du futur"
    assert normalize_value("e\u0301") == normalize_value("é")
    assert slugify("Portrait — Néon élégant") == "portrait-neon-elegant"


def test_collection_deduplication_and_close_values() -> None:
    existing = ["Geisha Nocturne", "Sakura Fantasy"]
    with pytest.raises(ValueError, match="existe déjà"):
        create_collection_reference("  geisha nocturne ", existing)
    assert find_close_values("Sakura Fantazy", existing) == ["Sakura Fantasy"]


def test_new_collection_is_pending() -> None:
    reference, similar = create_collection_reference("  Cyber   Sakura  ", ["Sakura Fantasy"])
    assert reference.value == "Cyber Sakura"
    assert reference.normalized_value == "cyber sakura"
    assert reference.is_new is True
    assert reference.sync_status is SyncStatus.PENDING
    assert similar == []


def test_style_suggestions_are_deduplicated_and_excluded() -> None:
    values = deduplicate_values(
        ["Sumi-e élégant", "  sumi-e ÉLÉGANT ", "modèle standard à dupliquer"],
        excluded={"modèle standard à dupliquer"},
    )
    assert values == ["Sumi-e élégant"]
