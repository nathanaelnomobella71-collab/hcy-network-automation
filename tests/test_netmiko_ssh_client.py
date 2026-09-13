"""Test unitaire de NetmikoSSHClient (3.9.1).

``netmiko.ConnectHandler`` est mocké : on vérifie la construction des
paramètres de connexion et la gestion des deux issues possibles (succès,
exception réseau) sans jamais ouvrir de session SSH réelle.
"""
from unittest.mock import MagicMock, patch

from core.models import Equipment
from core.netmiko_ssh_client import NetmikoSSHClient


def _device() -> Equipment:
    return Equipment(id=1, hostname="sw1", ip_address="192.168.10.5", equipment_type="switch")


@patch("core.netmiko_ssh_client.ConnectHandler")
def test_send_config_returns_success_result_on_normal_execution(mock_connect_handler):
    mock_connection = MagicMock()
    mock_connection.send_config_set.return_value = "config applied"
    mock_connect_handler.return_value = mock_connection

    client = NetmikoSSHClient(username="admin", password="pwd", secret="secret")
    result = client.send_config(_device(), ["interface Fa0/1", "shutdown"])

    assert result.success is True
    assert result.raw_output == "config applied"
    mock_connection.enable.assert_called_once()
    mock_connection.disconnect.assert_called_once()


@patch("core.netmiko_ssh_client.ConnectHandler", side_effect=OSError("host unreachable"))
def test_send_config_returns_failure_result_when_connection_fails(mock_connect_handler):
    client = NetmikoSSHClient(username="admin", password="pwd", secret="secret")

    result = client.send_config(_device(), ["shutdown"])

    assert result.success is False
    assert "host unreachable" in result.message
