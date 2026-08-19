from visual_ai_studio.domain.agent_contract import (
    AgentOutput,
    ConceptOutput,
    PublicationOutput,
    VisualOutput,
)
from visual_ai_studio.domain.output_modes import OutputMode


def test_agent_output_contract() -> None:
    output = AgentOutput(
        mode=OutputMode.INSTAGRAM,
        concept=ConceptOutput(
            title="Produit premium",
            intent="Créer de l'engagement",
            audience="Entrepreneurs",
        ),
        visual=VisualOutput(
            width=1080,
            height=1350,
            aspect_ratio="4:5",
            prompt="Premium editorial product photography",
            negative_prompt="low quality, distorted",
        ),
        publication=PublicationOutput(
            caption="Présentation du produit.",
            hashtags=["design", "creative"],
        ),
    )

    payload = output.model_dump(mode="json")

    assert payload["schema_version"] == "1.0"
    assert payload["mode"] == "instagram"
    assert payload["visual"]["width"] == 1080
    assert payload["publication"]["hashtags"] == ["design", "creative"]