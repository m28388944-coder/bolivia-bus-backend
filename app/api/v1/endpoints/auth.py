from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token
import uuid

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    existing_ci = db.query(User).filter(User.ci == data.ci).first()
    if existing_ci:
        raise HTTPException(status_code=400, detail="CI ya registrado")
    user = User(
        id=uuid.uuid4(),
        full_name=data.full_name,
        ci=data.ci,
        ci_extension=data.ci_extension,
        email=data.email,
        phone=data.phone,
        hashed_password=get_password_hash(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}

from fastapi import Header
from app.core.security import decode_token

@router.get("/me")
def get_me(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token requerido")
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token invalido")
    from uuid import UUID
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Acceso denegado - Solo administradores")
    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "email": user.email,
        "is_admin": user.is_admin
    }
