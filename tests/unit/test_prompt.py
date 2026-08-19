from visual_ai_studio.domain.models import (
    Brief,
)
from visual_ai_studio.domain.output_modes import (
    OutputMode,
)
from visual_ai_studio.domain.prompt_builder import (
    build_prompt,
)


def test_pinterest_prompt_targets_studio_visuel() -> None:
    brief = Brief(
        title="Campagne été",
        mode=OutputMode.PINTEREST,
        raw_idea="Portrait éditorial premium",
        audience="Femmes 25-45 ans",
    )

    result = build_prompt(
        brief
    )

    assert (
        "AGENT CIBLE : Studio Visuel"
        in result.text
    )

    assert (
        "INTENTION : CREATION_IMAGE"
        in result.text
    )

    assert (
        "SORTIE : PINTEREST"
        in result.text
    )

    assert (
        "1000 x 1500 px"
        in result.text
    )

    assert "2:3" in result.text

    assert (
        "Étape 1"
        in result.text
    )


def test_instagram_prompt_uses_feed_portrait() -> None:
    brief = Brief(
        title="Instagram test",
        mode=OutputMode.INSTAGRAM,
        raw_idea="Produit sur fond minimaliste",
    )

    result = build_prompt(
        brief
    )

    assert (
        "SORTIE : INSTAGRAM"
        in result.text
    )

    assert (
        "1080 x 1350 px"
        in result.text
    )

    assert "4:5" in result.text


def test_custom_prompt_accepts_free_format() -> None:
    brief = Brief(
        title="Bannière web",
        mode=OutputMode.CUSTOM,
        raw_idea="Visuel de landing page",
        target_width=1600,
        target_height=900,
        aspect_ratio="16:9",
    )

    result = build_prompt(
        brief
    )

    assert (
        "SORTIE : CUSTOM"
        in result.text
    )

    assert (
        "1600 x 900 px"
        in result.text
    )

    assert "16:9" in result.text


def test_collection_is_not_required() -> None:
    brief = Brief(
        title="Projet libre",
        mode=OutputMode.PINTEREST,
        raw_idea="Concept visuel",
        collection="",
    )

    result = build_prompt(
        brief
    )

    assert result.text