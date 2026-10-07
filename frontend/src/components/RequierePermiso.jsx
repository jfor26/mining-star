/**
 * Envuelve una pagina y la muestra solo si el cargo puede ver el modulo.
 * Es una ayuda de interfaz: la API vuelve a comprobar el permiso siempre.
 */
import { useSesion } from '../context/SesionContext.jsx'
import { SinPermiso } from './Comunes.jsx'

export default function RequierePermiso({ modulo, children }) {
  const { puede } = useSesion()
  return puede(modulo) ? children : <SinPermiso modulo={modulo} />
}
