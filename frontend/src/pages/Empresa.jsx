/**
 * La empresa: identidad, cultura, estructura y estrategia.
 * Contenido estatico tomado de src/datos/empresa.js.
 */
import { useState } from 'react'

import { Encabezado, Pestanas } from '../components/Comunes.jsx'
import {
  CANVAS, CULTURA, DIFERENCIAL, EDT_EMPRESA, EDT_SOFTWARE, IDENTIDAD, ORGANIGRAMA, PORTER,
  STAKEHOLDERS, VALOR_AGREGADO, VALORES,
} from '../datos/empresa.js'

function Nodo({ nodo }) {
  return (
    <li>
      <div className="nodo-org">
        <strong>{nodo.cargo}</strong>
        {nodo.rol && <small>Cargo en el sistema: {nodo.rol}</small>}
        {nodo.apoyo && <small className="apoyo">Staff: {nodo.apoyo.join(' · ')}</small>}
      </div>
      {nodo.hijos && <ul>{nodo.hijos.map((h) => <Nodo key={h.cargo} nodo={h} />)}</ul>}
    </li>
  )
}

function Edt({ titulo, filas }) {
  return (
    <section className="tarjeta">
      <h2>{titulo}</h2>
      <div className="edt">
        <div className="edt-raiz">0 · {titulo}</div>
        <div className="edt-ramas">
          {filas.map(([codigo, nombre, hijos]) => (
            <div key={codigo} className="edt-paquete">
              <strong>{codigo}. {nombre}</strong>
              <ul>{hijos.map((h) => <li key={h}>{h}</li>)}</ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

export default function Empresa() {
  const [pestana, setPestana] = useState('identidad')
  return (
    <>
      <Encabezado titulo="La empresa" descripcion={`${IDENTIDAD.marca} · ${IDENTIDAD.razonSocial} · ${IDENTIDAD.ubicacion}`} />
      <Pestanas activa={pestana} alCambiar={setPestana} pestanas={[
        ['identidad', 'Misión, visión y valores'], ['cultura', 'Cultura'], ['organigrama', 'Estructura'],
        ['porter', '5 fuerzas de Porter'], ['valor', 'Valor y diferencial'], ['stakeholders', 'Stakeholders'],
        ['canvas', 'Modelo de negocio'], ['edt', 'EDT'],
      ]} />

      {pestana === 'identidad' && (
        <>
          <div className="dos-iguales">
            <section className="tarjeta destacado"><h2>Misión</h2><p>{IDENTIDAD.mision}</p></section>
            <section className="tarjeta destacado"><h2>Visión 2030</h2><p>{IDENTIDAD.vision}</p></section>
          </div>
          <section className="tarjeta">
            <h2>Valores</h2>
            <div className="rejilla-valores">
              {VALORES.map(([v, d]) => <article key={v}><strong>{v}</strong><p>{d}</p></article>)}
            </div>
          </section>
        </>
      )}

      {pestana === 'cultura' && (
        <div className="dos-iguales">
          <section className="tarjeta"><h2>Principios de trabajo</h2>
            <ol className="lista-cultura">{CULTURA.principios.map((p) => <li key={p}>{p}</li>)}</ol>
          </section>
          <section className="tarjeta"><h2>Rituales</h2>
            <dl className="lista-definiciones">{CULTURA.rituales.map(([r, d]) => <div key={r}><dt>{r}</dt><dd>{d}</dd></div>)}</dl>
          </section>
        </div>
      )}

      {pestana === 'organigrama' && (
        <section className="tarjeta">
          <h2>Estructura jerárquica</h2>
          <p className="descripcion">Cada cargo tiene un rol en el sistema que define su acceso (ver Seguridad → Accesibilidad por cargo).</p>
          <div className="organigrama"><ul><Nodo nodo={ORGANIGRAMA} /></ul></div>
        </section>
      )}

      {pestana === 'porter' && (
        <section className="tarjeta">
          <h2>Las cinco fuerzas de Porter</h2>
          <p className="descripcion">Escala de 1 a 5: 5 es la mayor presión sobre la rentabilidad.</p>
          <div className="porter">
            {PORTER.map(([fuerza, nota, nivel, analisis, respuesta]) => (
              <article key={fuerza} className={`fuerza nivel-${nota}`}>
                <header><strong>{fuerza}</strong><span className="nota">{nivel} · {nota}/5</span></header>
                <div className="barra-nota" role="img" aria-label={`${nota} de 5`}><span style={{ width: `${nota * 20}%` }} /></div>
                <p>{analisis}</p>
                <p><strong>Respuesta:</strong> {respuesta}</p>
              </article>
            ))}
          </div>
          <p className="conclusion">Riesgo principal: el poder de los compradores. Ventaja principal: un título vigente cerca del consumo es difícil de replicar.</p>
        </section>
      )}

      {pestana === 'valor' && (
        <div className="dos-iguales">
          <section className="tarjeta"><h2>Agregación de valor</h2>
            <ol className="cadena-valor">{VALOR_AGREGADO.map(([e, d]) => <li key={e}><strong>{e}</strong><span>{d}</span></li>)}</ol>
          </section>
          <section className="tarjeta"><h2>Factor diferencial</h2>
            <dl className="lista-definiciones">{DIFERENCIAL.map(([e, d]) => <div key={e}><dt>{e}</dt><dd>{d}</dd></div>)}</dl>
          </section>
        </div>
      )}

      {pestana === 'stakeholders' && (
        <section className="tarjeta">
          <h2>Partes interesadas (stakeholders)</h2>
          <div className="tabla-contenedor">
            <table>
              <thead><tr><th>Interesado</th><th>Tipo</th><th>Poder</th><th>Interés</th><th>Estrategia</th></tr></thead>
              <tbody>{STAKEHOLDERS.map(([n, t, p, i, e]) => (
                <tr key={n}><td>{n}</td><td>{t}</td><td>{p}</td><td>{i}</td><td>{e}</td></tr>
              ))}</tbody>
            </table>
          </div>
        </section>
      )}

      {pestana === 'canvas' && (
        <section className="tarjeta">
          <h2>Modelo de negocio (lienzo Canvas)</h2>
          <div className="canvas">
            {CANVAS.map(([bloque, items], i) => (
              <article key={bloque} className={`bloque-canvas b${i}`}>
                <strong>{bloque}</strong>
                <ul>{items.map((it) => <li key={it}>{it}</li>)}</ul>
              </article>
            ))}
          </div>
        </section>
      )}

      {pestana === 'edt' && (
        <>
          <Edt titulo="EDT del proyecto de software Mining Star ERP" filas={EDT_SOFTWARE} />
          <Edt titulo="EDT de la empresa (reactivación del título minero)" filas={EDT_EMPRESA} />
        </>
      )}
    </>
  )
}
