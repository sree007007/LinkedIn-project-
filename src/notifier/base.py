"""Abstract notifier interface."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import Job


class Notifier(ABC):
    @abstractmethod
    def send(self, job: Job) -> bool:
        """Push a single job alert. Return True on success."""
        raise NotImplementedError
