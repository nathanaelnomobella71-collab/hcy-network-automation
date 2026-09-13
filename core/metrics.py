"""Instrumentation Prometheus — dictionnaire des métriques (2.7.2, Extrait 3.2).

Corrige l'avertissement "Import 'psycopg2' could not be resolved from
source" visible dans la capture d'écran de la version initiale (Figure 11
originale) : ce module ne dépend que de ``prometheus_client``.
"""
from __future__ import annotations

import logging

from prometheus_client import Counter, Gauge, start_http_server

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Trois indicateurs clés (KPIs), cf. Chapitre 2, 2.7.2 :
INCIDENTS_TOTAL = Counter(
    "hcy_incidents_total",
    "Nombre total d'incidents détectés",
    ["equipment", "type"],
)
FAILOVER_SUCCESS = Counter(
    "hcy_failover_success_total",
    "Nombre de remédiations réussies",
    ["equipment"],
)
EQUIPMENT_STATUS = Gauge(
    "hcy_equipment_status",
    "Statut de joignabilité (1=UP, 0=DOWN)",
    ["equipment"],
)


def start_metrics_server(port: int = 8000) -> None:
    """Démarre le serveur HTTP d'exportation Prometheus (cf. 3.6.1)."""
    start_http_server(port)
    logger.info("Serveur de métriques Prometheus démarré sur le port %s", port)
