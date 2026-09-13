"""Interface IIncidentRepository (pattern Repository) — Figure 2.4.

Isole l'accès aux données du reste de l'application (RF-05) : permet de
substituer PostgreSQL par un autre SGBD en ne modifiant qu'une classe, et
c'est précisément ce qui rend DatabaseLogger (observers/db_logger.py)
testable sans base de données réelle (3.9.1).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import Incident


class IIncidentRepository(ABC):
    @abstractmethod
    def save(self, incident: Incident) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_all(self) -> list[Incident]:
        raise NotImplementedError
