"""Offline mock source. Lets you test matching + Telegram without scraping.

Each fetch() returns one freshly-generated job so you can watch the whole
pipeline (dedupe -> match -> notify) work end to end.
"""
from __future__ import annotations

import time

from ..models import Job, Search
from .base import JobSource


class MockSource(JobSource):
    name = "mock"

    def fetch(self, search: Search, posted_within: str) -> list[Job]:
        now = int(time.time())
        kw = (search.keywords or "engineer").split()[0]
        return [
            Job(
                id=f"mock-{now}",
                title=f"{kw.title()} Developer",
                company="Acme Corp",
                location=search.location or "Remote",
                url=f"https://example.com/jobs/{now}",
                posted_at="",
                source="mock",
            )
        ]
