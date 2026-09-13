"""Tests unitaires du pattern Strategy (3.9.1, Extrait 3.7).

Isole les dépendances réseau par un double de test (``unittest.mock``) qui
respecte le contrat ``ISSHClient`` — aucune connexion SSH réelle n'est
ouverte, aucun équipement Cisco n'a besoin d'être disponible.
"""
from unittest.mock import MagicMock

from core.models import Equipment, Result
from strategies.failover_routing import FailoverRoutingStrategy
from strategies.interface_reset import InterfaceResetStrategy
from strategies.mac_isolation import MacIsolationStrategy


def _device(**overrides) -> Equipment:
    base = dict(
        id=1,
        hostname="sw-caisse",
        ip_address="192.168.10.5",
        equipment_type="switch",
        interface="FastEthernet0/1",
        backup_gateway="192.168.20.1",
    )
    base.update(overrides)
    return Equipment(**base)


def test_mac_isolation_sends_shutdown_command():
    device = _device()
    ssh_mock = MagicMock()
    ssh_mock.send_config.return_value = Result(success=True, message="ok")
    strategy = MacIsolationStrategy(ssh_mock)

    result = strategy.execute(device)

    sent_commands = ssh_mock.send_config.call_args[0][1]
    assert "shutdown" in sent_commands
    assert any("FastEthernet0/1" in cmd for cmd in sent_commands)
    assert result.success is True


def test_failover_routing_targets_specific_subnet_not_default_route():
    """Corrige l'Extrait 3.3 original (route 0.0.0.0/0) : sur une topologie à
    plusieurs routeurs de distribution, seule la route du sous-réseau en
    panne doit être injectée, pas une route par défaut globale."""
    device = _device(backup_gateway="10.10.2.2", lan_subnet="192.168.20.0/24")
    ssh_mock = MagicMock()
    ssh_mock.send_config.return_value = Result(success=True, message="ok")
    strategy = FailoverRoutingStrategy(ssh_mock)

    strategy.execute(device)

    sent_commands = ssh_mock.send_config.call_args[0][1]
    assert sent_commands == ["ip route 192.168.20.0 255.255.255.0 10.10.2.2"]


def test_failover_routing_falls_back_to_default_route_without_lan_subnet():
    """Compatibilité ascendante : sans lan_subnet renseigné (topologie à un
    seul routeur de distribution), retombe sur le comportement d'origine."""
    device = _device(backup_gateway="10.0.0.254", lan_subnet="")
    ssh_mock = MagicMock()
    ssh_mock.send_config.return_value = Result(success=True, message="ok")
    strategy = FailoverRoutingStrategy(ssh_mock)

    strategy.execute(device)

    sent_commands = ssh_mock.send_config.call_args[0][1]
    assert any("10.0.0.254" in cmd for cmd in sent_commands)
    assert any("0.0.0.0 0.0.0.0" in cmd for cmd in sent_commands)
    assert any(cmd.startswith("ip route 0.0.0.0 0.0.0.0") for cmd in sent_commands)


def test_interface_reset_bounces_interface():
    device = _device()
    ssh_mock = MagicMock()
    ssh_mock.send_config.return_value = Result(success=True, message="ok")
    strategy = InterfaceResetStrategy(ssh_mock)

    strategy.execute(device)

    sent_commands = ssh_mock.send_config.call_args[0][1]
    assert "shutdown" in sent_commands
    assert "no shutdown" in sent_commands


def test_strategy_returns_the_ssh_client_result_unchanged():
    """Une stratégie ne doit jamais masquer un échec renvoyé par le client SSH."""
    device = _device()
    ssh_mock = MagicMock()
    ssh_mock.send_config.return_value = Result(success=False, message="Timeout SSH")
    strategy = MacIsolationStrategy(ssh_mock)

    result = strategy.execute(device)

    assert result.success is False
    assert result.message == "Timeout SSH"
