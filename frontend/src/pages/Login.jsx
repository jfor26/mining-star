/**
 * Inicio de sesion con dos accesos: el personal de la empresa y los clientes
 * del portal. Ambos usan POST /api/v1/auth/login/; el servidor decide el rol
 * y la aplicacion lleva a cada uno a su interfaz.
 */
import { useState } from 'react'
import { Link, Navigate, useLocation, useSearchParams } from 'react-router-dom'

import { Aviso, Campo } from '../components/Comunes.jsx'
import { esCliente } from '../components/RutaProtegida.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { requerido, validar } from '../utils/validaciones.js'

const TEXTOS = {
  personal: {
    titulo: 'Bienvenido',
    subtitulo: 'Ingrese con el usuario que le asignó el Administrador. Cada ingreso genera un token de acceso personal.',
    usuario: 'Usuario',
    boton: 'Iniciar sesión',
    ayuda: '¿Olvidó su contraseña? El Administrador puede restablecerla desde Seguridad y accesos.',
  },
  cliente: {
    titulo: 'Portal de clientes',
    subtitulo: 'Consulte sus compras, descargue comprobantes y solicite cotizaciones con precios vigentes.',
    usuario: 'NIT o documento',
    boton: 'Entrar al portal',
    ayuda: '¿Aún no tiene acceso? Solicítelo a su asesor comercial de Mining Star.',
  },
}

const VENTAJAS = [
  ['M7 11V7a5 5 0 0 1 10 0v4M5 11h14v10H5z', 'Sesión con token JWT y bitácora de cada ingreso'],
  ['M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9M13.7 21a2 2 0 0 1-3.4 0', 'Avisos de stock mínimo, vencimientos normativos y pedidos'],
  ['M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z', 'Portal para que los clientes coticen y consulten sus compras'],
]

export default function Login() {
  const { usuario, iniciarSesion } = useSesion()
  const ubicacion = useLocation()
  const [parametros] = useSearchParams()
  const [modo, setModo] = useState(parametros.get('modo') === 'cliente' ? 'cliente' : 'personal')
  const [datos, setDatos] = useState({ username: '', password: '' })
  const [errores, setErrores] = useState({})
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [verClave, setVerClave] = useState(false)

  // Con la sesion iniciada se va a la interfaz que corresponde al rol.
  if (usuario) {
    const destino = esCliente(usuario) ? '/portal' : (ubicacion.state?.desde ?? '/')
    return <Navigate to={destino} replace />
  }

  const t = TEXTOS[modo]
  const cambiar = (evento) => setDatos({ ...datos, [evento.target.name]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(datos, { username: [requerido], password: [requerido] })
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return

    setEnviando(true)
    setMensaje('')
    try {
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
      <section className="login-marca">
        <div className="login-logo">
          <img src="/logo.png" alt="" width="64" height="64" />
          <div>
            <strong>Mining Star Services and Products ERP</strong>
            <span>Industrias Mineras S.A.S. · Payandé, Tolima</span>
          </div>
        </div>
        <div className="login-mensaje">
          <h1>La cantera, de la extracción a la venta, en un solo lugar.</h1>
          <p>Producción por turno, inventario, ventas, CRM y cumplimiento ante la ANM y CORTOLIMA. Cada cargo ve solo lo que le corresponde.</p>
          <ul>
            {VENTAJAS.map(([icono, texto]) => (
              <li key={texto}>
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                  strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d={icono} /></svg>
                {texto}
              </li>
            ))}
          </ul>
        </div>
        <footer className="pie-login">
          <img src="/logo-sena.svg" alt="SENA" width="34" height="34" />
          <small>Proyecto formativo SENA · Tecnólogo ADSO · Ficha 3235867</small>
        </footer>
      </section>

      <section className="login-formulario">
        <form className="tarjeta-login" onSubmit={enviar} noValidate>
          <div className="pestanas-login" role="tablist" aria-label="Tipo de acceso">
            {[['personal', 'Personal de la empresa'], ['cliente', 'Soy cliente']].map(([clave, texto]) => (
              <button key={clave} type="button" role="tab" aria-selected={modo === clave}
                className={modo === clave ? 'activa' : undefined}
                onClick={() => { setModo(clave); setErrores({}); setMensaje('') }}>{texto}</button>
            ))}
          </div>
          <h2>{t.titulo}</h2>
          <p>{t.subtitulo}</p>
          <Aviso tipo="error">{mensaje}</Aviso>
          <Campo etiqueta={t.usuario} nombre="username" value={datos.username}
            onChange={cambiar} error={errores.username} autoComplete="username" autoFocus
            inputMode={modo === 'cliente' ? 'numeric' : undefined} />
          <div className="campo-clave">
            <Campo etiqueta="Contraseña" nombre="password" type={verClave ? 'text' : 'password'} value={datos.password}
              onChange={cambiar} error={errores.password} autoComplete="current-password" />
            <button type="button" className="ver-clave" aria-pressed={verClave}
              aria-label={verClave ? 'Ocultar contraseña' : 'Mostrar contraseña'} onClick={() => setVerClave(!verClave)}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" /><circle cx="12" cy="12" r="3" />
              </svg>
            </button>
          </div>
          <button type="submit" className="boton primario grande" disabled={enviando}>
            {enviando ? 'Verificando…' : t.boton}
          </button>
          <p className="ayuda-login">{t.ayuda}</p>
          <Link to="/sitio" className="volver-sitio">← Ir al sitio de la empresa</Link>
        </form>
      </section>
    </div>
  )
}
