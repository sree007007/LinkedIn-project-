"""SQLite-backed store of already-seen job ids, for de-duplication.

Ensures each job is pushed exactly once across restarts.
"""
from __future__ import annotations

import sqlite3
import time

from .models import Job


class SeenStore:
    def __init__(self, path: str = "jobs.db"):
        self._conn = sqlite3.connect(path)
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS seen_jobs (
                id        TEXT PRIMARY KEY,
                seen_at   INTEGER NOT NULL
            )
            """
        )
        self._conn.commit()

    def filter_new(self, jobs: list[Job]) -> list[Job]:
        """Return only jobs not seen before (does not mark them yet)."""
        if not jobs:
            return []
        ids = [j.id for j in jobs]
        placeholders = ",".join("?" * len(ids))
        rows = self._conn.execute(
            f"SELECT id FROM seen_jobs WHERE id IN ({placeholders})", ids
        ).fetchall()
        known = {r[0] for r in rows}
        return [j for j in jobs if j.id not in known]

    def mark_seen(self, job: Job) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO seen_jobs (id, seen_at) VALUES (?, ?)",
            (job.id, int(time.time())),
        )
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()
