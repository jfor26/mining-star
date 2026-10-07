/**
 * CRM: embudo de oportunidades por etapa e historial de interacciones.
 * Consume /crm/oportunidades/ y /crm/interacciones/.
 */
import { useCallback, useEffect, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Pestanas, Tabla, erroresDeLaAPI } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { fecha, moneda } from '../utils/formato.js'
import { requerido, validar } from '../utils/validaciones.js'

const ETAPAS = [
  ['Prospecto', 'Prospecto'], ['Contactado', 'Contactado'], ['Cotizacion', 'Cotización'],
  ['Negociacion', 'Negociación'], ['Ganada', 'Ganada'], ['Perdida', 'Perdida'],
]
const TIPOS = ['Llamada', 'Correo', 'Visita', 'Reunion', 'WhatsApp']
const NUEVA = { cliente: '', titulo: '', etapa: 'Prospecto', valor_estimado: '', fecha_cierre_estimada: '' }
const NUEVA_INT = { cliente: '', oportunidad: '', tipo: 'Llamada', descripcion: '', proxima_accion: '' }

export default function Crm() {
  const { puede } = useSesion()
  const [pestana, setPestana] = useState('embudo')
  const [oportunidades, setOportunidades] = useState(null)
  const [interacciones, setInteracciones] = useState([])
  const [clientes, setClientes] = useState([])
  const [datos, setDatos] = useState(NUEVA)
  const [datosInt, setDatosInt] = useState(NUEVA_INT)
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })

  const cargar = useCallback(() => Promise.all([
    obtenerTodos('/crm/oportunidades/'), peticion('/crm/interacciones/?ordering=-fecha'),
  ]).then(([ops, ints]) => { setOportunidades(ops); setInteracciones(ints.results) }), [])

  useEffect(() => {
    Promise.all([obtenerTodos('/crm/oportunidades/'), peticion('/crm/interacciones/?ordering=-fecha')])
      .then(([ops, ints]) => { setOportunidades(ops); setInteracciones(ints.results) })
      .catch(() => setOportunidades([]))
    obtenerTodos('/clientes/?ordering=nombre').then(setClientes).catch(() => {})
  }, [cargar])

  async function mover(op, etapa) {
    try {
      await peticion(`/crm/oportunidades/${op.id}/`, { metodo: 'PATCH', datos: { etapa } })
      cargar()
    } catch (error) { setAviso({ tipo: 'error', texto: error.message }) }
  }

  async function crearOportunidad(e) {
    e.preventDefault()
    const encontrados = validar(datos, { cliente: [requerido], titulo: [requerido], valor_estimado: [requerido] })
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return
    try {
      await peticion('/crm/oportunidades/', {
        metodo: 'POST', datos: { ...datos, fecha_cierre_estimada: datos.fecha_cierre_estimada || null },
      })
      setDatos(NUEVA); setAviso({ tipo: 'exito', texto: 'Oportunidad creada.' }); cargar()
    } catch (error) { setErrores(erroresDeLaAPI(error)) }
  }

  async function crearInteraccion(e) {
    e.preventDefault()
    const encontrados = validar(datosInt, { cliente: [requerido], descripcion: [requerido] })
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return
    try {
      await peticion('/crm/interacciones/', {
        metodo: 'POST', datos: { ...datosInt, oportunidad: datosInt.oportunidad || null },
      })
      setDatosInt(NUEVA_INT); setAviso({ tipo: 'exito', texto: 'Interacción registrada.' }); cargar()
    } catch (error) { setErrores(erroresDeLaAPI(error)) }
  }

  if (!oportunidades) return <Cargando />
  const puedeEditar = puede('crm', 'editar')

  return (
    <>
      <Encabezado titulo="CRM" descripcion="Gestión de la relación con clientes: oportunidades, etapas y seguimiento." />
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      <Pestanas activa={pestana} alCambiar={setPestana}
        pestanas={[['embudo', 'Embudo de ventas'], ['interacciones', 'Interacciones'], ['nueva', 'Nueva oportunidad']]} />

      {pestana === 'embudo' && (
        <div className="tablero-kanban">
          {ETAPAS.map(([clave, nombre], i) => {
            const enEtapa = oportunidades.filter((o) => o.etapa === clave)
            const suma = enEtapa.reduce((s, o) => s + Number(o.valor_estimado), 0)
            return (
              <section key={clave} className={`columna-kanban etapa-${clave.toLowerCase()}`}>
                <header><strong>{nombre}</strong><small>{enEtapa.length} · {moneda(suma)}</small></header>
                {enEtapa.map((o) => (
                  <article key={o.id} className="tarjeta-kanban">
                    <strong>{o.titulo}</strong>
                    <small>{o.cliente_nombre}</small>
                    <span className="valor">{moneda(o.valor_estimado)}</span>
                    <small>Probabilidad {o.probabilidad} % · ponderado {moneda(o.valor_ponderado)}</small>
                    {puedeEditar && (
                      <div className="mover">
                        {i > 0 && <button type="button" className="boton fantasma pequeno" aria-label={`Mover a ${ETAPAS[i - 1][1]}`}
                          onClick={() => mover(o, ETAPAS[i - 1][0])}>←</button>}
                        {i < ETAPAS.length - 1 && <button type="button" className="boton fantasma pequeno" aria-label={`Mover a ${ETAPAS[i + 1][1]}`}
                          onClick={() => mover(o, ETAPAS[i + 1][0])}>→</button>}
                      </div>
                    )}
                  </article>
                ))}
              </section>
            )
          })}
        </div>
      )}

      {pestana === 'interacciones' && (
        <div className="dos-columnas">
          {puede('crm', 'crear') && (
            <section className="tarjeta">
              <h2>Registrar interacción</h2>
              <form onSubmit={crearInteraccion} noValidate>
                <Campo como="select" etiqueta="Cliente" nombre="cliente" value={datosInt.cliente} error={errores.cliente}
                  onChange={(e) => setDatosInt({ ...datosInt, cliente: e.target.value, oportunidad: '' })}>
                  <option value="">Seleccione</option>
                  {clientes.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
                </Campo>
                <Campo como="select" etiqueta="Oportunidad (opcional)" nombre="oportunidad" value={datosInt.oportunidad}
                  error={errores.oportunidad} onChange={(e) => setDatosInt({ ...datosInt, oportunidad: e.target.value })}>
                  <option value="">Ninguna</option>
                  {oportunidades.filter((o) => String(o.cliente) === datosInt.cliente).map((o) => <option key={o.id} value={o.id}>{o.titulo}</option>)}
                </Campo>
                <Campo como="select" etiqueta="Tipo" nombre="tipo" value={datosInt.tipo} onChange={(e) => setDatosInt({ ...datosInt, tipo: e.target.value })}>
                  {TIPOS.map((t) => <option key={t}>{t}</option>)}
                </Campo>
                <Campo como="textarea" etiqueta="Descripción" nombre="descripcion" rows="3" maxLength={500}
                  value={datosInt.descripcion} error={errores.descripcion} onChange={(e) => setDatosInt({ ...datosInt, descripcion: e.target.value })} />
                <Campo etiqueta="Próxima acción" nombre="proxima_accion" value={datosInt.proxima_accion}
                  onChange={(e) => setDatosInt({ ...datosInt, proxima_accion: e.target.value })} />
                <button type="submit" className="boton primario">Guardar interacción</button>
              </form>
            </section>
          )}
          <section className="tarjeta">
            <Tabla filas={interacciones} vacio="Sin interacciones." columnas={[
              { clave: 'fecha', titulo: 'Fecha', celda: (i) => fecha(i.fecha) },
              { clave: 'cliente_nombre', titulo: 'Cliente' },
              { clave: 'tipo_nombre', titulo: 'Tipo' },
              { clave: 'descripcion', titulo: 'Descripción' },
              { clave: 'proxima_accion', titulo: 'Próxima acción' },
            ]} />
          </section>
        </div>
      )}

      {pestana === 'nueva' && (
        puede('crm', 'crear') ? (
          <section className="tarjeta formulario-angosto">
            <h2>Nueva oportunidad</h2>
            <form onSubmit={crearOportunidad} noValidate>
              <Campo como="select" etiqueta="Cliente" nombre="cliente" value={datos.cliente} error={errores.cliente}
                onChange={(e) => setDatos({ ...datos, cliente: e.target.value })}>
                <option value="">Seleccione</option>
                {clientes.map((c) => <option key={c.id} value={c.id}>{c.nombre}</option>)}
              </Campo>
              <Campo etiqueta="Título" nombre="titulo" value={datos.titulo} error={errores.titulo} maxLength={150}
                onChange={(e) => setDatos({ ...datos, titulo: e.target.value })} />
              <div className="fila-campos">
                <Campo etiqueta="Valor estimado (COP)" nombre="valor_estimado" type="number" min="0" value={datos.valor_estimado}
                  error={errores.valor_estimado} onChange={(e) => setDatos({ ...datos, valor_estimado: e.target.value })} />
                <Campo como="select" etiqueta="Etapa" nombre="etapa" value={datos.etapa} onChange={(e) => setDatos({ ...datos, etapa: e.target.value })}>
                  {ETAPAS.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
                </Campo>
              </div>
              <Campo etiqueta="Cierre estimado" nombre="fecha_cierre_estimada" type="date" value={datos.fecha_cierre_estimada}
                onChange={(e) => setDatos({ ...datos, fecha_cierre_estimada: e.target.value })} />
              <button type="submit" className="boton primario">Crear oportunidad</button>
            </form>
          </section>
        ) : <p>Su cargo solo puede consultar el CRM.</p>
      )}
    </>
  )
}
