from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, RolUsuario
from app.config import settings
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"])

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    nombre: str
    email: str
    password: str
    telefono: str = None
    ci: str = None

def create_token(user_id: str, rol: str):
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user_id, "rol": rol, "exp": expire},
        settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email, User.activo == True).first()
    if not user or not pwd.verify(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_token(user.id, user.rol.value)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol": user.rol.value
        }
    }

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    user = User(
        nombre=req.nombre,
        email=req.email,
        password_hash=pwd.hash(req.password),
        telefono=req.telefono,
        ci=req.ci,
        rol=RolUsuario.pasajero
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id, user.rol.value)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "nombre": user.nombre, "email": user.email, "rol": user.rol.value}
    }