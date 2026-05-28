"""
Script para crear el usuario administrador inicial.
Ejecutar dentro del contenedor:
  docker compose exec app python create_admin.py
"""
import sys
import os
sys.path.insert(0, "/app")

from app.core.database import SessionLocal, engine
from app.core.database import Base
from app.models.user import User
from app.models.trip import Trip
from app.core.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

username = os.getenv("ADMIN_USERNAME", "admin")
email = os.getenv("ADMIN_EMAIL", "admin@lovingapp.com")
password = os.getenv("ADMIN_PASSWORD", "admin123")

existing = db.query(User).filter(User.username == username).first()
if existing:
    print(f"El usuario '{username}' ya existe.")
else:
    admin = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name="Administrador",
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    print(f"Admin creado: {username} / {password}")

db.close()
