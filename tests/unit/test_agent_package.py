from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = ROOT / "agent"


def test_studio_visuel_package_embeds_current_agent_and_ia_art_contract() -> None:
    package_path = AGENT_DIR / "studio-visuel-agent.zip"

    with ZipFile(package_path) as package:
        assert package.namelist() == ["LICENSE", "studio-visuel-agent.md", "skill.zip"]
        assert package.read("studio-visuel-agent.md") == (
            AGENT_DIR / "studio-visuel-agent.md"
        ).read_bytes()
        skill_zip = package.read("skill.zip")

    with ZipFile(BytesIO(skill_zip)) as skill_package:
        skill_text = skill_package.read("ia-art/SKILL.md").decode("utf-8")
        format_rules = skill_package.read(
            "ia-art/references/format-rules.md"
        ).decode("utf-8")
        delivery_contract = skill_package.read(
            "ia-art/references/delivery-contract.md"
        ).decode("utf-8")
        renderer = skill_package.read(
            "ia-art/scripts/render_ia_art.py"
        ).decode("utf-8")

    assert "# IA-Art 5.0.1" in skill_text
    assert "JPEG/JPG" in skill_text
    assert "fiche de synthèse" in skill_text
    assert "Markdown Notion" in skill_text
    assert "instagram.jpg" in format_rules
    assert "instagram-01.jpg" in format_rules
    assert "N JPEG/JPG Instagram" in delivery_contract
    assert "JPEG_QUALITY = 95" in renderer
    assert 'format="JPEG"' in renderer
