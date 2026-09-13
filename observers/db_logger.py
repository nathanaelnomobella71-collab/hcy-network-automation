"""DatabaseLogger — persiste chaque incident via le Repository (RF-05)."""
from __future__ import annotations

from core.models import Incident
from observers.base import IIncidentObserver
from repositories.base import IIncidentRepository


class DatabaseLogger(IIncidentObserver):
    """Journalise l'incident en base sans jamais accéder directement à SQL."""

    def __init__(self, repository: IIncidentRepository):
        self._repository = repository

    def update(self, incident: Incident) -> None:
        self._repository.save(incident)
