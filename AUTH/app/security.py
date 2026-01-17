import os, time
from passlib.context import CryptContext
from jose import jwt

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET = os.getenv("JWT_SECRET", "dev")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_EXPIRE_MIN = int(os.getenv("JWT_EXPIRE_MIN", "60"))

def hash_password(p: str) -> str:
    return pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return pwd.verify(p, h)

def create_token(email: str) -> str:
    exp = int(time.time()) + JWT_EXPIRE_MIN * 60
    return jwt.encode({"sub": email, "exp": exp}, JWT_SECRET, algorithm=JWT_ALG)
