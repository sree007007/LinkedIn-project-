"""Job sources. Pluggable: add a class implementing JobSource and register it."""
from __future__ import annotations

from .base import JobSource
from .linkedin_guest import LinkedInGuestSource
from .mock import MockSource


def get_source(name: str) -> JobSource:
    name = (name or "linkedin").lower()
    if name == "linkedin":
        return LinkedInGuestSource()
    if name == "mock":
        return MockSource()
    raise ValueError(f"Unknown source: {name!r}. Use 'linkedin' or 'mock'.")
