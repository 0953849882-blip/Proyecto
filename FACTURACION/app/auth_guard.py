import os
from fastapi import Header, HTTPException
from jose import jwt, JWTError

JWT_SECRET = os.getenv("JWT_SECRET", "dev")
JWT_ALG = os.getenv("JWT_ALG", "HS256")

def require_user(authorization: str = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Falta token Bearer")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload["sub"]  # email
    except JWTError:
        raise HTTPException(401, "Token inválido o expirado")
