"""Modèles Pydantic — validation des entrées/sorties de l'API (3.7)."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EquipmentOut(BaseModel):
    id: int
    hostname: str
    ip_address: str
    equipment_type: str
    location: str | None = None
    status: str
    lan_subnet: str | None = None

    model_config = {"from_attributes": True}


class IncidentOut(BaseModel):
    id: int
    equipment_id: int
    incident_type: str
    severity: str
    detected_at: datetime
    resolved: bool

    model_config = {"from_attributes": True}


class RemediationResult(BaseModel):
    incident_id: int
    success: bool
    message: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
