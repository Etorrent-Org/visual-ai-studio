from __future__ import annotations

import re
import unicodedata
from difflib import SequenceMatcher

from .models import ReferenceValue
from .statuses import SyncStatus

_SPACES = re.compile(r"\s+")
_SLUG_UNSAFE = re.compile(r"[^a-z0-9]+")


def clean_display_value(value: str) -> str:
    return _SPACES.sub(" ", unicodedata.normalize("NFC", value).strip())


def normalize_value(value: str) -> str:
    cleaned = clean_display_value(value).casefold()
    decomposed = unicodedata.normalize("NFKD", cleaned)
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def slugify(value: str) -> str:
    normalized = normalize_value(value)
    return _SLUG_UNSAFE.sub("-", normalized).strip("-") or "projet-sans-titre"


def deduplicate_values(values: list[str], excluded: set[str] | None = None) -> list[str]:
    excluded_norm = {normalize_value(item) for item in (excluded or set())}
    unique: dict[str, str] = {}
    for value in values:
        cleaned = clean_display_value(value)
        normalized = normalize_value(cleaned)
        if normalized and normalized not in excluded_norm:
            unique.setdefault(normalized, cleaned)
    return sorted(unique.values(), key=normalize_value)


def find_close_values(candidate: str, existing: list[str], threshold: float = 0.78) -> list[str]:
    target = normalize_value(candidate)
    return [
        value
        for value in existing
        if target != normalize_value(value)
        and SequenceMatcher(None, target, normalize_value(value)).ratio() >= threshold
    ]


def create_collection_reference(
    value: str, existing: list[str]
) -> tuple[ReferenceValue, list[str]]:
    cleaned = clean_display_value(value)
    if not cleaned:
        raise ValueError("Le nom de collection est obligatoire.")
    normalized = normalize_value(cleaned)
    exact = next((item for item in existing if normalize_value(item) == normalized), None)
    if exact is not None:
        raise ValueError(f"La collection « {exact} » existe déjà.")
    return (
        ReferenceValue(
            type="collection",
            value=cleaned,
            normalized_value=normalized,
            source="user",
            is_new=True,
            sync_status=SyncStatus.PENDING,
        ),
        find_close_values(cleaned, existing),
    )
