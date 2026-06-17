"""Abstract job source interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Job, Search


class JobSource(ABC):
    """Implement this to add a new data source (e.g. the official partner API)."""

    name: str = "base"

    @abstractmethod
    def fetch(self, search: Search, posted_within: str) -> list[Job]:
        """Return the most recent jobs for a search, newest first.

        Implementations should fail soft: on a network/parse error, log and
        return an empty list so the poll loop keeps running.
        """
        raise NotImplementedError
