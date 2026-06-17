"""Fallback notifier that prints to stdout. Used when Telegram isn't configured."""
from __future__ import annotations

from ..models import Job
from .base import Notifier


class ConsoleNotifier(Notifier):
    def send(self, job: Job) -> bool:
        print(
            f"[alert] {job.title} @ {job.company} "
            f"({job.location}) -> {job.url}"
        )
        return True
