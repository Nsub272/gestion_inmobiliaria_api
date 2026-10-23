# Gestión Inmobiliaria - API REST con Django REST Framework

API REST para administrar una inmobiliaria: propiedades, propietarios, clientes, agentes y contratos de arriendo o venta. Cada recurso ofrece **CRUD completo** (GET, POST, PUT, PATCH y DELETE).

Proyecto de la **Evaluación N.° 2 - Programación Backend** (modalidad individual).

| | |
|---|---|
| **Estudiante** | Erik Jara |
| **Docente** | Erick Bailey Rebolledo |
| **Sistema operativo de desarrollo** | EndeavourOS (Linux, basado en Arch) |
| **Base de datos** | MariaDB |

---

## 1. Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3.12+ | Lenguaje |
| Django | Framework web |
| Django REST Framework | Serializadores, ViewSets y Router |
| MariaDB + mysqlclient | Base de datos y driver de conexión |
| python-decouple | Lectura de variables de entorno desde `.env` |

---

## 2. Estructura del proyecto

```
.
├── manage.py
├── requirements.txt
├── sql.sql                        # Script SQL: base de datos, usuario y permisos
├── .env                           # Variables de entorno (SECRET_KEY y conexión)
├── README.md
├── motor_django/                  # Configuración del proyecto
│   ├── settings.py
│   └── urls.py                    # Rutas raíz: admin e include de la API
└── gestion_inmobiliaria_app/      # Aplicación principal
    ├── models.py                  # Modelo de datos (8 modelos)
    ├── serializers.py             # Serializadores y validaciones
    ├── views.py                   # ModelViewSet por recurso
    ├── urls.py                    # Rutas mediante DefaultRouter
    ├── admin.py
    └── migrations/                # Migraciones de la base de datos
```

---

## 3. Requisitos previos (EndeavourOS / Arch Linux)

```bash
sudo pacman -Syu
sudo pacman -S python python-pip git base-devel pkgconf mariadb mariadb-libs
```

`mariadb-libs`, `base-devel` y `pkgconf` son necesarios para compilar `mysqlclient`.

---

## 4. Instalación

```bash
git clone https://github.com/Nsub272/gestion_inmobiliaria_api.git
cd gestion_inmobiliaria_api

python -m venv venv
source venv/bin/activate          # en fish: source venv/bin/activate.fish
python -m pip install --upgrade pip
pip install -r requirements.txt
```


---

## 5. Configuración de MariaDB

Inicializar el servidor (solo la primera vez) y levantar el servicio:

```bash
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
sudo systemctl enable --now mariadb
```

Ejecutar el script que crea la base de datos, el usuario y asigna los permisos:

```bash
sudo mariadb < sql.sql
```

El script `sql.sql` contiene:

```sql
CREATE DATABASE IF NOT EXISTS gestion_inmobiliaria_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

CREATE USER IF NOT EXISTS 'inmo_user'@'localhost' IDENTIFIED BY '<contraseña del archivo sql.sql>';

GRANT ALL PRIVILEGES ON gestion_inmobiliaria_db.* TO 'inmo_user'@'localhost';

GRANT ALL PRIVILEGES ON `test\_gestion\_inmobiliaria\_db`.* TO 'inmo_user'@'localhost';

FLUSH PRIVILEGES;
```

Comprobar que el usuario funciona:

```bash
mariadb -u inmo_user -p -e "SHOW DATABASES;"
```

Debe aparecer `gestion_inmobiliaria_db`.

---

## 6. Variables de entorno

Las credenciales y la `SECRET_KEY` **no están escritas en `settings.py`**: se leen desde el archivo `.env`, ubicado junto a `manage.py`.

```env
SECRET_KEY='clave_secreta_de_django'
DEBUG=False

DB_NAME=gestion_inmobiliaria_db
DB_USER=inmo_user
DB_PASSWORD=<misma contraseña de sql.sql>
DB_HOST=localhost
DB_PORT=3306
```

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `False` por defecto: oculta datos internos y muestra las páginas de error propias. `True` solo para depurar |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | Datos de conexión creados con `sql.sql` |
| `DB_HOST`, `DB_PORT` | Servidor y puerto de MariaDB |

Las credenciales de este repositorio son solo de desarrollo. Para generar una `SECRET_KEY` nueva:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 7. Migraciones y ejecución

```bash
python manage.py migrate
python manage.py createsuperuser    # opcional, para el panel /admin/
python manage.py runserver --insecure
```

`--insecure` permite que `runserver` sirva los archivos estáticos (panel `/admin/` e interfaz navegable de la API) cuando `DEBUG=False`. Es solo para uso local.

Las migraciones del modelo ya están incluidas en `gestion_inmobiliaria_app/migrations/`. Si se modifica `models.py`:

```bash
python manage.py makemigrations
python manage.py migrate
```

| Sección | URL |
|---|---|
| API (raíz del router) | `http://127.0.0.1:8000/gestion_inmobiliaria_app/` |
| Panel de administración | `http://127.0.0.1:8000/admin/` |

---

## 8. Manejo de errores

Todas las operaciones se realizan mediante los endpoints generados por los `ModelViewSet`; el proyecto no incluye interfaces HTML propias. Las respuestas de error son JSON:

