"""Implémentation concrète d'ISSHClient basée sur Netmiko.

Corrige les deux défauts relevés dans la capture d'écran de la version
initiale du mémoire (Figure 12 originale) : l'import ``psycopg2`` qui n'avait
rien à faire dans ce module, et le logger utilisé sans être défini
(``"logging" is not defined``).

Nécessite le paquet tiers ``netmiko`` (cf. requirements.txt) : ce module
n'est donc pas exécuté par la suite de tests unitaires (3.9.1), qui teste les
stratégies via un ``ISSHClient`` mocké plutôt que cette classe elle-même.
"""
from __future__ import annotations

import logging

from netmiko import ConnectHandler

from core.models import Equipment, Result

logger = logging.getLogger(__name__)


class NetmikoSSHClient:
    """Connecteur SSH réel vers les équipements Cisco IOS (RFC 4253, cf. 1.4.3)."""

    def __init__(self, username: str, password: str, secret: str, device_type: str = "cisco_ios"):
        self._username = username
        self._password = password
        self._secret = secret
        self._device_type = device_type

    def send_config(self, device: Equipment, commands: list[str]) -> Result:
        """Se connecte à ``device`` via SSH et injecte les commandes CLI de remédiation."""
        cisco_device = {
            "device_type": self._device_type,
            "host": device.ip_address,
            "username": self._username,
            "password": self._password,
            "secret": self._secret,
        }
        try:
            logger.info("Connexion SSH en cours vers %s...", device.ip_address)
            net_connect = ConnectHandler(**cisco_device)
            net_connect.enable()

            output = net_connect.send_config_set(commands)
            logger.info("Remédiation appliquée sur %s:\n%s", device.ip_address, output)

            net_connect.disconnect()
            return Result(success=True, message="Remédiation appliquée", raw_output=output)
        except Exception as exc:  # noqa: BLE001 — isole toute défaillance réseau/SSH
            logger.error("Échec de la connexion SSH sur %s : %s", device.ip_address, str(exc))
            return Result(success=False, message=str(exc))
