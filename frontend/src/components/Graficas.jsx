/**
 * Tarjeta contenedora de graficas del dashboard.
 *
 * Cada grafica trae un boton "Ver tabla": quien no distingue colores, usa
 * lector de pantalla o quiere el dato exacto, lo encuentra en la tabla.
 * Los colores salen de una paleta categorica validada para daltonismo
 * (ver docs/05-interfaz-y-colores.md); el orden es fijo: cada serie
 * conserva su color aunque cambie el filtro.
 */
import { useState } from 'react'


export function TarjetaGrafica({ titulo, descripcion, filas, columnas, children, ancho = 1 }) {
  const [verTabla, setVerTabla] = useState(false)
  return (
    <section className={`tarjeta grafica ancho-${ancho}`}>
      <div className="cabecera-grafica">
        <div>
          <h2>{titulo}</h2>
          {descripcion && <p className="descripcion">{descripcion}</p>}
        </div>
        {filas && (
          <button type="button" className="boton fantasma pequeno" onClick={() => setVerTabla((v) => !v)}
            aria-pressed={verTabla}>
            {verTabla ? 'Ver gráfica' : 'Ver tabla'}
          </button>
        )}
      </div>
      {verTabla && filas ? (
        <div className="tabla-contenedor">
          <table>
            <thead><tr>{columnas.map(([, t]) => <th key={t}>{t}</th>)}</tr></thead>
            <tbody>
              {filas.map((f, i) => (
                <tr key={i}>{columnas.map(([c, , fmt]) => <td key={c}>{fmt ? fmt(f[c]) : f[c]}</td>)}</tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : children}
    </section>
  )
}

/** Tooltip con el formato de la aplicacion. */
export function Globo({ active, payload, label, formato = (v) => v }) {
  if (!active || !payload?.length) return null
  return (
    <div className="globo">
      <strong>{label}</strong>
      {payload.map((p) => (
        <div key={p.dataKey}>
          <span className="muestra" style={{ background: p.color ?? p.fill }} aria-hidden="true" />
          {p.name}: <strong>{formato(p.value)}</strong>
        </div>
      ))}
    </div>
  )
}
