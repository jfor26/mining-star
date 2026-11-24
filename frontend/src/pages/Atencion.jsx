/**
 * Atencion al cliente: PQRS radicadas en el sitio publico y mensajes del
 * formulario de contacto. Consume /api/v1/pqrs/ y /api/v1/contactos/.
 */
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Cargando, Encabezado, Estado } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'

const TONO = { Recibida: 'critico', EnTramite: 'aviso', Respondida: 'bien', Cerrada: 'neutro' }
const ESTADOS = [['EnTramite', 'En trámite'], ['Respondida', 'Respondida'], ['Cerrada', 'Cerrada']]
const fecha = (iso) => new Date(iso).toLocaleDateString('es-CO')
const diasDesde = (iso) => Math.floor((Date.now() - new Date(iso).getTime()) / 86400000)

export default function Atencion() {
  const { puede } = useSesion()
  const [vista, setVista] = useState('pqrs')
  const [pqrs, setPqrs] = useState(null)
  const [mensajes, setMensajes] = useState(null)
  const [filtro, setFiltro] = useState('pendientes')
  const [abierta, setAbierta] = useState(null)
  const [respuesta, setRespuesta] = useState({ estado: 'Respondida', respuesta: '' })
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })
  const editar = puede('pqrs', 'editar')

  const cargar = useCallback(() => {
    obtenerTodos('/pqrs/').then(setPqrs).catch(() => setPqrs([]))
    obtenerTodos('/contactos/').then(setMensajes).catch(() => setMensajes([]))
  }, [])
  useEffect(() => { cargar() }, [cargar])

  function abrir(q) {
    setAbierta(q)
    setRespuesta({ estado: q.estado === 'Recibida' ? 'Respondida' : q.estado, respuesta: q.respuesta })
  }

  async function guardar(evento) {
    evento.preventDefault()
    try {
      await peticion(`/pqrs/${abierta.id}/`, { metodo: 'PATCH', datos: respuesta })
      setAviso({ tipo: 'exito', texto: `${abierta.radicado} actualizada. El ciudadano verá la respuesta al consultar su radicado.` })
      setAbierta(null)
      cargar()
    } catch (e) {
      setAviso({ tipo: 'error', texto: (e.errores?.respuesta ?? [e.message]).join(' ') })
    }
  }

  async function atender(m) {
    await peticion(`/contactos/${m.id}/`, { metodo: 'PATCH', datos: { atendido: !m.atendido } })
    cargar()
  }

  const visibles = (pqrs ?? []).filter((q) => (filtro === 'pendientes' ? ['Recibida', 'EnTramite'].includes(q.estado) : true))
  const pendientes = (pqrs ?? []).filter((q) => ['Recibida', 'EnTramite'].includes(q.estado)).length
  const sinAtender = (mensajes ?? []).filter((m) => !m.atendido).length

  return (
    <>
      <Encabezado titulo="Atención al cliente" descripcion="PQRS radicadas en el sitio web y mensajes del formulario de contacto." />
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      <div className="pestanas" role="tablist" style={{ marginBottom: 16 }}>
        <button type="button" role="tab" aria-selected={vista === 'pqrs'} className={vista === 'pqrs' ? 'activa' : ''} onClick={() => setVista('pqrs')}>PQRS ({pendientes} pendientes)</button>
        <button type="button" role="tab" aria-selected={vista === 'mensajes'} className={vista === 'mensajes' ? 'activa' : ''} onClick={() => setVista('mensajes')}>Mensajes de contacto ({sinAtender} sin atender)</button>
      </div>

      {vista === 'pqrs' && (
        <div className={abierta ? 'dos-columnas' : 'una-columna'}>
          <section className="tarjeta">
            <div className="chips" role="group" aria-label="Filtrar PQRS">
              {[['pendientes', 'Pendientes'], ['todas', 'Todas']].map(([v, t]) => (
                <button key={v} type="button" className={`chip${filtro === v ? ' activo' : ''}`} aria-pressed={filtro === v} onClick={() => setFiltro(v)}>{t}</button>
              ))}
            </div>
            {!pqrs ? <Cargando /> : visibles.length === 0 ? <p className="descripcion">No hay PQRS en esta vista.</p> : (
              <ul className="lista-pqrs">
                {visibles.map((q) => (
                  <li key={q.id}>
                    <button type="button" className={abierta?.id === q.id ? 'activa' : undefined} onClick={() => abrir(q)}>
                      <span className="fila-pqrs"><strong>{q.radicado} · {q.tipo_texto}</strong><Estado tono={TONO[q.estado]}>{q.estado_texto}</Estado></span>
                      <span>{q.nombre}{q.cliente_nombre ? ` (cliente: ${q.cliente_nombre})` : ''}</span>
                      <small>Radicada el {fecha(q.creada)} · {diasDesde(q.creada) === 0 ? 'hoy' : `hace ${diasDesde(q.creada)} ${diasDesde(q.creada) === 1 ? 'día' : 'días'}`}</small>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
          {abierta && (
            <section className="tarjeta">
              <h2>{abierta.radicado} · {abierta.tipo_texto}</h2>
              <p className="descripcion">{abierta.nombre} · {abierta.documento} · {abierta.correo}{abierta.telefono ? ` · ${abierta.telefono}` : ''}</p>
              {abierta.cliente && <p><Link to={`/clientes/${abierta.cliente}`}>Ver ficha del cliente</Link></p>}
              <blockquote className="detalle-pqrs">{abierta.detalle}</blockquote>
              {editar ? (
                <form onSubmit={guardar} className="form-respuesta">
                  <label htmlFor="estado-pqrs">Estado</label>
                  <select id="estado-pqrs" value={respuesta.estado} onChange={(e) => setRespuesta({ ...respuesta, estado: e.target.value })}>
                    {ESTADOS.map(([v, t]) => <option key={v} value={v}>{t}</option>)}
                  </select>
                  <label htmlFor="respuesta-pqrs">Respuesta al ciudadano</label>
                  <textarea id="respuesta-pqrs" rows="6" value={respuesta.respuesta} onChange={(e) => setRespuesta({ ...respuesta, respuesta: e.target.value })} />
                  <div className="acciones-fila">
                    <button type="submit" className="boton primario">Guardar</button>
                    <button type="button" className="boton secundario" onClick={() => setAbierta(null)}>Cerrar</button>
                  </div>
                </form>
              ) : abierta.respuesta && <p><strong>Respuesta:</strong> {abierta.respuesta}</p>}
            </section>
          )}
        </div>
      )}

      {vista === 'mensajes' && (
        <section className="tarjeta">
          {!mensajes ? <Cargando /> : mensajes.length === 0 ? <p className="descripcion">No hay mensajes.</p> : (
            <ul className="lista-pqrs">
              {mensajes.map((m) => (
                <li key={m.id} className="mensaje-contacto">
                  <div>
                    <span className="fila-pqrs"><strong>{m.nombre}</strong>{m.atendido ? <Estado tono="bien">Atendido</Estado> : <Estado tono="aviso">Sin atender</Estado>}</span>
                    <span>{m.correo}{m.telefono ? ` · ${m.telefono}` : ''} · {fecha(m.creado)}</span>
                    <p>{m.mensaje}</p>
                  </div>
                  {editar && <button type="button" className="boton secundario pequeno" onClick={() => atender(m)}>{m.atendido ? 'Marcar sin atender' : 'Marcar atendido'}</button>}
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </>
  )
}
