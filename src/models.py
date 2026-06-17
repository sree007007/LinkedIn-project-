"""Shared data types."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Job:
    """A single job posting from any source."""

    id: str  # stable unique id used for de-duplication
    title: str
    company: str
    location: str
    url: str
    posted_at: str = ""  # ISO datetime string if the source provides one
    source: str = ""

    def haystack(self) -> str:
        """Lowercased text used for keyword include/exclude matching."""
        return f"{self.title} {self.company}".lower()


@dataclass
class Search:
    """One user-configured search with optional keyword filters."""

    keywords: str
    location: str = ""
    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)
