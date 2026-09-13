"""FailoverRoutingStrategy — bascule vers la liaison de secours.

Correspond au Scénario 2 du Chapitre 3 (3.10.4) et au diagramme de séquence
de la Figure 3.3. Version corrigée après revue de la topologie densifiée
(plusieurs routeurs de distribution) : l'Extrait 3.3 du mémoire injectait une
route par défaut (0.0.0.0/0), ce qui redirigerait TOUT le trafic du cœur de
réseau dès qu'un seul routeur de distribution tombe — correct avec un seul
routeur de distribution, mais trop grossier dès qu'il y en a plusieurs.
Cette version injecte une route spécifique au seul sous-réseau concerné
(``device.lan_subnet``), laissant les autres segments inchangés.
"""
from __future__ import annotations

import ipaddress
import logging

from core.models import Equipment, Result
from core.ssh_client import ISSHClient
from strategies.base import IRemediationStrategy

logger = logging.getLogger(__name__)


class FailoverRoutingStrategy(IRemediationStrategy):
    """Bascule de routage ciblée vers la liaison de secours (RF-04)."""

    def __init__(self, ssh_client: ISSHClient):
        self._ssh_client = ssh_client

    def execute(self, device: Equipment) -> Result:
        commands = [self._build_route_command(device)]
        return self._ssh_client.send_config(device, commands)

    @staticmethod
    def _build_route_command(device: Equipment) -> str:
        if not device.lan_subnet:
            # Compatibilité ascendante : sans sous-réseau déclaré, on retombe
            # sur le comportement d'origine (route par défaut) plutôt que de
            # planter — pertinent seulement sur une topologie à un seul
            # routeur de distribution.
            logger.warning(
                "Equipment %s sans lan_subnet : bascule par route par défaut (0.0.0.0/0), "
                "imprécise sur une topologie à plusieurs routeurs de distribution.",
                device.hostname,
            )
            return f"ip route 0.0.0.0 0.0.0.0 {device.backup_gateway}"

        network = ipaddress.ip_network(device.lan_subnet, strict=False)
        return f"ip route {network.network_address} {network.netmask} {device.backup_gateway}"
