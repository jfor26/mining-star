/**
 * Marco comun de las pantallas autenticadas: menu lateral, barra superior
 * y el area donde React Router pinta la pagina activa (<Outlet />).
 */
import { NavLink, Outlet } from 'react-router-dom'

import { useSesion } from '../context/SesionContext.jsx'

const MENU = [
  { ruta: '/', texto: 'Panel', icono: '▦' },
  { ruta: '/inventario', texto: 'Inventario', icono: '▤' },
  { ruta: '/clientes', texto: 'Clientes', icono: '☺' },
  { ruta: '/ventas', texto: 'Ventas', icono: '$' },
  { ruta: '/produccion', texto: 'Producción', icono: '⛏' },
]

export default function Diseno() {
  const { usuario, cerrarSesion } = useSesion()

  return (
    <div className="marco">
      <aside className="menu-lateral">
        <div className="marca">
          <img src="/logo.png" alt="" width="64" height="64" />
          <strong>Mining Star ERP</strong>
          <small>Ortega Espinosa y Cía. S.A.S.</small>
        </div>
        <nav aria-label="Menú principal">
          {MENU.map((opcion) => (
            <NavLink
              key={opcion.ruta}
              to={opcion.ruta}
              end={opcion.ruta === '/'}
              className={({ isActive }) => (isActive ? 'activo' : undefined)}
            >
              <span aria-hidden="true" className="icono">{opcion.icono}</span>
              {opcion.texto}
            </NavLink>
          ))}
        </nav>
        <button type="button" className="boton-salir" onClick={cerrarSesion}>
          Cerrar sesión
        </button>
      </aside>

      <div className="area">
        <header className="barra-superior">
          <span>Sistema Integral de Gestión Minera</span>
          <span className="usuario-actual">
            {usuario?.first_name || usuario?.username}
          </span>
        </header>
        <main className="contenido">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
