import { Link } from 'react-router-dom'

/** Pagina para rutas que no existen dentro de la aplicacion. */
export default function NoEncontrada() {
  return (
    <section className="tarjeta">
      <h1>Página no encontrada</h1>
      <p>La dirección no corresponde a ninguna pantalla del sistema.</p>
      <Link to="/" className="boton">Volver al panel</Link>
    </section>
  )
}
