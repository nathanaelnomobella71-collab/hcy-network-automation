"""API REST FastAPI (3.7, Extrait 3.5).

Remplace l'accès direct psycopg2 depuis Streamlit de la version initiale :
la couche Présentation (ui/streamlit_app.py) ne dialogue plus jamais
directement avec PostgreSQL, tout transite par cette API (Chapitre 2, 2.9).
"""
from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.security import OAuth2PasswordRequestForm  # noqa: E402

from api.auth import create_access_token, get_current_user, require_role, verify_password  # noqa: E402
from api.schemas import EquipmentOut, IncidentOut, RemediationResult, Token  # noqa: E402
from repositories.postgres_equipment_repository import PostgresEquipmentRepository  # noqa: E402
from repositories.postgres_repository import PostgresIncidentRepository  # noqa: E402

app = FastAPI(title="HCY Network Automation API", version="1.0.0")

DB_DSN = os.environ.get("HCY_DB_DSN", "")  # jamais en dur dans le code (3.7)
incident_repository = PostgresIncidentRepository(DB_DSN)
equipment_repository = PostgresEquipmentRepository(DB_DSN)

# Utilisateurs de démonstration — à remplacer par la table `users` (Tableau 2.7)
# une fois la migration correspondante appliquée en base.
_DEMO_USERS = {
    "admin": {"password_hash": os.environ.get("HCY_ADMIN_PASSWORD_HASH", ""), "role": "admin"},
}


@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    """Émet un jeton JWT après vérification des identifiants (RF-07)."""
    user = _DEMO_USERS.get(form_data.username)
    if not user or not user["password_hash"]:
        raise HTTPException(401, "Identifiants invalides")
    if not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(401, "Identifiants invalides")
    token = create_access_token({"sub": form_data.username, "role": user["role"]})
    return Token(access_token=token)


@app.get("/incidents", response_model=list[IncidentOut])
def list_incidents(user: dict = Depends(get_current_user)) -> list[IncidentOut]:
    """RF-06 — consultation de l'historique des incidents (Tableau 2.6)."""
    return incident_repository.find_all()


@app.get("/equipments", response_model=list[EquipmentOut])
def list_equipments(user: dict = Depends(get_current_user)) -> list[EquipmentOut]:
    """RF-01 — état courant des équipements supervisés, lu depuis PostgreSQL
    (et non plus une liste codée en dur, cf. run_engine.py)."""
    return equipment_repository.find_all()


@app.post("/remediate/{incident_id}", response_model=RemediationResult)
def remediate(
    incident_id: int, user: dict = Depends(require_role("admin", "technician"))
) -> RemediationResult:
    """RF-04 — déclenchement manuel d'une remédiation (Tableau 2.6, portail Streamlit).

    Le raccordement à ``NetworkEngine.handle()`` (core/engine.py) nécessite
    l'injection d'une instance de production (Collector/Analyzer/Factory
    initialisés avec les vraies dépendances SSH) ; il est délibérément
    laissé en dehors de ce squelette pour ne pas coupler l'API à une
    configuration figée à l'import.
    """
    raise HTTPException(501, "À raccorder à NetworkEngine.handle() lors du déploiement")
