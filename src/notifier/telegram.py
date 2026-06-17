"""Telegram push notifier via the Bot API."""
from __future__ import annotations

import html

import requests

from ..models import Job
from .base import Notifier


class TelegramNotifier(Notifier):
    def __init__(self, bot_token: str, chat_id: str, timeout: int = 10):
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id
        self._timeout = timeout

    def send(self, job: Job) -> bool:
        text = (
            f"🟢 <b>{html.escape(job.title)}</b>\n"
            f"🏢 {html.escape(job.company)}\n"
            f"📍 {html.escape(job.location)}\n"
            f"🔗 {html.escape(job.url)}"
        )
        try:
            resp = requests.post(
                self._url,
                json={
                    "chat_id": self._chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=self._timeout,
            )
        except requests.RequestException as exc:
            print(f"[telegram] send error: {exc}")
            return False

        if resp.status_code != 200:
            print(f"[telegram] HTTP {resp.status_code}: {resp.text[:200]}")
            return False
        return True
