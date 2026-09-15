from visual_ai_studio.domain.models import Brief
from visual_ai_studio.domain.output_modes import OutputMode
from visual_ai_studio.domain.prompt_builder import build_prompt


def test_instagram_prompt_targets_studio_visuel() -> None:
    brief = Brief(
        title="Campagne été",
        mode=OutputMode.INSTAGRAM,
        raw_idea="Portrait éditorial premium",
        audience="Femmes 25-45 ans",
    )
    result = build_prompt(brief)
    assert "AGENT CIBLE : Studio Visuel" in result.text
    assert "INTENTION : CREATION_IMAGE" in result.text
    assert "SORTIE : INSTAGRAM" in result.text
    assert "1080 x 1350 px" in result.text
    assert "4:5" in result.text
    assert "Étape 1" in result.text


def test_instagram_multi_image_prompt_describes_one_post() -> None:
    brief = Brief(
        title="Série Instagram",
        mode=OutputMode.INSTAGRAM,
        raw_idea="Une mini-série narrative",
        post_image_count=4,
    )
    result = build_prompt(brief)
    assert "Nombre de visuels principaux : 4" in result.text
    assert "4 visuels principaux cohérents à publier ensemble" in result.text
    assert "une seule publication" in result.text
    assert "JPEG/JPG réel" in result.text
    assert "PNG est accepté uniquement comme source intermédiaire" in result.text
    assert "fiche de synthèse PNG" in result.text
    assert "Markdown IA-Art" in result.text
    assert "livrables obligatoires" in result.text
    assert "N JPEG/JPG signés + 1 synthèse PNG + 1 Markdown + archive" in result.text


def test_custom_prompt_accepts_free_format() -> None:
    brief = Brief(
        title="Bannière web",
        mode=OutputMode.CUSTOM,
        raw_idea="Visuel de landing page",
        target_width=1600,
        target_height=900,
        aspect_ratio="16:9",
    )
    result = build_prompt(brief)
    assert "SORTIE : CUSTOM" in result.text
    assert "1600 x 900 px" in result.text
    assert "16:9" in result.text


def test_collection_is_not_required() -> None:
    brief = Brief(
        title="Projet libre",
        mode=OutputMode.INSTAGRAM,
        raw_idea="Concept visuel",
        collection="",
    )
    result = build_prompt(brief)
    assert result.text
