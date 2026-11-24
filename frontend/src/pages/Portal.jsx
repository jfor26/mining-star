/**
 * Portal de clientes: interfaz propia, distinta a la del personal.
 * El cliente ve sus compras, descarga comprobantes, solicita cotizaciones
 * (que llegan al CRM como oportunidades) y consulta el catalogo.
 * Consume /api/v1/portal/...; la API filtra todo por el cliente de la sesion.
 */
import { useCallback, useEffect, useRef, useState } from 'react'

import { descargarArchivo, peticion } from '../api/cliente.js'
import { SelectorTema } from '../components/Barra.jsx'
import { Aviso, Cargando, Estado, erroresDeLaAPI } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'

const moneda = (v) => `$ ${Number(v).toLocaleString('es-CO', { maximumFractionDigits: 0 })}`
const fecha = (iso) => new Date(`${iso}T00:00:00`).toLocaleDateString('es-CO')
const hoy = () => new Date().toISOString().slice(0, 10)
const TONO = { Recibida: 'neutro', 'En revisión': 'aviso', 'Cotización enviada': 'bien', 'En negociación': 'aviso', Aceptada: 'bien', Cerrada: 'neutro' }

export default function Portal() {
  const { usuario, cerrarSesion } = useSesion()
  const [resumen, setResumen] = useState(null)
  const [catalogo, setCatalogo] = useState([])
  const [items, setItems] = useState([{ producto: '', cantidad: 1 }])
  const [entrega, setEntrega] = useState('')
  const [observaciones, setObservaciones] = useState('')
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })
  const [enviando, setEnviando] = useState(false)
  const formulario = useRef(null)

  const cargar = useCallback(() => peticion('/portal/resumen/').then(setResumen), [])

  useEffect(() => {
    cargar().catch(() => setAviso({ tipo: 'error', texto: 'No fue posible cargar su información.' }))
    peticion('/portal/catalogo/').then(setCatalogo).catch(() => {})
  }, [cargar])

  const cambiarItem = (i, campo, valor) => setItems(items.map((it, j) => (j === i ? { ...it, [campo]: valor } : it)))
  const total = items.reduce((suma, it) => {
    const p = catalogo.find((c) => String(c.id) === String(it.producto))
    return suma + (p ? Number(p.precio) * Number(it.cantidad || 0) : 0)
  }, 0)

  function cotizar(producto) {
    const libre = items.findIndex((it) => !it.producto)
    if (libre >= 0) cambiarItem(libre, 'producto', String(producto.id))
    else setItems([...items, { producto: String(producto.id), cantidad: 1 }])
    formulario.current?.scrollIntoView?.({ behavior: 'smooth', block: 'start' })
  }

  async function enviar(evento) {
    evento.preventDefault()
    const validos = items.filter((it) => it.producto)
    const encontrados = {}
    if (!validos.length) encontrados.items = 'Elija al menos un producto.'
    if (validos.some((it) => !(Number(it.cantidad) >= 1))) encontrados.items = 'Las cantidades deben ser mayores que cero.'
    if (entrega && entrega < hoy()) encontrados.fecha_entrega = 'La fecha no puede estar en el pasado.'
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return
    setEnviando(true)
    try {
      await peticion('/portal/cotizaciones/', {
        metodo: 'POST',
        datos: {
          items: validos.map((it) => ({ producto: Number(it.producto), cantidad: Number(it.cantidad) })),
          fecha_entrega: entrega || null,
          observaciones,
        },
      })
      setAviso({ tipo: 'exito', texto: 'Solicitud enviada. Su asesor comercial le enviará la cotización.' })
      setItems([{ producto: '', cantidad: 1 }])
      setEntrega('')
      setObservaciones('')
      cargar()
    } catch (error) {
      const delServidor = erroresDeLaAPI(error)
      setErrores({ ...delServidor, items: delServidor.items ? 'Revise los productos y cantidades.' : undefined })
      setAviso({ tipo: 'error', texto: 'No se pudo enviar la solicitud. Revise los datos.' })
    } finally {
      setEnviando(false)
    }
  }

  async function comprobante(compra) {
    try {
      await descargarArchivo(`/portal/compras/${compra.id}/comprobante/`, `comprobante_${compra.numero}.pdf`)
    } catch {
      setAviso({ tipo: 'error', texto: 'No se pudo descargar el comprobante.' })
    }
  }

  const cliente = resumen?.cliente
  return (
    <div className="portal">
      <header className="portal-barra">
        <div className="portal-contenedor portal-barra-fila">
          <div className="portal-marca">
            <img src="/logo.png" alt="" width="42" height="42" />
            <div><strong>Mining Star Services and Products</strong><span>Portal de clientes</span></div>
          </div>
          <nav aria-label="Portal" className="portal-menu">
            <a href="#compras">Mis compras</a>
            <a href="#cotizar">Cotizar</a>
            <a href="#solicitudes">Mis solicitudes</a>
            <a href="#catalogo">Catálogo</a>
          </nav>
          <div className="portal-cuenta">
            <SelectorTema />
            <div className="portal-nombre"><strong>{cliente?.nombre ?? usuario?.first_name}</strong><span>NIT {usuario?.username}</span></div>
            <button type="button" className="boton secundario" onClick={cerrarSesion}>Salir</button>
          </div>
        </div>
      </header>

      <main className="portal-contenedor portal-cuerpo">
        <section className="portal-bienvenida">
          <div>
            <h1>Bienvenido a su portal</h1>
            <p>Consulte sus compras, descargue comprobantes y solicite cotizaciones con precios vigentes, sin llamar.</p>
          </div>
          <a href="#cotizar" className="boton grande portal-boton-claro">Solicitar cotización</a>
        </section>

        <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>

        {!resumen ? <Cargando /> : (
          <div className="portal-columnas">
            <section id="compras" className="tarjeta">
              <h2>Mis compras</h2>
              {resumen.compras.length === 0 ? <p className="descripcion">Aún no tiene compras registradas.</p> : (
                <div className="tabla-contenedor tabla-compras">
                  <table>
                    <thead><tr><th scope="col">N.º</th><th scope="col">Fecha</th><th scope="col">Productos</th><th scope="col">Total</th><th scope="col">Comprobante</th></tr></thead>
                    <tbody>
                      {resumen.compras.map((c) => (
                        <tr key={c.id}>
                          <td>{c.numero}</td>
                          <td>{fecha(c.fecha)}</td>
                          <td>{c.productos.join(', ')}</td>
                          <td>{moneda(c.total)}</td>
                          <td><button type="button" className="boton fantasma pequeno" onClick={() => comprobante(c)}
                            aria-label={`Descargar comprobante ${c.numero}`}>PDF</button></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>

            <section id="cotizar" className="tarjeta" ref={formulario}>
              <h2>Solicitar cotización</h2>
              <p className="descripcion">Su solicitud llega a su asesor comercial y queda registrada en nuestro CRM.</p>
              <form onSubmit={enviar} noValidate className="formulario-cotizacion">
                {items.map((it, i) => (
                  <div className="fila-item" key={i}>
                    <div className="campo">
                      <label htmlFor={`producto-${i}`}>Producto {items.length > 1 ? i + 1 : ''}</label>
                      <select id={`producto-${i}`} value={it.producto} onChange={(e) => cambiarItem(i, 'producto', e.target.value)}>
                        <option value="">Elija un producto…</option>
                        {catalogo.map((p) => <option key={p.id} value={p.id}>{p.nombre} · {moneda(p.precio)}</option>)}
                      </select>
                    </div>
                    <div className="campo">
                      <label htmlFor={`cantidad-${i}`}>Cantidad</label>
                      <input id={`cantidad-${i}`} type="number" min="1" inputMode="numeric" value={it.cantidad}
                        onChange={(e) => cambiarItem(i, 'cantidad', e.target.value)} />
                    </div>
                    {items.length > 1 && (
                      <button type="button" className="boton fantasma pequeno quitar-item" aria-label={`Quitar producto ${i + 1}`}
                        onClick={() => setItems(items.filter((_, j) => j !== i))}>Quitar</button>
                    )}
                  </div>
                ))}
                {errores.items && <small className="error" role="alert">{errores.items}</small>}
                <button type="button" className="boton fantasma pequeno" onClick={() => setItems([...items, { producto: '', cantidad: 1 }])}>
                  + Agregar otro producto
                </button>
                <div className={`campo${errores.fecha_entrega ? ' con-error' : ''}`}>
                  <label htmlFor="entrega">Fecha de entrega deseada (opcional)</label>
                  <input id="entrega" type="date" min={hoy()} value={entrega} onChange={(e) => setEntrega(e.target.value)}
                    aria-invalid={Boolean(errores.fecha_entrega)} />
                  {errores.fecha_entrega && <small className="error">{errores.fecha_entrega}</small>}
                </div>
                <div className="campo">
                  <label htmlFor="observaciones">Lugar de entrega u observaciones</label>
                  <textarea id="observaciones" rows="3" maxLength={500} value={observaciones} onChange={(e) => setObservaciones(e.target.value)} />
                </div>
                {total > 0 && <p className="valor-estimado">Valor estimado a precios vigentes: <strong>{moneda(total)}</strong></p>}
                <button type="submit" className="boton primario grande" disabled={enviando}>
                  {enviando ? 'Enviando…' : 'Enviar solicitud'}
                </button>
              </form>
            </section>
          </div>
        )}

        {resumen && (
          <section id="solicitudes" className="tarjeta">
            <h2>Mis solicitudes de cotización</h2>
            {resumen.solicitudes.length === 0 ? <p className="descripcion">Todavía no ha enviado solicitudes.</p> : (
              <ul className="lista-solicitudes">
                {resumen.solicitudes.map((s) => (
                  <li key={s.id}>
                    <div><strong>{s.titulo.replace('Cotización portal: ', '')}</strong><span>{fecha(s.fecha)} · {moneda(s.valor_estimado)}</span></div>
                    <Estado tono={TONO[s.estado] ?? 'neutro'}>{s.estado}</Estado>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )}

        <section id="catalogo" className="portal-catalogo">
          <h2>Catálogo y precios vigentes</h2>
          <div className="portal-productos">
            {catalogo.map((p) => (
              <article key={p.id} className="tarjeta portal-producto">
                <span className="categoria">{p.categoria}</span>
                <strong>{p.nombre}</strong>
                <small>{p.codigo}{p.disponible ? '' : ' · Agotado temporalmente'}</small>
                <div className="pie-producto">
                  <strong>{moneda(p.precio)}</strong>
                  <button type="button" className="boton secundario pequeno" onClick={() => cotizar(p)}
                    aria-label={`Cotizar ${p.nombre}`}>Cotizar</button>
                </div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}
