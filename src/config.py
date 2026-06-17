"""Load configuration from config.yaml + environment (.env)."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

import yaml
from dotenv import load_dotenv

from .models import Search


@dataclass
class Config:
    source: str = "linkedin"
    poll_interval_seconds: int = 300
    posted_within: str = "r3600"
    searches: list[Search] = field(default_factory=list)
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    @property
    def telegram_ready(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)


def load_config(path: str = "config.yaml") -> Config:
    load_dotenv()

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"{path} not found. Copy config.example.yaml to {path} and edit it."
        )

    with open(path, "r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh) or {}

    searches = [
        Search(
            keywords=str(s.get("keywords", "")).strip(),
            location=str(s.get("location", "")).strip(),
            include=[k.lower() for k in s.get("include", [])],
            exclude=[k.lower() for k in s.get("exclude", [])],
        )
        for s in raw.get("searches", [])
        if str(s.get("keywords", "")).strip()
    ]

    if not searches:
        raise ValueError("config.yaml must define at least one search with keywords.")

    interval = int(raw.get("poll_interval_seconds", 300))
    if interval < 60:
        # Guardrail: aggressive polling gets you blocked and is abusive.
        print(
            f"[config] poll_interval_seconds={interval} is too low; "
            "raising to 60 to stay respectful."
        )
        interval = 60

    return Config(
        source=str(raw.get("source", "linkedin")).lower(),
        poll_interval_seconds=interval,
        posted_within=str(raw.get("posted_within", "r3600")),
        searches=searches,
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
    )
