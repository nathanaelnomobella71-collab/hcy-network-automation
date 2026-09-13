"""Modèles de domaine partagés entre les couches métier, stratégies et repositories.

Ces classes correspondent au schéma physique de données défini au Chapitre 2
(Tableau 2.7) et au diagramme de classes (Figure 2.4). Elles ne dépendent que
de la bibliothèque standard, ce qui les rend testables sans base de données
réelle ni dépendance réseau.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class IncidentType(str, Enum):
    """Types d'anomalies détectées, conformes à RF-02 (Tableau 2.2)."""

    MAC_INTRUSION = "MAC_INTRUSION"
    LINK_DOWN = "LINK_DOWN"
    INTERFACE_FLAP = "INTERFACE_FLAP"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class UserRole(str, Enum):
    """Rôles RBAC — Architecture sécuritaire, Chapitre 2 (2.10)."""

    ADMIN = "admin"
    TECHNICIAN = "technician"


@dataclass
class Equipment:
    """Correspond à la table ``equipments`` (Tableau 2.7, étendue)."""

    id: int
    hostname: str
    ip_address: str
    equipment_type: str
    location: str = ""
    status: str = "UP"
    # Champs utilisés au moment de la remédiation :
    interface: str = ""       # interface concernée par l'incident courant
    backup_gateway: str = ""  # prochain saut de secours, utilisé par FailoverRoutingStrategy
    lan_subnet: str = ""      # sous-réseau desservi (ex. "192.168.20.0/24") — bascule ciblée, pas globale


@dataclass
class Incident:
    """Correspond à la table ``incidents`` (Tableau 2.7)."""

    id: int | None
    equipment_id: int
    incident_type: str
    severity: str
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved: bool = False


@dataclass
class Remediation:
    """Correspond à la table ``remediations`` (Tableau 2.7)."""

    id: int | None
    incident_id: int
    action_taken: str
    execution_status: str
    executed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Result:
    """Résultat renvoyé par ``IRemediationStrategy.execute()`` (Figure 2.4)."""

    success: bool
    message: str
    raw_output: str = ""
