"""RemediationFactory (pattern Factory) — Extrait 3.4.

Découple la sélection de la stratégie de son instanciation : centralise la
logique « quel type d'incident → quelle classe » (Chapitre 2, Tableau 2.5)
plutôt que de la disperser dans NetworkEngine.
"""
from __future__ import annotations

from core.models import IncidentType
from core.ssh_client import ISSHClient
from strategies.base import IRemediationStrategy
from strategies.failover_routing import FailoverRoutingStrategy
from strategies.interface_reset import InterfaceResetStrategy
from strategies.mac_isolation import MacIsolationStrategy


class RemediationFactory:
    """Sélectionne et instancie la stratégie adaptée au type d'incident (RF-04)."""

    def __init__(self, ssh_client: ISSHClient):
        self._ssh_client = ssh_client
        self._registry: dict[str, type[IRemediationStrategy]] = {
            IncidentType.MAC_INTRUSION.value: MacIsolationStrategy,
            IncidentType.LINK_DOWN.value: FailoverRoutingStrategy,
            IncidentType.INTERFACE_FLAP.value: InterfaceResetStrategy,
        }

    def create(self, incident_type: str) -> IRemediationStrategy:
        try:
            strategy_cls = self._registry[incident_type]
        except KeyError as exc:
            raise ValueError(f"Type d'incident inconnu : {incident_type!r}") from exc
        return strategy_cls(self._ssh_client)
