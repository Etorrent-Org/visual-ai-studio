from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from importlib.resources import files

from .models import Brief
from .output_modes import (
    OutputMode,
    preset_for,
)


@dataclass(frozen=True)
class PromptResult:
    text: str
    sha256: str
    brief_sha256: str


def brief_fingerprint(
    brief: Brief,
) -> str:
    data = json.dumps(
        brief.model_dump(mode="json"),
        sort_keys=True,
        ensure_ascii=False,
    )

    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _value(
    value: str,
    fallback: str = "Non renseigné",
) -> str:
    cleaned = value.strip()

    if cleaned:
        return cleaned

    return fallback


def _dimensions(
    width: int | None,
    height: int | None,
) -> str:
    if width is not None and height is not None:
        return f"{width} x {height} px"

    return "À préciser avec Studio Visuel"


def build_prompt(
    brief: Brief,
    template: str | None = None,
) -> PromptResult:
    if not brief.title.strip():
        raise ValueError("Le nom du projet est obligatoire pour préparer le prompt.")

    if not brief.raw_idea.strip():
        raise ValueError("L'idée brute est obligatoire pour préparer le prompt.")

    mode = OutputMode(brief.mode)

    preset = preset_for(mode)

    width = brief.target_width

    if width is None:
        width = preset.width

    height = brief.target_height

    if height is None:
        height = preset.height

    ratio = brief.aspect_ratio.strip()

    if not ratio:
        ratio = preset.aspect_ratio

    if not ratio:
        ratio = "À préciser avec Studio Visuel"

    if template is None:
        template = (
            files("visual_ai_studio.resources")
            .joinpath("prompt-template.txt")
            .read_text(encoding="utf-8")
        )

    has_reference = "NON"

    if brief.reference_image:
        has_reference = "OUI — joindre l'image dans la conversation"

    text_overlay = _value(
        brief.text_overlay,
        "Aucun texte demandé dans l'image",
    )

    values = {
        "mode": mode.value.upper(),
        "channel": preset.label,
        "title": brief.title,
        "collection": _value(
            brief.collection,
            "Aucune",
        ),
        "style": _value(
            brief.style,
        ),
        "raw_idea": brief.raw_idea,
        "audience": _value(
            brief.audience,
        ),
        "intent": _value(
            brief.intent,
        ),
        "subject": _value(
            brief.subject,
        ),
        "setting": _value(
            brief.setting,
        ),
        "ambience": _value(
            brief.ambience,
        ),
        "palette": _value(
            brief.palette,
        ),
        "lighting": _value(
            brief.lighting,
        ),
        "materials": _value(
            brief.materials,
        ),
        "composition": _value(
            brief.composition,
        ),
        "detail_level": _value(
            brief.detail_level,
        ),
        "required_elements": _value(
            brief.required_elements,
            "Aucun",
        ),
        "forbidden_elements": _value(
            brief.forbidden_elements,
            "Aucun",
        ),
        "text_overlay": text_overlay,
        "dimensions": _dimensions(
            width,
            height,
        ),
        "aspect_ratio": ratio,
        "has_reference": has_reference,
        "reference_note": _value(
            brief.reference_note,
            "Aucune",
        ),
        "notes": _value(
            brief.notes,
            "Aucune",
        ),
    }

    rendered = template

    for key, value in values.items():
        rendered = rendered.replace(
            "{{" + key + "}}",
            str(value),
        )

    rendered = rendered.strip() + "\n"

    return PromptResult(
        text=rendered,
        sha256=hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        brief_sha256=brief_fingerprint(brief),
    )
