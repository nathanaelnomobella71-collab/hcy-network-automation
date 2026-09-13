"""Interface IIncidentObserver (pattern Observer) — Figure 2.4.

Découple la détection d'un incident (NetworkEngine) de ses effets de bord
(persistance, métriques, alerte) : chaque abonné évolue indépendamment des
autres, et NetworkEngine n'a besoin de connaître aucun d'entre eux (cf.
Chapitre 1, 1.2.1 — justification du pattern).
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import Incident


class IIncidentObserver(ABC):
    @abstractmethod
    def update(self, incident: Incident) -> None:
        """Appelée par NetworkEngine après traitement d'un incident."""
        raise NotImplementedError
