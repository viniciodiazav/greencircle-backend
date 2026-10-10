# 🌿 Green Circle API (FastAPI Backend)

Backend RESTful para la plataforma **Green Circle App**, desarrollado con **Python 3.13+**, **FastAPI**, **SQLAlchemy ORM**, **Pydantic v2**, **JWT (JSON Web Tokens)** y conectado a base de datos **PostgreSQL**.

---

## 🔐 1. Seguridad, Autenticación y Control de Roles

La API implementa una política de **seguridad estricta**:
* **TODOS los endpoints administrativos requieren autenticación** mediante Bearer Token JWT en el encabezado `Authorization: Bearer <token>`.
* **ÚNICAMENTE existen 2 endpoints públicos** diseñados para clientes no autenticados en la aplicación móvil.

### 🌐 Endpoints Públicos (Los ÚNICOS 2 sin autenticación)
1. **`GET /api/publico/materiales`**  
   Devuelve **únicamente** el nombre y el precio de compra de los materiales activos (con formato numérico limpio):
   ```json
   [
     {
       "nombre": "Cartón Corrugado",
       "precio": "2.50"
     }
   ]
   ```
2. **`GET /api/publico/sucursales`**  
   Devuelve **únicamente** el nombre de la sucursal y su enlace de ubicación:
   ```json
   [
     {
       "nombre": "Sucursal Matriz Centro",
       "url": "https://maps.google.com/..."
     }
   ]
   ```

### 🛠️ Endpoints Administrativos (Requieren Bearer Token)
* **Usuarios (`/api/usuarios`):** Consultar, registrar nuevos usuarios y activar/desactivar cuentas (*Sin eliminación física*).
* **Materiales (`/api/materiales`):** Catálogo completo con códigos algorítmicos inmutables, alta (`POST`) y activación/desactivación (`PATCH`).
* **Precios (`/api/precios`):** Consulta de precios compra/venta, asignación y actualización (`POST`, `PATCH`).
* **Históricos (`/api/historicos-compra`, `/api/historicos-venta`):** Auditoría contable inmutable con soporte de parámetro de consulta `?limit=N` (*Solo lectura*).
* **Sucursales (`/api/sucursales`):** Gestión completa de centros de acopio (*Única entidad eliminable con DELETE*).

---

## 👤 2. Creación del Administrador Inicial

Existen **dos mecanismos** para gestionar el primer usuario administrador en producción o despliegue:

### Método A: Automático vía Variables de Entorno (Recomendado para Deploy)
Al iniciar la aplicación, el ciclo de vida de FastAPI verifica si existe algún administrador en la base de datos. Si no existe ninguno, lo crea automáticamente con los datos definidos en `.env`:

```env
FIRST_ADMIN_NOMBRE=Vinicio
FIRST_ADMIN_APELLIDO=Díaz
FIRST_ADMIN_USUARIO=admin
FIRST_ADMIN_PASSWORD=admin@admin
```

### Método B: Script CLI interactivo o desatendido (`create_admin.py`)
En el servidor o contenedor Docker, se puede invocar en cualquier momento el script:

```bash
# Modo interactivo (solicita datos y oculta la contraseña):
PYTHONPATH=backend backend/venv/bin/python backend/create_admin.py

# Modo directo por argumentos (para scripts de CI/CD):
PYTHONPATH=backend backend/venv/bin/python backend/create_admin.py --usuario admin --password admin --nombre "Administrador" --apellido "Sistema"
```
*(Si el usuario ya existía previamente, el script actualiza su hash bcrypt a la nueva contraseña y asegura sus privilegios de administrador activo).*

---

## ⚙️ 3. Variables de Entorno (`backend/.env`)

