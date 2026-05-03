import sys
sys.path.insert(0, ".")
from app.database import SessionLocal
from app.models.user import User, RolUsuario
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"])
db = SessionLocal()

existing = db.query(User).filter(User.email == "dev@boliviabus.bo").first()
if existing:
    print("Ya existe el usuario developer")
else:
    dev = User(
        nombre="Desarrollador Principal",
        email="dev@boliviabus.bo",
        password_hash=pwd.hash("dev1234"),
        rol=RolUsuario.developer,
        activo=True
    )
    db.add(dev)
    db.commit()
    print("✅ Usuario developer creado")
    print("   Email: dev@boliviabus.bo")
    print("   Password: dev1234")
    print("   Rol: developer")

db.close()
