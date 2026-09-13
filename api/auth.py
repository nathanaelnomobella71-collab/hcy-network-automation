"""Authentification JWT (RF-07, RNF-03, Extrait 3.5).

La logique pure de création/décodage de jeton (``create_access_token`` /
``decode_access_token``) est isolée des décorateurs FastAPI : elle ne dépend
que de PyJWT et peut donc être testée unitairement sans lancer de serveur
HTTP (cf. tests/test_auth.py). Les dépendances FastAPI (``get_current_user``,
``require_role``) restent de simples adaptateurs autour de cette logique.

Le hachage des mots de passe utilise directement le paquet ``bcrypt``
plutôt que ``passlib`` : les versions récentes de bcrypt (>=4.1) ont retiré
l'attribut interne ``__about__`` sur lequel passlib s'appuyait pour détecter
sa version, ce qui casse ``CryptContext`` (erreur ``AttributeError: module
'bcrypt' has no attribute '__about__'`` observée en pratique). Appeler
bcrypt directement supprime cette dépendance fragile plutôt que de figer
une version précise et de reporter le problème.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Jamais en dur dans le code — chargé depuis .env (cf. 3.7). La chaîne vide
# par défaut est délibérée : elle fait échouer explicitement toute émission
# de jeton en l'absence de configuration, plutôt que d'utiliser une valeur
# de secours non sécurisée.
SECRET_KEY = os.environ.get("HCY_JWT_SECRET", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# --- Logique pure (testable sans FastAPI, cf. tests/test_auth.py) ----------

def create_access_token(data: dict, secret_key: str = SECRET_KEY) -> str:
    to_encode = data.copy()
    to_encode["exp"] = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str, secret_key: str = SECRET_KEY) -> dict:
    """Décode et valide un jeton JWT. Lève ``jwt.PyJWTError`` si invalide/expiré."""
    return jwt.decode(token, secret_key, algorithms=[ALGORITHM])


def hash_password(password: str) -> str:
    """Hache un mot de passe avec bcrypt (sel aléatoire intégré au résultat)."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# --- Adaptateurs FastAPI -----------------------------------------------

def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Décode le jeton JWT porté par la requête ; lève 401 si invalide (Extrait 3.5)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Jeton invalide ou expiré",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        if payload.get("sub") is None:
            raise credentials_exception
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc
    return payload


def require_role(*allowed_roles: str):
    """Dépendance FastAPI imposant un rôle (RBAC, cf. Chapitre 2, 2.10)."""

    def _checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in allowed_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Rôle insuffisant")
        return user

    return _checker
