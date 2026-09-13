"""Tests de resolve_remediation_target() — correction du défaut de logique
repéré avant test réel sur GNS3 : la remédiation d'un lien tombé ne doit
jamais tenter de se connecter en SSH sur l'équipement injoignable
lui-même (cf. run_engine.py, docstring de resolve_remediation_target).
"""
from run_engine import resolve_remediation_target
from core.models import Equipment, Incident, IncidentType, Severity

INVENTORY = [
    Equipment(id=1, hostname="coeur-reseau", ip_address="10.10.0.1", equipment_type="routeur_coeur"),
    Equipment(
        id=2, hostname="routeur-urgences", ip_address="192.168.20.1",
        equipment_type="routeur_distribution", backup_gateway="192.168.20.2",
        lan_subnet="192.168.20.0/24",
    ),
    Equipment(id=3, hostname="routeur-secours", ip_address="192.168.20.2", equipment_type="routeur_distribution"),
    Equipment(
        id=4, hostname="sw-caisse", ip_address="192.168.10.5",
        equipment_type="switch_acces", interface="FastEthernet0/1",
    ),
]


def test_link_down_redirects_to_core_router_not_the_failed_device():
    failed_router = INVENTORY[1]  # routeur-urgences, injoignable
    incident = Incident(
        id=None, equipment_id=2,
        incident_type=IncidentType.LINK_DOWN.value, severity=Severity.CRITICAL.value,
    )

    target = resolve_remediation_target(incident, failed_router, INVENTORY)

    assert target.hostname == "coeur-reseau"
    assert target.ip_address == "10.10.0.1"
    assert target.backup_gateway == "192.168.20.2"
    assert target.lan_subnet == "192.168.20.0/24"


def test_link_down_preserves_backup_gateway_from_failed_device():
    """La route à injecter reste celle définie sur l'équipement en panne,
    même si c'est un autre équipement (coeur-reseau) qui reçoit la commande."""
    failed_router = INVENTORY[1]
    incident = Incident(
        id=None, equipment_id=2,
        incident_type=IncidentType.LINK_DOWN.value, severity=Severity.CRITICAL.value,
    )

    target = resolve_remediation_target(incident, failed_router, INVENTORY)

    assert target.backup_gateway == failed_router.backup_gateway


def test_mac_intrusion_targets_the_switch_itself():
    """Un switch en violation de sécurité MAC reste joignable : pas de
    redirection nécessaire, on le reconfigure directement."""
    switch = INVENTORY[3]
    incident = Incident(
        id=None, equipment_id=4,
        incident_type=IncidentType.MAC_INTRUSION.value, severity=Severity.HIGH.value,
    )

    target = resolve_remediation_target(incident, switch, INVENTORY)

    assert target is switch


def test_link_down_without_backup_gateway_falls_back_to_failed_device():
    """Si aucune passerelle de secours n'est configurée pour l'équipement,
    impossible de rediriger intelligemment : on retombe sur le comportement
    d'origine plutôt que de lever une exception."""
    router_without_backup = Equipment(
        id=5, hostname="routeur-isole", ip_address="192.168.30.1", equipment_type="routeur_distribution"
    )
    incident = Incident(
        id=None, equipment_id=5,
        incident_type=IncidentType.LINK_DOWN.value, severity=Severity.CRITICAL.value,
    )

    target = resolve_remediation_target(incident, router_without_backup, INVENTORY)

    assert target is router_without_backup


def test_missing_core_router_in_inventory_falls_back_safely():
    """Si 'coeur-reseau' n'existe pas en base (mauvaise config), on ne plante
    pas : on retombe sur l'équipement en panne plutôt que de lever une erreur
    non gérée dans la boucle de polling."""
    failed_router = INVENTORY[1]
    incident = Incident(
        id=None, equipment_id=2,
        incident_type=IncidentType.LINK_DOWN.value, severity=Severity.CRITICAL.value,
    )
    inventory_without_core = [e for e in INVENTORY if e.hostname != "coeur-reseau"]

    target = resolve_remediation_target(incident, failed_router, inventory_without_core)

    assert target is failed_router
