/**
 * Ficha del cliente (vista 360 del CRM): datos, compras, oportunidades,
 * linea de tiempo de interacciones y acceso al portal de clientes.
 * Consume GET /api/v1/clientes/{id}/ficha/ y /clientes/{id}/acceso-portal/.
 */
import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'

import { peticion } from '../api/cliente.js'
import { Aviso, Cargando, Estado } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'

const moneda = (v) => `$ ${Number(v).toLocaleString('es-CO', { maximumFractionDigits: 0 })}`
const fechaCorta = (iso) => new Date(iso.length === 10 ? `${iso}T00:00:00` : iso).toLocaleDateString('es-CO')
const TONO_ETAPA = { Ganada: 'bien', Perdida: 'neutro', Negociacion: 'aviso', Cotizacion: 'aviso' }

// oxlint-disable-next-line react/only-export-components
export const iniciales = (nombre) => nombre.split(/\s+/).filter((p) => /^[A-Za-zÁÉÍÓÚÑ]/.test(p)).slice(0, 2).map((p) => p[0]).join('').toUpperCase()

export default function FichaCliente() {
  const { id } = useParams()
  const { puede } = useSesion()
  const [ficha, setFicha] = useState(null)
  const [error, setError] = useState('')
  const [clave, setClave] = useState('')
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })

  const cargar = useCallback(() => (
    peticion(`/clientes/${id}/ficha/`).then(setFicha).catch((e) => setError(e.estado === 404 ? 'El cliente no existe.' : 'No se pudo cargar la ficha.'))
  ), [id])
  useEffect(() => { cargar() }, [cargar])

  async function darAcceso(evento) {
    evento.preventDefault()
    try {
      const r = await peticion(`/clientes/${id}/acceso-portal/`, { metodo: 'POST', datos: { clave } })
      setClave('')
      setAviso({ tipo: 'exito', texto: `Acceso al portal listo. El cliente entra con el usuario ${r.usuario} y la clave que usted le entregue.` })
      cargar()
    } catch (e) {
      setAviso({ tipo: 'error', texto: (e.errores?.clave ?? [e.message]).join(' ') })
    }
  }

  async function quitarAcceso() {
    await peticion(`/clientes/${id}/acceso-portal/`, { metodo: 'DELETE' })
    setAviso({ tipo: 'exito', texto: 'Se desactivó el acceso del cliente al portal.' })
    cargar()
  }

  if (error) return <Aviso tipo="error">{error}</Aviso>
  if (!ficha) return <Cargando />
  const { cliente } = ficha
  const dias = ficha.ultimo_contacto_dias
  const contactoAtrasado = dias !== null && dias >= 7

  return (
    <div className="ficha">
      <section className="tarjeta ficha-cabecera">
        <div className="ficha-identidad">
          <span className="avatar-cliente" aria-hidden="true">{iniciales(cliente.nombre)}</span>
          <div>
            <h1>{cliente.nombre}</h1>
            <p>{cliente.documento} · {cliente.empresa} · {cliente.correo} · {cliente.telefono}</p>
          </div>
        </div>
        {puede('crm', 'crear') && (
          <div className="acciones-fila">
            <Link className="boton secundario" to="/crm">Registrar interacción</Link>
            <Link className="boton primario" to="/crm">Nueva oportunidad</Link>
          </div>
        )}
      </section>

      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>

      <div className="indicadores-ficha">
        {ficha.compras && (
          <article className="tarjeta">
            <span>Compras</span>
            <strong>{moneda(ficha.compras.total)}</strong>
            <small>{ficha.compras.cantidad} {ficha.compras.cantidad === 1 ? 'venta vigente' : 'ventas vigentes'}</small>
          </article>
        )}
        {ficha.oportunidades && (
          <article className="tarjeta">
            <span>Oportunidades abiertas</span>
            <strong>{moneda(ficha.abiertas_valor)}</strong>
            <small>{ficha.oportunidades.filter((o) => !['Ganada', 'Perdida'].includes(o.etapa)).length} en el embudo</small>
          </article>
        )}
        <article className={`tarjeta${contactoAtrasado ? ' alerta-contacto' : ''}`}>
          <span>Último contacto</span>
          <strong>{dias === null ? 'Sin registro' : dias === 0 ? 'Hoy' : `Hace ${dias} ${dias === 1 ? 'día' : 'días'}`}</strong>
          <small>{contactoAtrasado ? 'Conviene contactarlo pronto' : 'Interacciones del CRM'}</small>
        </article>
      </div>

      <div className="dos-iguales">
        <div className="columna-ficha">
          {ficha.oportunidades && (
            <section className="tarjeta">
              <h2>Oportunidades</h2>
              {ficha.oportunidades.length === 0 ? <p className="descripcion">Sin oportunidades.</p> : (
                <ul className="lista-oportunidades">
                  {ficha.oportunidades.map((o) => (
                    <li key={o.id}>
                      <div><strong>{o.titulo}</strong><small>Probabilidad {o.probabilidad} %{o.origen === 'Portal' ? ' · desde el portal' : ''}</small></div>
                      <div className="derecha"><strong>{moneda(o.valor_estimado)}</strong><Estado tono={TONO_ETAPA[o.etapa] ?? 'neutro'}>{o.etapa_texto}</Estado></div>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          )}
          {ficha.compras && (
            <section className="tarjeta">
              <h2>Últimas compras</h2>
              {ficha.compras.ultimas.length === 0 ? <p className="descripcion">Sin compras registradas.</p> : (
                <div className="tabla-contenedor tabla-compras">
                  <table>
                    <thead><tr><th scope="col">N.º</th><th scope="col">Fecha</th><th scope="col">Productos</th><th scope="col">Total</th></tr></thead>
                    <tbody>
                      {ficha.compras.ultimas.map((v) => (
                        <tr key={v.id}><td>{v.numero}</td><td>{fechaCorta(v.fecha)}</td><td>{v.productos.join(', ')}</td><td>{moneda(v.total)}</td></tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          )}
          {puede('clientes', 'editar') && (
            <section className="tarjeta">
              <h2>Acceso al portal de clientes</h2>
              <p className="descripcion">
                {cliente.acceso_portal
                  ? `Activo. El cliente entra con el usuario ${cliente.documento}.`
                  : 'El cliente aún no tiene acceso. Asigne una clave segura y entréguesela por un medio privado.'}
              </p>
              <form className="form-acceso" onSubmit={darAcceso}>
                <label htmlFor="clave-portal">{cliente.acceso_portal ? 'Nueva clave' : 'Clave inicial'}</label>
                <input id="clave-portal" type="password" autoComplete="new-password" value={clave} onChange={(e) => setClave(e.target.value)} />
                <div className="acciones-fila">
                  <button type="submit" className="boton primario" disabled={!clave}>{cliente.acceso_portal ? 'Cambiar clave' : 'Dar acceso'}</button>
                  {cliente.acceso_portal && <button type="button" className="boton peligro" onClick={quitarAcceso}>Quitar acceso</button>}
                </div>
              </form>
            </section>
          )}
        </div>

        {ficha.interacciones && (
          <section className="tarjeta">
            <h2>Línea de tiempo</h2>
            {ficha.interacciones.length === 0 ? <p className="descripcion">Aún no hay interacciones registradas.</p> : (
              <ol className="linea-tiempo">
                {ficha.interacciones.map((i) => (
                  <li key={i.id} className={`evento-${i.tipo.toLowerCase()}`}>
                    <strong>{i.tipo_texto}{i.oportunidad ? ` · ${i.oportunidad}` : ''}</strong>
                    <span>{i.descripcion}</span>
                    {i.proxima_accion && <span className="proxima">Próxima acción: {i.proxima_accion}</span>}
                    <small>{fechaCorta(i.fecha)}{i.registrado_por ? ` · ${i.registrado_por}` : ''}</small>
                  </li>
                ))}
              </ol>
            )}
          </section>
        )}
      </div>
    </div>
  )
}
