/**
 * Seguridad: usuarios y cargos, bitacora de ingresos (tokens), matriz de
 * accesibilidad por cargo y copias de seguridad de la base de datos.
 */
import { useCallback, useEffect, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Estado, Pestanas, Tabla, erroresDeLaAPI } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { fecha } from '../utils/formato.js'

const ROLES = ['Administrador', 'Gerente', 'Supervisor', 'Comercial', 'Contador', 'Operario', 'Auxiliar']
const OPS = [['ver', 'V'], ['crear', 'C'], ['editar', 'E'], ['eliminar', 'X']]
const fechaHora = (iso) => (iso ? new Date(iso).toLocaleString('es-CO') : '—')

function Matriz() {
  const [matriz, setMatriz] = useState(null)
  useEffect(() => { peticion('/seguridad/matriz/').then(setMatriz).catch(() => {}) }, [])
  if (!matriz) return <Cargando />
  return (
    <section className="tarjeta">
      <h2>Accesibilidad por cargo</h2>
      <p className="descripcion">V = ver · C = crear · E = editar · X = eliminar. La API aplica esta misma matriz en cada petición.</p>
      <div className="tabla-contenedor">
        <table className="matriz">
          <thead>
            <tr><th>Módulo</th>{ROLES.map((r) => <th key={r}>{r}</th>)}</tr>
          </thead>
          <tbody>
            {Object.entries(matriz.modulos).map(([clave, nombre]) => (
              <tr key={clave}>
                <th scope="row">{nombre}</th>
                {ROLES.map((r) => {
                  const ops = matriz.roles[r][clave] ?? []
                  return (
                    <td key={r} className={ops.length ? 'con-acceso' : 'sin-acceso'}>
                      {ops.length ? OPS.filter(([o]) => ops.includes(o)).map(([, l]) => l).join(' ') : '—'}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function Usuarios() {
  const { puede, usuario: actual } = useSesion()
  const [usuarios, setUsuarios] = useState(null)
  const [nuevo, setNuevo] = useState({ username: '', email: '', first_name: '', password: '', password2: '', rol: 'Operario' })
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })
  const cargar = useCallback(() => obtenerTodos('/seguridad/usuarios/').then(setUsuarios), [])
  useEffect(() => { obtenerTodos('/seguridad/usuarios/').then(setUsuarios).catch(() => setUsuarios([])) }, [])

  async function accion(ruta, datos, texto) {
    try { await peticion(ruta, { metodo: 'POST', datos }); setAviso({ tipo: 'exito', texto }); cargar() }
    catch (error) { setAviso({ tipo: 'error', texto: error.message }) }
  }

  async function crear(e) {
    e.preventDefault()
    try {
      await peticion('/auth/registro/', { metodo: 'POST', datos: nuevo })
      setAviso({ tipo: 'exito', texto: `Usuario ${nuevo.username} creado con cargo ${nuevo.rol}.` })
      setNuevo({ username: '', email: '', first_name: '', password: '', password2: '', rol: 'Operario' }); setErrores({}); cargar()
    } catch (error) { setErrores(erroresDeLaAPI(error)) }
  }

  const cambiar = (e) => setNuevo({ ...nuevo, [e.target.name]: e.target.value })
  if (!usuarios) return <Cargando />
  return (
    <div className="dos-columnas invertido">
      <section className="tarjeta">
        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
        <Tabla filas={usuarios} columnas={[
          { clave: 'username', titulo: 'Usuario' },
          { clave: 'empleado', titulo: 'Empleado', celda: (u) => u.empleado ?? '—' },
          { clave: 'rol', titulo: 'Cargo', celda: (u) => (puede('seguridad', 'editar') && u.id !== actual.id ? (
            <select aria-label={`Cargo de ${u.username}`} value={u.rol ?? ''}
              onChange={(e) => accion(`/seguridad/usuarios/${u.id}/cambiar-rol/`, { rol: e.target.value }, `Cargo de ${u.username} actualizado.`)}>
              <option value="" disabled>Sin cargo</option>
              {ROLES.map((r) => <option key={r}>{r}</option>)}
            </select>
          ) : (u.rol ?? 'Sin cargo')) },
          { clave: 'last_login', titulo: 'Último ingreso', celda: (u) => fechaHora(u.last_login) },
          { clave: 'is_active', titulo: 'Estado', celda: (u) => <Estado tono={u.is_active ? 'bien' : 'neutro'}>{u.is_active ? 'Activo' : 'Inactivo'}</Estado> },
          { clave: 'acciones', titulo: '', celda: (u) => puede('seguridad', 'editar') && u.id !== actual.id && (
            <button type="button" className={`boton pequeno ${u.is_active ? 'peligro' : 'secundario'}`}
              onClick={() => accion(`/seguridad/usuarios/${u.id}/activar/`, undefined, `Cuenta de ${u.username} ${u.is_active ? 'desactivada' : 'activada'}.`)}>
              {u.is_active ? 'Desactivar' : 'Activar'}
            </button>
          ) },
        ]} />
      </section>
      {puede('seguridad', 'crear') && (
        <section className="tarjeta">
          <h2>Crear usuario</h2>
          <form onSubmit={crear} noValidate>
            <Campo etiqueta="Usuario" nombre="username" value={nuevo.username} onChange={cambiar} error={errores.username} autoComplete="off" />
            <Campo etiqueta="Nombre" nombre="first_name" value={nuevo.first_name} onChange={cambiar} />
            <Campo etiqueta="Correo" nombre="email" type="email" value={nuevo.email} onChange={cambiar} error={errores.email} />
            <Campo como="select" etiqueta="Cargo" nombre="rol" value={nuevo.rol} onChange={cambiar}>
              {ROLES.map((r) => <option key={r}>{r}</option>)}
            </Campo>
            <Campo etiqueta="Contraseña" nombre="password" type="password" value={nuevo.password} onChange={cambiar}
              error={errores.password ?? errores.non_field_errors} autoComplete="new-password" />
            <Campo etiqueta="Repetir contraseña" nombre="password2" type="password" value={nuevo.password2} onChange={cambiar}
              error={errores.password2} autoComplete="new-password" />
            <button type="submit" className="boton primario">Crear usuario</button>
          </form>
        </section>
      )}
    </div>
  )
}

function Bitacora() {
  const [registros, setRegistros] = useState(null)
  const [evento, setEvento] = useState('')
  useEffect(() => {
    peticion(`/seguridad/accesos/${evento ? `?evento=${evento}` : ''}`).then((d) => setRegistros(d.results)).catch(() => setRegistros([]))
  }, [evento])
  const TONO = { ingreso: 'bien', fallido: 'serio', bloqueado: 'critico', salida: 'neutro' }
  return (
    <section className="tarjeta">
      <div className="barra-filtros">
        <p className="descripcion">Cada ingreso emite un token JWT nuevo; aquí queda su identificador (jti), la IP y el navegador.</p>
        <select aria-label="Evento" value={evento} onChange={(e) => setEvento(e.target.value)}>
          <option value="">Todos los eventos</option>
          <option value="ingreso">Ingresos</option><option value="fallido">Fallidos</option>
          <option value="bloqueado">Bloqueados</option><option value="salida">Cierres de sesión</option>
        </select>
      </div>
      {!registros ? <Cargando /> : (
        <Tabla filas={registros} columnas={[
          { clave: 'fecha', titulo: 'Fecha y hora', celda: (r) => fechaHora(r.fecha) },
          { clave: 'nombre_usuario', titulo: 'Usuario' },
          { clave: 'evento', titulo: 'Evento', celda: (r) => <Estado tono={TONO[r.evento]}>{r.evento_nombre}</Estado> },
          { clave: 'ip', titulo: 'IP' },
          { clave: 'token_jti', titulo: 'Token (jti)', celda: (r) => (r.token_jti ? <code>{r.token_jti.slice(0, 12)}…</code> : '—') },
        ]} />
      )}
    </section>
  )
}

function Respaldos() {
  const { puede } = useSesion()
  const [lista, setLista] = useState(null)
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })
  const [ocupado, setOcupado] = useState(false)
  useEffect(() => { peticion('/seguridad/respaldos/').then(setLista).catch(() => setLista([])) }, [])
  async function crear() {
    setOcupado(true)
    try {
      const r = await peticion('/seguridad/respaldos/', { metodo: 'POST' })
      setLista(r.respaldos); setAviso({ tipo: 'exito', texto: r.mensaje })
    } catch (error) { setAviso({ tipo: 'error', texto: error.message }) } finally { setOcupado(false) }
  }
  return (
    <section className="tarjeta">
      <div className="barra-filtros">
        <p className="descripcion">Exportación JSON de todos los datos de PostgreSQL (y copia <code>.dump</code> si el servidor tiene <code>pg_dump</code>) en la carpeta <code>respaldos/</code>. Se conservan los 10 más recientes.</p>
        {puede('seguridad', 'crear') && (
          <button type="button" className="boton primario" onClick={crear} disabled={ocupado}>
            {ocupado ? 'Respaldando…' : 'Crear respaldo ahora'}
          </button>
        )}
      </div>
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      {!lista ? <Cargando /> : (
        <Tabla filas={lista} claveFila="archivo" vacio="Aún no hay respaldos." columnas={[
          { clave: 'archivo', titulo: 'Archivo', celda: (r) => <code>{r.archivo}</code> },
          { clave: 'fecha', titulo: 'Fecha', celda: (r) => `${fecha(r.fecha)} ${r.fecha.slice(11, 16)}` },
          { clave: 'tamano_kb', titulo: 'Tamaño', celda: (r) => `${r.tamano_kb} KB` },
          { clave: 'con_pg_dump', titulo: 'Copia .dump', celda: (r) => (r.con_pg_dump ? 'Sí' : 'No') },
        ]} />
      )}
    </section>
  )
}

export default function Seguridad() {
  const [pestana, setPestana] = useState('usuarios')
  return (
    <>
      <Encabezado titulo="Seguridad y accesos" descripcion="Usuarios y cargos, bitácora de ingresos con token, accesibilidad por cargo y respaldos." />
      <Pestanas activa={pestana} alCambiar={setPestana} pestanas={[
        ['usuarios', 'Usuarios y cargos'], ['bitacora', 'Bitácora de accesos'], ['matriz', 'Accesibilidad por cargo'], ['respaldos', 'Respaldos (backup)'],
      ]} />
      {pestana === 'usuarios' && <Usuarios />}
      {pestana === 'bitacora' && <Bitacora />}
      {pestana === 'matriz' && <Matriz />}
      {pestana === 'respaldos' && <Respaldos />}
    </>
  )
}
