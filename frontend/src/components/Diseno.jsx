/**
 * Marco comun de las pantallas autenticadas: menu lateral, barra superior
 * y el area donde React Router pinta la pagina activa (<Outlet />).
 *
 * El menu se arma con la matriz de permisos del cargo: cada empleado solo
 * ve los modulos a los que tiene acceso (accesibilidad por cargo).
 */
import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet } from 'react-router-dom'

import { sesion } from '../api/cliente.js'
import { BotonVolver, SelectorTema } from './Barra.jsx'
import { useCarrito } from '../context/CarritoContext.jsx'
import { useSesion } from '../context/SesionContext.jsx'

const SECCIONES = [
  {
    titulo: 'General',
    opciones: [
      { ruta: '/', texto: 'Dashboard', icono: '▦', modulo: 'panel' },
      { ruta: '/empresa', texto: 'La empresa', icono: '★', modulo: null },
    ],
  },
  {
    titulo: 'Operación',
    opciones: [
      { ruta: '/produccion', texto: 'Producción', icono: '⛏', modulo: 'produccion' },
      { ruta: '/inventario', texto: 'Inventario', icono: '▤', modulo: 'productos' },
    ],
  },
  {
    titulo: 'Comercial',
    opciones: [
      { ruta: '/tienda', texto: 'Tienda y brochure', icono: '🛒', modulo: 'pedidos' },
      { ruta: '/ventas', texto: 'Ventas', icono: '$', modulo: 'ventas' },
      { ruta: '/clientes', texto: 'Clientes', icono: '☺', modulo: 'clientes' },
      { ruta: '/crm', texto: 'CRM', icono: '◎', modulo: 'crm' },
    ],
  },
  {
    titulo: 'Gestión',
    opciones: [
      { ruta: '/empleados', texto: 'Empleados y cargos', icono: '👷', modulo: 'empleados' },
      { ruta: '/normativa', texto: 'Normativa minera y ambiental', icono: '§', modulo: 'normativa' },
      { ruta: '/mejora', texto: 'Mejora continua', icono: '↻', modulo: 'mejora' },
      { ruta: '/seguridad', texto: 'Seguridad y accesos', icono: '🔒', modulo: 'seguridad' },
    ],
  },
]

function horaCorta(fecha) {
  return fecha ? fecha.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' }) : '—'
}

/** Muestra hasta cuando es valido el token de acceso de esta sesion. */
function EstadoToken() {
  const [vence, setVence] = useState(() => sesion.venceElToken())
  useEffect(() => {
    const reloj = setInterval(() => setVence(sesion.venceElToken()), 30_000)
    return () => clearInterval(reloj)
  }, [])
  return (
    <span className="estado-token" title="El token JWT se renueva solo mientras la sesión siga activa">
      <span className="punto-verde" aria-hidden="true" /> Token activo · vence {horaCorta(vence)}
    </span>
  )
}

export default function Diseno() {
  const { usuario, cerrarSesion, puede } = useSesion()
  const { unidades } = useCarrito()
  const [menuAbierto, setMenuAbierto] = useState(false)

  return (
    <div className="marco">
      <aside className={`menu-lateral${menuAbierto ? ' abierto' : ''}`}>
        <div className="marca">
          <img src="/logo.png" alt="" width="132" height="88" />
          <strong>Mining Star ERP</strong>
          <small>Mining Star Services and Products</small>
          <small className="razon-social">Ortega Espinosa y Cía. S.A.S.</small>
        </div>
        <nav aria-label="Menú principal" onClick={() => setMenuAbierto(false)}>
          {SECCIONES.map((seccion) => {
            const visibles = seccion.opciones.filter((o) => !o.modulo || puede(o.modulo))
            if (visibles.length === 0) return null
            return (
              <div key={seccion.titulo} className="grupo-menu">
                <span className="titulo-grupo">{seccion.titulo}</span>
                {visibles.map((opcion) => (
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
              </div>
            )
          })}
        </nav>
        <div className="pie-menu">
          <img src="/logo-sena.svg" alt="Logo del SENA" width="38" height="38" />
          <small>Proyecto formativo SENA<br />Tecnólogo ADSO · Ficha 3235867</small>
        </div>
      </aside>

      <div className="area">
        <header className="barra-superior">
          <button type="button" className="boton icono-solo solo-movil" aria-label="Abrir menú"
            onClick={() => setMenuAbierto((v) => !v)}>☰</button>
          <BotonVolver />
          <EstadoToken />
          <div className="barra-derecha">
            <SelectorTema />
            {puede('pedidos', 'crear') && (
              <Link to="/tienda/carrito" className="boton fantasma carrito-boton" aria-label={`Carrito: ${unidades} unidades`}>
                🛒 <span className="contador">{unidades}</span>
              </Link>
            )}
            <span className="usuario-actual">
              <strong>{usuario?.first_name || usuario?.username}</strong>
              <span className="insignia-rol">{usuario?.rol ?? 'Sin cargo'}</span>
            </span>
            <button type="button" className="boton secundario pequeno" onClick={cerrarSesion}>
              Cerrar sesión
            </button>
          </div>
        </header>
        <main className="contenido">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