| Código | Situación |
|---|---|
| `400` | Datos inválidos o duplicados (RUT incorrecto, precio negativo, fechas incoherentes) |
| `404` | El registro solicitado no existe |
| `409` | No se puede eliminar un registro con datos asociados (`PROTECT`) |

El proyecto se entrega con `DEBUG=False` para no exponer información interna del servidor.

---

## 9. Arquitectura de la API

| Componente | Archivo | Función |
|---|---|---|
| Modelos | `models.py` | Clases que el ORM mapea a tablas de MariaDB |
| Serializadores | `serializers.py` | `ModelSerializer`: convierten modelos a JSON y validan los datos |
| ViewSets | `views.py` | `ModelViewSet`: implementan el CRUD completo de cada modelo |
| Rutas | `urls.py` | `DefaultRouter`: genera los endpoints de cada ViewSet |
| Rutas raíz | `motor_django/urls.py` | Admin e `include()` de la API |

---

## 10. Modelo de datos

```
Region 1 ── N Comuna 1 ── N Propiedad N ── 1 TipoPropiedad
                               │        N ── 1 Propietario
                               1
                               N
Cliente 1 ── N Contrato N ── 1 Agente
```

| Modelo | Descripción |
|---|---|
| `Region`, `Comuna`, `TipoPropiedad` | Catálogos de ubicación y tipos de propiedad |
| `Propietario`, `Cliente`, `Agente` | Personas (nombre, apellido, RUT único, correo, teléfono) |
| `Propiedad` | Inmueble con dirección, superficie, dormitorios, baños, precio, moneda (CLP/UF) y estado |
| `Contrato` | Arriendo o venta que une una propiedad, un cliente y un agente |

Todos los modelos incluyen `habilitado`, `created_at` y `updated_at`. Las claves foráneas usan `on_delete=PROTECT`.

---

## 11. Endpoints

Todos los recursos cuelgan de `/gestion_inmobiliaria_app/`:

| Recurso | Ruta base |
|---|---|
| Regiones | `/gestion_inmobiliaria_app/regiones/` |
| Comunas | `/gestion_inmobiliaria_app/comunas/` |
| Tipos de propiedad | `/gestion_inmobiliaria_app/tipos-propiedad/` |
| Propietarios | `/gestion_inmobiliaria_app/propietarios/` |
| Clientes | `/gestion_inmobiliaria_app/clientes/` |
| Agentes | `/gestion_inmobiliaria_app/agentes/` |
| Propiedades | `/gestion_inmobiliaria_app/propiedades/` |
| Contratos | `/gestion_inmobiliaria_app/contratos/` |

Cada recurso admite:

| Método | Ruta | Acción |
|---|---|---|
| `GET` | `<ruta base>/` | Listar |
| `POST` | `<ruta base>/` | Crear |
| `GET` | `<ruta base>/{id}/` | Obtener uno |
| `PUT` | `<ruta base>/{id}/` | Actualizar completo |
| `PATCH` | `<ruta base>/{id}/` | Actualizar parcialmente |
| `DELETE` | `<ruta base>/{id}/` | Eliminar |

Además, todas las listas aceptan `?search=texto` y `?ordering=campo`.

### Ejemplos con curl

```bash
curl -X POST http://127.0.0.1:8000/gestion_inmobiliaria_app/regiones/ \
  -H "Content-Type: application/json" \
  -d '{"codigo": "08", "nombre": "Biobío"}'

curl -X PATCH http://127.0.0.1:8000/gestion_inmobiliaria_app/regiones/1/ \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Región del Biobío"}'

curl -X DELETE http://127.0.0.1:8000/gestion_inmobiliaria_app/regiones/1/
```

### Validaciones y códigos de respuesta

- El **RUT** debe tener formato `12345678-5` (sin puntos) y dígito verificador válido (módulo 11).
- Precio, superficie y monto deben ser mayores a cero.
- Un contrato de arriendo requiere fecha de término, y esta no puede ser anterior al inicio.
- Las fechas se envían como `dd-mm-aaaa` (por ejemplo `01-03-2026`); también se acepta el formato ISO.
- Crear un registro duplicado o con datos inválidos responde **400**.
- Eliminar un registro con registros asociados responde **409** (no se pierde información por cascada).

> Orden sugerido para crear datos: región, comuna, tipo de propiedad, propietario, propiedad. Para un contrato se necesitan además un cliente y un agente.

---

## 12. Solución de problemas

| Problema | Solución |
|---|---|
| Error al instalar `mysqlclient` | `sudo pacman -S base-devel pkgconf mariadb-libs` |
| `externally-managed-environment` | Activar el entorno virtual antes de usar `pip` |
| `Can't connect to local MySQL server` | `sudo systemctl start mariadb` |
| `Access denied for user` | La contraseña del `.env` no coincide con la de MariaDB |
| `UndefinedValueError: SECRET_KEY` | El `.env` no está junto a `manage.py` |
| `Table doesn't exist` | Ejecutar `python manage.py migrate` |

Para actualizar las dependencias tras instalar una librería nueva: `pip freeze > requirements.txt`.

---

## Autor

Erik Jara - Evaluación N.° 2, Programación Backend.