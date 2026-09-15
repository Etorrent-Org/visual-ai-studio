import hashlib
from io import BytesIO
from pathlib import Path
from runpy import run_path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = ROOT / "agent"
PACKAGE_AGENT = run_path(str(AGENT_DIR / "package_agent.py"))
SKILL_SHA256 = PACKAGE_AGENT["SKILL_SHA256"]
build_agent_package = PACKAGE_AGENT["build_agent_package"]


def test_studio_visuel_package_embeds_current_agent_and_ia_art_contract(tmp_path: Path) -> None:
    skill_path, package_path = build_agent_package(tmp_path)

    assert hashlib.sha256(skill_path.read_bytes()).hexdigest() == SKILL_SHA256

    with ZipFile(package_path) as package:
        assert package.namelist() == ["LICENSE", "studio-visuel-agent.md", "skill.zip"]
        assert package.read("studio-visuel-agent.md") == (
            AGENT_DIR / "studio-visuel-agent.md"
        ).read_bytes()
        skill_zip = package.read("skill.zip")
        assert skill_zip == skill_path.read_bytes()

    with ZipFile(BytesIO(skill_zip)) as skill_package:
        assert skill_package.testzip() is None
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

    assert "# IA-Art 5.0.2" in skill_text
    assert "JPEG/JPG" in skill_text
    assert "fiche de synthèse" in skill_text
    assert "Markdown Notion" in skill_text
    assert "continue" in skill_text
    assert "Reprise automatique au tour suivant" in skill_text
    assert "même tour de reprise" in skill_text
    assert "instagram.jpg" in format_rules
    assert "instagram-01.jpg" in format_rules
    assert "PNG sources" in format_rules
    assert "N JPEG/JPG Instagram" in delivery_contract
    assert "packaging complet dans le même tour de reprise" in delivery_contract
    assert 'VERSION = "5.0.2"' in renderer
    assert "JPEG_QUALITY = 95" in renderer
    assert 'format="JPEG"' in renderer
