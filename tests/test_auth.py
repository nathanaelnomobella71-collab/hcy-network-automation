"""Tests unitaires de la logique JWT pure (3.9.1).

Ajoutés au-delà du plan de tests initial : ils couvrent partiellement l'écart
identifié au Chapitre 4 (4.4.2, OS3) entre la conception du contrôle d'accès
et sa validation empirique — en testant réellement l'émission et le décodage
des jetons, indépendamment du serveur FastAPI.
"""
import jwt
import pytest

from api.auth import create_access_token, decode_access_token, hash_password, verify_password

SECRET = "test-secret-not-for-production"


def test_create_and_decode_round_trip_preserves_claims():
    token = create_access_token({"sub": "admin", "role": "admin"}, secret_key=SECRET)

    payload = decode_access_token(token, secret_key=SECRET)

    assert payload["sub"] == "admin"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_decode_rejects_token_signed_with_a_different_secret():
    token = create_access_token({"sub": "admin", "role": "admin"}, secret_key=SECRET)

    with pytest.raises(jwt.PyJWTError):
        decode_access_token(token, secret_key="a-completely-different-secret")


def test_decode_rejects_expired_token():
    expired_token = jwt.encode(
        {"sub": "admin", "role": "admin", "exp": -1},
        SECRET,
        algorithm="HS256",
    )

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(expired_token, secret_key=SECRET)


def test_decode_rejects_malformed_token():
    with pytest.raises(jwt.PyJWTError):
        decode_access_token("not.a.valid.jwt", secret_key=SECRET)


def test_hash_password_round_trip_verifies_correctly():
    hashed = hash_password("admin123")

    assert verify_password("admin123", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("admin123")

    assert verify_password("wrong-password", hashed) is False


def test_hash_password_never_stores_the_plain_password():
    """Le hash ne doit jamais contenir le mot de passe en clair."""
    hashed = hash_password("admin123")

    assert "admin123" not in hashed
