from __future__ import annotations

import argparse
import base64
import hashlib
from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
AGENT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = AGENT_DIR / "package"
SKILL_SHA256 = "f3c8a560954217d2688455df97c78ff1096add9bb44833bd032c3c21c34fccc1"


def load_skill_zip() -> bytes:
    parts = sorted(PACKAGE_DIR.glob("skill.zip.b64.part*"))
    if not parts:
        raise RuntimeError("Aucun segment du Skill IA-Art n'a été trouvé.")

    encoded = "".join("".join(part.read_text(encoding="ascii").split()) for part in parts)
    skill_zip = base64.b64decode(encoded, validate=True)
    digest = hashlib.sha256(skill_zip).hexdigest()
    if digest != SKILL_SHA256:
        raise RuntimeError(
            f"Checksum du Skill invalide : {digest}, attendu {SKILL_SHA256}."
        )

    with ZipFile(BytesIO(skill_zip)) as archive:
        bad_file = archive.testzip()
        if bad_file is not None:
            raise RuntimeError(f"Skill ZIP corrompu : {bad_file}")
        if "ia-art/SKILL.md" not in archive.namelist():
            raise RuntimeError("Le Skill IA-Art ne contient pas ia-art/SKILL.md.")

    return skill_zip


def build_agent_package(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    skill_zip = load_skill_zip()

    skill_path = output_dir / "skill.zip"
    skill_path.write_bytes(skill_zip)

    agent_path = output_dir / "studio-visuel-agent.zip"
    with ZipFile(agent_path, "w", compression=ZIP_DEFLATED) as archive:
        archive.write(ROOT / "LICENSE", "LICENSE")
        archive.write(AGENT_DIR / "studio-visuel-agent.md", "studio-visuel-agent.md")
        archive.writestr("skill.zip", skill_zip)

    with ZipFile(agent_path) as archive:
        if archive.namelist() != ["LICENSE", "studio-visuel-agent.md", "skill.zip"]:
            raise RuntimeError("Structure du package Studio Visuel invalide.")
        if archive.testzip() is not None:
            raise RuntimeError("Package Studio Visuel corrompu.")

    return skill_path, agent_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Construit les packages Studio Visuel et IA-Art.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=AGENT_DIR / "dist",
        help="Dossier de sortie (agent/dist par défaut).",
    )
    args = parser.parse_args()

    skill_path, agent_path = build_agent_package(args.output_dir)
    print(f"Skill : {skill_path}")
    print(f"Agent : {agent_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
