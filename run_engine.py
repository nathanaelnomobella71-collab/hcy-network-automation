"""Point d'entrée : démarre le moteur de surveillance en continu (RF-01).

Lance la boucle infinie décrite par le diagramme d'activité (Chapitre 2,
Figure 2.5) et la boucle de rétroaction du Chapitre 1 (1.4.6) :
collecte -> analyse -> remédiation (Strategy/Factory) -> notification
(Observer). C'est le processus hôte "Tier 2" mentionné en 3.4 — à lancer
en dehors de Docker Compose, sur le même réseau que la GNS3 VM
(interface Host-Only VirtualBox).

Usage :
    python run_engine.py
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import replace

from dotenv import load_dotenv

load_dotenv()

from core.analyzer import Analyzer  # noqa: E402
from core.collector import Collector  # noqa: E402
from core.engine import NetworkEngine  # noqa: E402
from core.metrics import EQUIPMENT_STATUS, start_metrics_server  # noqa: E402
from core.models import Equipment, IncidentType  # noqa: E402
from core.netmiko_ssh_client import NetmikoSSHClient  # noqa: E402
from observers.alert_notifier import AlertNotifier  # noqa: E402
from observers.db_logger import DatabaseLogger  # noqa: E402
from observers.prometheus_exporter import PrometheusExporter  # noqa: E402
from repositories.postgres_equipment_repository import PostgresEquipmentRepository  # noqa: E402
from repositories.postgres_repository import PostgresIncidentRepository  # noqa: E402
from strategies.factory import RemediationFactory  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def resolve_remediation_target(
    incident, failed_device: Equipment, equipment_list: list[Equipment]
) -> Equipment:
    """Détermine SUR QUEL équipement la remédiation doit réellement se
    connecter en SSH.

    Correction d'un défaut de logique repéré avant test réel sur GNS3 : la
    version précédente appelait ``strategy.execute(failed_device)``, ce qui
    tentait une connexion SSH sur l'équipement injoignable lui-même — un
    routeur en panne ne répond jamais en SSH. Conformément au diagramme de
    séquence (Figure 3.3), la bascule de routage doit s'exécuter depuis un
    équipement resté joignable (ici : le routeur de cœur), qui reçoit la
    nouvelle route par défaut pointant vers la liaison de secours.

    Pour une isolation MAC (Figure 3.2), l'équipement fautif (le switch
    d'accès lui-même) est toujours joignable — c'est justement lui qu'on
    reconfigure — donc aucune redirection n'est nécessaire dans ce cas.
    """
    if incident.incident_type != IncidentType.LINK_DOWN.value or not failed_device.backup_gateway:
        return failed_device

    core = next((e for e in equipment_list if e.hostname == "coeur-reseau"), None)
    if core is None:
        logger.error(
            "Impossible de router la remédiation : aucun équipement 'coeur-reseau' en base."
        )
        return failed_device

    # Équipement synthétique, non persisté : même identité de connexion que
    # le cœur de réseau (réellement joignable), mais portant la route de
    # secours et le sous-réseau spécifiques à l'équipement en panne — pour
    # que FailoverRoutingStrategy cible ce seul sous-réseau (cf. sa docstring).
    return replace(
        core,
        backup_gateway=failed_device.backup_gateway,
        lan_subnet=failed_device.lan_subnet,
    )


def build_engine() -> tuple[NetworkEngine, Collector, Analyzer, PostgresEquipmentRepository]:
    """Assemble l'orchestrateur avec ses vraies dépendances (injection manuelle)."""
    ssh_client = NetmikoSSHClient(
        username=os.environ["HCY_CISCO_USERNAME"],
        password=os.environ["HCY_CISCO_PASSWORD"],
        secret=os.environ["HCY_CISCO_SECRET"],
    )
    collector = Collector(polling_interval=5)
    analyzer = Analyzer()
    factory = RemediationFactory(ssh_client)
    engine = NetworkEngine(collector, analyzer, factory)

    dsn = os.environ["HCY_DB_DSN"]
    incident_repository = PostgresIncidentRepository(dsn)
    equipment_repository = PostgresEquipmentRepository(dsn)

    engine.register_observer(DatabaseLogger(incident_repository))  # RF-05
    engine.register_observer(PrometheusExporter())                  # RF-06
    engine.register_observer(AlertNotifier())                       # 1.4.7

    return engine, collector, analyzer, equipment_repository


def main() -> None:
    engine, collector, analyzer, equipment_repository = build_engine()

    start_metrics_server(port=8000)  # cf. 3.6.1, scrapé par prometheus.yml (engine:8000)
    engine.start_polling()

    try:
        while engine.running:
            # RF-01 : relit l'inventaire à chaque cycle plutôt qu'une fois au
            # démarrage — un équipement ajouté/retiré en base (ou via un futur
            # écran d'administration) est pris en compte sans redémarrage.
            equipment_list = equipment_repository.find_all()
            if not equipment_list:
                logger.warning(
                    "Aucun équipement en base (table 'equipments' vide) — "
                    "vérifie sql/init.sql / HCY_DB_DSN."
                )

            for device in equipment_list:
                reachable = collector.ping_device(device.ip_address)
                EQUIPMENT_STATUS.labels(equipment=device.hostname).set(1 if reachable else 0)

                new_status = "UP" if reachable else "DOWN"
                if new_status != device.status:
                    equipment_repository.update_status(device.id, new_status)
                    logger.info("%s : statut mis à jour -> %s", device.hostname, new_status)

                incident = analyzer.evaluate_metrics(
                    {"equipment_id": device.id, "reachable": reachable}
                )
                if incident is not None:
                    logger.warning(
                        "Incident détecté sur %s : %s", device.hostname, incident.incident_type
                    )
                    remediation_target = resolve_remediation_target(incident, device, equipment_list)
                    engine.handle(incident, remediation_target)

            time.sleep(collector.polling_interval)
    except KeyboardInterrupt:
        engine.stop_engine()
        logger.info("Arrêt demandé par l'utilisateur (Ctrl+C).")


if __name__ == "__main__":
    main()
