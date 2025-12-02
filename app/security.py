from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from app.config import settings


# Hashing Configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Nimmt ein Klartext-Passwort und gibt den Hash zurück."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vergleicht ein Klartext-Passwort mit einem Hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Erstellt einen JWT-Token mit einer Ablaufszeit
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Standardablaufzeit: 60 Minuten
        expire = datetime.utcnow() + timedelta(minutes=60)
    # 'exp' ist ein reserviertes Feld im JWT für das Ablaufdatum
    to_encode.update({"exp": expire})
    encoded_jwt = (jwt.encode
                   (to_encode,
                    settings.jwt_secret_key,
                    algorithm=settings.jwt_algorithm
    ))
    return encoded_jwt