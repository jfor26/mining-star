/**
 * Repositorio de requisitos que exigen la autoridad minera (ANM), la
 * ambiental (CORTOLIMA) y demas entidades, con alertas de vencimiento.
 */
import { useCallback, useEffect, useState } from 'react'

import { obtenerTodos, peticion } from '../api/cliente.js'
import { Aviso, Cargando, Encabezado, Estado, Tabla } from '../components/Comunes.jsx'
import { useSesion } from '../context/SesionContext.jsx'
import { fecha } from '../utils/formato.js'

const TONO_ESTADO = { Cumplido: 'bien', EnTramite: 'aviso', Pendiente: 'serio', Vencido: 'critico' }
const ESTADOS = [['Cumplido', 'Cumplido'], ['EnTramite', 'En trámite'], ['Pendiente', 'Pendiente'], ['Vencido', 'Vencido']]

function Vencimiento({ r }) {
  if (r.dias_para_vencer === null) return <span className="texto-suave">Permanente</span>
  const tono = r.alerta === 'vencido' ? 'critico' : r.alerta === 'proximo' ? 'aviso' : 'neutro'
  const texto = r.dias_para_vencer < 0 ? `vencido hace ${-r.dias_para_vencer} d` : `en ${r.dias_para_vencer} d`
  return <span>{fecha(r.fecha_vencimiento)} <Estado tono={tono}>{texto}</Estado></span>
}

export default function Normativa() {
  const { puede } = useSesion()
  const [lista, setLista] = useState(null)
  const [filtro, setFiltro] = useState({ categoria: '', estado: '', search: '' })
  const [detalle, setDetalle] = useState(null)
  const [aviso, setAviso] = useState('')

  const consultar = useCallback(() => {
    const q = new URLSearchParams(Object.entries(filtro).filter(([, v]) => v)).toString()
    return obtenerTodos(`/normativa/${q ? `?${q}` : ''}`)
  }, [filtro])
  const cargar = useCallback(() => consultar().then(setLista), [consultar])
  useEffect(() => { consultar().then(setLista).catch(() => setLista([])) }, [consultar])

  async function cambiarEstado(r, estado) {
    await peticion(`/normativa/${r.id}/`, { metodo: 'PATCH', datos: { estado } })
    setAviso(`"${r.nombre}" quedó como ${ESTADOS.find(([c]) => c === estado)[1]}.`)
    cargar()
  }

  return (
    <>
      <Encabezado titulo="Requisitos mineros y ambientales"
        descripcion="Repositorio de obligaciones ante la ANM, CORTOLIMA, Ministerio del Trabajo, DIAN y SIC. Las fechas son de demostración: validar con el asesor jurídico minero." />
      <Aviso tipo="exito" alCerrar={() => setAviso('')}>{aviso}</Aviso>
      <section className="tarjeta">
        <div className="barra-filtros">
          <input type="search" placeholder="Buscar requisito o norma…" aria-label="Buscar" value={filtro.search}
            onChange={(e) => setFiltro({ ...filtro, search: e.target.value })} />
          <select aria-label="Categoría" value={filtro.categoria} onChange={(e) => setFiltro({ ...filtro, categoria: e.target.value })}>
            <option value="">Todas las categorías</option>
            {['Minero', 'Ambiental', 'SST', 'Tributario', 'Datos'].map((c) => <option key={c}>{c}</option>)}
          </select>
          <select aria-label="Estado" value={filtro.estado} onChange={(e) => setFiltro({ ...filtro, estado: e.target.value })}>
            <option value="">Todos los estados</option>
            {ESTADOS.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
          </select>
        </div>
        {!lista ? <Cargando /> : (
          <Tabla filas={lista} vacio="Sin requisitos." columnas={[
            { clave: 'autoridad', titulo: 'Autoridad' },
            { clave: 'nombre', titulo: 'Requisito', celda: (r) => (
              <button type="button" className="enlace" onClick={() => setDetalle(detalle?.id === r.id ? null : r)}>{r.nombre}</button>
            ) },
            { clave: 'norma', titulo: 'Norma' },
            { clave: 'periodicidad', titulo: 'Periodicidad' },
            { clave: 'fecha_vencimiento', titulo: 'Vencimiento', celda: (r) => <Vencimiento r={r} /> },
            { clave: 'estado', titulo: 'Estado', celda: (r) => (puede('normativa', 'editar') ? (
              <select aria-label={`Estado de ${r.nombre}`} value={r.estado} onChange={(e) => cambiarEstado(r, e.target.value)}>
                {ESTADOS.map(([c, n]) => <option key={c} value={c}>{n}</option>)}
              </select>
            ) : <Estado tono={TONO_ESTADO[r.estado]}>{r.estado_nombre}</Estado>) },
          ]} />
        )}
      </section>
      {detalle && (
        <section className="tarjeta">
          <h2>{detalle.nombre}</h2>
          <p><strong>{detalle.autoridad_nombre}</strong> · {detalle.categoria_nombre} · {detalle.norma}</p>
          <p>{detalle.descripcion}</p>
          <p className="texto-suave">Responsable: {detalle.responsable_nombre ?? 'sin asignar'}</p>
        </section>
      )}
    </>
  )
}
