/**
 * Asistente Mining Star: boton flotante y panel de chat.
 * Envia cada pregunta a POST /api/v1/asistente/ y muestra la respuesta con
 * su fuente. La conversacion vive solo en memoria (se borra al recargar).
 */
import { useEffect, useRef, useState } from 'react'

import { peticion } from '../api/cliente.js'
import { useSesion } from '../context/SesionContext.jsx'

const SUGERENCIAS_INICIALES = ['¿Cuánto stock hay de caliza?', '¿Qué requisitos vencen pronto?', '¿Cuál fue la última venta?']

export default function Asistente() {
  const { usuario } = useSesion()
  const [abierto, setAbierto] = useState(false)
  const [pregunta, setPregunta] = useState('')
  const [esperando, setEsperando] = useState(false)
  const [sugerencias, setSugerencias] = useState(SUGERENCIAS_INICIALES)
  const [mensajes, setMensajes] = useState(() => [{
    de: 'bot',
    texto: `Hola, ${usuario?.first_name || usuario?.username || ''}. Puedo consultar inventario, producción, ventas, clientes, normativa y PQRS. ¿Qué necesita saber?`,
  }])
  const fin = useRef(null)
  const campo = useRef(null)

  useEffect(() => { fin.current?.scrollIntoView?.({ block: 'end' }) }, [mensajes, abierto])
  useEffect(() => { if (abierto) campo.current?.focus() }, [abierto])

  async function preguntar(texto) {
    const limpia = texto.trim()
    if (!limpia || esperando) return
    setMensajes((m) => [...m, { de: 'yo', texto: limpia }])
    setPregunta('')
    setEsperando(true)
    try {
      const r = await peticion('/asistente/', { metodo: 'POST', datos: { pregunta: limpia } })
      setMensajes((m) => [...m, { de: 'bot', texto: r.respuesta, fuente: r.fuente }])
      if (r.sugerencias?.length) setSugerencias(r.sugerencias.filter((s) => s !== limpia).slice(0, 3))
    } catch {
      setMensajes((m) => [...m, { de: 'bot', texto: 'No pude consultar el sistema en este momento. Intente de nuevo.' }])
    } finally {
      setEsperando(false)
    }
  }

  return (
    <>
      {abierto && (
        <section className="asistente" role="dialog" aria-label="Asistente Mining Star">
          <header>
            <div>
              <strong>Asistente Mining Star</strong>
              <span>Responde con los datos del sistema según su cargo</span>
            </div>
            <button type="button" aria-label="Cerrar asistente" onClick={() => setAbierto(false)}>✕</button>
          </header>
          <div className="asistente-mensajes" aria-live="polite">
            {mensajes.map((m, i) => (
              <div key={i} className={`mensaje-${m.de}`}>
                <p>{m.texto}</p>
                {m.fuente && <small>Fuente: {m.fuente}</small>}
              </div>
            ))}
            {esperando && <div className="mensaje-bot"><p>Consultando…</p></div>}
            <div ref={fin} />
          </div>
          <div className="asistente-sugerencias">
            {sugerencias.map((s) => <button key={s} type="button" onClick={() => preguntar(s)}>{s}</button>)}
          </div>
          <form onSubmit={(e) => { e.preventDefault(); preguntar(pregunta) }}>
            <label htmlFor="pregunta-asistente" className="sr-only">Escriba su pregunta</label>
            <input id="pregunta-asistente" ref={campo} value={pregunta} maxLength={300} placeholder="Escriba su pregunta…"
              onChange={(e) => setPregunta(e.target.value)} />
            <button type="submit" aria-label="Enviar pregunta" disabled={!pregunta.trim() || esperando}>➤</button>
          </form>
        </section>
      )}
      <button type="button" className="boton-asistente" aria-expanded={abierto} onClick={() => setAbierto(!abierto)}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>
        Asistente
      </button>
    </>
  )
}
