with open('app/api/v1/endpoints/auth.py', 'r', encoding='utf-8') as f:
    content = f.read()

extra = '''
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
    user = db.query(User).filter(User.id == payload.get("sub")).first()
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
'''

with open('app/api/v1/endpoints/auth.py', 'w', encoding='utf-8') as f:
    f.write(content + extra)
print('OK: auth.py actualizado')