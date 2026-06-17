"""The poll loop: fetch -> dedupe -> match -> notify."""
from __future__ import annotations

import time

from .config import Config
from .matcher import matches
from .notifier.base import Notifier
from .sources.base import JobSource
from .store import SeenStore


class Poller:
    def __init__(
        self,
        config: Config,
        source: JobSource,
        notifier: Notifier,
        store: SeenStore,
    ):
        self.config = config
        self.source = source
        self.notifier = notifier
        self.store = store

    def run_once(self) -> int:
        """Run one polling pass across all searches. Returns # alerts sent."""
        sent = 0
        for search in self.config.searches:
            jobs = self.source.fetch(search, self.config.posted_within)
            new_jobs = self.store.filter_new(jobs)

            for job in new_jobs:
                # Always mark as seen so a non-matching or failed job isn't
                # reconsidered forever; we only notify if it matches.
                self.store.mark_seen(job)
                if matches(job, search):
                    if self.notifier.send(job):
                        sent += 1

            if new_jobs:
                print(
                    f"[poll] '{search.keywords}': {len(jobs)} fetched, "
                    f"{len(new_jobs)} new"
                )
        return sent

    def run_forever(self) -> None:
        interval = self.config.poll_interval_seconds
        print(
            f"[poller] started. source={self.source.name} "
            f"interval={interval}s searches={len(self.config.searches)}"
        )
        while True:
            try:
                sent = self.run_once()
                if sent:
                    print(f"[poll] sent {sent} alert(s)")
            except Exception as exc:  # keep the loop alive on any error
                print(f"[poll] unexpected error: {exc}")
            time.sleep(interval)
