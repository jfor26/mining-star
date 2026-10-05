/**
 * Impide ver las pantallas internas sin haber iniciado sesion.
 * Guarda la ruta que se queria visitar para volver a ella despues del login.
 */
import { Navigate, useLocation } from 'react-router-dom'

import { useSesion } from '../context/SesionContext.jsx'

export default function RutaProtegida({ children }) {
  const { usuario } = useSesion()
  const ubicacion = useLocation()

  if (!usuario) {
    return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />
  }
  return children
}
