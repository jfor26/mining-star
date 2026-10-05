# Mining Star — Front-end en React

Interfaz web de Mining Star construida con **React 19** y **Vite**. No accede a
la base de datos: todo lo obtiene de la API REST de Django (`/api/v1/`), con
autenticación por tokens JWT.

| Pantalla | Ruta | Servicios que consume | Historia de usuario |
|---|---|---|---|
| Inicio de sesión | `/login` | `POST /auth/login/` | Control de acceso |
| Panel | `/` | `GET /resumen/`, `GET /productos/stock-bajo/` | Notificación por inventario bajo |
| Inventario | `/inventario` | `GET /productos/?search=` | HU-002 Consultar stock |
| Clientes | `/clientes` | `GET` y `POST /clientes/` | Registro de clientes |
| Ventas | `/ventas` | `POST /ventas/registrar/`, `POST /ventas/{id}/anular/` | HU-003 Crear pedido de venta |
| Producción | `/produccion` | `POST /produccion/`, `GET /produccion/stock-materia-prima/` | HU-001 Registrar producción diaria |

## Requisitos

- Node.js 20.19 o superior (probado con 22.21).
- El servidor Django en marcha en `http://127.0.0.1:8000`.

## Uso

```bash
cd frontend
npm install        # solo la primera vez
npm run dev        # abre http://localhost:5173
```

En desarrollo, Vite reenvía las peticiones `/api` al servidor Django
(`vite.config.js`), así que no hace falta configurar CORS.

## Calidad

```bash
npm run lint       # analizador estático oxlint
npm test           # 13 pruebas con Vitest y Testing Library
npm run build      # versión de producción en dist/
```

## Estructura

```
src/
├── api/cliente.js          Peticiones HTTP, token JWT y su renovación
├── context/SesionContext   Estado de la sesión compartido
├── components/             Diseño, RutaProtegida y componentes comunes
├── pages/                  Una página por pantalla
├── utils/                  Formato colombiano y validaciones
└── __tests__/              Pruebas automatizadas
```
