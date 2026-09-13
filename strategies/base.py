"""Interface IRemediationStrategy (pattern Strategy) — Figure 2.4, Extrait 3.3.

Chaque type d'incident (RF-02) est corrigé par une stratégie interchangeable
implémentant ce contrat unique. Ajouter un nouveau type de remédiation
revient à écrire une nouvelle classe et une entrée dans le registre de
RemediationFactory (strategies/factory.py), sans jamais modifier
NetworkEngine (core/engine.py) — principe Ouvert/Fermé de SOLID, cf.
Chapitre 2, Tableau 2.5.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import Equipment, Result


class IRemediationStrategy(ABC):
    """Contrat commun à toutes les stratégies de remédiation (RF-04)."""

    @abstractmethod
    def execute(self, device: Equipment) -> Result:
        """Applique l'action corrective sur ``device`` et renvoie le résultat."""
        raise NotImplementedError
