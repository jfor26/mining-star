/**
 * Inicio de sesion. Consume POST /api/v1/auth/login/ y guarda los tokens.
 */
import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { Aviso, Campo } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { requerido, validar } from '../utils/validaciones.js'

export default function Login() {
  const { usuario, iniciarSesion } = useSesion()
  const ubicacion = useLocation()
  const [datos, setDatos] = useState({ username: '', password: '' })
  const [errores, setErrores] = useState({})
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)

  // Con la sesion iniciada se vuelve a la pantalla que se queria visitar.
  if (usuario) return <Navigate to={ubicacion.state?.desde ?? '/'} replace />

  const cambiar = (evento) => setDatos({ ...datos, [evento.target.name]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(datos, { username: [requerido], password: [requerido] })
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return

    setEnviando(true)
    setMensaje('')
    try {
      // Al actualizarse la sesion, el componente se vuelve a pintar y el
      // <Navigate> de arriba hace la redireccion.
      await iniciarSesion(datos.username.trim(), datos.password)
    } catch (error) {
      // El servidor devuelve el mismo mensaje si el usuario no existe o si la
      // contrasena esta mal; aqui se muestra tal cual.
      setMensaje(error.estado ? error.message : 'No fue posible conectar con el servidor.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="pantalla-login">
      <div className="login-banner" aria-hidden="true">
        <img src="/banner-login.jpg" alt="" />
      </div>
      <form className="tarjeta-login" onSubmit={enviar} noValidate>
        <img src="/logo.png" alt="Mining Star ERP" width="150" height="100" className="logo-login" />
        <h1>Bienvenido</h1>
        <p>Ingrese con el usuario que le asignó el Administrador. Cada ingreso genera un token de acceso personal.</p>
        <Aviso tipo="error">{mensaje}</Aviso>
        <Campo etiqueta="Usuario" nombre="username" value={datos.username}
          onChange={cambiar} error={errores.username} autoComplete="username" autoFocus />
        <Campo etiqueta="Contraseña" nombre="password" type="password" value={datos.password}
          onChange={cambiar} error={errores.password} autoComplete="current-password" />
        <button type="submit" className="boton primario grande" disabled={enviando}>
          {enviando ? 'Verificando…' : 'Iniciar sesión'}
        </button>
        <footer className="pie-login">
          <img src="/logo-sena.svg" alt="SENA" width="34" height="34" />
          <small>Proyecto formativo · Tecnólogo en Análisis y Desarrollo de Software · SENA</small>
        </footer>
      </form>
    </div>
  )
}
