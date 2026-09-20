# Mining Star ERP

Sistema de gestión para operación minera: clientes, proveedores, productos,
empleados y ventas, con exportación de reportes a Excel y PDF.

Construido con **Django 6.0** y **SQLite**.

---

## Requisitos

- Python 3.12 o superior
- pip

## Instalación

```bash
# 1. Clonar o abrir la carpeta del proyecto
cd "Mining Star"

# 2. Crear el entorno virtual
python -m venv .venv

# 3. Activarlo
.venv\Scripts\activate        # Windows (PowerShell o CMD)
source .venv/bin/activate     # Linux / macOS / WSL

# 4. Instalar las dependencias
pip install -r requirements.txt        # solo ejecucion
pip install -r requirements-dev.txt    # ejecucion + herramientas de calidad (ruff)

# 5. Crear el archivo de configuración local
copy .env.example .env        # Windows
cp .env.example .env          # Linux / macOS

# 6. Generar una clave secreta y pegarla en .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 7. Aplicar las migraciones
python manage.py migrate

# 8. Crear el usuario administrador
python manage.py createsuperuser

# 9. Levantar el servidor
python manage.py runserver
```

La aplicación queda en <http://127.0.0.1:8000/>
y el panel de administración en <http://127.0.0.1:8000/admin/>

---

## Variables de entorno

Se definen en `.env`, que **no se sube a Git**. Ver `.env.example`.

| Variable | Para qué sirve |
|---|---|
| `DJANGO_SECRET_KEY` | Clave criptográfica de firmas y sesiones. Única por instalación. |
| `DJANGO_DEBUG` | `True` en desarrollo, `False` siempre en producción. |
| `DJANGO_ALLOWED_HOSTS` | Dominios autorizados, separados por coma. |

---

## Estructura

```
Mining Star/
├── config/                 Configuración del proyecto Django
│   ├── settings.py         Lee los secretos desde .env
│   └── urls.py
├── core/                   Aplicación principal
│   ├── models.py           Cliente, Proveedor, Producto, Empleado, Venta, DetalleVenta
│   ├── forms.py            Validación de todos los datos de entrada
│   ├── admin.py            Los 6 modelos registrados en /admin/
│   ├── exportadores.py     Generadores de Excel y PDF reutilizables
│   ├── tests.py            18 pruebas automatizadas
│   └── views/              Un módulo por dominio
│       ├── autenticacion.py
│       ├── panel.py
│       ├── clientes.py
│       ├── proveedores.py
│       ├── productos.py
│       ├── empleados.py
│       └── ventas.py
├── templates/
│   ├── base.html           Plantilla madre; las demás heredan de ella
│   └── _mensajes.html      Bloque de mensajes reutilizable
└── static/                 CSS, JavaScript e imágenes
```

---

## Comandos útiles

```bash
python manage.py test                  # Ejecutar las 18 pruebas
python manage.py check                 # Revisión de configuración
python manage.py check --deploy        # Revisión previa a producción
python manage.py makemigrations        # Generar migraciones tras cambiar modelos
python manage.py migrate               # Aplicarlas

ruff check .                           # Detectar problemas de estilo y errores
ruff format .                          # Formatear el código
```

---

## Antes de desplegar a producción

1. `DJANGO_DEBUG=False` en el `.env` del servidor.
2. `DJANGO_SECRET_KEY` **distinta** a la de desarrollo.
3. `DJANGO_ALLOWED_HOSTS` con el dominio real.
4. `python manage.py collectstatic`.
5. Cambiar SQLite por PostgreSQL si va a haber varios usuarios simultáneos.
6. Servir siempre por HTTPS.
