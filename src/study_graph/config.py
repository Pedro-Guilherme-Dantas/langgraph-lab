import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    mode: str
    model: str


def load_settings() -> Settings:
    load_dotenv()
    return Settings(
        mode=os.getenv("STUDY_GRAPH_MODE", "demo"),
        model=os.getenv("STUDY_GRAPH_MODEL", "openai:gpt-4.1-mini"),
    )
