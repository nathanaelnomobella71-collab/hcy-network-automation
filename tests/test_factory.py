"""Tests unitaires du pattern Factory (3.9.1, Extrait 3.7)."""
from unittest.mock import MagicMock

import pytest

from strategies.factory import RemediationFactory
from strategies.failover_routing import FailoverRoutingStrategy
from strategies.interface_reset import InterfaceResetStrategy
from strategies.mac_isolation import MacIsolationStrategy


def test_factory_returns_mac_isolation_strategy():
    factory = RemediationFactory(ssh_client=MagicMock())
    assert isinstance(factory.create("MAC_INTRUSION"), MacIsolationStrategy)


def test_factory_returns_failover_routing_strategy():
    factory = RemediationFactory(ssh_client=MagicMock())
    assert isinstance(factory.create("LINK_DOWN"), FailoverRoutingStrategy)


def test_factory_returns_interface_reset_strategy():
    factory = RemediationFactory(ssh_client=MagicMock())
    assert isinstance(factory.create("INTERFACE_FLAP"), InterfaceResetStrategy)


def test_factory_raises_on_unknown_incident_type():
    factory = RemediationFactory(ssh_client=MagicMock())
    with pytest.raises(ValueError):
        factory.create("UNKNOWN_TYPE")


def test_factory_injects_the_same_ssh_client_into_every_strategy():
    """Vérifie que la Factory propage bien sa dépendance SSH (injection de dépendance)."""
    shared_ssh_client = MagicMock()
    factory = RemediationFactory(ssh_client=shared_ssh_client)

    strategy = factory.create("MAC_INTRUSION")

    assert strategy._ssh_client is shared_ssh_client
