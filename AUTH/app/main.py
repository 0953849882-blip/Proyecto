import time, random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

from fastapi.middleware.cors import CORSMiddleware  

from .db import init_db, get_conn
from .security import hash_password, verify_password, create_token

OTP_TTL_SECONDS = 4 * 60  

app = FastAPI(title="Auth OTP (4 min) + JWT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],
)

init_db()

def seed_demo_user():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users(email,password_hash) VALUES(?,?)",
            ("luis@test.com", hash_password("123456"))
        )
        conn.commit()
        print(" Usuario demo creado: luis@test.com / 123456")
    except Exception:
        print("ℹ Usuario demo ya existe: luis@test.com")
    finally:
        conn.close()

seed_demo_user()


class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class OtpRequestIn(BaseModel):
    email: EmailStr

class OtpVerifyIn(BaseModel):
    email: EmailStr
    code: str

def cleanup_expired_otps(conn):
    now = int(time.time())
    cur = conn.cursor()
    cur.execute("DELETE FROM otp_codes WHERE expires_at < ?", (now,))
    conn.commit()

@app.get("/health")
def health():
    return {"status": "ok", "service": "auth"}

@app.post("/auth/register")
def register(data: RegisterIn):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users(email,password_hash) VALUES(?,?)",
            (data.email, hash_password(data.password))
        )
        conn.commit()
        return {"message": "Usuario creado"}
    except Exception:
        raise HTTPException(400, "Email ya registrado")
    finally:
        conn.close()

@app.post("/auth/login")
def login(data: LoginIn):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT password_hash FROM users WHERE email=?", (data.email,))
    row = cur.fetchone()
    conn.close()

    if not row or not verify_password(data.password, row[0]):
        raise HTTPException(401, "Credenciales incorrectas")

    return {"message": "Credenciales OK. Solicita código OTP con /auth/request-otp"}

@app.post("/auth/request-otp")
def request_otp(data: OtpRequestIn):
    conn = get_conn()
    cleanup_expired_otps(conn)

    code = str(random.randint(100000, 999999))
    expires_at = int(time.time()) + OTP_TTL_SECONDS

    cur = conn.cursor()
    cur.execute("DELETE FROM otp_codes WHERE email=?", (data.email,))
    cur.execute(
        "INSERT INTO otp_codes(email, code, expires_at) VALUES (?,?,?)",
        (data.email, code, expires_at)
    )
    conn.commit()
    conn.close()

    return {
        "message": "OTP generado (válido 4 minutos)",
        "demo_code": code,
        "expires_in_seconds": OTP_TTL_SECONDS
    }

@app.post("/auth/verify-otp")
def verify_otp(data: OtpVerifyIn):
    conn = get_conn()
    cleanup_expired_otps(conn)

    cur = conn.cursor()
    cur.execute("SELECT id, code, expires_at FROM otp_codes WHERE email=?", (data.email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(400, "No hay OTP activo (o ya expiró)")

    otp_id, saved_code, exp = row
    now = int(time.time())

    if now > exp:
        cur.execute("DELETE FROM otp_codes WHERE id=?", (otp_id,))
        conn.commit()
        conn.close()
        raise HTTPException(400, "OTP expirado")

    if data.code != saved_code:
        conn.close()
        raise HTTPException(400, "OTP incorrecto")

    cur.execute("DELETE FROM otp_codes WHERE id=?", (otp_id,))
    conn.commit()
    conn.close()

    token = create_token(data.email)
    return {"token": token, "type": "bearer"}
