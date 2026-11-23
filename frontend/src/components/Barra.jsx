/**
 * Controles de la barra superior: boton para volver a la pantalla anterior y
 * selector de tema (sugerencias del instructor, 8 de octubre de 2026).
 */
import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { TEMAS, aplicarTema, leerTema } from '../utils/tema.js'

export function BotonVolver() {
  const navegar = useNavigate()
  const { pathname } = useLocation()
  if (pathname === '/') return null
  // Si se entro directo por la URL no hay pantalla anterior: se va al inicio.
  const volver = () => (window.history.state?.idx > 0 ? navegar(-1) : navegar('/'))
  return (
    <button type="button" className="boton fantasma pequeno boton-volver" onClick={volver}>
      <span aria-hidden="true">←</span> Volver
    </button>
  )
}

export function SelectorTema() {
  const [tema, setTema] = useState(leerTema)
  const elegir = (nuevo) => { setTema(nuevo); aplicarTema(nuevo) }
  return (
    <div className="selector-tema" role="radiogroup" aria-label="Tema de la interfaz">
      {TEMAS.map(([clave, icono, texto]) => (
        <button key={clave} type="button" role="radio" aria-checked={tema === clave} title={texto} aria-label={texto}
          className={tema === clave ? 'activo' : undefined} onClick={() => elegir(clave)}>
          {icono}
        </button>
      ))}
    </div>
  )
}
