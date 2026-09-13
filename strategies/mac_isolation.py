"""MacIsolationStrategy — isolation d'un port en violation de sécurité MAC.

Correspond au Scénario 1 du Chapitre 3 (3.10.3) et au diagramme de séquence
de la Figure 3.2 : le port est désactivé (``shutdown``) dès qu'une adresse
MAC absente de la liste blanche est détectée sur une prise surveillée.
"""
from __future__ import annotations

from core.models import Equipment, Result
from core.ssh_client import ISSHClient
from strategies.base import IRemediationStrategy


class MacIsolationStrategy(IRemediationStrategy):
    """Isolation d'un port en violation de sécurité MAC (RF-04)."""

    def __init__(self, ssh_client: ISSHClient):
        self._ssh_client = ssh_client

    def execute(self, device: Equipment) -> Result:
        commands = [
            f"interface {device.interface}",
            "description ISOLATED_BY_HCY_AUTOMATION",
            "shutdown",
        ]
        return self._ssh_client.send_config(device, commands)
