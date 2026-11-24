/**
 * Campana de notificaciones de la barra superior.
 * Consulta GET /api/v1/notificaciones/ al cargar y cada 2 minutos; los avisos
 * son solo de los modulos del cargo del usuario (los filtra la API).
 */
import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { peticion } from '../api/cliente.js'

const TIPOS = {
  normativa: { texto: 'Normativa', icono: 'M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M9 13h6M9 17h4' },
  inventario: { texto: 'Inventario', icono: 'M21 8l-9-5-9 5 9 5 9-5zM3 8v8l9 5 9-5V8' },
  tienda: { texto: 'Tienda', icono: 'M6 6h15l-2 9H8zM6 6 5 3H2M9 20h.01M18 20h.01' },
  crm: { texto: 'CRM', icono: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 11h-6' },
}
const INTERVALO_MS = 120000

export default function Campana() {
  const navegar = useNavigate()
  const [datos, setDatos] = useState({ sin_leer: 0, resultados: [] })
  const [abierta, setAbierta] = useState(false)
  const [filtro, setFiltro] = useState('todas')
  const caja = useRef(null)

  const cargar = useCallback(() => {
    peticion('/notificaciones/').then(setDatos).catch(() => {})
  }, [])

  useEffect(() => {
    cargar()
    const intervalo = setInterval(cargar, INTERVALO_MS)
    return () => clearInterval(intervalo)
  }, [cargar])

  // Cerrar con Escape o al hacer clic fuera del panel.
  useEffect(() => {
    if (!abierta) return undefined
    const fuera = (e) => { if (caja.current && !caja.current.contains(e.target)) setAbierta(false) }
    const escape = (e) => { if (e.key === 'Escape') setAbierta(false) }
    document.addEventListener('mousedown', fuera)
    document.addEventListener('keydown', escape)
    return () => { document.removeEventListener('mousedown', fuera); document.removeEventListener('keydown', escape) }
  }, [abierta])

  async function marcar(cuerpo) {
    await peticion('/notificaciones/', { metodo: 'POST', datos: cuerpo }).catch(() => {})
    cargar()
  }

  function abrir(aviso) {
    if (!aviso.leida) marcar({ claves: [aviso.clave] })
    setAbierta(false)
    navegar(aviso.ruta)
  }

  const tiposPresentes = [...new Set(datos.resultados.map((a) => a.tipo))]
  const visibles = datos.resultados.filter((a) => (
    filtro === 'todas' || (filtro === 'sinleer' ? !a.leida : a.tipo === filtro)
  ))
  const etiqueta = datos.sin_leer
    ? `Notificaciones: ${datos.sin_leer} sin leer`
    : 'Notificaciones: no hay avisos nuevos'

  return (
    <div className="campana" ref={caja}>
      <button type="button" className="boton-campana" aria-label={etiqueta} aria-expanded={abierta}
        aria-haspopup="dialog" onClick={() => setAbierta(!abierta)}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 0 1-3.4 0" />
        </svg>
        {datos.sin_leer > 0 && <span className="contador-campana" aria-hidden="true">{datos.sin_leer > 99 ? '99+' : datos.sin_leer}</span>}
      </button>

      {abierta && (
        <section className="panel-avisos" role="dialog" aria-label="Notificaciones">
          <header>
            <div className="fila-titulo">
              <h2>Notificaciones</h2>
              {datos.sin_leer > 0 && (
                <button type="button" className="enlace" onClick={() => marcar({ todas: true })}>Marcar todo como leído</button>
              )}
            </div>
            <div className="chips" role="group" aria-label="Filtrar notificaciones">
              {[['todas', 'Todas'], ['sinleer', `Sin leer (${datos.sin_leer})`],
                ...tiposPresentes.map((t) => [t, TIPOS[t]?.texto ?? t])].map(([clave, texto]) => (
                <button key={clave} type="button" className={`chip${filtro === clave ? ' activo' : ''}`}
                  aria-pressed={filtro === clave} onClick={() => setFiltro(clave)}>{texto}</button>
              ))}
            </div>
          </header>
          <ul className="lista-avisos">
            {visibles.length === 0 && <li className="sin-avisos">No hay avisos en esta vista.</li>}
            {visibles.map((a) => (
              <li key={a.clave}>
                <button type="button" className={`aviso-item tipo-${a.tipo}${a.leida ? '' : ' nuevo'}`} onClick={() => abrir(a)}>
                  <span className="icono-aviso" aria-hidden="true">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
                      strokeLinecap="round" strokeLinejoin="round"><path d={TIPOS[a.tipo]?.icono} /></svg>
                  </span>
                  <span className="cuerpo-aviso">
                    <strong>{a.titulo}{!a.leida && <span className="sr-only"> (sin leer)</span>}</strong>
                    <span>{a.texto}</span>
                    <small>{TIPOS[a.tipo]?.texto}</small>
                  </span>
                </button>
              </li>
            ))}
          </ul>
          <footer>Solo ve los avisos de los módulos de su cargo.</footer>
        </section>
      )}
    </div>
  )
}
