/**
 * Impide ver las pantallas sin haber iniciado sesion y separa las dos
 * interfaces: los clientes van al portal y el personal al sistema interno.
 * Guarda la ruta que se queria visitar para volver a ella despues del login.
 */
import { Navigate, useLocation } from 'react-router-dom'

import { useSesion } from '../context/SesionContext.jsx'

// oxlint-disable-next-line react/only-export-components
export const esCliente = (usuario) => usuario?.rol === 'Cliente'

export default function RutaProtegida({ children, paraClientes = false }) {
  const { usuario } = useSesion()
  const ubicacion = useLocation()

  if (!usuario) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />
  }
  if (esCliente(usuario) !== paraClientes) {
    return <Navigate to={esCliente(usuario) ? '/portal' : '/'} replace />
  }
  return children
}
