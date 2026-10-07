## MVP: seguridad por cargo, dashboard, CRM, tienda con Stripe y gestión minera

### Qué cambia
- **Seguridad**: matriz de acceso cargo × módulo aplicada a la API, a las vistas web y al menú; registro de usuarios restringido al Administrador; token JWT por ingreso con bitácora (jti, IP, navegador); bloqueo por intentos fallidos; rotación y lista negra de tokens; cierre de sesión en el servidor.
- **Base de datos**: modelos de CRM, pedidos, normativa, mejora continua y bitácora de accesos; empleado vinculado a su usuario; índices y restricciones nuevas; grupos por cargo creados por migración.
- **Tienda**: catálogo/brochure imprimible, carrito, pedidos y pago con Stripe Checkout (o modo simulado sin llaves), webhook con verificación de firma, confirmación idempotente.
- **Dashboard** con gráficas (Recharts) filtradas por cargo.
- **Gestión**: repositorio normativo minero y ambiental con alertas, mejora continua PHVA, página de empresa (misión, visión, valores, cultura, organigrama, Porter, valor agregado, diferencial, stakeholders, Canvas, EDT).
- **Respaldo**: comandos `respaldar_bd`, `restaurar_bd` y botón en Seguridad; `cargar_demo` con un usuario por cargo.
- **Interfaz**: paleta tomada del logo, botones con variantes y estados, banner del login sin marcas de terceros, logo del SENA.
- **Documentación** en `docs/` y guía de presentación.

### Cómo probar
```bash
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py test core            # 112 pruebas
cd frontend && npm install && npm test   # 16 pruebas
```

### Notas para quien revisa
- Los usuarios existentes que no son superusuarios quedan **sin cargo** y sin acceso hasta que el Administrador les asigne uno (Seguridad → Usuarios y cargos).
- `POST /auth/registro/` ya no es público y ya no devuelve tokens.
- Nueva dependencia: `stripe==16.0.0` (backend) y `recharts` (frontend).
