from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .output_modes import OutputMode


class ConceptOutput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = ""
    intent: str = ""
    audience: str = ""
    rationale: str = ""


class VisualOutput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    width: int | None = Field(default=None, ge=1)
    height: int | None = Field(default=None, ge=1)
    aspect_ratio: str = ""
    prompt: str = ""
    negative_prompt: str = ""
    text_overlay: str = ""


class PublicationOutput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = ""
    caption: str = ""
    alt_text: str = ""
    hashtags: list[str] = Field(default_factory=list)


class AgentOutput(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    mode: OutputMode
    concept: ConceptOutput = Field(default_factory=ConceptOutput)
    visual: VisualOutput = Field(default_factory=VisualOutput)
    publication: PublicationOutput = Field(default_factory=PublicationOutput)
