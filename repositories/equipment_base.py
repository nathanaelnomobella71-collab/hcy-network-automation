"""Interface IEquipmentRepository (pattern Repository) — extension de la
Figure 2.4 : la persistance des incidents avait un Repository dédié, mais
l'inventaire des équipements n'en avait aucun avant cette itération — c'est
ce qui obligeait ``run_engine.py`` à coder sa liste d'équipements en dur au
lieu de l'interroger réellement depuis PostgreSQL (Tableau 2.7).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import Equipment


class IEquipmentRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Equipment]:
        raise NotImplementedError

    @abstractmethod
    def update_status(self, equipment_id: int, status: str) -> None:
        raise NotImplementedError
