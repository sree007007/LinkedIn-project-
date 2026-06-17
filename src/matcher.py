"""Keyword include/exclude matching for a job against a search's filters."""
from __future__ import annotations

from .models import Job, Search


def matches(job: Job, search: Search) -> bool:
    """True if the job passes the search's include/exclude keyword filters.

    - include: if set, the job title+company must contain at least one term.
    - exclude: if any term appears, the job is rejected.
    Matching is case-insensitive substring matching.
    """
    text = job.haystack()

    if search.exclude and any(term in text for term in search.exclude):
        return False

    if search.include and not any(term in text for term in search.include):
        return False

    return True
