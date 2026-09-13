"""Abstraction du client SSH utilisé par les stratégies de remédiation.

Les stratégies (strategies/*.py) dépendent de cette interface — pas de
l'implémentation Netmiko concrète (core/netmiko_ssh_client.py). Cette
inversion de dépendance (principe D de SOLID, cf. Chapitre 1, 1.2.1) est ce
qui permet de tester MacIsolationStrategy, FailoverRoutingStrategy, etc. avec
un simple ``unittest.mock.MagicMock`` (3.9.1), sans jamais ouvrir de
connexion SSH réelle ni dépendre de la bibliothèque netmiko pendant les tests
unitaires.
"""
from __future__ import annotations

from typing import Protocol

from core.models import Equipment, Result


class ISSHClient(Protocol):
    """Contrat minimal requis par les stratégies de remédiation."""

    def send_config(self, device: Equipment, commands: list[str]) -> Result:
        """Ouvre une session vers ``device`` et applique ``commands``."""
        ...