| Variable | Tipo | Valor Predeterminado | Descripción |
|---|---|---|---|
| `PORT` | Entero | `8000` | Puerto TCP de FastAPI. |
| `HOST` | String | `0.0.0.0` | Dirección IP de escucha. |
| `DEBUG` | Booleano | `True` | Habilita logs SQL y recarga automática. |
| `DB_USER` | String | `greencircle` | Usuario de PostgreSQL. |
| `DB_PASSWORD` | String | `greencircle` | Contraseña de PostgreSQL. |
| `DB_HOST` | String | `localhost` | Host de la base de datos. |
| `DB_PORT` | Entero | `5432` | Puerto estándar de PostgreSQL. |
| `DB_NAME` | String | `greencircle` | Nombre de la base de datos. |
| `JWT_SECRET_KEY` | String | `greencircle-super-secret-jwt-key-2026-production` | Llave secreta para firmar tokens. |
| `JWT_ALGORITHM` | String | `HS256` | Algoritmo de firma criptográfica. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Entero | `1440` | Tiempo de vida del token (24 horas). |
| `FIRST_ADMIN_USUARIO` | String | `admin` | Usuario administrador inicial. |
| `FIRST_ADMIN_PASSWORD` | String | `admin` | Contraseña del administrador inicial. |

---

## 🚀 4. ¿Cómo levantar el servidor Backend?

Desde la raíz del proyecto `GreenCircleApp/`:

```bash
PYTHONPATH=backend backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

* **Swagger UI interactivo:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Verificación de Salud:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 📡 5. Catálogo Completo de Endpoints

### 🌐 Endpoints Públicos (Libres de autenticación)
* `GET /api/publico/materiales`: Devuelve `[ { "nombre": "...", "precio": "..." } ]` de materiales activos.
* `GET /api/publico/sucursales`: Devuelve `[ { "nombre": "...", "url": "..." } ]` de las sucursales.

### 🔑 Autenticación (`/api/auth`)
* `POST /api/auth/login`: Formulario OAuth2 compatible con Swagger UI (`username`, `password`).
* `POST /api/auth/login-json`: JSON Body estándar para clientes frontend (`{ "usuario": "admin", "password": "..." }`).
* `GET /api/auth/me`: Retorna los datos del usuario autenticado con su token actual.

### 📦 Materiales (`/api/materiales`) - *Requiere Token*
* `GET /api/materiales`: Catálogo completo con códigos autogenerados y estado `activo`.
* `GET /api/materiales/{codigo}`: Detalle completo de un material.
* `POST /api/materiales`: Registra un nuevo material. Si no se provee código, el backend/DB lo genera algorítmicamente (`[PREF]-[DDMMYY]-[DIGITO]`). Nace en estado inactivo.
* `PATCH /api/materiales/{codigo}/activo`: Modifica el estado activo/inactivo (validado por trigger en BD).

### 💰 Precios Vigentes (`/api/precios`) - *Requiere Token*
* `GET /api/precios`: Lista de todos los precios de compra y venta actuales.
* `GET /api/precios/{codigo}`: Precios vigentes de un material en específico.
* `POST /api/precios`: Asigna los precios iniciales de un material.
* `PATCH /api/precios/{codigo}`: Actualiza precios de compra o venta. Desencadena trigger SCD Tipo 2 en BD.

### 📈 Históricos Contables (`/api/historicos-compra`, `/api/historicos-venta`) - *Requiere Token*
* `GET /api/historicos-compra?limit=10`: Consulta cronológica del histórico de compras. Parámetro `limit` configurable (ej: `10`, `50`, `100`, `500`).
* `GET /api/historicos-venta?limit=10`: Consulta cronológica del histórico de ventas con parámetro `limit`.

### 🏢 Sucursales (`/api/sucursales`) - *Requiere Token*
* `GET /api/sucursales`: Lista completa de centros de acopio con IDs.
* `POST /api/sucursales`: Crea un nuevo centro de acopio (`nombre`, `url`).
* `PATCH /api/sucursales/{id}`: Actualiza nombre o URL de una sucursal.
* `DELETE /api/sucursales/{id}`: Elimina definitivamente una sucursal.
