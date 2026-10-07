/**
 * Sistema de mejora continua con el ciclo PHVA (Planear, Hacer, Verificar,
 * Actuar). Cualquier empleado puede proponer una accion; supervisores y
 * gerencia la mueven por el ciclo y la cierran verificando su eficacia.
 */
import { useCallback, useEffect, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Campo, Cargando, Encabezado, Estado, erroresDeLaAPI } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { fecha } from '../utils/formato.js'
import { requerido, validar } from '../utils/validaciones.js'

const FASES = ['Planear', 'Hacer', 'Verificar', 'Actuar', 'Cerrada']
const ORIGENES = [['Empleado', 'Sugerencia de empleado'], ['Auditoria', 'Auditoría'], ['Cliente', 'Queja de cliente'],
  ['SST', 'Incidente de SST'], ['Ambiental', 'Hallazgo ambiental'], ['Indicador', 'Indicador fuera de meta']]
const NUEVA = { titulo: '', origen: 'Empleado', tipo: 'Mejora', descripcion: '' }

export default function Mejora() {
  const { puede } = useSesion()
  const [acciones, setAcciones] = useState(null)
  const [datos, setDatos] = useState(NUEVA)
  const [errores, setErrores] = useState({})
  const [aviso, setAviso] = useState({ tipo: '', texto: '' })

  const cargar = useCallback(async () => setAcciones(await obtenerTodos('/mejora/')), [])
  useEffect(() => { obtenerTodos('/mejora/').then(setAcciones).catch(() => setAcciones([])) }, [])

  async function crear(e) {
    e.preventDefault()
    const encontrados = validar(datos, { titulo: [requerido], descripcion: [requerido] })
    setErrores(encontrados)
    if (Object.keys(encontrados).length) return
    try {
      await peticion('/mejora/', { metodo: 'POST', datos })
      setDatos(NUEVA); setAviso({ tipo: 'exito', texto: 'Propuesta registrada en la fase Planear.' }); cargar()
    } catch (error) { setErrores(erroresDeLaAPI(error)) }
  }

  async function avanzar(a) {
    const siguiente = FASES[FASES.indexOf(a.fase) + 1]
    let resultado = a.resultado
    if (siguiente === 'Cerrada' && !resultado) {
      resultado = window.prompt('Para cerrar, describa cómo se verificó la eficacia de la acción:') ?? ''
      if (!resultado.trim()) return
    }
    try {
      await peticion(`/mejora/${a.id}/`, { metodo: 'PATCH', datos: { fase: siguiente, resultado } })
      cargar()
    } catch (error) { setAviso({ tipo: 'error', texto: Object.values(erroresDeLaAPI(error)).join(' ') || error.message }) }
  }

  return (
    <>
      <Encabezado titulo="Mejora continua" descripcion="Ciclo PHVA: cada problema se planea, se ejecuta, se verifica y se estandariza." />
      <Aviso tipo={aviso.tipo} alCerrar={() => setAviso({ tipo: '', texto: '' })}>{aviso.texto}</Aviso>
      <div className="ciclo-phva" aria-hidden="true">
        {['Planear', 'Hacer', 'Verificar', 'Actuar'].map((f, i) => <span key={f} className={`fase-${i}`}>{f}</span>)}
      </div>
      {!acciones ? <Cargando /> : (
        <div className="tablero-kanban phva">
          {FASES.map((fase) => (
            <section key={fase} className="columna-kanban">
              <header><strong>{fase}</strong><small>{acciones.filter((a) => a.fase === fase).length}</small></header>
              {acciones.filter((a) => a.fase === fase).map((a) => (
                <article key={a.id} className="tarjeta-kanban">
                  <strong>{a.titulo}</strong>
                  <Estado tono={a.tipo === 'Correctiva' ? 'serio' : a.tipo === 'Preventiva' ? 'aviso' : 'bien'}>{a.tipo}</Estado>
                  <small>{a.origen_nombre}</small>
                  {a.plan_accion && <small>Plan: {a.plan_accion}</small>}
                  {a.resultado && <small>Eficacia: {a.resultado}</small>}
                  <small>Responsable: {a.responsable_nombre ?? '—'} · {fecha(a.fecha_compromiso)}</small>
                  {fase !== 'Cerrada' && puede('mejora', 'editar') && (
                    <button type="button" className="boton fantasma pequeno" onClick={() => avanzar(a)}>
                      Pasar a {FASES[FASES.indexOf(fase) + 1]} →
                    </button>
                  )}
                </article>
              ))}
            </section>
          ))}
        </div>
      )}
      {puede('mejora', 'crear') && (
        <section className="tarjeta formulario-angosto">
          <h2>Proponer una mejora</h2>
          <form onSubmit={crear} noValidate>
            <Campo etiqueta="Título" nombre="titulo" value={datos.titulo} error={errores.titulo} maxLength={150}
              onChange={(e) => setDatos({ ...datos, titulo: e.target.value })} />
            <div className="fila-campos">
              <Campo como="select" etiqueta="Origen" nombre="origen" value={datos.origen} onChange={(e) => setDatos({ ...datos, origen: e.target.value })}>
                {ORIGENES.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
              </Campo>
              <Campo como="select" etiqueta="Tipo" nombre="tipo" value={datos.tipo} onChange={(e) => setDatos({ ...datos, tipo: e.target.value })}>
                {['Mejora', 'Correctiva', 'Preventiva'].map((t) => <option key={t}>{t}</option>)}
              </Campo>
            </div>
            <Campo como="textarea" rows="3" etiqueta="Situación encontrada" nombre="descripcion" value={datos.descripcion}
              error={errores.descripcion} onChange={(e) => setDatos({ ...datos, descripcion: e.target.value })} />
            <button type="submit" className="boton primario">Registrar propuesta</button>
          </form>
        </section>
      )}
    </>
  )
}
