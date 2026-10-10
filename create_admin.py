#!/usr/bin/env python3
"""
Script utilitario de línea de comandos para crear o actualizar un usuario administrador en Green Circle.
Ideal para entornos de despliegue (Docker, Kubernetes, VPS, Render, Railway, etc.).

Uso:
  # Modo interactivo (solicita datos de forma segura, ocultando la contraseña):
  python create_admin.py

  # Modo no interactivo (ideal para scripts de inicialización o CI/CD):
  python create_admin.py --usuario superadmin --password "Secreta2026+" --nombre "Admin" --apellido "General"
"""

import sys
import getpass
import argparse
from pathlib import Path

# Asegurar que el paquete app esté en el sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database import SessionLocal
from app.models.usuario import Usuario
from app.security import hash_password

def crear_o_actualizar_admin(usuario: str, password: str, nombre: str, apellido: str):
    usuario_clean = usuario.strip().lower()
    if not usuario_clean:
        print("❌ Error: El nombre de usuario no puede estar vacío.")
        sys.exit(1)
    if not password:
        print("❌ Error: La contraseña no puede estar vacía.")
        sys.exit(1)

    with SessionLocal() as db:
        user_existente = db.query(Usuario).filter(Usuario.usuario == usuario_clean).first()
        if user_existente:
            print(f"ℹ️ El usuario '{usuario_clean}' ya existe. Actualizando contraseña y permisos a Administrador Activo...")
            user_existente.nombre = nombre.strip() if nombre else user_existente.nombre
            user_existente.apellido = apellido.strip() if apellido else user_existente.apellido
            user_existente.password_hash = hash_password(password)
            user_existente.admin = True
            user_existente.activo = True
            db.commit()
            print(f"✅ Administrador '{usuario_clean}' actualizado exitosamente.")
        else:
            nuevo_admin = Usuario(
                nombre=nombre.strip() or "Administrador",
                apellido=apellido.strip() or "Sistema",
                usuario=usuario_clean,
                password_hash=hash_password(password),
                admin=True,
                activo=True
            )
            db.add(nuevo_admin)
            db.commit()
            print(f"✅ Administrador '{usuario_clean}' creado exitosamente en la base de datos.")

def main():
    parser = argparse.ArgumentParser(description="Crear o actualizar usuario administrador en Green Circle.")
    parser.add_argument("--usuario", "-u", type=str, help="Nombre de usuario (ej. admin)")
    parser.add_argument("--password", "-p", type=str, help="Contraseña del administrador")
    parser.add_argument("--nombre", "-n", type=str, default="Admin", help="Nombre del administrador")
    parser.add_argument("--apellido", "-a", type=str, default="General", help="Apellido del administrador")

    args = parser.parse_args()

    # Si se pasan por argumentos, ejecutar directamente
    if args.usuario and args.password:
        crear_o_actualizar_admin(
            usuario=args.usuario,
            password=args.password,
            nombre=args.nombre,
            apellido=args.apellido
        )
        return

    # Si no, solicitar de forma interactiva
    print("🌿 Green Circle - Asistente de Creación de Administrador")
    print("-" * 55)
    usuario = input("Nombre de usuario [admin]: ").strip() or "admin"
    nombre = input("Nombre de pila [Admin]: ").strip() or "Admin"
    apellido = input("Apellido [General]: ").strip() or "General"
    
    password = getpass.getpass("Contraseña: ")
    password_confirm = getpass.getpass("Confirmar contraseña: ")

    if password != password_confirm:
        print("❌ Error: Las contraseñas no coinciden.")
        sys.exit(1)

    crear_o_actualizar_admin(
        usuario=usuario,
        password=password,
        nombre=nombre,
        apellido=apellido
    )

if __name__ == "__main__":
    main()
