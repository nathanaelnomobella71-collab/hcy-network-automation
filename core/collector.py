"""Collector — collecte d'état réseau en continu (RF-01, Figure 2.4)."""
from __future__ import annotations

import logging
import subprocess

logger = logging.getLogger(__name__)


class Collector:
    """Interroge les équipements réseau via ICMP/SNMP (cf. 1.4.2)."""

    def __init__(self, polling_interval: int = 5):
        self.polling_interval = polling_interval

    def ping_device(self, ip: str) -> bool:
        """Test de joignabilité ICMP (RFC 792, cf. 1.4.2)."""
        try:
            result = subprocess.run(
                ["ping", "-c", "1", "-W", "1", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2,
                check=False,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError) as exc:
            logger.warning("Ping impossible vers %s : %s", ip, exc)
            return False

    def check_snmp_status(self, ip: str) -> dict:
        """Interrogation SNMP (RFC 1157, cf. 1.4.2).

        Implémentation de référence minimale : à raccorder à ``pysnmp`` (ou
        équivalent) pour interroger réellement les MIB en production. Isolée
        dans sa propre méthode pour rester substituable sans toucher au
        reste du Collector (principe de responsabilité unique).
        """
        return {"ip": ip, "cpu_usage": None, "bandwidth_usage": None}

    def scrape_metrics(self) -> dict:
        """Métriques internes du Collector lui-même (fréquence de polling, etc.)."""
        return {"polling_interval": self.polling_interval}
