"""InterfaceResetStrategy — réinitialisation d'une interface instable.

Troisième stratégie de remédiation (avec MacIsolationStrategy et
FailoverRoutingStrategy), qui complète l'objectif OS2 du mémoire
(« ≥ 3 stratégies de remédiation interchangeables sans modification du
moteur », Introduction générale, §4.2 ; validée en 4.4.1). Traite les
micro-coupures répétées d'une interface (« flapping ») en la redémarrant.
"""
from __future__ import annotations

from core.models import Equipment, Result
from core.ssh_client import ISSHClient
from strategies.base import IRemediationStrategy


class InterfaceResetStrategy(IRemediationStrategy):
    """Réinitialisation (bounce) d'une interface signalant des instabilités répétées."""

    def __init__(self, ssh_client: ISSHClient):
        self._ssh_client = ssh_client

    def execute(self, device: Equipment) -> Result:
        commands = [
            f"interface {device.interface}",
            "shutdown",
            "no shutdown",
        ]
        return self._ssh_client.send_config(device, commands)
